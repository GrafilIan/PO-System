from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from .forms import PurchaseOrderForm
from .models import PurchaseOrder


# Create your views here.
def index(request):
    return render(request, 'supplier/sample.html')

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
        orders = PurchaseOrder.objects.all()
        return render(request, 'dashboards/front_desk_dashboard.html', {'orders': orders})
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

def purchase_order_list(request):
    orders = PurchaseOrder.objects.all()
    return render(request, 'dashboards/front_desk_dashboard.html', {'orders': orders})
