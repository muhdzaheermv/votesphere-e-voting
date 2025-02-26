import pandas as pd
import openpyxl
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from .models import ElectionManager,ElectionCampaign,Election,Candidate,Voter,Vote
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.core.files.storage import default_storage

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

def upload_voters(request, campaign_id):
    if request.method == "POST":
        file = request.FILES.get("excel_file")

        if not file:
            return render(request, "upload_voters.html", {"error": "No file uploaded"})

        try:
            # ✅ Read the Excel file
            df = pd.read_excel(file)

            # ✅ Ensure campaign exists
            campaign = ElectionCampaign.objects.get(id=campaign_id)

            # ✅ Iterate through rows and create voter objects
            voters_to_create = []
            for _, row in df.iterrows():
                voters_to_create.append(Voter(
                    campaign=campaign,  # ✅ Assign campaign_id
                    student_id=row["Student ID"],
                    name=row["Name"],
                    date_of_birth=row["Date of Birth"],
                    email=row["Email Address"],
                    phone_number=row["Phone Number"],
                    course_name=row["Course Name"],
                    department=row["Department"],
                    year_of_study=row["Year of Study"],
                    semester=row["Semester"]
                ))

            # ✅ Bulk create voters for performance optimization
            Voter.objects.bulk_create(voters_to_create)

            return redirect("voters_list", campaign_id=campaign.id)

        except KeyError as e:
            return render(request, "upload_voters.html", {"error": f"Missing column in Excel: {str(e)}"})
        except Exception as e:
            return render(request, "upload_voters.html", {"error": f"Error: {str(e)}"})

    return render(request, "upload_voters.html")


def voters_list(request, campaign_id):
    campaign = get_object_or_404(ElectionCampaign, id=campaign_id)
    voters = Voter.objects.filter(campaign=campaign)
    return render(request, "voter_list.html", {"campaign": campaign, "voters": voters})

def delete_all_voters(request, campaign_id):
    campaign = get_object_or_404(ElectionCampaign, id=campaign_id)
    Voter.objects.filter(campaign=campaign).delete()
    return redirect("voters_list", campaign_id=campaign.id)

def voter_login(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")

        try:
            voter = Voter.objects.get(student_id=student_id)

            if not voter.is_approved:  # ✅ Check if voter is approved
                messages.error(request, "Your account is not approved yet. Please contact the election manager.")
                return redirect("voter_login")  # 🔄 Redirect back to login page with error

            # ✅ If approved, store voter ID in session
            request.session["voter_id"] = voter.id

            # ✅ Redirect to voter dashboard with voter ID
            return redirect(reverse("voter_dashboard", args=[voter.id]))

        except Voter.DoesNotExist:
            messages.error(request, "Invalid Student ID. Please try again.")
            return redirect("voter_login")

    return render(request, "voter_login.html")

def voter_dashboard(request, voter_id):
    voter = Voter.objects.get(id=voter_id)
    elections = Election.objects.filter(campaign__voter=voter)  # Get elections for this voter

    return render(request, "voter_dashboard.html", {"voter": voter, "elections": elections})

def vote_page(request, voter_id):
    elections = Election.objects.all()  # ✅ Fetch all elections
    return render(request, "vote_page.html", {"elections": elections})

def submit_vote(request, election_id):
    if request.method == "POST":
        voter = get_object_or_404(Voter, id=request.session.get("voter_id"))  # Ensure voter is logged in
        election = get_object_or_404(Election, id=election_id)
        candidate_id = request.POST.get("vote")

        # ✅ Check if the voter has already voted in this election
        if Vote.objects.filter(voter=voter, election=election).exists():
            messages.error(request, f"You have already voted in the election: {election.name}.")
            return redirect("vote_page", voter_id=voter.id)

        # ✅ Save the vote
        candidate = get_object_or_404(Candidate, id=candidate_id)
        Vote.objects.create(voter=voter, election=election, candidate=candidate)

        messages.success(request, f"Your vote for {candidate.name} in the election '{election.name}' has been submitted successfully!")
        return redirect("vote_page", voter_id=voter.id)

    return redirect("vote_page", voter_id=request.session.get("voter_id"))

def approve_voters(request, campaign_id):
    campaign = get_object_or_404(ElectionCampaign, id=campaign_id)
    voters = Voter.objects.filter(campaign=campaign)  # Get voters of the campaign
    return render(request, "approve_voters.html", {"campaign": campaign, "voters": voters})

def approve_voter(request, voter_id):
    voter = get_object_or_404(Voter, id=voter_id)
    voter.is_approved = True
    voter.save()
    messages.success(request, f"Voter {voter.name} has been approved!")
    return redirect("approve_voters", campaign_id=voter.campaign.id)

def disapprove_voter(request, voter_id):
    voter = get_object_or_404(Voter, id=voter_id)
    voter.is_approved = False
    voter.save()
    messages.success(request, f"Voter {voter.name} has been disapproved.")
    return redirect("approve_voters", campaign_id=voter.campaign.id)

def election_results(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    candidates = Candidate.objects.filter(election=election)

    total_votes = Vote.objects.filter(candidate__election=election).count()

    results = []
    for candidate in candidates:
        votes = Vote.objects.filter(candidate=candidate).count()
        percentage = (votes / total_votes) * 100 if total_votes > 0 else 0
        results.append({
            "candidate": candidate,
            "votes": votes,
            "percentage": round(percentage, 2)
        })

    return render(request, "election_results.html", {
        "election": election,
        "results": results,
        "total_votes": total_votes
    })



