from django import forms
from django.forms import ModelForm, Textarea, TextInput, Select, EmailInput, PasswordInput
from services.models import CustomUser, PhoneNumbers, service, reservation
from accounts.models import ServiceCount
from django.core.validators import MaxLengthValidator, MinValueValidator, MinLengthValidator, MaxValueValidator, RegexValidator
from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserChangeForm, PasswordChangeForm
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core import validators
from django.core.exceptions import ValidationError
from django.contrib import auth


numerical_field = RegexValidator(r'[0][0-9]+', 'ادخل رقم هاتف أو جوال صحيح يبدأ بصفر')

class CustomUserForm(forms.ModelForm):
    confirm_password = forms.CharField(max_length=20, widget=PasswordInput(attrs={'placeholder': 'تأكيد كلمة المرور', 'class':"form-control",}), label = '')
    phones           = forms.CharField(max_length=15, required = True, widget=TextInput(attrs={'placeholder': 'رقم الهاتف أو الجوال', 'class':"form-control", 'id':'phoneNumber'}) ,validators=[MinLengthValidator(9, message='ادخل رقم هاتف مكون من تسعة أرقام على الأقل'), numerical_field], label = '')
    class Meta:
        model = CustomUser
        fields = [
            'name',
            'address_gov',
            'address_street',
            'email',
            'phones',
            'username',
            'password',
            'confirm_password',
        ]
        labels = {
            'name' : '',
            'address_gov' : '',
            'address_street' : '',
            'email' : '',
            'username' : '',
            'password' : '',
            
        }
        widgets = {
            'name': TextInput(attrs={'placeholder': 'الاسم', 'class':"form-control"}),
            'address_gov' : Select(attrs={'empty_label': 'المحافظة', 'class':"form-control"}),
            'address_street' : TextInput(attrs={'placeholder': 'العنوان: المركز، القرية، الشارع', 'class':"form-control"}),
            'email' :  EmailInput(attrs={'placeholder': 'البريد الإليكتروني', 'class':"form-control"}),
            'username' :  TextInput(attrs={'placeholder': 'اسم المستخدم', 'class':"form-control", 'autocomplete':"off"}),
            'password' :  PasswordInput(attrs={'placeholder': 'كلمة المرور', 'class':"form-control", 'autocomplete':"off"}),
        }
        
class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        label='',
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'اسم المستخدم', 'class':"form-control", })
    )
    password = forms.CharField(max_length=20, widget=PasswordInput(attrs={'placeholder': 'كلمة المرور', 'class':"form-control",}), label = '')
    error_messages = {
        'invalid_login': _("الرجاء التأكد من اسم المستخدم وكلمة المرور"),
        'inactive': _("هذا المستخدم موقوف"),
    }

class CenterForm(forms.ModelForm):
    confirm_password = forms.CharField(max_length=20, widget=PasswordInput(attrs={'placeholder': 'تأكيد كلمة المرور', 'class':"form-control",}), label = '')
    phones           = forms.CharField(max_length=15, required = True, widget=TextInput(attrs={'placeholder': 'رقم الهاتف أو الجوال', 'class':"form-control", 'id':'phoneNumber'}) ,validators=[MinLengthValidator(9, message='ادخل رقم هاتف مكون من تسعة أرقام على الأقل'), numerical_field], label = '')

    class Meta:
        model = CustomUser
        fields = [
            'name',
            'address_gov',
            'address_street',
            'email',
            'phones',
            'username',
            'password',
            'confirm_password',
            'services',
        ]
        labels = {
            'name' : '',
            'address_gov' : '',
            'address_street' : '',
            'email' : '',
            'username' : '',
            'password' : '',
            'services' : 'خدمات',
            
        }
        widgets = {
            'name': TextInput(attrs={'placeholder': 'الاسم', 'class':"form-control"}),
            'address_gov' : Select(attrs={'empty_label': 'المحافظة', 'class':"form-control"}),
            'address_street' : TextInput(attrs={'placeholder': 'العنوان: المركز، القرية، الشارع', 'class':"form-control"}),
            'email' :  EmailInput(attrs={'placeholder': 'البريد الإليكتروني', 'class':"form-control"}),
            'username' :  TextInput(attrs={'placeholder': 'اسم المستخدم', 'class':"form-control", 'autocomplete':"off"}),
            'password' :  PasswordInput(attrs={'placeholder': 'كلمة المرور', 'class':"form-control", 'autocomplete':"off"}),
            'services' : forms.CheckboxSelectMultiple(),
        }

