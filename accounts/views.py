from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.db.models import Count, DecimalField, Sum, Value, Q
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST

from designs.models import Design
from finance.models import Expense, Payment, PaymentStatus, Statistics
from orders.models import Order, OrderStatus

from .models import UserProfile


MONEY_FIELD = DecimalField(max_digits=14, decimal_places=2)


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def get_role(user):
    if user.is_staff or user.is_superuser:
        return UserProfile.Role.ADMIN
    return getattr(getattr(user, 'profile', None), 'role', UserProfile.Role.BUYER)


def role_redirect(user):
    """Return the correct dashboard URL for a user based on their role."""
    role = get_role(user)
    if role == UserProfile.Role.ADMIN:
        return reverse_lazy('admin_dashboard')
    if role == UserProfile.Role.EMPLOYEE:
        return reverse_lazy('employee_orders')
    return reverse_lazy('buyer_dashboard')


def _admin_required(view_func):
    """Decorator: only admin (is_staff/is_superuser) can access."""
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse_lazy('login')}?next={request.path}")
        if get_role(request.user) != UserProfile.Role.ADMIN:
            return redirect(role_redirect(request.user))
        return view_func(request, *args, **kwargs)
    return wrapper


def _employee_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse_lazy('login')}?next={request.path}")
        if get_role(request.user) != UserProfile.Role.EMPLOYEE:
            return redirect(role_redirect(request.user))
        return view_func(request, *args, **kwargs)
    return wrapper


def _buyer_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse_lazy('login')}?next={request.path}")
        if get_role(request.user) != UserProfile.Role.BUYER:
            return redirect(role_redirect(request.user))
        return view_func(request, *args, **kwargs)
    return wrapper


# ─────────────────────────────────────────────
#  Auth views
# ─────────────────────────────────────────────

class SiteLoginView(LoginView):
    """Login page — redirects to the correct panel based on role."""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        # If ?next= is set, honour it; otherwise go to role-based dashboard
        next_url = self.get_redirect_url()
        if next_url:
            return next_url
        return role_redirect(self.request.user)


def public_home(request):
    # Always show the public catalog — authenticated users see it too
    designs = Design.objects.prefetch_related('colors__color', 'colors__stone_size')
    return render(request, 'accounts/public_home.html', {'designs': designs})


def auth_choice(request):
    if request.user.is_authenticated:
        return redirect(request.GET.get('next') or role_redirect(request.user))
    return render(request, 'accounts/auth_choice.html', {
        'next_url': request.GET.get('next') or reverse_lazy('buyer_dashboard'),
    })


def signup(request):
    """Only buyers can self-register."""
    if request.user.is_authenticated:
        return redirect(role_redirect(request.user))

    next_url = request.GET.get('next') or request.POST.get('next') or reverse_lazy('buyer_dashboard')
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
    """Generic redirect — sends user to their role-specific panel."""
    return redirect(role_redirect(request.user))


# ─────────────────────────────────────────────
#  ADMIN panel
# ─────────────────────────────────────────────

@_admin_required
def admin_dashboard(request):
    # Summary stats
    total_orders   = Order.objects.count()
    pending_orders = Order.objects.filter(status__code='sent').count()
    total_buyers   = User.objects.filter(profile__role='buyer').count()
    total_employees = User.objects.filter(profile__role='employee').count()

    accepted_payments = Payment.objects.filter(status__code='accepted').aggregate(
        total=Coalesce(Sum('amount'), Value(0), output_field=MONEY_FIELD)
    )['total']

    total_expenses = Expense.objects.aggregate(
        total=Coalesce(Sum('total_amount'), Value(0), output_field=MONEY_FIELD)
    )['total']

    recent_orders = (
        Order.objects
        .select_related('design', 'buyer', 'status', 'employee')
        .order_by('-created_at')[:8]
    )

    recent_payments = (
        Payment.objects
        .select_related('order__design', 'order__buyer', 'status')
        .order_by('-created_at')[:6]
    )

    statuses = OrderStatus.objects.annotate(cnt=Count('orders')).order_by('id')
    stats_months = Statistics.objects.order_by('-month')[:6]

    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_buyers': total_buyers,
        'total_employees': total_employees,
        'accepted_payments': accepted_payments,
        'total_expenses': total_expenses,
        'profit': accepted_payments - total_expenses,
        'recent_orders': recent_orders,
        'recent_payments': recent_payments,
        'statuses': statuses,
        'stats_months': stats_months,
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@_admin_required
def admin_orders(request):
    status_code = request.GET.get('status', '')
    search = request.GET.get('q', '').strip()

    orders = Order.objects.select_related('design', 'buyer', 'employee', 'status')
    if status_code:
        orders = orders.filter(status__code=status_code)
    if search:
        orders = orders.filter(
            Q(design__name__icontains=search) |
            Q(buyer__username__icontains=search) |
            Q(id__icontains=search)
        )

    statuses = OrderStatus.objects.annotate(order_count=Count('orders'))
    context = {
        'orders': orders,
        'statuses': statuses,
        'active_status': status_code,
        'search': search,
        'total_orders': Order.objects.count(),
        'new_orders': Order.objects.filter(status__code='sent').count(),
    }
    return render(request, 'accounts/admin_orders.html', context)


