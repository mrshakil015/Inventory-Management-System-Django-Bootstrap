from django.shortcuts import render

# Create your views here.

def index(request):
    context={
        "title": "Dashboard",
        "subTitle": "AI",
    }
    return render(request,"index.html", context)

def employee_list(request):
    
    return render(request,'employees/employee-list.html')

def add_employee(request):
    
    return render(request,'employees/add-employee.html')