import pandas as pd
import openpyxl
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from openpyxl.workbook import Workbook

from .forms import PurchaseOrderForm, UploadFileForm, ItemInventoryForm
from .models import PurchaseOrder, ArchiveFolder, ItemInventory, SupplierFolder, InventoryHistory, SiteInventoryFolder, \
    ClientInventoryFolder
from datetime import datetime
from openpyxl.styles import Font, PatternFill
from io import BytesIO
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum
# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'authentication/login.html', {'error': 'Invalid credentials'})
    return render(request, 'authentication/login.html')


@login_required
def dashboard_view(request):
    if request.user.groups.filter(name='Accountant').exists():
        return render(request, 'dashboards/accountant_dashboard.html')
    elif request.user.groups.filter(name='Front Desk').exists():
        return purchase_order_list(request)
    elif request.user.groups.filter(name='Inventory Manager').exists():
        return inventory_table(request)
    elif request.user.is_superuser:
        return render(request, 'dashboards/front_desk_dashboard.html')
    else:
        return HttpResponse('No role assigned')


def logout_view(request):
    logout(request)
    return redirect('login')

# For Creating or Adding Records

def purchase_order_create(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            # Save the new purchase order
            purchase_order = form.save(commit=False)

            # Get the supplier name from the purchase order
            supplier_name = purchase_order.supplier

            if supplier_name:
                # Create or get the SupplierFolder associated with this supplier
                folder, created = SupplierFolder.objects.get_or_create(name=supplier_name)

                # Associate the new purchase order with the supplier's folder
                purchase_order.supplier_folder = folder
                purchase_order.save()

                # Ensure all existing purchase orders with the same supplier are associated with the folder
                matching_orders = PurchaseOrder.objects.filter(supplier=supplier_name, supplier_folder__isnull=True)
                for order in matching_orders:
                    order.supplier_folder = folder
                    order.save()

            # Check if an inventory record for the item exists
            inventory_item = ItemInventory.objects.filter(
                supplier=purchase_order.supplier,
                po_product_name=purchase_order.particulars,
                unit=purchase_order.unit,
                price=purchase_order.price,
            ).first()

            if inventory_item:
                # Update existing inventory record
                inventory_item.quantity_in += purchase_order.quantity
            else:
                # Create a new inventory record
                inventory_item = ItemInventory(
                    supplier=purchase_order.supplier,
                    po_product_name=purchase_order.particulars,
                    unit=purchase_order.unit,
                    quantity_in=purchase_order.quantity,
                    price=purchase_order.price,
                    delivery_ref=purchase_order.delivery_ref,
                    delivery_no=purchase_order.delivery_no,
                    invoice_type=purchase_order.invoice_type,
                    invoice_no=purchase_order.invoice_no,
                )
            inventory_item.save()

            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error'})
    else:
        form = PurchaseOrderForm()

    return render(request, 'records/purchase_order_form.html', {'form': form})


def purchase_order_edit(request, id):
    order = get_object_or_404(PurchaseOrder, id=id)

    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=order)
        if form.is_valid():
            purchase_order = form.save()

            # Update or create inventory item
            inventory_item = ItemInventory.objects.filter(
                supplier=purchase_order.supplier,
                po_product_name=purchase_order.particulars,
                unit=purchase_order.unit,
                price=purchase_order.price,
            ).first()

            if inventory_item:
                # Update existing inventory record
                inventory_item.quantity_in += purchase_order.quantity
            else:
                # Create a new inventory record
                inventory_item = ItemInventory(
                    supplier=purchase_order.supplier,
                    po_product_name=purchase_order.particulars,
                    unit=purchase_order.unit,
                    quantity_in=purchase_order.quantity,
                    price=purchase_order.price,
                )

            # Save the inventory item
            inventory_item.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('dashboard')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error'})
    else:
        form = PurchaseOrderForm(instance=order)

    return render(request, 'records/purchase_order_edit.html', {'form': form, 'order': order})



