from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password
from services.models import CustomUser, PhoneNumbers, Governorates, service, reservation
from accounts.models import ServiceCount
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from services.forms import CustomUserForm, CustomAuthenticationForm, CenterForm, reservationForm, UpdateUserForm, Change_password, ServiceCountForm
import re
from django.db.models import Q

# Create your views here.
services_list = service.objects.all()
phone_regex   = re.compile("^[0][0-9]+$")
def center_profile(request):
    if  not request.user.is_authenticated or not request.user.user_is_center():
        context = {
        'gov_list' : Governorates,
        'serv_list': services_list,
        }
        return render(request, 'main.html', context)
    centerObj            = CustomUser.objects.get(pk=request.user.id)
    services             = centerObj.services.all()
    serv_count = list()
    for serv in services:
        try:
            serv_count.append(ServiceCount.objects.get(userObj = centerObj ,service_name = serv.service_name).service_count)
        except ServiceCount.DoesNotExist:
            serv_count.append(1)
    current_reservations = reservation.objects.filter(center = centerObj, is_confirmed = True, is_declined = False)
    for cur_serv in current_reservations:
        cur_serv.reservationServed()
        cur_serv.save()
    current_reservations = reservation.objects.filter(center = centerObj, is_confirmed = True, is_served = False, is_declined = False)
    new_orders           = reservation.objects.filter(center = centerObj, is_confirmed = False, is_served = False, is_declined = False, checkOut__gte = datetime.today())

    newOrderCount = list()
    curServCountList = list()
    remainingServCountList = list()
    for serv in services:
        curServCountList.append(current_reservations.filter(service = serv).count())
        newOrderCount.append(new_orders.filter(service = serv).count())
        try:
            remainingServCountList.append(ServiceCount.objects.get(userObj = centerObj ,service_name = serv.service_name).service_count - current_reservations.filter(service = serv).count())
        except ServiceCount.DoesNotExist:
            remainingServCountList.append('غير متاح')
    the_list = zip(remainingServCountList ,serv_count, services, curServCountList, newOrderCount)
    context = {
        'serv_list'         : the_list,
        'centername'        : centerObj,
        'title'             : 'ملف منشأة',
    }
    return render(request, 'accounts/center_profile.html', context)

def view_orders(request, page_number):
    if  not request.user.is_authenticated or not request.user.user_is_center():
        context = {
        'gov_list' : Governorates,
        'serv_list': services_list,
        }
        return render(request, 'main.html', context)
    centerObj             = CustomUser.objects.get(pk=request.user.id, name = request.POST['centerObj'])
    if request.method == 'POST':
        serviceObj        = request.POST['service_name']
    else:
        serviceObj        = request.GET['service_name']
    new_orders_of_service = reservation.objects.filter(center = centerObj, service = serviceObj, is_confirmed = False, is_served = False, is_declined = False, checkOut__gte = datetime.today())
    paginator             = Paginator(new_orders_of_service, 5)
    page                  = page_number
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    context = {
        'title'         : 'قائمة الحجوزات الجديدة',
        'service'       : serviceObj,
        'orders_list'   : orders,
    }
    return render(request, 'accounts/view_orders.html', context)

def decline_order(request):
    order = reservation.objects.get(pk=request.POST['order_id'])
    order.declineReservation()
    order.save()
    centerObj             = CustomUser.objects.get(pk=request.user.id)
    serviceObj            = request.POST['serviceObj']
    new_orders_of_service = reservation.objects.filter(center = centerObj, service = serviceObj, is_confirmed = False, is_served = False, is_declined = False, checkOut__gte = datetime.today())
    context = {
        'title'         : 'قائمة الحجوزات الجديدة',
        'service'       : serviceObj,
        'orders_list'   : new_orders_of_service,
    }
    return render(request, 'accounts/view_orders.html', context)

