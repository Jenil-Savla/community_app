from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from rest_framework.authtoken.models import Token

class Village(models.Model):
    name = models.CharField(max_length=40)
    talak = models.CharField(max_length=40)
    district = models.CharField(max_length=40)
    pincode = models.PositiveIntegerField(default=000000)
    shakha = models.CharField(max_length=50, default="None")
    no_of_families = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class Family(models.Model):
    head = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    village = models.ForeignKey(Village, on_delete=models.CASCADE)
    home_address = models.CharField(max_length=1000, default="None")
    village_address = models.CharField(max_length=1000, default="None")

    def __str__(self):
        return f"{self.head.first_name} - {self.head.email}"

class OccupationAddress(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    occupation_address = models.CharField(max_length=1000, default="None")

    def __str__(self):
        return self.family.head.email

# Create your models here.
class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):

    GENDERS = (('M','Male'),
    ('F','Female'),
    ('O','Other'))

    MARITIAL = (('Single','Single'),
    ('Married','Married'),
    ('Divorced','Divorced'),
    ('Widowed','Widowed'))

    username=None
    email = models.EmailField(("Email Address"),primary_key=True)
    phone = models.BigIntegerField(default=0000000000)
    relation = models.CharField(max_length=50, default="Self")
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    dob = models.DateField(blank=True, null=True)
    education = models.CharField(max_length=50)
    occupation = models.CharField(max_length=50)
    village = models.CharField(max_length=50)
    gender = models.CharField(default = 'Male',max_length = 10)
    blood_group=models.CharField(max_length=50)
    maritial_status = models.CharField(default = 'Single',max_length = 10)
    in_laws_village = models.CharField(max_length=50, blank=True, null=True)
    profile_pic = models.ImageField(upload_to = 'users/',blank = True, null=True)
    related_family = models.ForeignKey(Family, on_delete=models.CASCADE, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS=[]

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def token(self):
        token = Token.objects.get(user=User.objects.get(self.id))
        return token
    
class Event(models.Model):
    name = models.CharField(max_length=80)
    about = models.TextField(max_length=255)
    date = models.DateField()
    venue = models.CharField(max_length=1000, default="N/A")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    photos = models.URLField(blank = True, null=True)
    pdf = models.URLField(blank = True, null=True)
    picture = models.ImageField(upload_to = 'events/',blank = True, null=True)

    def __str__(self):
        return self.name