class reservationForm(forms.ModelForm):
    userPhones  = forms.CharField(widget=forms.Select(), label = 'اختر رقم هاتفك الأساسي')
    class Meta:
        model = reservation
        fields = [
            'center',
            'user',
            'userPhones',
            'service',
            'checkIn',
            'checkOut',
        ]
        labels = {
            'center' : 'المنشأة الطبية',
            'user' : 'طالب الحجز',
            'service' : 'اختر الخدمة',
            'checkIn' : 'تاريخ الدخول',
            'checkOut' : 'تاريخ الخروج',
        }
        widgets = {
            'center'    : TextInput(attrs={'class':"form-control",}),
            'user'      : TextInput(attrs={'class':"form-control",}),
            'userPhones': Select(attrs={'class':"form-control", 'id' : 'selectReserv'}),
            'service'   : Select(attrs={'empty_label': 'الخدمة', 'class':"form-control, 'id' : 'selectReserv'"}),
            'checkIn'   : forms.DateInput(attrs={'type':"date", 'id' : "datePicker"}),
            'checkOut'  : forms.DateInput(attrs={'type':"date", 'id' : "datePicker1"}),
        }

class UpdateUserForm(UserChangeForm):
    phones           = forms.CharField(max_length=15, required = True, widget=TextInput(attrs={'placeholder': 'رقم الهاتف أو الجوال', 'class':"form-control", 'id':'phoneNumber'}) ,validators=[MinLengthValidator(9, message='ادخل رقم هاتف مكون من تسعة أرقام على الأقل'), numerical_field], label = '')
    class Meta:
        model = CustomUser
        fields = [
            'name',
            'address_gov',
            'address_street',
            'email',
            'phones',
            'username',
            'services',
        ]
        labels = {
            'name' : '',
            'address_gov' : '',
            'address_street' : '',
            'email' : '',
            'username' : '',
        }
        widgets = {
            'name': TextInput(attrs={'placeholder': 'الاسم', 'class':"form-control"}),
            'address_gov' : Select(attrs={'empty_label': 'المحافظة', 'class':"form-control"}),
            'address_street' : TextInput(attrs={'placeholder': 'العنوان: المركز، القرية، الشارع', 'class':"form-control",}),
            'email' :  EmailInput(attrs={'placeholder': 'البريد الإليكتروني', 'class':"form-control"}),
            'username' :  TextInput(attrs={'placeholder': 'اسم المستخدم', 'class':"form-control", 'autocomplete':"off",}),
            'services' : forms.CheckboxSelectMultiple(),
        }

class Change_password(forms.ModelForm):
    new_password1 = forms.CharField(max_length=20, widget=PasswordInput(attrs={'placeholder': 'كلمة المرور الجديدة', 'class':"form-control",}), label = '')
    new_password2 = forms.CharField(max_length=20, widget=PasswordInput(attrs={'placeholder': 'تأكيد كلمة المرور الجديدة', 'class':"form-control",}), label = '')
    class Meta:
        model = CustomUser
        fields = [
            'password',
            'new_password1',
            'new_password2',
        ]
        labels = {
            'password' : '',
            'new_password1' : '',
            'new_password2' : '',
        }
        widgets = {
            'password' :  PasswordInput(attrs={'placeholder': 'كلمة المرور', 'class':"form-control", 'autofocus': 'autofocus'}),
        }

class ServiceCountForm(forms.ModelForm):
    class Meta:
        model = ServiceCount
        fields = [
            
            'service_count',
        ]
        labels = {
            
            'service_count' : '',
        }
        widgets = {
           
            'service_count' : forms.NumberInput(attrs={'class':"form-control", 'min' : '1', 'size' : "4"}),
        }