from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

from django.shortcuts import render, redirect
from .models import ElectionManager

def register_manager(request):
    if request.method == "POST":
        id_number = request.POST.get("id_number")
        profile_picture = request.FILES.get("profile_picture")
        full_name = request.POST.get("full_name")
        username = request.POST.get("username")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        address = request.POST.get("address")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        errors = {}

        # Validation checks
        if ElectionManager.objects.filter(id_number=id_number).exists():
            errors["id_number"] = "ID number already exists."

        if not full_name.replace(" ", "").isalpha():
            errors["full_name"] = "Full name cannot contain numbers."

        if ElectionManager.objects.filter(username=username).exists():
            errors["username"] = "Username already taken."

        if not phone_number.isdigit() or len(phone_number) != 10:
            errors["phone_number"] = "Phone number must be exactly 10 digits."

        if ElectionManager.objects.filter(email=email).exists():
            errors["email"] = "Email already registered."

        if password != confirm_password:
            errors["password"] = "Passwords do not match."
            
        if len(password) < 8:
                errors["password"] = "Password must be at least 8 characters long."

        if errors:
            return render(request, "register_manager.html", {"errors": errors})

        # Create new Election Manager
        manager = ElectionManager(
            id_number=id_number,
            profile_picture=profile_picture,
            full_name=full_name,
            username=username,
            phone_number=phone_number,
            email=email,
            address=address,
            password=password  # In real applications, hash the password
        )
        manager.save()
        return redirect("login_manager")

    return render(request, "register_manager.html")


def login_manager(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            manager = ElectionManager.objects.get(username=username, password=password)
            request.session["manager_id"] = manager.id  # Store session
            return redirect("manager_dashboard")
        except ElectionManager.DoesNotExist:
            return render(request, "login_manager.html", {"error": "Invalid username or password"})

    return render(request, "login_manager.html")


def manager_dashboard(request):
    if "manager_id" not in request.session:
        return redirect("login_manager")  # Redirect to login if not logged in
    return render(request, "manager_dashboard.html")