def confirm_order(request):
    userObj          = CustomUser.objects.get(pk=request.POST['userObj'])
    order            = reservation.objects.get(pk=request.POST['order_id'])
    order.center     = request.user
    order.user       = userObj
    order.userPhones = request.POST['userPhones']
    order.service    = request.POST['service']
    order.checkIn    = request.POST['checkIn']
    order.checkOut   = request.POST['checkOut']
    order.confirmReservation()
    order.save()
    centerObj             = CustomUser.objects.get(pk=request.user.id)
    serviceObj            = request.POST['serviceObj']
    new_orders_of_service = reservation.objects.filter(center = centerObj, service = serviceObj, is_confirmed = False, is_served = False, is_declined = False, checkOut__gte = datetime.today())
    messages.success(request, 'تم تأكيد الحجز بنجاح')
    context = {
        'title'         : 'قائمة الحجوزات الجديدة',
        'service'       : serviceObj,
        'orders_list'   : new_orders_of_service,
    }
    return render(request, 'accounts/view_orders.html', context)

def modify_order(request):
    userObj          = CustomUser.objects.get(pk=request.POST['userObj'])
    order            = reservation.objects.get(pk=request.POST['order_id'])
    order.center     = order.center
    order.user       = userObj
    order.userPhones = request.POST['userPhones']
    order.service    = service.objects.get(pk=request.POST['service']).service_name
    order.checkIn    = request.POST['checkIn']
    order.checkOut   = request.POST['checkOut']
    order.save()
    person                = request.user
    user_reservations     = reservation.objects.filter(user = person).order_by('-checkOut')
    paginator             = Paginator(user_reservations, 5)
    page                  = 1
    try:
        reservations = paginator.page(page)
    except PageNotAnInteger:
        reservations = paginator.page(1)
    except EmptyPage:
        reservations = paginator.page(paginator.num_pages)
    context = {
        'title'         : 'حجوزاتي',
        'reservations'  : reservations,
    }
    return render(request, 'accounts/my_orders.html', context)

def review_order(request):
    order       = reservation.objects.get(pk=request.POST['order_id'])
    services    = order.center.services.all()
    context     = {
        'title'     : 'مراجعة حجز',
        'order'     : order,
        'serv_list' : services,
    }
    return render(request, 'accounts/review_order.html', context)

def edit_profile(request):
    user             = request.user
    my_form          = UpdateUserForm(instance=request.user)
    phone_numbers    = user.phonenumbers_set.all()
    phone_nums = list()
    for phone in phone_numbers:
        phone_nums.append(phone.getNumber())
    context     = {
        'title'      : 'تعديل بياناتي',
        'form'       : my_form,
        'user'       : user,
        'gov_list'   : Governorates,
        'services'   : services_list,
        'phone_nums' : phone_nums,
    }
    return render(request, 'accounts/edit_profile.html', context)

def update_profile(request):
    user       = request.user
    my_form    = UpdateUserForm(request.POST, instance=request.user)
    if my_form.is_valid():
        phone_nums      = request.POST.getlist('phones')
        for num in phone_nums:
            if (PhoneNumbers.objects.filter(phone = num).exclude(user=user).count() > 0):
                my_form.add_error('phones', 'رقم هاتف أو جوال مكرر')
                break
            elif not (phone_regex.match(num)):
                 my_form.add_error('phones', 'ادخل رقم هاتف أو جوال صحيح يبدأ بصفر مُكون من أرقام فقط')
                 break
    if not my_form.errors:
        user.name           = my_form.cleaned_data['name']
        user.address_gov    = my_form.cleaned_data['address_gov']
        user.address_street = my_form.cleaned_data['address_street']
        user.email          = my_form.cleaned_data['email']
        phone_nums          = request.POST.getlist('phones')
        user.phonenumbers_set.all().delete()
        for num in phone_nums:
            user.phonenumbers_set.create(phone=num)
        if user.user_is_center():
            serv_list  = my_form.cleaned_data.get('services')
            user.services.set(serv_list)

        user.save()
        return HttpResponseRedirect(reverse('accounts:successful_update', args=()))
    if my_form.errors:
        return render(request, 'accounts/edit_profile.html', {'form.errors': my_form.errors,
                                                             'form' : my_form, 'phone_nums' : phone_nums,})