def purchase_order_list(request):
    query = request.GET.get('q')  # Single search input
    page_number = request.GET.get('page', 1)

    orders_list = PurchaseOrder.objects.filter(folder__isnull=True, archived=False)

    # If there's a search query, filter the orders accordingly
    if query:
        try:
            # Try to interpret the query as a date first
            date_obj = datetime.strptime(query, '%b %d, %Y').date()
            orders_list = orders_list.filter(date=date_obj)
        except ValueError:
            try:
                # Try parsing month and year only (e.g., "Aug 2024")
                date_obj = datetime.strptime(query, '%b %Y')
                orders_list = orders_list.filter(date__year=date_obj.year, date__month=date_obj.month)
            except ValueError:
                try:
                    # Try parsing full month name and year (e.g., "August 2024")
                    date_obj = datetime.strptime(query, '%B %Y')
                    orders_list = orders_list.filter(date__year=date_obj.year, date__month=date_obj.month)
                except ValueError:
                    try:
                        # Try parsing month only (e.g., "08" for August or "11" for November)
                        month_number = int(query)
                        orders_list = orders_list.filter(date__month=month_number)
                    except ValueError:
                        # If not a date, treat it as a general text search
                        orders_list = orders_list.filter(
                            Q(po_number__icontains=query) |
                            Q(purchaser__icontains=query) |
                            Q(brand__icontains=query) |
                            Q(item_code__icontains=query) |
                            Q(particulars__icontains=query) |
                            Q(quantity__icontains=query) |
                            Q(unit__icontains=query) |
                            Q(price__icontains=query) |
                            Q(total_amount__icontains=query) |
                            Q(site_delivered__icontains=query) |
                            Q(fbbd_ref_number__icontains=query) |
                            Q(remarks__icontains=query) |
                            Q(supplier__icontains=query) |
                            Q(delivery_ref__icontains=query) |
                            Q(delivery_no__icontains=query) |
                            Q(invoice_type__icontains=query) |
                            Q(invoice_no__icontains=query) |
                            Q(payment_req_ref__icontains=query) |
                            Q(payment_details__icontains=query) |
                            Q(remarks2__icontains=query)
                        )

    paginator = Paginator(orders_list, 20)  # Show 20 orders per page
    try:
        orders = paginator.page(page_number)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    folders = ArchiveFolder.objects.all()

    return render(request, 'dashboards/front_desk_dashboard.html', {
        'orders': orders,
        'query': query,
        'page_number': page_number,
        'folders': folders
    })




# --------------------------------------For Exporting Records----------------------------------------------
def export_orders_to_excel(request):
    query = request.GET.get('q')  # Search query parameter
    date_query = request.GET.get('date')  # Date query parameter

    # Start with all orders
    orders_list = PurchaseOrder.objects.filter(folder__isnull=True)

    # Apply search filter
    if query:
        orders_list = orders_list.filter(
            Q(date__icontains=query) |
            Q(po_number__icontains=query) |
            Q(purchaser__icontains=query) |
            Q(brand__icontains=query) |
            Q(item_code__icontains=query) |
            Q(particulars__icontains=query) |
            Q(quantity__icontains=query) |
            Q(unit__icontains=query) |
            Q(price__icontains=query) |
            Q(total_amount__icontains=query) |
            Q(site_delivered__icontains=query) |
            Q(fbbd_ref_number__icontains=query) |
            Q(remarks__icontains=query) |
            Q(supplier__icontains=query) |
            Q(delivery_ref__icontains=query) |
            Q(delivery_no__icontains=query) |
            Q(invoice_type__icontains=query) |
            Q(invoice_no__icontains=query) |
            Q(payment_req_ref__icontains=query) |
            Q(payment_details__icontains=query) |
            Q(remarks2__icontains=query)
        )

    # Apply date filter
    if date_query:
        try:
            date_obj = datetime.strptime(date_query, '%b %d, %Y').date()
            orders_list = orders_list.filter(date=date_obj)
        except ValueError:
            try:
                date_obj = datetime.strptime(date_query, '%b %Y')
                orders_list = orders_list.filter(date__year=date_obj.year, date__month=date_obj.month)
            except ValueError:
                try:
                    date_obj = datetime.strptime(date_query, '%B %Y')
                    orders_list = orders_list.filter(date__year=date_obj.year, date__month=date_obj.month)
                except ValueError:
                    try:
                        month_number = int(date_query)
                        orders_list = orders_list.filter(date__month=month_number)
                    except ValueError:
                        try:
                            date_obj = datetime.strptime(date_query, '%B')
                            orders_list = orders_list.filter(date__month=date_obj.month)
                        except ValueError:
                            pass

    # Create a workbook and a sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Purchase Orders'

    header_font = Font(bold=True)
    blue_fill = PatternFill(start_color='00B0F0', end_color='00B0F0', fill_type='solid')
    currency_format = '#,##0.00'

    # Define the headers
    headers = [
        'Date', 'PO Number', 'Purchaser', 'Brand', 'Item Code', 'Particulars',
        'Quantity', 'Unit', 'Price', 'Total Amount',
        'Site Delivered', 'FBBD Ref#', 'Remarks', 'Supplier', 'Delivery Ref#',
        'Delivery No.', 'Invoice Type', 'Invoice No.', 'Payment Req Ref#',
        'Payment Details', 'Remarks2'
    ]
    sheet.append(headers)

    for cell in sheet[1]:
        cell.font = header_font
        cell.fill = blue_fill
        cell.value = cell.value.upper() if cell.value is not None else cell.value

    # Populate the sheet with data
    for order in orders_list:
        sheet.append([
            order.date.strftime('%Y-%m-%d') if order.date else 'N/A', order.po_number, order.purchaser, order.brand, order.item_code,
            order.particulars, order.quantity, order.unit, order.price, order.total_amount, order.site_delivered,
            order.fbbd_ref_number, order.remarks, order.supplier, order.delivery_ref, order.delivery_no,
            order.invoice_type, order.invoice_no, order.payment_req_ref, order.payment_details, order.remarks2
        ])

    for cell in sheet['I']:  # Assuming price is in column I (index 9)
        if cell.row > 1:  # Skip header row
            cell.number_format = currency_format

    for cell in sheet['J']:  # Assuming total_amount is in column J (index 10)
        if cell.row > 1:  # Skip header row
            cell.number_format = currency_format

    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter  # Get the column name (e.g., 'A', 'B', etc.)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)  # Add extra space for better visibility
        sheet.column_dimensions[column_letter].width = adjusted_width

    # Create an in-memory buffer
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    # Set the response to return the Excel file
    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=PurchaseOrders.xlsx'
    return response


