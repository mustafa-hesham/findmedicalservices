from django.contrib import admin
from django import forms
from .forms import CustomUserForm
from .models import CustomUser, PhoneNumbers, governorate, service, reservation
# Register your models here.
class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser
    readonly_fields=('name', 'address_gov', 'address_street', 'email', 'username', 'password','date_joined','last_login',)

class PhoneAdmin(admin.ModelAdmin):
    model = PhoneNumbers
    readonly_fields=('user', 'phone',)

class GovAdmin(admin.ModelAdmin):
    model = governorate
    readonly_fields=('gov_name',)

admin.site.register(CustomUser)
admin.site.register(PhoneNumbers)
admin.site.register(governorate, GovAdmin)
admin.site.register(service)
admin.site.register(reservation)
