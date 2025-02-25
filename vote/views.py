
from django.shortcuts import render, redirect,get_object_or_404
from .models import ElectionManager,ElectionCampaign,Election,Candidate

def index(request):
    return render(request, 'index.html')


def register_manager(request):
    if request.method == "POST":
        id_number = request.POST.get("id_number")
        profile_picture = request.FILES.get("profile_picture")
        fullname = request.POST.get("fullname")  # ✅ Ensure this matches the model field
        username = request.POST.get("username")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        address = request.POST.get("address")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # ✅ Check if passwords match
        if password != confirm_password:
            return render(request, "register_manager.html", {"error": "Passwords do not match."})

        # ✅ Ensure unique fields are not duplicated
        if ElectionManager.objects.filter(username=username).exists():
            return render(request, "register_manager.html", {"error": "Username already exists."})

        if ElectionManager.objects.filter(email=email).exists():
            return render(request, "register_manager.html", {"error": "Email already registered."})

        if ElectionManager.objects.filter(id_number=id_number).exists():
            return render(request, "register_manager.html", {"error": "ID number already exists."})

        if ElectionManager.objects.filter(phone_number=phone_number).exists():
            return render(request, "register_manager.html", {"error": "Phone number already registered."})

        # ✅ Create Election Manager
        manager = ElectionManager(
            id_number=id_number,
            profile_picture=profile_picture,
            fullname=fullname,  # ✅ Matches model field name
            username=username,
            phone_number=phone_number,
            email=email,
            address=address,
            password=password  # ⚠️ In a real project, hash passwords before saving!
        )
        manager.save()

        return redirect("/login_manager/")  # ✅ Redirect to login after successful registration

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

    # ✅ Fetch campaigns only created by this manager
    campaigns = ElectionCampaign.objects.filter(manager=manager)

    return render(request, "manager_dashboard.html", {"manager": manager, "campaigns": campaigns})

def create_campaign(request, manager_id):  # ✅ Ensure manager_id is passed
    manager = get_object_or_404(ElectionManager, id=manager_id)  # ✅ Get Manager Object

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        image = request.FILES.get("image")

        # ✅ Create campaign with manager
        campaign = ElectionCampaign(
            manager=manager,  # ✅ Assign manager here
            name=name,
            description=description,
            start_time=start_time,
            end_time=end_time,
            image=image
        )
        campaign.save()

        return redirect(f"/manager/{manager.id}/dashboard/")  # ✅ Redirect to manager dashboard

    return render(request, "create_campaign.html", {"manager": manager})

# List All Campaigns
def campaign_list(request, manager_id):
    campaigns = ElectionCampaign.objects.all()
    manager = get_object_or_404(ElectionManager, id=manager_id)  # ✅ Ensure manager is retrieved
    return render(request, "campaign_list.html", {"campaigns": campaigns, "manager": manager})


def edit_campaign(request, campaign_id):
    campaign = get_object_or_404(ElectionCampaign, id=campaign_id)
    manager = campaign.manager  # ✅ Get the manager from the campaign

    if request.method == "POST":
        campaign.name = request.POST.get("name")
        campaign.description = request.POST.get("description")
        campaign.start_time = request.POST.get("start_time")
        campaign.end_time = request.POST.get("end_time")

        if "image" in request.FILES:
            campaign.image = request.FILES["image"]

        campaign.save()

        return redirect(f"/manager/{manager.id}/campaigns/")  # ✅ Redirect with `manager_id`

    return render(request, "edit_campaign.html", {"campaign": campaign, "manager": manager})

# Delete Election Campaign
def delete_campaign(request, campaign_id):
    campaign = get_object_or_404(ElectionCampaign, id=campaign_id)
    manager_id = campaign.manager.id  # ✅ Get manager ID before deleting
    campaign.delete()

    return redirect(f"/manager/{manager_id}/campaigns/")  # ✅ Redirect with `manager_id`

# Create Election Inside a Campaign
def create_election(request, campaign_id):
    campaign = get_object_or_404(ElectionCampaign, id=campaign_id)
    manager_id = campaign.manager.id  # ✅ Get the manager ID from the campaign

    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            Election.objects.create(campaign=campaign, name=name)

        return redirect(f"/manager/{manager_id}/campaigns/")  # ✅ Redirect with `manager_id`

    return render(request, "create_election.html", {"campaign": campaign, "manager_id": manager_id})

def edit_election(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    campaign = election.campaign
    manager_id = campaign.manager.id  # ✅ Get the manager ID from the campaign

    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            election.name = name
            election.save()
            return redirect(f"/manager/{manager_id}/campaigns/")  # ✅ Redirect with `manager_id`

    return render(request, "edit_election.html", {"election": election, "manager_id": manager_id})


def delete_election(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    campaign = election.campaign
    manager_id = campaign.manager.id  # ✅ Get the manager ID from the campaign

    election.delete()

    return redirect(f"/manager/{manager_id}/campaigns/")  # ✅ Redirect with `manager_id`

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

def create_candidate(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    candidates = Candidate.objects.filter(election=election)  # ✅ Fetch candidates for this election

    if request.method == "POST":
        name = request.POST.get("name")
        subtitle = request.POST.get("subtitle")
        profile_picture = request.FILES.get("profile_picture")

        if not name:
            return render(request, "create_candidate.html", {"error": "Name is required.", "election": election, "candidates": candidates})

        candidate = Candidate(election=election, name=name, subtitle=subtitle, profile_picture=profile_picture)
        candidate.save()

        # ✅ If "Create and Add Another" was clicked, reload form
        if "create_another" in request.POST:
            return render(request, "create_candidate.html", {"election": election, "candidates": candidates, "success": "Candidate added!"})

        return redirect(f"/elections/{election.id}/candidates/")  # ✅ Redirect to candidate list

    return render(request, "create_candidate.html", {"election": election, "candidates": candidates})

def delete_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    election_id = candidate.election.id
    candidate.delete()
    return redirect(f"/elections/{election_id}/candidates/create/")

def edit_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)

    if request.method == "POST":
        candidate.name = request.POST.get("name")
        candidate.subtitle = request.POST.get("subtitle")
        
        if request.FILES.get("profile_picture"):
            candidate.profile_picture = request.FILES.get("profile_picture")
        
        candidate.save()
        return redirect(f"/elections/{candidate.election.id}/candidates/create/")

    return render(request, "edit_candidate.html", {"candidate": candidate})

