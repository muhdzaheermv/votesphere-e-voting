from django.db import models
from django.contrib.auth.models import User

class ElectionManager(models.Model):
    id_number = models.CharField(max_length=20, unique=True)
    profile_picture = models.ImageField(upload_to="profiles/", null=True, blank=True)
    fullname = models.CharField(max_length=255)  # ✅ Make sure this field exists
    username = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)
    address = models.TextField()
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.username
    

class ElectionCampaign(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    image = models.ImageField(upload_to="campaigns/", null=True, blank=True)

    def __str__(self):
        return self.name

class Election(models.Model):
    campaign = models.ForeignKey(ElectionCampaign, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)  # ✅ Only Election Name now

    def __str__(self):
        return f"{self.name} - {self.campaign.name}"

