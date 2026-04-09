from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, Avg
from django.db.models.functions import TruncDate
from django.shortcuts import render, redirect
from django.utils import timezone

from apps.accounts.models import User
from apps.wallet.models import Wallet, Transaction, MasterWallet
from apps.transfers.models import Transfer
from apps.crypto.models import CryptoDeposit, ExchangeRate, LlanocoinTransaction
from apps.marketplace.models import Merchant, MerchantPayment
from apps.microcredit.models import Microcredit, MicrocreditProduct, MicrocreditPayment
from apps.notifications.models import Notification


def login_view(request):
    """Vista de inicio de sesion para el panel de administracion."""
    error = None
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '')
        remember = request.POST.get('remember', False)

        user = authenticate(request, phone_number=phone_number, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            if not remember:
                request.session.set_expiry(0)
            next_url = request.GET.get('next', '/dashboard/')
            return redirect(next_url)
        else:
            error = 'Credenciales invalidas o no tiene permisos de administrador.'

    return render(request, 'dashboard/login.html', {'error': error})


def logout_view(request):
    """Cerrar sesion y redirigir al login."""
    logout(request)
    return redirect('dashboard:login')


@login_required(login_url='/dashboard/login/')
def dashboard_view(request):
    """Panel principal con estadisticas generales."""
    now = timezone.now()
    today = now.date()
    thirty_days_ago = now - timedelta(days=30)

    # Stats cards
    total_users = User.objects.count()
    total_cop = Wallet.objects.aggregate(total=Sum('balance_cop'))['total'] or Decimal('0')
    total_llo = Wallet.objects.aggregate(total=Sum('balance_llo'))['total'] or Decimal('0')
    transactions_today = Transaction.objects.filter(created_at__date=today).count()

    # Transactions last 30 days (for line chart)
    daily_transactions = (
        Transaction.objects
        .filter(created_at__gte=thirty_days_ago)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    chart_labels = [item['date'].strftime('%d/%m') for item in daily_transactions]
    chart_data = [item['count'] for item in daily_transactions]

    # Transaction type distribution (pie chart)
    type_distribution = (
        Transaction.objects
        .filter(created_at__gte=thirty_days_ago)
        .values('transaction_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    pie_labels = [item['transaction_type'] for item in type_distribution]
    pie_data = [item['count'] for item in type_distribution]

    # Type display names map
    type_display = dict(Transaction.TransactionType.choices)
    pie_labels_display = [type_display.get(label, label) for label in pie_labels]

    # Recent transactions
    recent_transactions = (
        Transaction.objects
        .select_related('wallet__user')
        .order_by('-created_at')[:10]
    )

    # Recent registrations
    recent_users = User.objects.order_by('-created_at')[:5]

    # Active microcredits summary
    active_microcredits = Microcredit.objects.filter(
        status__in=['ACTIVE', 'DISBURSED']
    ).count()
    total_disbursed = Microcredit.objects.filter(
        status__in=['ACTIVE', 'DISBURSED', 'PAID']
    ).aggregate(total=Sum('amount_approved'))['total'] or Decimal('0')

    context = {
        'total_users': total_users,
        'total_cop': total_cop,
        'total_llo': total_llo,
        'transactions_today': transactions_today,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'pie_labels': pie_labels_display,
        'pie_data': pie_data,
        'recent_transactions': recent_transactions,
        'recent_users': recent_users,
        'active_microcredits': active_microcredits,
        'total_disbursed': total_disbursed,
        'page_title': 'Dashboard',
    }
    return render(request, 'dashboard/index.html', context)


@login_required(login_url='/dashboard/login/')
def users_view(request):
    """Vista de gestion de usuarios."""
    search = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')

    users = User.objects.all().order_by('-created_at')

    if search:
        users = users.filter(
            Q(phone_number__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(document_number__icontains=search)
        )
    if status_filter == 'verified':
        users = users.filter(is_verified=True)
    elif status_filter == 'unverified':
        users = users.filter(is_verified=False)
    elif status_filter == 'merchant':
        users = users.filter(is_merchant=True)

    # Simple pagination
    page = int(request.GET.get('page', 1))
    per_page = 20
    total = users.count()
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    users = users[(page - 1) * per_page:page * per_page]

    # Prefetch wallets
    user_list = list(users)
    user_ids = [u.id for u in user_list]
    wallets = {w.user_id: w for w in Wallet.objects.filter(user_id__in=user_ids)}
    for u in user_list:
        u._wallet_cache = wallets.get(u.id)

    context = {
        'users': user_list,
        'search': search,
        'status_filter': status_filter,
        'page': page,
        'total_pages': total_pages,
        'total': total,
        'page_range': range(max(1, page - 2), min(total_pages + 1, page + 3)),
        'page_title': 'Usuarios',
    }
    return render(request, 'dashboard/users.html', context)


@login_required(login_url='/dashboard/login/')
def wallet_overview_view(request):
    """Vista general de billeteras."""
    wallets = Wallet.objects.select_related('user').order_by('-balance_cop')

    total_wallets = wallets.count()
    total_cop = wallets.aggregate(total=Sum('balance_cop'))['total'] or Decimal('0')
    total_llo = wallets.aggregate(total=Sum('balance_llo'))['total'] or Decimal('0')

    # Master wallet
    try:
        master_wallet = MasterWallet.objects.get_master()
    except Exception:
        master_wallet = None

    # Simple pagination
    page = int(request.GET.get('page', 1))
    per_page = 20
    total = wallets.count()
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    wallets_page = wallets[(page - 1) * per_page:page * per_page]

    context = {
        'wallets': wallets_page,
        'total_wallets': total_wallets,
        'total_cop': total_cop,
        'total_llo': total_llo,
        'master_wallet': master_wallet,
        'page': page,
        'total_pages': total_pages,
        'page_range': range(max(1, page - 2), min(total_pages + 1, page + 3)),
        'page_title': 'Billeteras',
    }
    return render(request, 'dashboard/wallets.html', context)


@login_required(login_url='/dashboard/login/')
def transactions_view(request):
    """Vista de transacciones con filtros."""
    tx_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    currency = request.GET.get('currency', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    transactions = Transaction.objects.select_related('wallet__user').order_by('-created_at')

    if tx_type:
        transactions = transactions.filter(transaction_type=tx_type)
    if status:
        transactions = transactions.filter(status=status)
    if currency:
        transactions = transactions.filter(currency=currency)
    if date_from:
        transactions = transactions.filter(created_at__date__gte=date_from)
    if date_to:
        transactions = transactions.filter(created_at__date__lte=date_to)

    # Simple pagination
    page = int(request.GET.get('page', 1))
    per_page = 25
    total = transactions.count()
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    transactions_page = transactions[(page - 1) * per_page:page * per_page]

    context = {
        'transactions': transactions_page,
        'tx_type': tx_type,
        'status': status,
        'currency': currency,
        'date_from': date_from,
        'date_to': date_to,
        'transaction_types': Transaction.TransactionType.choices,
        'status_choices': Transaction.Status.choices,
        'currency_choices': Transaction.Currency.choices,
        'page': page,
        'total_pages': total_pages,
        'total': total,
        'page_range': range(max(1, page - 2), min(total_pages + 1, page + 3)),
        'page_title': 'Transacciones',
    }
    return render(request, 'dashboard/transactions.html', context)


@login_required(login_url='/dashboard/login/')
def transfers_view(request):
    """Vista de transferencias P2P."""
    now = timezone.now()
    today = now.date()

    transfers = Transfer.objects.select_related('sender', 'receiver').order_by('-created_at')

    # Stats
    today_transfers = transfers.filter(created_at__date=today, status='COMPLETED')
    today_count = today_transfers.count()
    today_volume = today_transfers.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    today_commissions = today_transfers.aggregate(total=Sum('commission_amount'))['total'] or Decimal('0')

    # Filters
    status = request.GET.get('status', '')
    if status:
        transfers = transfers.filter(status=status)

    # Simple pagination
    page = int(request.GET.get('page', 1))
    per_page = 25
    total = transfers.count()
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    transfers_page = transfers[(page - 1) * per_page:page * per_page]

    context = {
        'transfers': transfers_page,
        'today_count': today_count,
        'today_volume': today_volume,
        'today_commissions': today_commissions,
        'status': status,
        'status_choices': Transfer.Status.choices,
        'page': page,
        'total_pages': total_pages,
        'total': total,
        'page_range': range(max(1, page - 2), min(total_pages + 1, page + 3)),
        'page_title': 'Transferencias',
    }
    return render(request, 'dashboard/transfers.html', context)


@login_required(login_url='/dashboard/login/')
def crypto_view(request):
    """Vista de Crypto y Llanocoin."""
    # Exchange rates
    exchange_rates = ExchangeRate.objects.all()

    # Pending deposits
    pending_deposits = CryptoDeposit.objects.filter(
        status__in=['PENDING', 'CONFIRMING']
    ).select_related('user').order_by('-created_at')[:20]

    # All deposits
    all_deposits = CryptoDeposit.objects.select_related('user').order_by('-created_at')[:50]

    # LLO stats
    total_llo_circulation = Wallet.objects.aggregate(total=Sum('balance_llo'))['total'] or Decimal('0')
    llo_transactions = LlanocoinTransaction.objects.order_by('-created_at')[:20]
    total_llo_bought = LlanocoinTransaction.objects.filter(
        transaction_type='BUY', status='COMPLETED'
    ).aggregate(total=Sum('amount_llo'))['total'] or Decimal('0')
    total_llo_sold = LlanocoinTransaction.objects.filter(
        transaction_type='SELL', status='COMPLETED'
    ).aggregate(total=Sum('amount_llo'))['total'] or Decimal('0')

    context = {
        'exchange_rates': exchange_rates,
        'pending_deposits': pending_deposits,
        'all_deposits': all_deposits,
        'total_llo_circulation': total_llo_circulation,
        'llo_transactions': llo_transactions,
        'total_llo_bought': total_llo_bought,
        'total_llo_sold': total_llo_sold,
        'page_title': 'Crypto & Llanocoin',
    }
    return render(request, 'dashboard/crypto.html', context)


@login_required(login_url='/dashboard/login/')
def merchants_view(request):
    """Vista del marketplace y comerciantes."""
    merchants = Merchant.objects.select_related('user', 'category').order_by('-created_at')

    total_merchants = merchants.count()
    verified_merchants = merchants.filter(is_verified=True).count()
    active_merchants = merchants.filter(is_active=True).count()

    # Search
    search = request.GET.get('q', '').strip()
    if search:
        merchants = merchants.filter(
            Q(business_name__icontains=search) |
            Q(city__icontains=search)
        )

    # Simple pagination
    page = int(request.GET.get('page', 1))
    per_page = 20
    total = merchants.count()
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    merchants_page = merchants[(page - 1) * per_page:page * per_page]

    context = {
        'merchants': merchants_page,
        'total_merchants': total_merchants,
        'verified_merchants': verified_merchants,
        'active_merchants': active_merchants,
        'search': search,
        'page': page,
        'total_pages': total_pages,
        'page_range': range(max(1, page - 2), min(total_pages + 1, page + 3)),
        'page_title': 'Marketplace',
    }
    return render(request, 'dashboard/merchants.html', context)


@login_required(login_url='/dashboard/login/')
def microcredits_view(request):
    """Vista de microcreditos."""
    microcredits = Microcredit.objects.select_related('user', 'product').order_by('-created_at')

    # Stats
    active_loans = microcredits.filter(status__in=['ACTIVE', 'DISBURSED']).count()
    total_disbursed = microcredits.filter(
        status__in=['ACTIVE', 'DISBURSED', 'PAID']
    ).aggregate(total=Sum('amount_approved'))['total'] or Decimal('0')
    total_repaid = microcredits.aggregate(total=Sum('amount_repaid'))['total'] or Decimal('0')
    defaulted_count = microcredits.filter(status='DEFAULTED').count()
    total_count = microcredits.count()
    default_rate = (defaulted_count / total_count * 100) if total_count > 0 else 0

    # Status distribution for pie chart
    status_distribution = (
        microcredits.values('status')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    status_display = dict(Microcredit.Status.choices)
    mc_pie_labels = [status_display.get(s['status'], s['status']) for s in status_distribution]
    mc_pie_data = [s['count'] for s in status_distribution]

    # Filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        microcredits = microcredits.filter(status=status_filter)

    # Simple pagination
    page = int(request.GET.get('page', 1))
    per_page = 20
    total = microcredits.count()
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    microcredits_page = microcredits[(page - 1) * per_page:page * per_page]

    context = {
        'microcredits': microcredits_page,
        'active_loans': active_loans,
        'total_disbursed': total_disbursed,
        'total_repaid': total_repaid,
        'default_rate': round(default_rate, 1),
        'mc_pie_labels': mc_pie_labels,
        'mc_pie_data': mc_pie_data,
        'status_filter': status_filter,
        'status_choices': Microcredit.Status.choices,
        'page': page,
        'total_pages': total_pages,
        'page_range': range(max(1, page - 2), min(total_pages + 1, page + 3)),
        'page_title': 'Microcreditos',
    }
    return render(request, 'dashboard/microcredits.html', context)


@login_required(login_url='/dashboard/login/')
def notifications_view(request):
    """Vista de notificaciones."""
    notifications = Notification.objects.select_related('user').order_by('-created_at')

    # Filter
    ntype = request.GET.get('type', '')
    channel = request.GET.get('channel', '')
    if ntype:
        notifications = notifications.filter(notification_type=ntype)
    if channel:
        notifications = notifications.filter(channel=channel)

    # Simple pagination
    page = int(request.GET.get('page', 1))
    per_page = 25
    total = notifications.count()
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    notifications_page = notifications[(page - 1) * per_page:page * per_page]

    context = {
        'notifications': notifications_page,
        'ntype': ntype,
        'channel': channel,
        'type_choices': Notification.NotificationType.choices,
        'channel_choices': Notification.Channel.choices,
        'page': page,
        'total_pages': total_pages,
        'total': total,
        'page_range': range(max(1, page - 2), min(total_pages + 1, page + 3)),
        'page_title': 'Notificaciones',
    }
    return render(request, 'dashboard/notifications.html', context)


@login_required(login_url='/dashboard/login/')
def llanocoin_view(request):
    """Vista de estadisticas de Llanocoin."""
    total_llo_circulation = Wallet.objects.aggregate(total=Sum('balance_llo'))['total'] or Decimal('0')
    total_wallets_with_llo = Wallet.objects.filter(balance_llo__gt=0).count()

    llo_transactions = LlanocoinTransaction.objects.select_related('user').order_by('-created_at')[:50]

    total_bought = LlanocoinTransaction.objects.filter(
        transaction_type='BUY', status='COMPLETED'
    ).aggregate(total=Sum('amount_llo'))['total'] or Decimal('0')
    total_sold = LlanocoinTransaction.objects.filter(
        transaction_type='SELL', status='COMPLETED'
    ).aggregate(total=Sum('amount_llo'))['total'] or Decimal('0')
    total_rewards = LlanocoinTransaction.objects.filter(
        transaction_type='REWARD', status='COMPLETED'
    ).aggregate(total=Sum('amount_llo'))['total'] or Decimal('0')

    # Get LLO rate
    try:
        llo_rate = ExchangeRate.objects.get(currency='LLO')
    except ExchangeRate.DoesNotExist:
        llo_rate = None

    context = {
        'total_llo_circulation': total_llo_circulation,
        'total_wallets_with_llo': total_wallets_with_llo,
        'llo_transactions': llo_transactions,
        'total_bought': total_bought,
        'total_sold': total_sold,
        'total_rewards': total_rewards,
        'llo_rate': llo_rate,
        'page_title': 'Llanocoin (LLO)',
    }
    return render(request, 'dashboard/llanocoin.html', context)


@login_required(login_url='/dashboard/login/')
def reports_view(request):
    """Vista de reportes financieros."""
    now = timezone.now()
    date_from = request.GET.get('date_from', (now - timedelta(days=30)).strftime('%Y-%m-%d'))
    date_to = request.GET.get('date_to', now.strftime('%Y-%m-%d'))

    # Financial summary
    transactions_in_range = Transaction.objects.filter(
        created_at__date__gte=date_from,
        created_at__date__lte=date_to,
        status='COMPLETED',
    )

    total_deposits = transactions_in_range.filter(
        transaction_type='DEPOSIT'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    total_withdrawals = transactions_in_range.filter(
        transaction_type='WITHDRAWAL'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    total_commissions = Transfer.objects.filter(
        created_at__date__gte=date_from,
        created_at__date__lte=date_to,
        status='COMPLETED',
    ).aggregate(total=Sum('commission_amount'))['total'] or Decimal('0')

    total_transfers_volume = Transfer.objects.filter(
        created_at__date__gte=date_from,
        created_at__date__lte=date_to,
        status='COMPLETED',
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    # Revenue by source (commissions from different types)
    transfer_commissions = total_commissions
    merchant_commissions = MerchantPayment.objects.filter(
        created_at__date__gte=date_from,
        created_at__date__lte=date_to,
        status='COMPLETED',
    ).aggregate(total=Sum('commission_amount'))['total'] or Decimal('0')

    revenue_labels = ['Comisiones Transferencias', 'Comisiones Marketplace']
    revenue_data = [float(transfer_commissions), float(merchant_commissions)]

    # User growth (daily registrations)
    daily_registrations = (
        User.objects
        .filter(created_at__date__gte=date_from, created_at__date__lte=date_to)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    growth_labels = [item['date'].strftime('%d/%m') for item in daily_registrations]
    growth_data = [item['count'] for item in daily_registrations]

    # New users in range
    new_users = User.objects.filter(
        created_at__date__gte=date_from,
        created_at__date__lte=date_to,
    ).count()

    context = {
        'date_from': date_from,
        'date_to': date_to,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'total_commissions': total_commissions,
        'total_transfers_volume': total_transfers_volume,
        'revenue_labels': revenue_labels,
        'revenue_data': revenue_data,
        'growth_labels': growth_labels,
        'growth_data': growth_data,
        'new_users': new_users,
        'page_title': 'Reportes',
    }
    return render(request, 'dashboard/reports.html', context)
