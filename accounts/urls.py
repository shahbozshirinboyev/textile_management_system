from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    # ── Public ──────────────────────────────────────────
    path('', views.public_home, name='public_home'),
    path('login/', views.SiteLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('auth/', views.auth_choice, name='auth_choice'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('designs/<uuid:design_id>/', views.design_detail, name='design_detail'),

    # ── Admin panel ──────────────────────────────────────
    path('panel/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/orders/', views.admin_orders, name='admin_orders'),
    path('panel/orders/<int:order_id>/update/', views.admin_update_order, name='admin_update_order'),
    path('panel/payments/', views.admin_payments, name='admin_payments'),
    path('panel/payments/<int:payment_id>/update/', views.admin_update_payment, name='admin_update_payment'),
    path('panel/users/', views.admin_users, name='admin_users'),
    path('panel/users/<int:user_id>/role/', views.admin_update_user_role, name='admin_update_user_role'),

    # ── Employee panel ───────────────────────────────────
    path('employee/orders/', views.employee_orders, name='employee_orders'),
    path('employee/orders/<int:order_id>/status/', views.update_order_status, name='update_order_status'),

    # ── Buyer panel ──────────────────────────────────────
    path('buyer/', views.buyer_dashboard, name='buyer_dashboard'),
    path('buyer/designs/', views.design_catalog, name='design_catalog'),
    path('buyer/orders/new/', views.create_order, name='create_order'),
    path('buyer/orders/new/<uuid:design_id>/', views.create_order, name='create_order_for_design'),
    path('buyer/payments/new/', views.create_payment, name='create_payment'),
    path('buyer/payments/new/<int:order_id>/', views.create_payment, name='create_payment_for_order'),
]
