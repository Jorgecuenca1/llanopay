"""Seed countries and currencies for SuperNova global platform."""
from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.global_features.models import Country, Currency


COUNTRIES = [
    # (code, code3, name, name_es, flag, phone, currency)
    ('CO', 'COL', 'Colombia', 'Colombia', '🇨🇴', '+57', 'COP'),
    ('US', 'USA', 'United States', 'Estados Unidos', '🇺🇸', '+1', 'USD'),
    ('MX', 'MEX', 'Mexico', 'México', '🇲🇽', '+52', 'MXN'),
    ('BR', 'BRA', 'Brazil', 'Brasil', '🇧🇷', '+55', 'BRL'),
    ('AR', 'ARG', 'Argentina', 'Argentina', '🇦🇷', '+54', 'ARS'),
    ('CL', 'CHL', 'Chile', 'Chile', '🇨🇱', '+56', 'CLP'),
    ('PE', 'PER', 'Peru', 'Perú', '🇵🇪', '+51', 'PEN'),
    ('EC', 'ECU', 'Ecuador', 'Ecuador', '🇪🇨', '+593', 'USD'),
    ('VE', 'VEN', 'Venezuela', 'Venezuela', '🇻🇪', '+58', 'VES'),
    ('UY', 'URY', 'Uruguay', 'Uruguay', '🇺🇾', '+598', 'UYU'),
    ('PY', 'PRY', 'Paraguay', 'Paraguay', '🇵🇾', '+595', 'PYG'),
    ('BO', 'BOL', 'Bolivia', 'Bolivia', '🇧🇴', '+591', 'BOB'),
    ('PA', 'PAN', 'Panama', 'Panamá', '🇵🇦', '+507', 'PAB'),
    ('CR', 'CRI', 'Costa Rica', 'Costa Rica', '🇨🇷', '+506', 'CRC'),
    ('GT', 'GTM', 'Guatemala', 'Guatemala', '🇬🇹', '+502', 'GTQ'),
    ('SV', 'SLV', 'El Salvador', 'El Salvador', '🇸🇻', '+503', 'USD'),
    ('HN', 'HND', 'Honduras', 'Honduras', '🇭🇳', '+504', 'HNL'),
    ('NI', 'NIC', 'Nicaragua', 'Nicaragua', '🇳🇮', '+505', 'NIO'),
    ('DO', 'DOM', 'Dominican Republic', 'República Dominicana', '🇩🇴', '+1', 'DOP'),
    ('CU', 'CUB', 'Cuba', 'Cuba', '🇨🇺', '+53', 'CUP'),
    ('PR', 'PRI', 'Puerto Rico', 'Puerto Rico', '🇵🇷', '+1', 'USD'),
    ('ES', 'ESP', 'Spain', 'España', '🇪🇸', '+34', 'EUR'),
    ('FR', 'FRA', 'France', 'Francia', '🇫🇷', '+33', 'EUR'),
    ('DE', 'DEU', 'Germany', 'Alemania', '🇩🇪', '+49', 'EUR'),
    ('IT', 'ITA', 'Italy', 'Italia', '🇮🇹', '+39', 'EUR'),
    ('GB', 'GBR', 'United Kingdom', 'Reino Unido', '🇬🇧', '+44', 'GBP'),
    ('PT', 'PRT', 'Portugal', 'Portugal', '🇵🇹', '+351', 'EUR'),
    ('CA', 'CAN', 'Canada', 'Canadá', '🇨🇦', '+1', 'CAD'),
    ('JP', 'JPN', 'Japan', 'Japón', '🇯🇵', '+81', 'JPY'),
    ('CN', 'CHN', 'China', 'China', '🇨🇳', '+86', 'CNY'),
    ('IN', 'IND', 'India', 'India', '🇮🇳', '+91', 'INR'),
    ('AU', 'AUS', 'Australia', 'Australia', '🇦🇺', '+61', 'AUD'),
    ('CH', 'CHE', 'Switzerland', 'Suiza', '🇨🇭', '+41', 'CHF'),
    ('SE', 'SWE', 'Sweden', 'Suecia', '🇸🇪', '+46', 'SEK'),
    ('NO', 'NOR', 'Norway', 'Noruega', '🇳🇴', '+47', 'NOK'),
    ('NL', 'NLD', 'Netherlands', 'Países Bajos', '🇳🇱', '+31', 'EUR'),
]