def export_archived_orders_to_excel(request, folder_id):
    try:
        # Get the folder by ID
        folder = ArchiveFolder.objects.get(id=folder_id)
        orders_list = PurchaseOrder.objects.filter(folder=folder)

        # Create a workbook and a sheet
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Archived Orders'

        # Define header styles
        header_font = Font(bold=True)
        blue_fill = PatternFill(start_color='00B0F0', end_color='00B0F0', fill_type='solid')
        currency_format = '#,##0.00'

        # Define the headers
        headers = [
            'Date', 'PO Number', 'Purchaser', 'Brand', 'Item Code', 'Particulars',
            'Quantity', 'Unit', 'Price', 'Total Amount',
            'Site Delivered', 'FBBD Ref#', 'Remarks', 'Supplier', 'Delivery Ref#',
            'Delivery No.', 'Invoice Type', 'Invoice No.', 'Payment Req Ref#',
            'Payment Details', 'Remarks2'
        ]
        sheet.append(headers)

        for cell in sheet[1]:
            cell.font = header_font
            cell.fill = blue_fill
            cell.value = cell.value.upper() if cell.value is not None else cell.value

        # Populate the sheet with data
        for order in orders_list:
            sheet.append([
                order.date.strftime('%Y-%m-%d') if order.date else 'N/A', order.po_number, order.purchaser, order.brand,
                order.item_code,
                order.particulars, order.quantity, order.unit, order.price, order.total_amount, order.site_delivered,
                order.fbbd_ref_number, order.remarks, order.supplier, order.delivery_ref, order.delivery_no,
                order.invoice_type, order.invoice_no, order.payment_req_ref, order.payment_details, order.remarks2
            ])

        for cell in sheet['I']:  # Assuming price is in column I (index 9)
            if cell.row > 1:  # Skip header row
                cell.number_format = currency_format

        for cell in sheet['J']:  # Assuming total_amount is in column J (index 10)
            if cell.row > 1:  # Skip header row
                cell.number_format = currency_format

        for column in sheet.columns:
            max_length = 0
            column_letter = column[0].column_letter  # Get the column name (e.g., 'A', 'B', etc.)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)  # Add extra space for better visibility
            sheet.column_dimensions[column_letter].width = adjusted_width

        # Create an in-memory buffer
        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        # Set the response to return the Excel file
        response = HttpResponse(
            buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=ArchivedOrders_{folder.name}.xlsx'
        return response

    except ArchiveFolder.DoesNotExist:
        return HttpResponse("Folder not found", status=404)


def export_supplier_contents(request, folder_id):
    try:
        # Get the supplier folder by ID
        folder = SupplierFolder.objects.get(id=folder_id)
        orders_list = PurchaseOrder.objects.filter(supplier=folder.name)

        # Create a workbook and a sheet
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Supplier Orders'

        # Define header styles
        header_font = Font(bold=True)
        blue_fill = PatternFill(start_color='00B0F0', end_color='00B0F0', fill_type='solid')
        currency_format = '#,##0.00'

        # Define the headers
        headers = [
            'Date', 'PO Number', 'Purchaser', 'Brand', 'Item Code', 'Particulars',
            'Quantity', 'Unit', 'Price', 'Total Amount',
            'Site Delivered', 'FBBD Ref#', 'Remarks', 'Supplier', 'Delivery Ref#',
            'Delivery No.', 'Invoice Type', 'Invoice No.', 'Payment Req Ref#',
            'Payment Details', 'Remarks2'
        ]
        sheet.append(headers)

        for cell in sheet[1]:
            cell.font = header_font
            cell.fill = blue_fill
            cell.value = cell.value.upper() if cell.value is not None else cell.value

        # Populate the sheet with data
        for order in orders_list:
            sheet.append([
                order.date.strftime('%Y-%m-%d') if order.date else 'N/A', order.po_number, order.purchaser, order.brand,
                order.item_code,
                order.particulars, order.quantity, order.unit, order.price, order.total_amount, order.site_delivered,
                order.fbbd_ref_number, order.remarks, order.supplier, order.delivery_ref, order.delivery_no,
                order.invoice_type, order.invoice_no, order.payment_req_ref, order.payment_details, order.remarks2
            ])

        for cell in sheet['I']:  # Assuming price is in column I (index 9)
            if cell.row > 1:  # Skip header row
                cell.number_format = currency_format

        for cell in sheet['J']:  # Assuming total_amount is in column J (index 10)
            if cell.row > 1:  # Skip header row
                cell.number_format = currency_format

        for column in sheet.columns:
            max_length = 0
            column_letter = column[0].column_letter  # Get the column name (e.g., 'A', 'B', etc.)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)  # Add extra space for better visibility
            sheet.column_dimensions[column_letter].width = adjusted_width

        # Create an in-memory buffer
        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        # Set the response to return the Excel file
        response = HttpResponse(
            buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=SupplierOrders_{folder.name}.xlsx'
        return response

    except SupplierFolder.DoesNotExist:
        return HttpResponse("Supplier Folder not found", status=404)


# For Archiving Methods
def create_folder(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        if folder_name:
            try:
                ArchiveFolder.objects.create(name=folder_name)
                return JsonResponse({'status': 'success', 'message': 'Folder created successfully!'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Error creating folder: {e}'})
    return render(request, 'archive/list_folders.html')


def list_folders(request):
    folders = ArchiveFolder.objects.all()
    return render(request, 'archive/list_folders.html', {'folders': folders})


def delete_folder(request, folder_id):
    folder = ArchiveFolder.objects.get(id=folder_id)
    orders = PurchaseOrder.objects.filter(folder=folder)

    # Archive the orders instead of deleting them
    orders.update(archived=True)

    # Optionally, you might want to disassociate the orders from the folder
    # orders.update(folder=None)

    folder.delete()
    return redirect('purchase_order_list')


def archive_orders(request, folder_id):
    folder = ArchiveFolder.objects.get(id=folder_id)
    orders = PurchaseOrder.objects.filter(folder=folder)

    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'archive/archive_orders.html', {
        'folder': folder,
        'orders': page_obj
    })


def move_orders_to_folder(request):
    if request.method == 'POST':
        folder_id = request.POST.get('folder')
        order_ids = request.POST.getlist('orders')

        if not folder_id or not order_ids:
            messages.error(request, 'Please select both a folder and orders to move.')
            return redirect('purchase_order_list')

        folder = get_object_or_404(ArchiveFolder, id=folder_id)

        try:
            updated_orders = PurchaseOrder.objects.filter(id__in=order_ids).update(folder=folder)
            if updated_orders > 0:
                messages.success(request, f'{updated_orders} orders successfully moved to {folder.name}.')
            else:
                messages.warning(request, 'No orders were moved.')
        except Exception as e:
            messages.error(request, f'An error occurred while moving orders: {str(e)}')
            return redirect('purchase_order_list')

        return redirect('purchase_order_list')

    return redirect('purchase_order_list')



# For Uploading Files
def handle_uploaded_file(f):
    df = pd.read_excel(f, engine='openpyxl')
    df = df.fillna('')  # Replace NaN with an empty string

    for _, row in df.iterrows():
        # Create or update the PurchaseOrder
        purchase_order = PurchaseOrder(
            date=row.get('DATE'),
            po_number=row.get('PO NUMBER'),
            purchaser=row.get('PURCHASER'),
            brand=row.get('BRAND'),
            item_code=row.get('ITEM CODE'),
            particulars=row.get('PARTICULAR'),
            quantity=row.get('QTY'),
            unit=row.get('UNIT'),
            price=row.get('PRICE'),
            total_amount=row.get('T. AMOUNT'),
            site_delivered=row.get('SITE DELIVERED'),
            fbbd_ref_number=row.get('FBBD REF#'),
            remarks=row.get('REMARKS'),
            supplier=row.get('SUPPLIER'),
            delivery_ref=row.get('DELIVERY REF#'),
            delivery_no=row.get('DELIVERY NO.'),
            invoice_type=row.get('INVOICE TYPE'),
            invoice_no=row.get('INVOICE NO.'),
            payment_req_ref=row.get('PAYMENT REQ REF#'),
            payment_details=row.get('PAYMENT DETAILS'),
            remarks2=row.get('REMARKS2')
        )

        # Check if the supplier folder exists or create a new one
        supplier_name = purchase_order.supplier
        if supplier_name:
            folder, created = SupplierFolder.objects.get_or_create(name=supplier_name)
            # Optionally handle updates to the folder if needed

            # Update the purchase order to reference the SupplierFolder
            purchase_order.supplier_folder = folder

        # Save the purchase order
        purchase_order.save()

        # Check if an inventory record for the item exists
        inventory_item = ItemInventory.objects.filter(
            supplier=purchase_order.supplier,
            po_product_name=purchase_order.particulars,
            unit=purchase_order.unit,
            price=purchase_order.price,
        ).first()

        if inventory_item:
            # Update existing inventory record
            inventory_item.quantity_in += purchase_order.quantity
        else:
            # Create a new inventory record
            inventory_item = ItemInventory(
                supplier=purchase_order.supplier,
                po_product_name=purchase_order.particulars,
                unit=purchase_order.unit,
                quantity_in=purchase_order.quantity,
                price=purchase_order.price,
                delivery_ref=purchase_order.delivery_ref,
                delivery_no=purchase_order.delivery_no,
                invoice_type=purchase_order.invoice_type,
                invoice_no=purchase_order.invoice_no,
            )

        # Save the inventory item
        inventory_item.save()


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                handle_uploaded_file(request.FILES['file'])
                return JsonResponse({'status': 'success', 'message': 'File uploaded and data imported successfully.'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        form = UploadFileForm()
    return render(request, 'records/upload.html', {'form': form})


# -----------------------------For INVENTORY----------------------------------------------

def inventory_table(request):
    query = request.GET.get('q')  # 'q' is the name of the search input field

    # Start with all inventory items
    inventory_items = ItemInventory.objects.all()

    # If there's a search query, filter the inventory items accordingly
    if query:
        inventory_items = inventory_items.filter(
            Q(item_code__icontains=query) |
            Q(supplier__icontains=query) |
            Q(po_product_name__icontains=query) |
            Q(new_product_name__icontains=query) |
            Q(unit__icontains=query) |
            Q(quantity_in__icontains=query) |
            Q(quantity_out__icontains=query) |
            Q(price__icontains=query) |
            Q(stock__icontains=query)
        )

    paginator = Paginator(inventory_items, 20)  # Paginate after every 20 entries
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboards/inventory_clerk_dashboard.html', {
        'page_obj': page_obj
    })


def inventory_edit(request, id):
    inventory_item = get_object_or_404(ItemInventory, id=id)

    if request.method == 'POST':
        form = ItemInventoryForm(request.POST, instance=inventory_item)
        if form.is_valid():
            updated_item = form.save(commit=False)
            location_type = form.cleaned_data.get('location_type')
            location_name = form.cleaned_data.get('location_name')
            updated_item.site_or_client_choice = location_type

            if location_type == 'site':
                # Create or get the site folder
                folder, created = SiteInventoryFolder.objects.get_or_create(name=location_name)
                updated_item.site_inventory_folder = folder

                # Save the updated item
                updated_item.save()

                # Update or associate existing transactions with the folder
                InventoryHistory.objects.filter(site_delivered=location_name).update(site_inventory_folder=folder)

            elif location_type == 'client':
                # Create or get the client folder
                client_folder, created = ClientInventoryFolder.objects.get_or_create(name=location_name)
                updated_item.client_inventory_folder = client_folder

                # Save the updated item
                updated_item.save()

                # Update or associate existing transactions with the client folder
                InventoryHistory.objects.filter(client=location_name).update(client_inventory_folder=client_folder)

            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    else:
        form = ItemInventoryForm(instance=inventory_item)

    return render(request, 'inventory/inventory_edit.html', {'form': form, 'item': inventory_item})


def export_inventory_to_excel(request):
    query = request.GET.get('q')  # Search query parameter

    # Start with all inventory items
    inventory_list = ItemInventory.objects.all()

    # Apply search filter
    if query:
        inventory_list = inventory_list.filter(
            Q(item_code__icontains=query) |
            Q(supplier__icontains=query) |
            Q(po_product_name__icontains=query) |
            Q(new_product_name__icontains=query) |
            Q(unit__icontains=query) |
            Q(quantity_in__icontains=query) |
            Q(quantity_out__icontains=query) |
            Q(stock__icontains=query) |
            Q(price__icontains=query) |
            Q(total_amount__icontains=query)
        )

    # Create a workbook and a sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Inventory'

    header_font = Font(bold=True)
    blue_fill = PatternFill(start_color='00B0F0', end_color='00B0F0', fill_type='solid')
    currency_format = '#,##0.00'

    # Define the headers
    headers = [
        'Item Code', 'Supplier', 'PO Product Name', 'New Product Name', 'Unit',
        'Quantity In', 'Quantity Out', 'Stock', 'Price', 'Total Amount'
    ]
    sheet.append(headers)

    for cell in sheet[1]:
        cell.font = header_font
        cell.fill = blue_fill

    # Populate the sheet with data
    for item in inventory_list:
        sheet.append([
            item.item_code, item.supplier, item.po_product_name, item.new_product_name,
            item.unit, item.quantity_in, item.quantity_out, item.stock,
            item.price, item.total_amount
        ])

    for cell in sheet['I']:  # Assuming price is in column I (index 9)
        if cell.row > 1:  # Skip header row
            cell.number_format = currency_format

    for cell in sheet['J']:  # Assuming total_amount is in column J (index 10)
        if cell.row > 1:  # Skip header row
            cell.number_format = currency_format

    # Adjust column widths
    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter  # Get the column name (e.g., 'A', 'B', etc.)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)  # Add extra space for better visibility
        sheet.column_dimensions[column_letter].width = adjusted_width

    # Create an in-memory buffer
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    # Set the response to return the Excel file
    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=Inventory.xlsx'
    return response


def export_site_folder_contents(request, folder_id):
    try:
        # Get the site inventory folder by ID
        folder = SiteInventoryFolder.objects.get(id=folder_id)
        transactions = InventoryHistory.objects.filter(site_inventory_folder=folder)

        # Create a workbook and a sheet
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Site Inventory Records'

        # Define header styles
        header_font = Font(bold=True)
        blue_fill = PatternFill(start_color='00B0F0', end_color='00B0F0', fill_type='solid')
        currency_format = '#,##0.00'

        # Define the headers
        headers = [
            'Transaction ID', 'Site Delivered', 'Date', 'Item', 'Quantity In', 'Quantity Out',
            'Price', 'Total Amount', 'Delivery Ref', 'Delivery No.'
        ]
        sheet.append(headers)

        for cell in sheet[1]:
            cell.font = header_font
            cell.fill = blue_fill
            cell.value = cell.value.upper() if cell.value is not None else cell.value

        # Populate the sheet with data
        for transaction in transactions:
            sheet.append([
                transaction.id,
                transaction.site_delivered,
                transaction.date.strftime('%Y-%m-%d') if transaction.date else 'N/A',
                str(transaction.item),  # Convert ItemInventory instance to string
                transaction.quantity_in,
                transaction.quantity_out,
                transaction.price,
                transaction.total_amount,
                transaction.delivery_ref,
                transaction.delivery_no,
            ])

        # Apply currency format to price and total_amount columns
        for cell in sheet['G']:  # Assuming price is in column G (index 7)
            if cell.row > 1:  # Skip header row
                cell.number_format = currency_format

        for cell in sheet['H']:  # Assuming total_amount is in column H (index 8)
            if cell.row > 1:  # Skip header row
                cell.number_format = currency_format

        # Adjust column widths
        for column in sheet.columns:
            max_length = 0
            column_letter = column[0].column_letter  # Get the column name (e.g., 'A', 'B', etc.)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)  # Add extra space for better visibility
            sheet.column_dimensions[column_letter].width = adjusted_width

        # Create an in-memory buffer
        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        # Set the response to return the Excel file
        response = HttpResponse(
            buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=SiteInventory_{folder.name}.xlsx'
        return response

    except SiteInventoryFolder.DoesNotExist:
        return HttpResponse("Site Inventory Folder not found", status=404)



def export_client_folder_contents(request, folder_id):
    try:
        # Get the client inventory folder by ID
        folder = ClientInventoryFolder.objects.get(id=folder_id)
        transactions = InventoryHistory.objects.filter(client_inventory_folder=folder)

        # Create a workbook and a sheet
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Client Inventory Records'

        # Define header styles
        header_font = Font(bold=True)
        blue_fill = PatternFill(start_color='00B0F0', end_color='00B0F0', fill_type='solid')
        currency_format = '#,##0.00'

        # Define the headers
        headers = [
            'Transaction ID', 'Client', 'Date', 'Item', 'Quantity In', 'Quantity Out',
            'Price', 'Total Amount', 'Delivery Ref', 'Delivery No.', 'Invoice Type', 'Invoice#'
        ]
        sheet.append(headers)

        for cell in sheet[1]:
            cell.font = header_font
            cell.fill = blue_fill
            cell.value = cell.value.upper() if cell.value is not None else cell.value

        # Populate the sheet with data
        for transaction in transactions:
            sheet.append([
                transaction.id,
                transaction.client if transaction.client else 'N/A',  # Using client as a string directly
                transaction.date.strftime('%Y-%m-%d') if transaction.date else 'N/A',
                str(transaction.item),  # Convert ItemInventory instance to string
                transaction.quantity_in,
                transaction.quantity_out,
                transaction.price,
                transaction.total_amount,
                transaction.delivery_ref,
                transaction.delivery_no,
                transaction.invoice_type,
                transaction.invoice_no,
            ])

        # Apply currency format to price and total_amount columns
        for cell in sheet['G']:  # Assuming price is in column G (index 7)
            if cell.row > 1:  # Skip header row
                cell.number_format = currency_format

        for cell in sheet['H']:  # Assuming total_amount is in column H (index 8)
            if cell.row > 1:  # Skip header row
                cell.number_format = currency_format

        # Adjust column widths
        for column in sheet.columns:
            max_length = 0
            column_letter = column[0].column_letter  # Get the column name (e.g., 'A', 'B', etc.)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)  # Add extra space for better visibility
            sheet.column_dimensions[column_letter].width = adjusted_width

        # Create an in-memory buffer
        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        # Set the response to return the Excel file
        response = HttpResponse(
            buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=ClientInventory_{folder.name}.xlsx'
        return response

    except ClientInventoryFolder.DoesNotExist:
        return HttpResponse("Client Inventory Folder not found", status=404)


#----------------------------Transaction History----------------------------------------------
def transaction_history(request):
    query = request.GET.get('q')  # Get search query from request
    page_number = request.GET.get('page', 1)  # Get page number from request

    # Retrieve all records from InventoryHistory
    transactions = InventoryHistory.objects.all().order_by('-date')

    # Apply search filter if a query is present
    if query:
        try:
            # Try to interpret the query as a date first
            date_obj = datetime.strptime(query, '%b %d, %Y').date()
            transactions = transactions.filter(date=date_obj)
        except ValueError:
            try:
                # Try parsing month and year only (e.g., "Aug 2024")
                date_obj = datetime.strptime(query, '%b %Y')
                transactions = transactions.filter(date__year=date_obj.year, date__month=date_obj.month)
            except ValueError:
                try:
                    # Try parsing full month name and year (e.g., "August 2024")
                    date_obj = datetime.strptime(query, '%B %Y')
                    transactions = transactions.filter(date__year=date_obj.year, date__month=date_obj.month)
                except ValueError:
                    try:
                        # Try parsing month only (e.g., "08" for August or "11" for November)
                        month_number = int(query)
                        transactions = transactions.filter(date__month=month_number)
                    except ValueError:
                        # If not a date, treat it as a general text search
                        transactions = transactions.filter(
                            Q(item_code__icontains=query) |
                            Q(supplier__icontains=query) |
                            Q(po_product_name__icontains=query) |
                            Q(new_product_name__icontains=query) |
                            Q(unit__icontains=query) |
                            Q(quantity_out__icontains=query) |
                            Q(price__icontains=query) |
                            Q(total_amount__icontains=query) |
                            Q(site_delivered__icontains=query) |
                            Q(client__icontains=query)
                        )

    # Paginate the filtered transactions
    paginator = Paginator(transactions, 20)  # Show 20 transactions per page
    try:
        transactions_page = paginator.page(page_number)
    except PageNotAnInteger:
        transactions_page = paginator.page(1)
    except EmptyPage:
        transactions_page = paginator.page(paginator.num_pages)

    return render(request, 'Inventory/transaction_history.html', {
        'transactions': transactions_page,
        'query': query,
        'page_number': page_number
    })


def create_site_inventory_folder(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')

        if folder_name:
            new_folder, created = SiteInventoryFolder.objects.get_or_create(name=folder_name)

            if created:
                # Handle matching transactions here
                matching_transactions = InventoryHistory.objects.filter(site_delivered=folder_name)
                for transaction in matching_transactions:
                    transaction.site_inventory_folder = new_folder
                    transaction.save()

                return JsonResponse({'success': True, 'message': 'Folder created successfully.'})
            else:
                return JsonResponse({'success': False, 'message': 'Folder with this name already exists.'})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})



def delete_site_inventory_folder(request, folder_id):
    if request.method == 'POST':
        folder = get_object_or_404(SiteInventoryFolder, id=folder_id)
        folder.delete()  # This will set the site_inventory_folder field in InventoryHistory to NULL
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})



def site_inventory_folder_list(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')

        if folder_name:
            # Create or get the folder
            new_folder, created = SiteInventoryFolder.objects.get_or_create(name=folder_name)

            if created:
                # Handle matching orders here
                matching_orders = PurchaseOrder.objects.filter(site_delivered=folder_name)
                for order in matching_orders:
                    order.site_inventory_folder = new_folder
                    order.save()

                return JsonResponse({'success': True, 'message': 'Folder created and orders updated successfully.'})
            else:
                return JsonResponse({'success': False, 'message': 'Folder with this name already exists.'})

    # Handling GET requests to render the folder list
    folders = SiteInventoryFolder.objects.all()
    context = {
        'folders': folders,
    }
    return render(request, 'Inventory/site_inventory_folder_list.html', context)


def view_site_inventory_folder_contents(request, folder_id):
    folder = get_object_or_404(SiteInventoryFolder, id=folder_id)
    transactions_list = InventoryHistory.objects.filter(site_inventory_folder=folder)

    # Calculate total_amount
    total_amount = transactions_list.aggregate(total_amount_sum=Sum('total_amount'))['total_amount_sum'] or 0

    # Pagination
    paginator = Paginator(transactions_list, 20)  # Show 20 transactions per page
    page_number = request.GET.get('page')
    try:
        transactions = paginator.page(page_number)
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)

    context = {
        'folder': folder,
        'transactions': transactions,
        'total_amount': total_amount,
    }

    return render(request, 'Inventory/site_folder_contents.html', context)


def create_client_inventory_folder(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')

        if folder_name:
            new_folder, created = ClientInventoryFolder.objects.get_or_create(name=folder_name)

            if created:
                # Handle matching transactions here
                matching_transactions = InventoryHistory.objects.filter(client=folder_name)
                for transaction in matching_transactions:
                    transaction.client_inventory_folder = new_folder
                    transaction.save()

                return JsonResponse({'success': True, 'message': 'Client folder created and transactions updated successfully.'})
            else:
                return JsonResponse({'success': False, 'message': 'Client folder with this name already exists.'})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


def delete_client_inventory_folder(request, folder_id):
    if request.method == 'POST':
        folder = get_object_or_404(ClientInventoryFolder, id=folder_id)
        folder.delete()  # This will set the client_inventory_folder field in InventoryHistory to NULL
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


def client_inventory_folder_list(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')

        if folder_name:
            # Create or get the folder
            new_folder, created = ClientInventoryFolder.objects.get_or_create(name=folder_name)

            if created:
                # Handle matching orders here
                matching_orders = PurchaseOrder.objects.filter(client=folder_name)
                for order in matching_orders:
                    order.client_inventory_folder = new_folder
                    order.save()

                return JsonResponse({'success': True, 'message': 'Folder created and orders updated successfully.'})
            else:
                return JsonResponse({'success': False, 'message': 'Folder with this name already exists.'})

    # Handling GET requests to render the folder list
    folders = ClientInventoryFolder.objects.all()
    context = {
        'folders': folders,
    }
    return render(request, 'Inventory/client_inventory_folder_list.html', context)


def view_client_inventory_folder_contents(request, folder_id):
    folder = get_object_or_404(ClientInventoryFolder, id=folder_id)
    transactions_list = InventoryHistory.objects.filter(client_inventory_folder=folder)

    total_amount = transactions_list.aggregate(total_amount_sum=Sum('total_amount'))['total_amount_sum'] or 0

    # Pagination
    paginator = Paginator(transactions_list, 20)  # Show 20 transactions per page
    page_number = request.GET.get('page')
    try:
        transactions = paginator.page(page_number)
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)

    context = {
        'folder': folder,
        'transactions': transactions,
        'total_amount': total_amount,
    }

    return render(request, 'Inventory/client_folder_contents.html', context)

# ----------------------------SUPPLIER----------------------------------------------

def delete_supplier_folder(request, folder_id):
    if request.method == 'POST':
        folder = get_object_or_404(SupplierFolder, id=folder_id)
        folder.delete()  # This will set the supplier_folder field in PurchaseOrder to NULL
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


def supplier_list_folders(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')

        if folder_name:
            new_folder, created = SupplierFolder.objects.get_or_create(name=folder_name)

            if created:
                # Handle matching orders here
                matching_orders = PurchaseOrder.objects.filter(supplier=folder_name)
                for order in matching_orders:
                    order.supplier_folder = new_folder
                    order.save()

                return JsonResponse({'success': True, 'message': 'Folder created successfully.'})
            else:
                return JsonResponse({'success': False, 'message': 'Folder with this name already exists.'})

    # Handling GET requests to render the folder list
    folders = SupplierFolder.objects.all()
    context = {
        'folders': folders,
    }
    return render(request, 'supplier/supplier_list_folders.html', context)


def view_folder_contents(request, folder_id):
    folder = get_object_or_404(SupplierFolder, id=folder_id)
    purchase_orders = PurchaseOrder.objects.filter(supplier_folder=folder)

    context = {
        'folder': folder,
        'purchase_orders': purchase_orders,
    }

    return render(request, 'supplier/view_folder_contents.html', context)

