from django.urls import path
from django.conf import settings
from . import views
from .views import login_view, dashboard_view, logout_view, purchase_order_list, export_orders_to_excel

urlpatterns = [
    path('', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('purchase-order/create/', views.purchase_order_create, name='purchase_order_create'),
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('purchase_order/edit/<int:id>/', views.purchase_order_edit, name='purchase_order_edit'),
    path('purchase_order_supplier/edit/<int:id>/', views.purchase_order_edit_supplier, name='purchase_order_edit_supplier'),

    path('export-orders/', export_orders_to_excel, name='export_orders_to_excel'),
    path('folders/', views.list_folders, name='list_folders'),
    path('folders/create/', views.create_folder, name='create_folder'),
    path('folders/<int:folder_id>/delete/', views.delete_folder, name='delete_folder'),
    path('folders/<int:folder_id>/archive/', views.archive_orders, name='archive_orders'),
    path('move-orders/', views.move_orders_to_folder, name='move_orders_to_folder'),

    path('upload/', views.upload_file, name='upload_file'),
    path('inventory/', views.inventory_table, name='inventory_table'),
    path('inventory/form/', views.inventory_form, name='inventory_form'),
    path('inventory/edit/<int:id>/', views.inventory_edit, name='inventory_edit'),

    path('transaction-history/', views.transaction_history, name='transaction_history'),

    path('export-inventory/', views.export_inventory_to_excel, name='export_inventory_to_excel'),
    path('export_archived_orders/<int:folder_id>/', views.export_archived_orders_to_excel,
         name='export_archived_orders'),
    path('supfolders/', views.supplier_list_folders, name='supplier_list_folders'),
    path('supfolders/<int:folder_id>/view/', views.view_folder_contents, name='view_folder_contents'),
    path('supfolders/<int:folder_id>/delete/', views.delete_supplier_folder, name='delete_supplier_folder'),
    path('export-supplier-contents/<int:folder_id>/', views.export_supplier_contents, name='export_supplier_contents'),
    path('export_all_suppliers/', views.export_all_supplier_folders, name='export_all_suppliers'),

    path('site-inventory/create-folder/', views.create_site_inventory_folder, name='create_site_inventory_folder'),
    path('site-inventory/delete-folder/<int:folder_id>/', views.delete_site_inventory_folder,
         name='delete_site_inventory_folder'),
    path('site-inventory/folders/', views.site_inventory_folder_list, name='site_inventory_folder_list'),
    path('site-inventory/folder/<int:folder_id>/', views.view_site_inventory_folder_contents,
         name='view_site_inventory_folder_contents'),
    path('export-site-folder-contents/<int:folder_id>/', views.export_site_folder_contents,
         name='export_site_folder_contents'),
    path('export-all-site-inventory-folders/', views.export_all_site_inventory_folders,
         name='export_all_site_inventory_folders'),

    path('create-client-folder/', views.create_client_inventory_folder, name='create_client_inventory_folder'),
    path('delete-client-folder/<int:folder_id>/', views.delete_client_inventory_folder,
         name='delete_client_inventory_folder'),
    path('client-folder-list/', views.client_inventory_folder_list, name='client_inventory_folder_list'),
    path('client-folder-contents/<int:folder_id>/', views.view_client_inventory_folder_contents,
         name='view_client_inventory_folder_contents'),
    path('client-folder/export/<int:folder_id>/', views.export_client_folder_contents,
         name='export_client_folder_contents'),
    path('export-all-client-folders/', views.export_all_client_folders, name='export_all_client_folders'),
    path('bulk_edit_inventory/', views.bulk_edit_inventory, name='bulk_edit_inventory'),
    path('remove-cart-item/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),

    path('new-records/', views.new_records_view, name='new_records'),
    path('export-transaction-history/', views.export_transaction_history_to_excel,
         name='export_transaction_history_to_excel'),
    path('bulk_edit_purchase_order/', views.bulk_edit_purchase_order, name='bulk_edit_purchase_order'),
    path('po_remove_cart_item/<int:item_id>/', views.po_remove_cart_item, name='po_remove_cart_item'),
    path('remove_all_cart_items/', views.remove_all_cart_items, name='remove_all_cart_items'),
    path('item_code_list/', views.item_code_list, name='item_code_list'),

]