@_admin_required
@require_POST
def admin_update_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    status_id = request.POST.get('status')
    sale_price = request.POST.get('sale_price')
    cost_price = request.POST.get('cost_price')
    employee_id = request.POST.get('employee')

    if status_id:
        order.status = get_object_or_404(OrderStatus, id=status_id)
    if sale_price:
        try:
            order.sale_price = float(sale_price)
        except ValueError:
            pass
    if cost_price:
        try:
            order.cost_price = float(cost_price)
        except ValueError:
            pass
    if employee_id:
        try:
            order.employee = User.objects.get(id=employee_id)
        except User.DoesNotExist:
            pass
    order.save()
    messages.success(request, f'Zakaz #{order.id} yangilandi.')
    return redirect(request.POST.get('next') or 'admin_orders')


@_admin_required
def admin_payments(request):
    status_code = request.GET.get('status', '')
    payments = Payment.objects.select_related('order__design', 'order__buyer', 'status')
    if status_code:
        payments = payments.filter(status__code=status_code)

    payment_statuses = PaymentStatus.objects.all()
    total_accepted = Payment.objects.filter(status__code='accepted').aggregate(
        total=Coalesce(Sum('amount'), Value(0), output_field=MONEY_FIELD)
    )['total']
    total_pending = Payment.objects.filter(status__code='sent').aggregate(
        total=Coalesce(Sum('amount'), Value(0), output_field=MONEY_FIELD)
    )['total']

    context = {
        'payments': payments,
        'payment_statuses': payment_statuses,
        'active_status': status_code,
        'total_accepted': total_accepted,
        'total_pending': total_pending,
    }
    return render(request, 'accounts/admin_payments.html', context)


@_admin_required
@require_POST
def admin_update_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    status_id = request.POST.get('status')
    if status_id:
        payment.status = get_object_or_404(PaymentStatus, id=status_id)
        payment.save(update_fields=['status', 'updated_at'])
    messages.success(request, f'To\'lov #{payment.id} statusi yangilandi.')
    return redirect(request.POST.get('next') or 'admin_payments')


@_admin_required
def admin_users(request):
    role_filter = request.GET.get('role', '')
    users = User.objects.select_related('profile').order_by('-date_joined')
    if role_filter:
        if role_filter == 'admin':
            users = users.filter(is_staff=True)
        else:
            users = users.filter(profile__role=role_filter, is_staff=False)

    buyers    = User.objects.filter(profile__role='buyer', is_staff=False).count()
    employees = User.objects.filter(profile__role='employee', is_staff=False).count()
    admins    = User.objects.filter(is_staff=True).count()

    context = {
        'users': users,
        'role_filter': role_filter,
        'buyers': buyers,
        'employees': employees,
        'admins': admins,
    }
    return render(request, 'accounts/admin_users.html', context)


@_admin_required
@require_POST
def admin_update_user_role(request, user_id):
    target = get_object_or_404(User, id=user_id)
    new_role = request.POST.get('role')
    if new_role in ('buyer', 'employee'):
        target.profile.role = new_role
        target.profile.save(update_fields=['role', 'updated_at'])
        target.is_staff = False
        target.save(update_fields=['is_staff'])
        messages.success(request, f'{target.username} roli yangilandi.')
    return redirect('admin_users')


# ─────────────────────────────────────────────
#  EMPLOYEE panel
# ─────────────────────────────────────────────

@_employee_required
def employee_orders(request):
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
        'my_orders': Order.objects.filter(employee=request.user).count(),
    }
    return render(request, 'accounts/employee_orders.html', context)


@_employee_required
@require_POST
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    status = get_object_or_404(OrderStatus, id=request.POST.get('status'))
    order.status = status
    if not order.employee:
        order.employee = request.user
    order.save(update_fields=['status', 'employee', 'updated_at'])
    messages.success(request, f'Zakaz #{order.id} statusi yangilandi.')
    return redirect(request.POST.get('next') or 'employee_orders')


# ─────────────────────────────────────────────
#  BUYER panel
# ─────────────────────────────────────────────

@_buyer_required
def buyer_dashboard(request):
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
    orders_total = orders.aggregate(
        total=Coalesce(Sum('sale_price'), Value(0), output_field=MONEY_FIELD)
    )['total']
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


@_buyer_required
def design_catalog(request):
    designs = Design.objects.prefetch_related('colors__color', 'colors__stone_size')
    return render(request, 'accounts/design_catalog.html', {'designs': designs})


def design_detail(request, design_id):
    design = get_object_or_404(
        Design.objects.prefetch_related('colors__color', 'colors__stone_size'),
        id=design_id,
    )
    return render(request, 'accounts/design_detail.html', {
        'design': design,
        'is_authenticated': request.user.is_authenticated,
    })


@_buyer_required
def create_order(request, design_id=None):
    designs = Design.objects.all()
    selected_design = None
    if design_id:
        selected_design = get_object_or_404(Design, id=design_id)

    if request.method == 'POST':
        design = get_object_or_404(Design, id=request.POST.get('design'))
        status, _ = OrderStatus.objects.get_or_create(code='sent', defaults={'name': 'Sent'})
        quantity = max(1, int(request.POST.get('quantity') or 1))
        Order.objects.create(
            design=design,
            buyer=request.user,
            date=timezone.localdate(),
            quantity=quantity,
            note=request.POST.get('note', '').strip(),
            status=status,
        )
        messages.success(request, "Zakaz yuborildi. Xodimlar tez orada ko'rib chiqadi.")
        return redirect('buyer_dashboard')

    return render(request, 'accounts/order_form.html', {
        'designs': designs,
        'selected_design': selected_design,
    })


@_buyer_required
def create_payment(request, order_id=None):
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
        messages.success(request, "To'lov cheki yuborildi.")
        return redirect('buyer_dashboard')

    return render(request, 'accounts/payment_form.html', {
        'orders': orders,
        'selected_order': selected_order,
    })
