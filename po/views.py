from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
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
            return render(request, 'authentication/login.html', {'error': 'Invalid credentials'})
    return render(request, 'authentication/login.html')

@login_required
def dashboard_view(request):
    if request.user.groups.filter(name='Accountant').exists():
        return render(request, 'dashboards/accountant_dashboard.html')
    elif request.user.groups.filter(name='Front Desk').exists():
        return render(request, 'dashboards/front_desk_dashboard.html')
    elif request.user.groups.filter(name='Inventory Clerk').exists():
        return render(request, 'dashboards/inventory_clerk_dashboard.html')
    else:
        return HttpResponse('No role assigned')

def logout_view(request):
    logout(request)
    return redirect('login')