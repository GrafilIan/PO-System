from django.urls import path
from django.conf import settings
from . import views
from .views import login_view, dashboard_view, logout_view, purchase_order_list

urlpatterns = [
    path('supplier/', views.index, name='index'),
    path('', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('purchase-order/create/', views.purchase_order_create, name='purchase_order_create'),
    path('purchase-order/success/', views.purchase_order_success, name='purchase_order_success'),
    path('purchase-orders/', views.purchase_order_list, name='dashboard'),
]