def successful_update(request):
    context = {
        'title' : 'تعديل ناجح',
    }
    return render(request, 'accounts/successful_update.html', context)

def change_password(request):
    my_form = Change_password(request.POST or None)
    if request.method == 'POST':
        if my_form.is_valid():
            if not request.user.check_password(my_form.cleaned_data['password']):
                my_form.add_error('password', 'كلمة مرور خاطئة')
            if my_form.cleaned_data['new_password1'] != my_form.cleaned_data['new_password2']:
                my_form.add_error('new_password1', 'تأكيد كلمة المرور الجديدة لا يُطابق كلمة المرور الجديدة')
        if not my_form.errors:
            request.user.password = make_password(my_form.cleaned_data['new_password1'])
            request.user.save()
            update_session_auth_hash(request, request.user)
            return HttpResponseRedirect(reverse('accounts:successful_update',args=()))
        elif my_form.errors:
            context = {
                'title'         : 'تغيير كلمة المرور',
                'form'          : my_form,
                'form.errors'   : my_form.errors,
            }
            return render(request, 'accounts/change_password.html', context)

    else:
        my_form = Change_password(request.POST or None)
        context = {
            'title' : 'تغيير كلمة المرور',
            'form'  : my_form,
        }
        return render(request, 'accounts/change_password.html', context)

def center_services_count(request):
    if not request.user.is_authenticated or not request.user.user_is_center():
        context = {
        'gov_list' : Governorates,
        'serv_list': services_list,
        }
        return render(request, 'main.html', context)
    user      = request.user
    serv_list = user.services.all()
    cur_reserv = list()
    for serv_name in serv_list:
        cur_reserv.append(reservation.objects.filter(center = user, service = serv_name ,is_confirmed = True, is_served = False, is_declined = False).count())
    serv_count = list()
    errors = list()
    for serv in serv_list:
        try:
            serv_count.append(ServiceCount.objects.get(userObj = user ,service_name = serv.service_name).service_count)
        except ServiceCount.DoesNotExist:
            serv_count.append(1)
    if request.method == 'POST':
        service_count_list = request.POST.getlist('service_count')
        reserve = zip(cur_reserv, service_count_list)
        for service_count in service_count_list:
            if not service_count.isnumeric():
                errors.append('يجب أن يكون العدد مكون من أرقام صحيحة فقط أكبر من الصفر')
                break
        for server, client in reserve:
            if client.isnumeric():
                if int(client) < server:
                    errors.append('يجب أن يكون عدد الوحدات أكبر من أو يساوي عدد الحجوزات الحالية')
                    break
                
        if errors:        
            the_list = zip(serv_list, serv_count, cur_reserv)
            context = {
                'title' : 'عدد وحدات الخدمة',
                'serv_list' : the_list,
                'centername' : user,
                'errors' : errors,
            }
            return render(request, 'accounts/service_count.html', context)
        if not errors:
            service_names = request.POST.getlist('service_name')
            servs_list = zip(service_names, service_count_list)
            for name, count in servs_list:
                try:
                    servObj = ServiceCount.objects.get(userObj = user ,service_name = name)
                    servObj.service_count = count
                    servObj.save()
                except ServiceCount.DoesNotExist:
                    user.servicecount_set.create(service_name = name, service_count = count)
            return HttpResponseRedirect(reverse('accounts:successful_update',args=()))
    else:
        the_list = zip(serv_list, serv_count, cur_reserv)
        context = {
            'title' : 'عدد وحدات الخدمة',
            'serv_list' : the_list,
            'centername' : user,
        }
        return render(request, 'accounts/service_count.html', context)

