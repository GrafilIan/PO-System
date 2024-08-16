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
    path('export-orders/', export_orders_to_excel, name='export_orders_to_excel'),

    path('folders/', views.list_folders, name='list_folders'),
    path('folders/create/', views.create_folder, name='create_folder'),
    path('folders/<int:folder_id>/delete/', views.delete_folder, name='delete_folder'),
    path('folders/<int:folder_id>/archive/', views.archive_orders, name='archive_orders'),
    path('move-orders/', views.move_orders_to_folder, name='move_orders_to_folder'),
    path('upload/', views.upload_file, name='upload_file'),

    path('inventory/', views.inventory_table, name='inventory_table'),
    path('inventory/edit/<int:id>/', views.inventory_edit, name='inventory_edit'),
    path('export-inventory/', views.export_inventory_to_excel, name='export_inventory_to_excel'),
    path('export_archived_orders/<int:folder_id>/', views.export_archived_orders_to_excel, name='export_archived_orders'),

]
