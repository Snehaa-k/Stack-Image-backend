from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator
import uuid
from django.utils import timezone
from datetime import timedelta


# Create your models here.

class CustomUser(AbstractUser):
    username = models.CharField(max_length=223, null=True)
    email = models.EmailField(max_length=223, unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    password = models.CharField(max_length=223)
    phonenumber = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be exactly 10 digits."
            )
        ],
        null=True,
        blank=True
    )
    groups = models.ManyToManyField(Group, related_name="custom_user_groups")
    reset_token = models.CharField(max_length=100, blank=True, null=True)
    token_expiration = models.DateTimeField(blank=True, null=True)
    user_permissions = models.ManyToManyField(
        Permission, related_name="custom_user_permissions"
    )
    
    def create_reset_token(self):
        self.reset_token = uuid.uuid4().hex
        self.token_expiration = timezone.now() + timedelta(seconds=60)  
        self.save()
    
    def __str__(self):
        return self.username
    
class ImageModal(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="images")
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="uploads/",max_length=300)
    order = models.PositiveIntegerField(default=0)
   
    def __str__(self):
        return self.title
