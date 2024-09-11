from django.urls import path
from . import views

urlpatterns = [
    # View to handle transaction history
    path('juban/transaction-history/', views.juban_transaction_history, name='juban_transaction_history'),

    # View to delete a site inventory folder
    path('juban/site-inventory-folder/delete/<int:folder_id>/', views.juban_delete_site_inventory_folder, name='juban_delete_site_inventory_folder'),

    # View to list site inventory folders
    path('juban/site-inventory-folder/list/', views.juban_site_inventory_folder_list, name='juban_site_inventory_folder_list'),

    # View to create a site inventory folder
    path('juban/site-inventory-folder/create/', views.juban_create_site_inventory_folder, name='juban_create_site_inventory_folder'),

    # View to display the contents of a site inventory folder
    path('juban/site-inventory-folder/view/<int:folder_id>/', views.juban_view_site_inventory_folder_contents, name='juban_view_site_inventory_folder_contents'),

    # View to export all site inventory folders to a zip file
    path('juban/site-inventory-folder/export/all/', views.juban_export_all_site_inventory_folders, name='juban_export_all_site_inventory_folders'),

    # View to export a single site inventory folder's contents to Excel
    path('juban/site-inventory-folder/export/<int:folder_id>/', views.juban_export_site_folder_contents, name='juban_export_site_folder_contents'),

    # View to export all client folders to a zip file
    path('juban/client-folder/export/all/', views.juban_export_all_client_folders, name='juban_export_all_client_folders'),

    # View to export a single client folder's contents to Excel
    path('juban/client-folder/export/<int:folder_id>/', views.juban_export_client_folder_contents, name='juban_export_client_folder_contents'),

    # View to export inventory data to Excel
    path('juban/inventory/export/', views.juban_export_inventory_to_excel, name='juban_export_inventory_to_excel'),

    # View to list the item codes
    path('juban/item-code-list/', views.juban_item_code_list, name='juban_item_code_list'),

    # View for the inventory form (create)
    path('juban/inventory-form/', views.juban_inventory_form, name='juban_inventory_form'),

    # View to display the inventory table
    path('juban/inventory-table/', views.juban_inventory_table, name='juban_inventory_table'),

    # View to edit an inventory item
    path('juban/inventory/edit/<int:id>/', views.juban_inventory_edit, name='juban_inventory_edit'),

    # View to display new records
    path('juban/new-records/', views.juban_new_records_view, name='juban_new_records_view'),
]