def view_current_orders(request, page_number):
    if  not request.user.is_authenticated or not request.user.user_is_center():
        context = {
        'gov_list' : Governorates,
        'serv_list': services_list,
        }
        return render(request, 'main.html', context)
    centerObj             = request.user
    if request.method == 'POST':
        serviceObj            = request.POST['service_name']
    else:
        serviceObj            = request.GET['service_name']
    new_orders_of_service = reservation.objects.filter(center = centerObj, service = serviceObj, is_confirmed = True, is_served = False, is_declined = False, checkOut__gte = datetime.today())
    paginator             = Paginator(new_orders_of_service, 5)
    page                  = page_number
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    context = {
        'title'         : 'قائمة الحجوزات الحالية',
        'service'       : serviceObj,
        'orders_list'   : orders,
    }
    return render(request, 'accounts/current_orders.html', context)

def decline_confirmed_order(request):
    order = reservation.objects.get(pk=request.POST['order_id'])
    order.declineReservation()
    order.save()
    centerObj             = request.user
    serviceObj            = request.POST['service_name']
    new_orders_of_service = reservation.objects.filter(center = centerObj, service = serviceObj, is_confirmed = True, is_served = False, is_declined = False, checkOut__gte = datetime.today())
    paginator             = Paginator(new_orders_of_service, 5)
    page                  = 1
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    context = {
        'title'         : 'قائمة الحجوزات الحالية',
        'service'       : serviceObj,
        'orders_list'   : orders,
    }
    return render(request, 'accounts/current_orders.html', context)

def view_past_orders(request, page_number):
    if  not request.user.is_authenticated or not request.user.user_is_center():
        context = {
        'gov_list' : Governorates,
        'serv_list': services_list,
        }
        return render(request, 'main.html', context)
    centerObj             = request.user
    if request.method == 'POST':
        serviceObj            = request.POST['service_name']
    else:
        serviceObj            = request.GET['service_name']
    past_orders_of_service = reservation.objects.filter(center = centerObj, service = serviceObj, is_confirmed = True, is_served = True, is_declined = False, checkOut__lte = datetime.today())
    paginator             = Paginator(past_orders_of_service, 5)
    page                  = page_number
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    context = {
        'title'         : 'قائمة الحجوزات السابقة',
        'service'       : serviceObj,
        'orders_list'   : orders,
    }
    return render(request, 'accounts/past_orders.html', context)

def view_rejected_orders(request, page_number):
    if  not request.user.is_authenticated or not request.user.user_is_center():
        context = {
        'gov_list' : Governorates,
        'serv_list': services_list,
        }
        return render(request, 'main.html', context)
    centerObj                  = request.user
    if request.method == 'POST':
        serviceObj             = request.POST['service_name']
    else:
        serviceObj             = request.GET['service_name']
    rejected_orders_of_service = reservation.objects.filter(center = centerObj, service = serviceObj, is_declined = True, checkOut__gte = datetime.today())
    paginator                  = Paginator(rejected_orders_of_service, 5)
    page                       = page_number
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    context = {
        'title'         : 'قائمة الحجوزات المرفوضة',
        'service'       : serviceObj,
        'orders_list'   : orders,
    }
    return render(request, 'accounts/rejected_orders.html', context)

def user_orders(request, page_number):
    if  not request.user.is_authenticated or request.user.user_is_center():
        context = {
        'gov_list' : Governorates,
        'serv_list': services_list,
        }
        return render(request, 'main.html', context)
    person                = request.user
    user_reservations     = reservation.objects.filter(user = person)
    user_reservations     = reservation.objects.filter(user = person).order_by('-checkOut')
    paginator             = Paginator(user_reservations, 5)
    page                  = page_number
    try:
        reservations = paginator.page(page)
    except PageNotAnInteger:
        reservations = paginator.page(1)
    except EmptyPage:
        reservations = paginator.page(paginator.num_pages)
    context = {
        'title'         : 'حجوزاتي',
        'reservations'  : reservations,
    }
    return render(request, 'accounts/my_orders.html', context)