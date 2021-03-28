from django.db import models
from django import forms
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager
from django.utils import timezone
from datetime import datetime, date
from django.contrib import admin
from django.conf import settings
from django.core.validators import MaxLengthValidator, MinValueValidator, MinLengthValidator, MaxValueValidator, RegexValidator

alphaField = RegexValidator(r'[a-zA-Z\s\-\']+|[\u0621-\u064A ]+', 'مسموح فقط بإدخال حروف عربية أو لاتينية للأسماء')
emailField = RegexValidator(r'[a-zA-Z][a-zA-Z0-9_\.-]+\@[a-zA-Z]+[a-zA-Z0-9]+\.[a-z]+(\.[a-z]+)?', 'ادخل عنوان بريد إليكتروني صحيح')
usernameField = RegexValidator(r'[a-zA-Z][a-zA-Z0-9_\.-]+', 'ادخل اسم مستخدم صحيح يبدأ بحرف ويمكن أن يحتوي على أرقام أو شرطة سفلية _ أو شرطة - أو نقطة')
numerical_field = RegexValidator(r'[0][0-9]+', 'ادخل رقم هاتف أو جوال صحيح يبدأ بصفر')

class governorate(models.Model):
    gov_name     = models.CharField(max_length=20, unique=True)
    def __str__(self):
        return self.gov_name

class service(models.Model):
    service_name =  models.CharField(max_length=30, unique=True)
    def __str__(self):
        return self.service_name

services      = [('', 'خدمة')]
services     += service.objects.all().values_list('service_name', 'service_name')

Governorates  = [('', 'محافظة')]
Governorates += governorate.objects.all().values_list('gov_name', 'gov_name')

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email,password=None):
        if not username:
            raise ValueError("Users must have a username.")
        if not email:
            raise ValueError("Users must have an email address.")
        if not password:
            raise ValueError("Users must have a password.")

        user_obj = self.model(
            email = self.normalize_email(email),
            username = username
        )
        user_obj.active      = True
        user_obj.is_admin    = False
        user_obj.date_joined = timezone.now()
        user_obj.set_password(password)
        user_obj.save(using=self._db)
        return user_obj

    def create_superuser(self, username, email, password):
        user_obj = self.create_user(email = email,
            username = username,
            password = password,
        )
        user_obj.is_admin     = True
        user_obj.is_superuser = True
        user_obj.is_staff     = True
        user_obj.is_active    = True  
        user_obj.save(using=self._db)
        return user_obj

class CustomUser(AbstractBaseUser):
    
    name             = models.CharField(max_length=50, unique=True, error_messages={'unique': 'اسم مكرر'}, validators=[MinLengthValidator(5, message='يجب أن يكون الاسم مُكون من خمسة أحرف على الأقل'), alphaField])
    address_gov      = models.CharField(max_length=20, choices=Governorates)
    address_street   = models.CharField(max_length = 150, validators=[MinLengthValidator(5, message='يجب أن يكون العنوان مُكون من خمسة أحرف على الأقل')])
    email            = models.CharField(verbose_name='email address', unique=True, error_messages={'unique': 'بريد إليكتروني مكرر'}, max_length=254, validators=[emailField])
    username         = models.CharField(max_length=20, unique=True, error_messages={'unique': 'اسم مستخدم مكرر'}, validators=[MinLengthValidator(6, message='يجب أن يكون اسم المستحدم مُكون من ستة أحرف على الأقل'), usernameField])
    is_center        = models.BooleanField(default=False)
    is_admin         = models.BooleanField(default=False)
    is_staff         = models.BooleanField(default=False)
    is_active        = models.BooleanField(default=True)
    is_superuser     = models.BooleanField(default=False)
    date_joined      = models.DateTimeField(default=timezone.now)
    services         = models.ManyToManyField(service, blank=True)       

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    objects = CustomUserManager()

    def __str__(self):
        if self.is_admin:
            return self.username
        else:
            return self.name

    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return self.is_admin
    
    def user_is_center(self):
        return self.is_center

class PhoneNumbers(models.Model):
    class Meta:
        verbose_name_plural = 'Phone numbers'

    user         = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    phone        = models.CharField(max_length=15, unique=True, error_messages={'unique': 'رقم هاتف أو جوال مكرر'}, validators=[MinLengthValidator(9, message='ادخل رقم هاتف مكون من تسعة أرقام على الأقل'), numerical_field])

    def __str__(self):
        return self.user.name
    def getNumber(self):
        return self.phone

class reservation(models.Model):
    center          = models.ForeignKey(CustomUser, on_delete = models.CASCADE, related_name = 'center')
    user            = models.ForeignKey(CustomUser, on_delete = models.CASCADE, related_name = 'client')
    userPhones      = models.CharField(max_length=15, validators=[MinLengthValidator(9, message='ادخل رقم هاتف مكون من تسعة أرقام على الأقل'), numerical_field])
    service         = models.CharField(max_length=20)
    checkIn         = models.DateField()
    checkOut        = models.DateField()
    is_confirmed    = models.BooleanField(default=False)
    is_served       = models.BooleanField(default=False)
    is_declined     = models.BooleanField(default=False)

    def __str__(self):
        return self.center.name + ' ' +self.user.name

    def validDate(self):
        return self.checkOut >= self.checkIn and self.checkIn >= timezone.now
    
    def reservationServed(self):
        if self.checkOut < date.today():
            self.is_served = True
        else:
            self.is_served = False

    def reservationNotAnswered(self):
        if self.checkOut < date.today() and self.is_confirmed == False:
            return True
    
    def numberOfDays(self):
        return (self.checkOut - self.checkIn).days

    def declineReservation(self):
        self.is_declined = True

    def confirmReservation(self):
        self.is_confirmed = True
        self.is_declined = False

    
