from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from .forms import PurchaseOrderForm
from .models import PurchaseOrder, ArchiveFolder
from datetime import datetime
import openpyxl
from openpyxl.styles import NamedStyle, Font, PatternFill
from io import BytesIO

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
        return render(request, 'dashboards/inventory_clerk_dashboard.html')
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
            form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error'})
    else:
        form = PurchaseOrderForm()

    return render(request, 'records/purchase_order_form.html', {'form': form})




def purchase_order_success(request):
    return render(request, 'records/purchase_order_success.html')


# For Viewing Records
def purchase_order_list(request):
    query = request.GET.get('q')  # 'q' is the name of the search input field
    date_query = request.GET.get('date')  # 'date' is the name of the date input field

    # Start with all orders
    orders_list = PurchaseOrder.objects.all()

    # If there's a search query, filter the orders accordingly
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

    # If there's a date query, filter by date
    if date_query:
        try:
            # Try parsing full date (e.g., "Aug 11, 2024")
            date_obj = datetime.strptime(date_query, '%b %d, %Y').date()
            orders_list = orders_list.filter(date=date_obj)
        except ValueError:
            try:
                # Try parsing month and year only (e.g., "Aug 2024")
                date_obj = datetime.strptime(date_query, '%b %Y')
                orders_list = orders_list.filter(date__year=date_obj.year, date__month=date_obj.month)
            except ValueError:
                try:
                    # Try parsing full month name and year (e.g., "August 2024")
                    date_obj = datetime.strptime(date_query, '%B %Y')
                    orders_list = orders_list.filter(date__year=date_obj.year, date__month=date_obj.month)
                except ValueError:
                    try:
                        # Try parsing month only (e.g., "08" for August or "11" for November)
                        month_number = int(date_query)
                        orders_list = orders_list.filter(date__month=month_number)
                    except ValueError:
                        try:
                            # Try parsing full month name only (e.g., "August")
                            date_obj = datetime.strptime(date_query, '%B')
                            orders_list = orders_list.filter(date__month=date_obj.month)
                        except ValueError:
                            pass  # Handle invalid date input gracefully



    paginator = Paginator(orders_list, 20)  # Paginate after every 20 entries
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)

    return render(request, 'dashboards/front_desk_dashboard.html', {'orders': orders})


def purchase_order_edit(request, id):
    order = get_object_or_404(PurchaseOrder, id=id)

    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('dashboard')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error'})
    else:
        form = PurchaseOrderForm(instance=order)

    return render(request, 'records/purchase_order_edit.html', {'form': form, 'order': order})


# For Exporting Records

def export_orders_to_excel(request):
    query = request.GET.get('q')  # Search query parameter
    date_query = request.GET.get('date')  # Date query parameter

    # Start with all orders
    orders_list = PurchaseOrder.objects.all()

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


    # Populate the sheet with data
    for order in orders_list:
        sheet.append([
            order.date.strftime('%Y-%m-%d'), order.po_number, order.purchaser, order.brand, order.item_code,
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


# For Archiving Methods

def create_folder(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        if folder_name:
            ArchiveFolder.objects.create(name=folder_name)
            return redirect('list_folders')
    return render(request, 'archive/create_folder.html')

def list_folders(request):
    folders = ArchiveFolder.objects.all()
    return render(request, 'archive/list_folders.html', {'folders': folders})

def delete_folder(request, folder_id):
    folder = ArchiveFolder.objects.get(id=folder_id)
    folder.delete()
    return redirect('list_folders')

def archive_orders(request, folder_id):
    folder = ArchiveFolder.objects.get(id=folder_id)
    orders = PurchaseOrder.objects.filter(folder=folder)
    return render(request, 'archive_orders.html', {'folder': folder, 'orders': orders})





