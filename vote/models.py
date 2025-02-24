from django.db import models

class ElectionManager(models.Model):
    id_number = models.CharField(max_length=20, unique=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    full_name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)
    address = models.TextField()
    password = models.CharField(max_length=100)  # Store hashed password in real applications

    def __str__(self):
        return self.username
