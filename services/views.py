from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .models import CustomUser, PhoneNumbers, Governorates, service, reservation
from accounts.models import ServiceCount
from django.conf import settings
from .forms import CustomUserForm, CustomAuthenticationForm, CenterForm, reservationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import re
# Create your views here.

phone_regex = re.compile("^[0][0-9]+$")

def index(request):
    services = service.objects.all()
    context = {
        'gov_list' : Governorates,
        'serv_list': services,
    }
    return render(request, 'main.html', context)


def register_center(request):
    services = service.objects.all()
    if  request.user.is_authenticated:
        context = {
        'gov_list' : Governorates,
        'serv_list': services,
        }
        return render(request, 'main.html', context)
    my_form = CenterForm(request.POST or None)
    context = {
        'form' : my_form,
        'title' : 'تسجيل منشأة طبية',
    }
    return render(request, 'services/register_center.html', context)

def save_center_data(request):
    my_form = CenterForm(request.POST or None)
    if my_form.is_valid():
        password = my_form.cleaned_data['password']
        confirm_password =  my_form.cleaned_data['confirm_password']
        if password != confirm_password:
            my_form.add_error('confirm_password', 'تأكيد كلمة المرور لا يُطابق كلمة المرور')

        phone_num = request.POST.getlist('phones')
        for num in phone_num:
            if (PhoneNumbers.objects.filter(phone = num).count() > 0):
                my_form.add_error('phones', 'رقم هاتف أو جوال مكرر')
                break
            elif not (phone_regex.match(num)):
                 my_form.add_error('phones', 'ادخل رقم هاتف أو جوال صحيح يبدأ بصفر مُكون من أرقام فقط')
                 break

    if not my_form.errors:
        my_form.cleaned_data['password'] = make_password(my_form.cleaned_data['password'])
        my_form.cleaned_data['confirm_password'] = make_password(my_form.cleaned_data['confirm_password'])
        CustomUser.objects.create(name=my_form.cleaned_data['name'], address_gov=my_form.cleaned_data['address_gov'], 
        address_street=my_form.cleaned_data['address_street'], email=my_form.cleaned_data['email'],
        username=my_form.cleaned_data['username'], is_center=True, password=my_form.cleaned_data['password'])
        phone_num      = request.POST.getlist('phones')
        services_list  = my_form.cleaned_data.get('services')
        user = CustomUser.objects.get(username=my_form.cleaned_data['username'])
        for serv in services_list:
            user.services.add(serv)
            user.servicecount_set.create(service_name = serv.service_name, service_count = 1)
        for num in phone_num:
            user.phonenumbers_set.create(phone=num)
        return HttpResponseRedirect(reverse('index', args=()))
        
    if my_form.errors:
        phone_num = request.POST.getlist('phones')
        return render(request, 'services/register_center.html', {'form.errors': my_form.errors,
                                                             'form' : my_form, 'phone_nums' : phone_num})

def register_user(request):
    services = service.objects.all()
    if  request.user.is_authenticated:
        context = {
        'gov_list' : Governorates,
        'serv_list': services,
        }
        return render(request, 'main.html', context)
    my_form = CustomUserForm(request.POST or None)
    context = {
        'form' : my_form,
        'title' : 'تسجيل مستخدم جديد',
    }
    return render(request, 'services/register_user.html', context)

def save_user_data(request):
     my_form = CustomUserForm(request.POST or None)
     if my_form.is_valid():
        password = my_form.cleaned_data['password']
        confirm_password =  my_form.cleaned_data['confirm_password']
        if password != confirm_password:
            my_form.add_error('confirm_password', 'تأكيد كلمة المرور لا يُطابق كلمة المرور')

        phone_num = request.POST.getlist('phones')
        for num in phone_num:
            if (PhoneNumbers.objects.filter(phone = num).count() > 0):
                my_form.add_error('phones', 'رقم هاتف أو جوال مكرر')
                break
            elif not (phone_regex.match(num)):
                 my_form.add_error('phones', 'ادخل رقم هاتف أو جوال صحيح يبدأ بصفر مُكون من أرقام فقط')
                 break

     if not my_form.errors:
        my_form.cleaned_data['password'] = make_password(my_form.cleaned_data['password'])
        my_form.cleaned_data['confirm_password'] = make_password(my_form.cleaned_data['confirm_password'])
        CustomUser.objects.create(name=my_form.cleaned_data['name'], address_gov=my_form.cleaned_data['address_gov'], 
        address_street=my_form.cleaned_data['address_street'], email=my_form.cleaned_data['email'],
        username=my_form.cleaned_data['username'], password=my_form.cleaned_data['password'])
        phone_num = request.POST.getlist('phones')
        user = CustomUser.objects.get(username=my_form.cleaned_data['username'])
        for num in phone_num:
            user.phonenumbers_set.create(phone=num)
        return HttpResponseRedirect(reverse('index', args=()))
        
     if my_form.errors:
        phone_num = request.POST.getlist('phones')
        return render(request, 'services/register_user.html', {'form.errors': my_form.errors,
                                                             'form' : my_form, 'phone_nums' : phone_num})

