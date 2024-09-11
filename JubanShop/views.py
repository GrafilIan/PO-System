import json
import zipfile
from datetime import datetime
from io import BytesIO

import openpyxl
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from openpyxl.styles import PatternFill, Font
from openpyxl.workbook import Workbook

from .forms import JubanItemInventoryListForm, JubanItemInventoryQuantityForm, JubanEditRemarksForm
from .models import JubanItemInventory, JubanItemCodeList, JubanSiteInventoryFolder, JubanInventoryHistory, \
    JubanClientInventoryFolder


def juban_inventory_form(request):
    if request.method == 'POST':
        form = JubanItemInventoryListForm(request.POST)
        po_product_name = request.POST.get('po_product_name')

        # Check if the po_product_name already exists in the Juban database
        if JubanItemInventory.objects.filter(po_product_name=po_product_name).exists():
            messages.error(request, 'PO Product Name already exists. Please use a different name.')
        elif form.is_valid():
            # Save the form to create the item
            item = form.save(commit=False)  # Get the instance but don't save it to the database yet

            # Manually calculate the stock
            item.stock = item.quantity_in - item.quantity_out  # Calculate stock based on quantity_in and quantity_out

            # Now save the item with the updated stock value
            item.save()

            messages.success(request, 'Item successfully added!')
            return redirect('juban_inventory_form')  # Redirect to the same form page
        else:
            messages.error(request, 'There was an error adding the item. Please try again.')
    else:
        form = JubanItemInventoryListForm()

    return render(request, 'jubanshop/Inventory/juban_inventory_form.html', {'form': form})


def juban_inventory_table(request):
    query = request.GET.get('q')

    # Fetch all inventory items, ordered by 'po_product_name'
    inventory_items = JubanItemInventory.objects.all().order_by('po_product_name')

    # If there is a search query, filter the results
    if query:
        inventory_items = inventory_items.filter(
            Q(item_code__icontains=query) |
            Q(supplier__icontains=query) |
            Q(po_product_name__icontains=query) |
            Q(unit__icontains=query) |
            Q(quantity_in__icontains=query) |
            Q(quantity_out__icontains=query) |
            Q(stock__icontains=query)
        )

    # Ensure the ItemCodeList gets updated if necessary
    for item in inventory_items:
        if not JubanItemCodeList.objects.filter(item_code=item.item_code, po_product_name=item.po_product_name).exists():
            JubanItemCodeList.objects.create(
                item_code=item.item_code,
                po_product_name=item.po_product_name,
                unit=item.unit
            )

    # Paginate the results, displaying 100 items per page
    paginator = Paginator(inventory_items, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Render the results in the dashboard template
    return render(request, 'dashboards/inventory_clerk_dashboard.html', {
        'page_obj': page_obj
    })


def juban_new_records_view(request):
    # Define the timeframe for what constitutes a "new" record (e.g., last 24 hours)
    timeframe = timezone.now() - timezone.timedelta(hours=24)

    # Get all records created in the last 24 hours, ordered by most recent
    new_records = JubanItemInventory.objects.filter(created_at__gte=timeframe).order_by('-created_at')

    return render(request, 'Jubanshop/Inventory/juban_new_records.html', {
        'new_records': new_records
    })


def juban_inventory_edit(request, id):
    inventory_item = get_object_or_404(JubanItemInventory, id=id)

    if request.method == 'POST':
        form = JubanItemInventoryQuantityForm(request.POST, instance=inventory_item)
        if form.is_valid():
            updated_item = form.save(commit=False)

            # Check if an existing record with the same supplier and po_product_name already exists
            existing_inventory_item = JubanItemInventory.objects.filter(
                supplier=updated_item.supplier,
                po_product_name=updated_item.po_product_name
            ).exclude(id=id).first()

            if existing_inventory_item:
                # If a matching record exists, update its quantities and stock
                existing_inventory_item.quantity_in += updated_item.quantity_in
                existing_inventory_item.quantity_out += updated_item.quantity_out
                existing_inventory_item.stock = existing_inventory_item.quantity_in - existing_inventory_item.quantity_out
                existing_inventory_item.save()

                # Optionally, delete the current record or return success message
                inventory_item.delete()  # Remove the current item as it merges with the existing one.
            else:
                # If no matching record, update the current inventory item
                updated_item.stock = updated_item.quantity_in - updated_item.quantity_out
                updated_item.save()

            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    else:
        form = JubanItemInventoryQuantityForm(instance=inventory_item)

    return render(request, 'Jubanshop/Inventory/juban_inventory_edit.html', {'form': form, 'item': inventory_item})


def juban_item_code_list(request):
    query = request.GET.get('q')  # Get the search query from the URL
    if query:
        # Filter results based on the search query
        saved_items = JubanItemCodeList.objects.filter(
            Q(item_code__icontains=query) |
            Q(po_product_name__icontains=query) |
            Q(unit__icontains=query)
        )
    else:
        saved_items = JubanItemCodeList.objects.all()  # If no search, return all items

    return render(request, 'Jubanshop/Inventory/juban_item_code_list.html', {'saved_items': saved_items, 'query': query})


def juban_export_inventory_to_excel(request):
    query = request.GET.get('q')  # Search query parameter

    # Start with all inventory items
    inventory_list = JubanItemInventory.objects.all()

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
        'Item Code', 'Supplier', 'Particular', 'New Product Name', 'Unit',
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
    response['Content-Disposition'] = 'attachment; filename=Juban_Inventory.xlsx'
    return response


def juban_export_site_folder_contents(request, folder_id):
    try:
        # Get the Juban site inventory folder by ID
        folder = JubanSiteInventoryFolder.objects.get(id=folder_id)
        transactions = JubanInventoryHistory.objects.filter(site_inventory_folder=folder)

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
                str(transaction.item),  # Convert JubanItemInventory instance to string
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
        response['Content-Disposition'] = f'attachment; filename=Juban_SiteInventory_{folder.name}.xlsx'
        return response

    except JubanSiteInventoryFolder.DoesNotExist:
        return HttpResponse("Site Inventory Folder not found", status=404)


def juban_export_all_site_inventory_folders(request):
    # Create an in-memory buffer to hold the zip file
    buffer = BytesIO()

    # Create a zip file in the buffer
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Iterate through each site inventory folder
        for folder in JubanSiteInventoryFolder.objects.all():
            # Get transactions for the folder
            transactions = JubanInventoryHistory.objects.filter(site_inventory_folder=folder)

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
                    str(transaction.item),  # Convert JubanItemInventory instance to string
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
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2)
                sheet.column_dimensions[column_letter].width = adjusted_width

            # Save the workbook to a bytes buffer
            excel_buffer = BytesIO()
            workbook.save(excel_buffer)
            excel_buffer.seek(0)

            # Add the workbook to the zip file
            zf.writestr(f'SiteInventoryRecords_{folder.name}.xlsx', excel_buffer.getvalue())

    buffer.seek(0)

    # Set the response to return the zip file
    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=juban_site_inventory_folders.zip'
    return response


