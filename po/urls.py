from django.urls import path
from django.conf import settings
from . import views
from .views import login_view, dashboard_view, logout_view

urlpatterns = [
    path('supplier/', views.index, name='index'),
    path('', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout/', logout_view, name='logout'),
]
