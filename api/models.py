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
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        print(user)
        user.set_password(password)
        user.save(using=self._db)
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

    username=models.CharField(max_length=50, unique=True, blank=True, null=True)
    email = models.EmailField(("Email Address"), primary_key=True)
    email_id = models.EmailField(("Email"), blank=True, null=True)
    phone = models.BigIntegerField(default=0000000000)
    additional_phone = models.BigIntegerField(default=0000000000)
    relation = models.CharField(max_length=50, default="Self")
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    dob = models.DateField(blank=True, null=True)
    education = models.CharField(max_length=50)
    occupation = models.CharField(max_length=50)
    village = models.CharField(max_length=50)
    shakha = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(default = 'Male',max_length = 10)
    blood_group=models.CharField(max_length=50)
    maritial_status = models.CharField(default = 'Single',max_length = 10)
    in_laws_village = models.CharField(max_length=50, blank=True, null=True)
    in_laws_shakha = models.CharField(max_length=50, blank=True, null=True)
    in_laws_name = models.CharField(max_length=50, blank=True, null=True)
    profile_pic = models.ImageField(upload_to = 'users/',blank = True, null=True)
    related_family = models.ForeignKey(Family, on_delete=models.CASCADE, blank=True, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS=[]

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def token(self):
        token = Token.objects.get(user=User.objects.get(self.id))
        return token
    
class Event(models.Model):
    name = models.CharField(max_length=255)
    about = models.TextField()
    date = models.DateField()
    venue = models.CharField(max_length=1000, default="N/A")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    photos = models.URLField(blank = True, null=True)
    pdf = models.URLField(blank = True, null=True)
    picture = models.ImageField(upload_to = 'events/',blank = True, null=True)

    def __str__(self):
        return self.name

class Content(models.Model):
    title = models.CharField(max_length=255)
    details = models.TextField()

    def __str__(self):
        return self.title
    
class SocietyMember(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=80)

    def __str__(self):
        return self.name
    
class Founder(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=80)
    about = models.TextField()
    profile_pic = models.ImageField(upload_to = 'founders/',blank = True, null=True)

    def __str__(self):
        return self.name

class CommitteeMember(models.Model):
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=80, default="Member")
    detail = models.TextField(default="Current Committee Member")
    profile_pic = models.ImageField(upload_to = 'committee-members/',blank = True, null=True)

    def __str__(self):
        return self.name
    
class Blog(models.Model):
    title = models.CharField(max_length=255)
    details = models.TextField(default="NA")
    picture = models.ImageField(upload_to = 'blogs/',blank = True, null=True)
    phone = models.BigIntegerField(default=0000000000)
    is_advertisement = models.BooleanField(default=False)
    is_job = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title