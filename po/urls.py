from django.urls import path
from django.conf import settings
from . import views
from .views import login_view, dashboard_view, logout_view, purchase_order_list, export_orders_to_excel

urlpatterns = [
    path('', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('purchase-order/create/', views.purchase_order_create, name='purchase_order_create'),
    path('purchase-order/success/', views.purchase_order_success, name='purchase_order_success'),
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('purchase_order/edit/<int:id>/', views.purchase_order_edit, name='purchase_order_edit'),
    path('export-orders/', export_orders_to_excel, name='export_orders_to_excel'),

]
