from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views


urlpatterns = [
    path('', views.public_home, name='public_home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('auth/', views.auth_choice, name='auth_choice'),
    path('login/', views.SiteLoginView.as_view(), name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('buyer/', views.buyer_dashboard, name='buyer_dashboard'),
    path('buyer/designs/', views.design_catalog, name='design_catalog'),
    path('buyer/orders/new/', views.create_order, name='create_order'),
    path('buyer/orders/new/<uuid:design_id>/', views.create_order, name='create_order_for_design'),
    path('buyer/payments/new/', views.create_payment, name='create_payment'),
    path('buyer/payments/new/<int:order_id>/', views.create_payment, name='create_payment_for_order'),
    path('employee/orders/', views.employee_orders, name='employee_orders'),
    path('employee/orders/<int:order_id>/status/', views.update_order_status, name='update_order_status'),
]
