from django.urls import path, include
from . import views

app_name = 'accounts'
urlpatterns = [
    path('center_profile', views.center_profile, name = 'center_profile'),
    path('view_orders/<int:page_number>', views.view_orders, name = 'view_orders'),
    path('decline_order', views.decline_order, name = 'decline_order'),
    path('review_order', views.review_order, name = 'review_order'),
    path('confirm_order', views.confirm_order, name = 'confirm_order'),
    path('edit_profile', views.edit_profile, name = 'edit_profile'),
    path('update_profile', views.update_profile, name = 'update_profile'),
    path('successful_update', views.successful_update, name = 'successful_update'),
    path('change_password/', views.change_password, name='change_password'),
    path('services_count/', views.center_services_count, name='center_services_count'),
    path('view_current_orders/<int:page_number>', views.view_current_orders, name = 'view_current_orders'),
    path('view_past_orders/<int:page_number>', views.view_past_orders, name = 'view_past_orders'),
    path('view_rejected_orders/<int:page_number>', views.view_rejected_orders, name = 'view_rejected_orders'),
    path('user_orders/<int:page_number>', views.user_orders, name = 'user_orders'),
    path('decline_confirmed_order', views.decline_confirmed_order, name = 'decline_confirmed_order'),
    path('modify_order', views.modify_order, name = 'modify_order'),
]