CURRENCIES = [
    # (code, name, symbol, decimals, rate_to_usd, is_crypto)
    ('USD', 'US Dollar', '$', 2, '1.00', False),
    ('EUR', 'Euro', '€', 2, '0.92', False),
    ('GBP', 'British Pound', '£', 2, '0.79', False),
    ('JPY', 'Japanese Yen', '¥', 0, '149.50', False),
    ('CNY', 'Chinese Yuan', '¥', 2, '7.24', False),
    ('CAD', 'Canadian Dollar', 'C$', 2, '1.36', False),
    ('AUD', 'Australian Dollar', 'A$', 2, '1.52', False),
    ('CHF', 'Swiss Franc', 'CHF', 2, '0.87', False),
    ('COP', 'Peso Colombiano', '$', 0, '4100.00', False),
    ('MXN', 'Peso Mexicano', '$', 2, '17.20', False),
    ('BRL', 'Real Brasileño', 'R$', 2, '5.05', False),
    ('ARS', 'Peso Argentino', '$', 2, '850.00', False),
    ('CLP', 'Peso Chileno', '$', 0, '950.00', False),
    ('PEN', 'Sol Peruano', 'S/', 2, '3.75', False),
    ('VES', 'Bolívar Venezolano', 'Bs', 2, '36.50', False),
    ('UYU', 'Peso Uruguayo', '$U', 2, '39.00', False),
    ('PYG', 'Guaraní Paraguayo', '₲', 0, '7350.00', False),
    ('BOB', 'Boliviano', 'Bs', 2, '6.91', False),
    ('PAB', 'Balboa Panameño', 'B/.', 2, '1.00', False),
    ('CRC', 'Colón Costarricense', '₡', 2, '520.00', False),
    ('GTQ', 'Quetzal Guatemalteco', 'Q', 2, '7.80', False),
    ('HNL', 'Lempira Hondureño', 'L', 2, '24.70', False),
    ('NIO', 'Córdoba Nicaragüense', 'C$', 2, '36.70', False),
    ('DOP', 'Peso Dominicano', 'RD$', 2, '58.50', False),
    ('CUP', 'Peso Cubano', '₱', 2, '24.00', False),
    ('INR', 'Rupia India', '₹', 2, '83.20', False),
    ('SEK', 'Corona Sueca', 'kr', 2, '10.55', False),
    ('NOK', 'Corona Noruega', 'kr', 2, '10.70', False),
    # Crypto
    ('LLO', 'SuperNova Coin', 'SN', 2, '4100.00', True),
    ('BTC', 'Bitcoin', '₿', 8, '0.000023', True),
    ('ETH', 'Ethereum', 'Ξ', 8, '0.00038', True),
    ('USDT', 'Tether USD', '₮', 2, '1.00', True),
]


class Command(BaseCommand):
    help = 'Seed countries and currencies for SuperNova'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding currencies...')
        for code, name, symbol, decimals, rate, is_crypto in CURRENCIES:
            Currency.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'symbol': symbol,
                    'decimal_places': decimals,
                    'rate_to_usd': Decimal(rate),
                    'is_crypto': is_crypto,
                    'is_active': True,
                },
            )
        self.stdout.write(self.style.SUCCESS(f'  {len(CURRENCIES)} currencies seeded'))

        self.stdout.write('Seeding countries...')
        for code, code3, name, name_es, flag, phone, currency in COUNTRIES:
            Country.objects.update_or_create(
                code=code,
                defaults={
                    'code3': code3,
                    'name': name,
                    'name_es': name_es,
                    'flag_emoji': flag,
                    'phone_code': phone,
                    'default_currency': currency,
                    'is_supported': True,
                },
            )
        self.stdout.write(self.style.SUCCESS(f'  {len(COUNTRIES)} countries seeded'))
        self.stdout.write(self.style.SUCCESS('Done!'))