def juban_export_client_folder_contents(request, folder_id):
    try:
        # Get the client inventory folder by ID
        folder = JubanClientInventoryFolder.objects.get(id=folder_id)
        transactions = JubanInventoryHistory.objects.filter(client_inventory_folder=folder)

        # Create a workbook and a sheet
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Client Inventory Records'

        # Define header styles
        header_font = Font(bold=True)
        gold_fill = PatternFill(start_color='F59B00', end_color='F59B00', fill_type='solid')
        currency_format = '#,##0.00'

        # Define the headers
        headers = [
            'Transaction ID', 'Client', 'Date', 'Item', 'Quantity In', 'Quantity Out',
            'Price', 'Total Amount', 'Delivery Ref', 'Delivery No.', 'Invoice Type', 'Invoice#'
        ]
        sheet.append(headers)

        for cell in sheet[1]:
            cell.font = header_font
            cell.fill = gold_fill
            cell.value = cell.value.upper() if cell.value is not None else cell.value

        # Populate the sheet with data
        for transaction in transactions:
            sheet.append([
                transaction.id,
                transaction.client if transaction.client else 'N/A',
                transaction.date.strftime('%Y-%m-%d') if transaction.date else 'N/A',
                str(transaction.item),
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
        for cell in sheet['G']:
            if cell.row > 1:
                cell.number_format = currency_format

        for cell in sheet['H']:
            if cell.row > 1:
                cell.number_format = currency_format

        # Adjust column widths
        for column in sheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
                adjusted_width = (max_length + 2)
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
        response['Content-Disposition'] = f'attachment; filename=JubanClientInventory_{folder.name}.xlsx'
        return response

    except JubanClientInventoryFolder.DoesNotExist:
        return HttpResponse("Client Inventory Folder not found", status=404)



def juban_export_all_client_folders(request):
    # Create an in-memory buffer to hold the zip file
    buffer = BytesIO()

    # Create a zip file in the buffer
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Iterate through each client folder
        for folder in JubanClientInventoryFolder.objects.all():
            # Get inventory records for the folder
            transactions = JubanInventoryHistory.objects.filter(client_inventory_folder=folder)

            # Create a workbook and a sheet
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = 'Client Inventory Records'

            # Define header styles
            header_font = Font(bold=True)
            gold_fill = PatternFill(start_color='F59B00', end_color='F59B00', fill_type='solid')
            currency_format = '#,##0.00'

            # Define the headers
            headers = [
                'Transaction ID', 'Client', 'Date', 'Item', 'Quantity In', 'Quantity Out',
                'Price', 'Total Amount', 'Delivery Ref', 'Delivery No.', 'Invoice Type', 'Invoice#'
            ]
            sheet.append(headers)

            for cell in sheet[1]:
                cell.font = header_font
                cell.fill = gold_fill
                cell.value = cell.value.upper() if cell.value is not None else cell.value

            # Populate the sheet with data
            for transaction in transactions:
                sheet.append([
                    transaction.id,
                    transaction.client if transaction.client else 'N/A',
                    transaction.date.strftime('%Y-%m-%d') if transaction.date else 'N/A',
                    str(transaction.item),
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
            for cell in sheet['G']:
                if cell.row > 1:
                    cell.number_format = currency_format

            for cell in sheet['H']:
                if cell.row > 1:
                    cell.number_format = currency_format

            # Adjust column widths
            for column in sheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2)
                sheet.column_dimensions[column_letter].width = adjusted_width

            # Save the workbook to a bytes buffer
            excel_buffer = BytesIO()
            workbook.save(excel_buffer)
            excel_buffer.seek(0)

            # Add the workbook to the zip file
            zf.writestr(f'JubanClientInventory_{folder.name}.xlsx', excel_buffer.getvalue())

    buffer.seek(0)

    # Set the response to return the zip file
    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=juban_client_inventory_folders.zip'
    return response


def juban_transaction_history(request):
    query = request.GET.get('q')  # Get search query from request
    page_number = request.GET.get('page', 1)  # Get page number from request

    # Dictionary to map full and abbreviated month names to month numbers
    month_mapping = {
        "January": "1", "February": "2", "March": "3", "April": "4",
        "May": "5", "June": "6", "July": "7", "August": "8",
        "September": "9", "October": "10", "November": "11", "December": "12",
        "Jan": "1", "Feb": "2", "Mar": "3", "Apr": "4",
        "Jun": "6", "Jul": "7", "Aug": "8", "Sep": "9", "Oct": "10", "Nov": "11", "Dec": "12"
    }

    # Retrieve all records from JubanInventoryHistory and exclude records where date is null
    transactions = JubanInventoryHistory.objects.exclude(date__isnull=True).order_by('-date')

    # Apply search filter if a query is present
    if query:
        try:
            # Try to interpret the query as a full date (e.g., 'Aug 20, 2024')
            date_obj = datetime.strptime(query, '%b %d, %Y').date()
            transactions = transactions.filter(date=date_obj)
        except ValueError:
            # If it's not a full date, check if the query is a month name (full or abbreviated)
            for month_name, month_number in month_mapping.items():
                if month_name.lower() in query.lower():
                    # Check if the query contains a year
                    year = None
                    try:
                        year = int(query.split()[-1])  # Try to extract the year
                    except (ValueError, IndexError):
                        pass

                    # Filter based on month and possibly year
                    if year:
                        transactions = transactions.filter(date__month=month_number, date__year=year)
                    else:
                        transactions = transactions.filter(date__month=month_number)
                    break
            else:
                # If not a date or month, treat as a general text search
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
    paginator = Paginator(transactions, 100)  # Show 100 transactions per page
    try:
        transactions_page = paginator.page(page_number)
    except PageNotAnInteger:
        transactions_page = paginator.page(1)
    except EmptyPage:
        transactions_page = paginator.page(paginator.num_pages)

    return render(request, 'Jubanshop/Inventory/juban_transaction_history.html', {
        'transactions': transactions_page,
        'query': query,
        'page_number': page_number
    })


def juban_create_site_inventory_folder(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')

        if folder_name:
            new_folder, created = JubanSiteInventoryFolder.objects.get_or_create(name=folder_name)

            if created:
                # Handle matching transactions here
                matching_transactions = JubanInventoryHistory.objects.filter(site_delivered=folder_name)
                for transaction in matching_transactions:
                    transaction.site_inventory_folder = new_folder
                    transaction.save()

                return JsonResponse({'success': True, 'message': 'Folder created successfully.'})
            else:
                return JsonResponse({'success': False, 'message': 'Folder with this name already exists.'})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


def juban_delete_site_inventory_folder(request, folder_id):
    if request.method == 'POST':
        folder = get_object_or_404(JubanSiteInventoryFolder, id=folder_id)
        folder.delete()  # This will set the site_inventory_folder field in JubanInventoryHistory to NULL
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


def juban_site_inventory_folder_list(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')

        if folder_name:
            # Create or get the folder
            new_folder, created = JubanSiteInventoryFolder.objects.get_or_create(name=folder_name)

            if created:
                return JsonResponse({'success': True, 'message': 'Folder created successfully.'})
            else:
                return JsonResponse({'success': False, 'message': 'Folder with this name already exists.'})

    # Handling GET requests to render the folder list
    folders = JubanSiteInventoryFolder.objects.all()
    context = {
        'folders': folders,
    }
    return render(request, 'Jubanshop/Inventory/juban_site_inventory_folder_list.html', context)


def juban_view_site_inventory_folder_contents(request, folder_id):
    folder = get_object_or_404(JubanSiteInventoryFolder, id=folder_id)
    transactions_list = JubanInventoryHistory.objects.filter(site_inventory_folder=folder)

    # Calculate total_amount
    total_amount = transactions_list.aggregate(total_amount_sum=Sum('total_amount'))['total_amount_sum'] or 0

    # Pagination
    paginator = Paginator(transactions_list, 100)  # Show 100 transactions per page
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

    return render(request, 'Jubanshop/Inventory/juban_site_folder_contents.html', context)



def juban_create_client_inventory_folder(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')

        if folder_name:
            new_folder, created = JubanClientInventoryFolder.objects.get_or_create(name=folder_name)

            if created:
                # Handle matching transactions here
                matching_transactions = JubanInventoryHistory.objects.filter(client=folder_name)
                for transaction in matching_transactions:
                    transaction.client_inventory_folder = new_folder
                    transaction.save()

                return JsonResponse(
                    {'success': True, 'message': 'Client folder created and transactions updated successfully.'})
            else:
                return JsonResponse({'success': False, 'message': 'Client folder with this name already exists.'})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


def juban_delete_client_inventory_folder(request, folder_id):
    if request.method == 'POST':
        folder = get_object_or_404(JubanClientInventoryFolder, id=folder_id)
        folder.delete()  # This will set the client_inventory_folder field in JubanInventoryHistory to NULL
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


def juban_client_inventory_folder_list(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')

        if folder_name:
            # Create or get the folder
            new_folder, created = JubanClientInventoryFolder.objects.get_or_create(name=folder_name)

            if created:
                return JsonResponse({'success': True, 'message': 'Folder created successfully.'})
            else:
                return JsonResponse({'success': False, 'message': 'Folder with this name already exists.'})

    # Handling GET requests to render the folder list
    folders = JubanClientInventoryFolder.objects.all()
    context = {
        'folders': folders,
    }
    return render(request, 'Jubanshop/Inventory/juban_client_inventory_folder_list.html', context)


def juban_view_client_inventory_folder_contents(request, folder_id):
    folder = get_object_or_404(JubanClientInventoryFolder, id=folder_id)
    transactions_list = JubanInventoryHistory.objects.filter(client_inventory_folder=folder)

    total_amount = transactions_list.aggregate(total_amount_sum=Sum('total_amount'))['total_amount_sum'] or 0

    # Pagination
    paginator = Paginator(transactions_list, 100)  # Show 100 transactions per page
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

    return render(request, 'Jubanshop/Inventory/juban_client_folder_contents.html', context)


def juban_edit_inventory_history_remarks(request, folder_id, record_id):
    # Get the folder and record
    folder = get_object_or_404(JubanClientInventoryFolder, id=folder_id)
    record = get_object_or_404(JubanInventoryHistory, client_inventory_folder=folder, id=record_id)

    if request.method == 'POST':
        form = JubanEditRemarksForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('juban_view_client_inventory_folder_contents', folder_id=folder_id)  # Redirect to folder view after edit
    else:
        form = JubanEditRemarksForm(instance=record)

    context = {
        'form': form,
        'folder': folder,
        'record': record
    }
    return render(request, 'Jubanshop/Inventory/juban_client_folder_contents.html', context)


@csrf_exempt
def juban_edit_remarks(request, transaction_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        remarks = data.get('remarks', '')

        try:
            transaction = JubanInventoryHistory.objects.get(id=transaction_id)
            transaction.remarks = remarks
            transaction.save()
            return JsonResponse({'success': True})
        except JubanInventoryHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Transaction not found'}, status=404)

    return JsonResponse({'success': False}, status=400)




