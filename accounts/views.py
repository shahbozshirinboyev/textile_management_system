from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.db.models import Count, DecimalField, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST

from designs.models import Design
from finance.models import Payment, PaymentStatus
from orders.models import Order, OrderStatus

from .models import UserProfile


MONEY_FIELD = DecimalField(max_digits=14, decimal_places=2)


def get_role(user):
    if user.is_staff or user.is_superuser:
        return UserProfile.Role.ADMIN
    return getattr(getattr(user, 'profile', None), 'role', UserProfile.Role.BUYER)


class SiteLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy('dashboard')


def public_home(request):
    if request.user.is_authenticated:
        return dashboard(request)

    designs = Design.objects.prefetch_related('colors__color', 'colors__stone_size')
    return render(request, 'accounts/public_home.html', {'designs': designs})


def auth_choice(request):
    if request.user.is_authenticated:
        return redirect(request.GET.get('next') or 'dashboard')
    return render(request, 'accounts/auth_choice.html', {
        'next_url': request.GET.get('next') or reverse_lazy('dashboard'),
    })


def signup(request):
    if request.user.is_authenticated:
        return redirect(request.GET.get('next') or 'dashboard')

    next_url = request.GET.get('next') or request.POST.get('next') or reverse_lazy('dashboard')
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        user.profile.role = UserProfile.Role.BUYER
        user.profile.save(update_fields=['role', 'updated_at'])
        login(request, user)
        return redirect(next_url)

    return render(request, 'accounts/signup.html', {
        'form': form,
        'next_url': next_url,
    })


@login_required
def dashboard(request):
    role = get_role(request.user)
    if role == UserProfile.Role.ADMIN:
        return redirect('/admin/')
    if role == UserProfile.Role.EMPLOYEE:
        return redirect('employee_orders')
    return redirect('buyer_dashboard')


@login_required
def buyer_dashboard(request):
    if get_role(request.user) != UserProfile.Role.BUYER:
        return dashboard(request)

    orders = (
        Order.objects
        .filter(buyer=request.user)
        .select_related('design', 'status')
        .prefetch_related('payments')
    )
    accepted_payments = Payment.objects.filter(
        order__buyer=request.user,
        status__code='accepted',
    ).aggregate(total=Coalesce(Sum('amount'), Value(0), output_field=MONEY_FIELD))['total']
    orders_total = orders.aggregate(total=Coalesce(Sum('sale_price'), Value(0), output_field=MONEY_FIELD))['total']
    recent_orders = orders[:6]
    recent_payments = (
        Payment.objects
        .filter(order__buyer=request.user)
        .select_related('order', 'order__design', 'status')
        .order_by('-date', '-created_at')[:5]
    )

    context = {
        'orders_count': orders.count(),
        'accepted_payments': accepted_payments,
        'orders_total': orders_total,
        'balance': accepted_payments - orders_total,
        'recent_orders': recent_orders,
        'recent_payments': recent_payments,
    }
    return render(request, 'accounts/buyer_dashboard.html', context)


@login_required
def design_catalog(request):
    if get_role(request.user) != UserProfile.Role.BUYER:
        return dashboard(request)

    designs = Design.objects.prefetch_related('colors__color', 'colors__stone_size')
    return render(request, 'accounts/design_catalog.html', {'designs': designs})


@login_required
def create_order(request, design_id=None):
    if get_role(request.user) != UserProfile.Role.BUYER:
        return dashboard(request)

    designs = Design.objects.all()
    selected_design = None
    if design_id:
        selected_design = get_object_or_404(Design, id=design_id)

    if request.method == 'POST':
        design = get_object_or_404(Design, id=request.POST.get('design'))
        status, _ = OrderStatus.objects.get_or_create(code='sent', defaults={'name': 'Sent'})
        Order.objects.create(
            design=design,
            buyer=request.user,
            date=timezone.localdate(),
            note=request.POST.get('note', '').strip(),
            status=status,
        )
        messages.success(request, 'Zakaz yuborildi. Xodimlar tez orada ko\'rib chiqadi.')
        return redirect('buyer_dashboard')

    return render(request, 'accounts/order_form.html', {
        'designs': designs,
        'selected_design': selected_design,
    })


@login_required
def create_payment(request, order_id=None):
    if get_role(request.user) != UserProfile.Role.BUYER:
        return dashboard(request)

    orders = Order.objects.filter(buyer=request.user).select_related('design')
    selected_order = None
    if order_id:
        selected_order = get_object_or_404(orders, id=order_id)

    if request.method == 'POST':
        order = get_object_or_404(orders, id=request.POST.get('order'))
        status, _ = PaymentStatus.objects.get_or_create(code='sent', defaults={'name': 'Sent'})
        Payment.objects.create(
            order=order,
            date=timezone.localdate(),
            amount=request.POST.get('amount') or 0,
            receipt_image=request.FILES.get('receipt_image'),
            status=status,
        )
        messages.success(request, 'To\'lov cheki yuborildi.')
        return redirect('buyer_dashboard')

    return render(request, 'accounts/payment_form.html', {
        'orders': orders,
        'selected_order': selected_order,
    })


@login_required
def employee_orders(request):
    if get_role(request.user) != UserProfile.Role.EMPLOYEE:
        return dashboard(request)

    status_code = request.GET.get('status', '')
    orders = Order.objects.select_related('design', 'buyer', 'employee', 'status')
    if status_code:
        orders = orders.filter(status__code=status_code)

    statuses = OrderStatus.objects.annotate(order_count=Count('orders'))
    context = {
        'orders': orders,
        'statuses': statuses,
        'active_status': status_code,
        'total_orders': Order.objects.count(),
        'new_orders': Order.objects.filter(status__code='sent').count(),
    }
    return render(request, 'accounts/employee_orders.html', context)


@login_required
@require_POST
def update_order_status(request, order_id):
    if get_role(request.user) != UserProfile.Role.EMPLOYEE:
        return dashboard(request)

    order = get_object_or_404(Order, id=order_id)
    status = get_object_or_404(OrderStatus, id=request.POST.get('status'))
    order.status = status
    if not order.employee:
        order.employee = request.user
    order.save(update_fields=['status', 'employee', 'updated_at'])
    messages.success(request, f'Zakaz #{order.id} statusi yangilandi.')
    return redirect(request.POST.get('next') or 'employee_orders')

# Create your views here.
