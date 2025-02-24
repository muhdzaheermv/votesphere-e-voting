
from django.shortcuts import render, redirect,get_object_or_404
from .models import ElectionManager,ElectionCampaign,Election

def index(request):
    return render(request, 'index.html')


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
            return redirect("manager_dashboard", manager_id=manager.id)  # ✅ Pass manager_id correctly
        except ElectionManager.DoesNotExist:
            return render(request, "login_manager.html", {"error": "Invalid username or password"})

    return render(request, "login_manager.html")


def manager_dashboard(request, manager_id):
    manager = get_object_or_404(ElectionManager, id=manager_id)
    return render(request, "manager_dashboard.html", {"manager": manager})

def create_campaign(request):
    if request.method == "POST":
        name = request.POST["name"]
        description = request.POST["description"]
        start_time = request.POST["start_time"]
        end_time = request.POST["end_time"]
        image = request.FILES.get("image")

        ElectionCampaign.objects.create(
            name=name, description=description, start_time=start_time, end_time=end_time, image=image
        )

        return redirect("campaign_list")

    return render(request, "create_campaign.html")

# List All Campaigns
def campaign_list(request, manager_id):
    campaigns = ElectionCampaign.objects.all()
    manager = get_object_or_404(ElectionManager, id=manager_id)  # ✅ Ensure manager is retrieved
    return render(request, "campaign_list.html", {"campaigns": campaigns, "manager": manager})


# Edit Election Campaign
def edit_campaign(request, campaign_id):
    campaign = get_object_or_404(ElectionCampaign, id=campaign_id)

    if request.method == "POST":
        campaign.name = request.POST.get("name", campaign.name)  # Avoids KeyError
        campaign.description = request.POST.get("description", campaign.description)
        campaign.start_time = request.POST.get("start_time", campaign.start_time)
        campaign.end_time = request.POST.get("end_time", campaign.end_time)

        if "image" in request.FILES:  # Checks if an image was uploaded
            campaign.image = request.FILES["image"]

        campaign.save()
        return redirect("campaign_list")

    return render(request, "edit_campaign.html", {"campaign": campaign})

# Delete Election Campaign
def delete_campaign(request, campaign_id):
    campaign = get_object_or_404(ElectionCampaign, id=campaign_id)
    campaign.delete()
    return redirect("campaign_list")

# Create Election Inside a Campaign
def create_election(request, campaign_id):
    campaign = get_object_or_404(ElectionCampaign, id=campaign_id)

    if request.method == "POST":
        name = request.POST["name"]  # ✅ Only the name is needed

        Election.objects.create(campaign=campaign, name=name)
        return redirect("campaign_list")

    return render(request, "create_election.html", {"campaign": campaign})

# Edit Election
def edit_election(request, election_id):
    election = get_object_or_404(Election, id=election_id)

    if request.method == "POST":
        election.name = request.POST.get("name", election.name)
        election.save()
        return redirect("campaign_list")

    return render(request, "edit_election.html", {"election": election})


def delete_election(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    campaign_id = election.campaign.id
    election.delete()
    return redirect("campaign_list")

def view_profile(request, manager_id):
    manager = get_object_or_404(ElectionManager, id=manager_id)
    return render(request, "view_profile.html", {"manager": manager})


def edit_profile(request, manager_id):
    manager = get_object_or_404(ElectionManager, id=manager_id)

    if request.method == "POST":
        manager.fullname = request.POST.get("fullname", manager.fullname)  # ✅ Ensure this matches models.py
        manager.phone_number = request.POST.get("phone_number", manager.phone_number)
        manager.email = request.POST.get("email", manager.email)
        manager.address = request.POST.get("address", manager.address)

        if "profile_picture" in request.FILES:
            manager.profile_picture = request.FILES["profile_picture"]

        manager.save()
        return redirect("view_profile", manager_id=manager.id)

    return render(request, "edit_profile.html", {"manager": manager})