class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm

def logout_view(request):
    logout(request)
    return redirect('%s?next=%s' % (settings.LOGOUT_REDIRECT_URL, request.path))

def search_results(request, page_number):
    services = service.objects.all()
    searchByName = request.GET['searchByName']
    governorate  = request.GET['address_gov_sb']
    services_list = request.GET.getlist('services')
    centers_list = CustomUser.objects.filter(is_center = True, address_gov = governorate, services__isnull = False).distinct()
    if services_list and not searchByName:
        centers_list = CustomUser.objects.filter(is_center = True, address_gov = governorate, services__in=services_list)
    if searchByName and services_list:
        centers_list = CustomUser.objects.filter(is_center = True, address_gov = governorate, services__in=services_list, name__contains = searchByName)
    if searchByName and not services_list:
        centers_list = CustomUser.objects.filter(is_center = True, address_gov = governorate, name__contains = searchByName).order_by('id')
    paginator = Paginator(centers_list, 5)
    page = page_number
    try:
        centers = paginator.page(page)
    except PageNotAnInteger:
        centers = paginator.page(1)
    except EmptyPage:
        centers = paginator.page(paginator.num_pages)
    context = {
        'title'         : 'نتائج البحث',
        'centers_list'  : centers,
        'gov_list'      : Governorates,
        'serv_list'     : services,
        'searchByName'  : searchByName,
        'governorate'   : governorate,
        'services_list' : services_list,
    }
    return render(request, 'services/results.html', context)

def reservation_page(request):
    services = service.objects.all()
    userID      = request.POST['user_id']
    centerID    = request.POST['center_id']
    if not request.user.is_authenticated:
        my_form = CustomUserForm()
        context = {
        'form' : my_form,
        'title' : 'تسجيل مستخدم جديد',
        }
        return render(request, 'services/register_user.html', context)
    else:
        userObj    = CustomUser.objects.get(pk=userID)
        userPhones = userObj.phonenumbers_set.all
        centerObj  = CustomUser.objects.get(pk=centerID)
        services   = centerObj.services.all()
        serv_list = list()
        for serv in services:
            current_reservations = reservation.objects.filter(center = centerObj, is_confirmed = True, is_served = False, is_declined = False, service = serv).count()
            try:
                serv_count       = ServiceCount.objects.get(userObj = centerObj ,service_name = serv.service_name).service_count
            except ServiceCount.DoesNotExist:
                serv_count       = 1
            if current_reservations < serv_count:
                serv_list.append(serv)
            if len(serv_list) == 0:
                context = {
                    'title' : 'منشأة طبية محجوزة',
                    'center': centerObj,
                }
                return render(request, 'services/center_is_full.html', context)
        my_form    = reservationForm(request.POST or None)
        context = {
            'title'     : 'حجز خدمة',
            'user'      : userObj,
            'serv_list' : serv_list,
            'center'    : centerObj,
            'userPhones': userPhones,
            'form'      : my_form,
        }
        return render(request, 'services/reservation.html', context)

def save_reservation(request):
    userObj    = CustomUser.objects.get(pk=request.POST['user_id'])
    centerObj  = CustomUser.objects.get(pk=request.POST['center_id'])
    service_r = service.objects.get(pk=request.POST['service'])
    reservation.objects.create(center = centerObj, user = userObj, userPhones = request.POST['userPhones'], 
    service = service_r, checkIn = request.POST['checkIn'], checkOut = request.POST['checkOut'], is_confirmed = False,
    is_served = False, is_declined = False)

    return HttpResponseRedirect(reverse('successful_reservation', args=()))

def successful_reservation(request):
    context = {
        'title' : 'حجز',
    }
    return render(request, 'services/successful_reservation.html', context)