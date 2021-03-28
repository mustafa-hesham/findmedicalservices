from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register_center/', views.register_center, name='register_center'),
    path('register_user/', views.register_user, name='register_user'),
    path('save_center_data/', views.save_center_data, name='save_center_data'),
    path('save_user_data/', views.save_user_data, name='save_user_data'),
    path('login/', views.CustomLoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('results/<int:page_number>', views.search_results, name='results'),
    path('reservation/', views.reservation_page, name='reservation'),
    path('save_reservation/', views.save_reservation, name='save_reservation'),
    path('successful_reservation/', views.successful_reservation, name='successful_reservation'),
]
