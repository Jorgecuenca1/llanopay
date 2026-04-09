import logging
from decimal import Decimal

import requests
from celery import shared_task
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def verify_crypto_deposit(self, deposit_id: int):
    """
    Verifica un deposito crypto on-chain y acredita la billetera
    del usuario cuando tenga suficientes confirmaciones.
    """
    from apps.crypto.blockchain import BlockchainService
    from apps.crypto.models import CryptoDeposit, ExchangeRate

    try:
        deposit = CryptoDeposit.objects.select_for_update().get(id=deposit_id)
    except CryptoDeposit.DoesNotExist:
        logger.error(f"Deposito {deposit_id} no encontrado")
        return

    if deposit.status in (CryptoDeposit.Status.CREDITED, CryptoDeposit.Status.FAILED):
        logger.info(f"Deposito {deposit_id} ya esta en estado final: {deposit.status}")
        return

    service = BlockchainService()

    # Verificar que la transaccion va a la wallet maestra
    if not service.is_transaction_to_master(deposit.tx_hash, deposit.network):
        deposit.status = CryptoDeposit.Status.FAILED
        deposit.save(update_fields=['status'])
        logger.warning(
            f"Deposito {deposit_id}: transaccion {deposit.tx_hash} no va "
            f"a la wallet maestra"
        )
        return

    # Obtener confirmaciones
    confirmations = service.get_transaction_confirmations(
        deposit.tx_hash, deposit.network
    )
    deposit.confirmations = confirmations

    if confirmations == 0:
        deposit.status = CryptoDeposit.Status.PENDING
        deposit.save(update_fields=['confirmations', 'status'])
        # Reintentar en 60 segundos
        raise self.retry(countdown=60)

    if confirmations < deposit.required_confirmations:
        deposit.status = CryptoDeposit.Status.CONFIRMING
        deposit.save(update_fields=['confirmations', 'status'])
        # Reintentar en 30 segundos
        raise self.retry(countdown=30)

    # Transaccion confirmada - acreditar billetera
    with transaction.atomic():
        deposit.status = CryptoDeposit.Status.CONFIRMED
        deposit.confirmed_at = timezone.now()

        # Calcular monto COP
        rate = ExchangeRate.get_rate(deposit.currency)
        deposit.exchange_rate = rate
        deposit.cop_amount = deposit.amount * rate

        deposit.save(update_fields=[
            'confirmations', 'status', 'confirmed_at',
            'exchange_rate', 'cop_amount',
        ])

        # Acreditar billetera del usuario
        try:
            wallet = deposit.user.wallet
            wallet.balance += deposit.cop_amount
            wallet.save(update_fields=['balance'])

            deposit.status = CryptoDeposit.Status.CREDITED
            deposit.credited_at = timezone.now()
            deposit.save(update_fields=['status', 'credited_at'])

            logger.info(
                f"Deposito {deposit_id} acreditado: "
                f"{deposit.cop_amount} COP al usuario {deposit.user_id}"
            )
        except Exception as e:
            logger.error(
                f"Error acreditando deposito {deposit_id} "
                f"a billetera: {e}"
            )
            raise


@shared_task
def update_exchange_rates():
    """
    Tarea periodica para actualizar las tasas de cambio cripto/COP
    desde CoinGecko.
    """
    from django.core.cache import cache

    from apps.crypto.models import ExchangeRate

    coin_ids = {
        'USDT': 'tether',
        'ETH': 'ethereum',
        'BTC': 'bitcoin',
    }

    try:
        ids_param = ','.join(coin_ids.values())
        url = (
            f"https://api.coingecko.com/api/v3/simple/price"
            f"?ids={ids_param}&vs_currencies=cop"
        )
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        for currency, coin_id in coin_ids.items():
            if coin_id in data and 'cop' in data[coin_id]:
                rate_cop = Decimal(str(data[coin_id]['cop']))
                ExchangeRate.objects.update_or_create(
                    currency=currency,
                    defaults={
                        'rate_cop': rate_cop,
                        'source': 'coingecko',
                    },
                )
                # Invalidar cache
                cache.delete(f'exchange_rate_{currency}')
                logger.info(f"Tasa {currency}/COP actualizada: {rate_cop}")

        # Actualizar Llanocoin (tasa fija configurable)
        from django.conf import settings
        llo_rate = Decimal(str(settings.LLO_COP_RATE))
        ExchangeRate.objects.update_or_create(
            currency='LLO',
            defaults={
                'rate_cop': llo_rate,
                'source': 'internal',
            },
        )
        cache.delete('exchange_rate_LLO')

        logger.info("Tasas de cambio actualizadas exitosamente")

    except requests.RequestException as e:
        logger.error(f"Error de red actualizando tasas de cambio: {e}")
    except Exception as e:
        logger.error(f"Error actualizando tasas de cambio: {e}")


@shared_task
def check_pending_deposits():
    """
    Tarea periodica que revisa depositos pendientes o en confirmacion
    y lanza la verificacion de cada uno.
    """
    from apps.crypto.models import CryptoDeposit

    pending_statuses = [
        CryptoDeposit.Status.PENDING,
        CryptoDeposit.Status.CONFIRMING,
    ]

    pending_deposits = CryptoDeposit.objects.filter(
        status__in=pending_statuses
    ).values_list('id', flat=True)

    count = 0
    for deposit_id in pending_deposits:
        verify_crypto_deposit.delay(deposit_id)
        count += 1

    if count:
        logger.info(f"Relanzada verificacion para {count} depositos pendientes")
