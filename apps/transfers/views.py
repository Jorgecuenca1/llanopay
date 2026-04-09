from decimal import Decimal

from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User, OTPCode
from apps.transfers.models import Transfer, TransferLimit, ScheduledTransfer
from apps.transfers.serializers import (
    TransferCreateSerializer,
    TransferConfirmSerializer,
    TransferDetailSerializer,
    TransferLimitSerializer,
    ScheduledTransferSerializer,
)

# Umbral en COP a partir del cual se requiere OTP
OTP_THRESHOLD_COP = Decimal('500000')


class TransferCreateView(APIView):
    """POST - Inicia una transferencia P2P.

    Si el monto en COP equivale a mas de 500,000 se requiere confirmacion OTP.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TransferCreateSerializer(
            data=request.data, context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        sender = request.user
        data = serializer.validated_data
        receiver = User.objects.get(phone_number=data['receiver_phone'])

        # Crear la transferencia
        transfer = Transfer(
            sender=sender,
            receiver=receiver,
            amount=data['amount'],
            currency=data['currency'],
            description=data.get('description', ''),
        )
        transfer.calculate_commission()

        # Determinar si requiere OTP
        from django.conf import settings as django_settings
        if data['currency'] == Transfer.Currency.LLO:
            cop_equivalent = data['amount'] * Decimal(str(django_settings.LLO_COP_RATE))
        else:
            cop_equivalent = data['amount']

        if cop_equivalent > OTP_THRESHOLD_COP:
            transfer.status = Transfer.Status.OTP_REQUIRED
            transfer.save()

            # Generar OTP para el remitente
            otp = OTPCode(
                user=sender,
                purpose=OTPCode.Purpose.TRANSFER,
            )
            otp.save()

            return Response(
                {
                    'transfer': TransferDetailSerializer(transfer).data,
                    'otp_required': True,
                    'message': (
                        'Transferencia creada. Se requiere confirmacion OTP. '
                        f'Codigo enviado a {sender.phone_number}.'
                    ),
                },
                status=status.HTTP_201_CREATED,
            )

        # Monto bajo, ejecutar directamente
        transfer.status = Transfer.Status.PENDING
        transfer.save()
        transfer.execute()

        return Response(
            {
                'transfer': TransferDetailSerializer(transfer).data,
                'otp_required': False,
                'message': 'Transferencia completada exitosamente.',
            },
            status=status.HTTP_201_CREATED,
        )


class TransferConfirmView(APIView):
    """POST - Confirma una transferencia que requiere OTP."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TransferConfirmSerializer(
            data=request.data, context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        transfer = Transfer.objects.get(
            pk=data['transfer_id'],
            sender=request.user,
        )

        # Verificar OTP
        otp = OTPCode.objects.filter(
            user=request.user,
            purpose=OTPCode.Purpose.TRANSFER,
            code=data['otp_code'],
            is_used=False,
        ).order_by('-created_at').first()

        if not otp or not otp.is_valid:
            return Response(
                {'detail': 'Codigo OTP invalido o expirado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Marcar OTP como usado
        otp.is_used = True
        otp.save(update_fields=['is_used'])

        # Ejecutar la transferencia
        transfer.otp_verified = True
        transfer.save(update_fields=['otp_verified'])
        transfer.execute()

        return Response(
            {
                'transfer': TransferDetailSerializer(transfer).data,
                'message': 'Transferencia confirmada y completada exitosamente.',
            },
            status=status.HTTP_200_OK,
        )


class TransferListView(generics.ListAPIView):
    """GET - Lista las transferencias enviadas y recibidas del usuario."""
    permission_classes = [IsAuthenticated]
    serializer_class = TransferDetailSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Transfer.objects.filter(
            Q(sender=user) | Q(receiver=user),
        ).select_related('sender', 'receiver')

        # Filtros opcionales
        direction = self.request.query_params.get('direction')
        if direction == 'sent':
            queryset = queryset.filter(sender=user)
        elif direction == 'received':
            queryset = queryset.filter(receiver=user)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        currency = self.request.query_params.get('currency')
        if currency:
            queryset = queryset.filter(currency=currency)

        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)

        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        return queryset


class TransferDetailView(generics.RetrieveAPIView):
    """GET - Detalle de una transferencia especifica."""
    permission_classes = [IsAuthenticated]
    serializer_class = TransferDetailSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        return Transfer.objects.filter(
            Q(sender=user) | Q(receiver=user),
        ).select_related('sender', 'receiver')


class TransferLimitView(APIView):
    """GET/PUT - Ver o actualizar los limites de transferencia del usuario."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit, _created = TransferLimit.objects.get_or_create(user=request.user)
        serializer = TransferLimitSerializer(limit)
        return Response(serializer.data)

    def put(self, request):
        limit, _created = TransferLimit.objects.get_or_create(user=request.user)
        serializer = TransferLimitSerializer(limit, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ScheduledTransferViewSet(viewsets.ModelViewSet):
    """CRUD para transferencias programadas del usuario."""
    permission_classes = [IsAuthenticated]
    serializer_class = ScheduledTransferSerializer

    def get_queryset(self):
        return ScheduledTransfer.objects.filter(
            sender=self.request.user,
        ).select_related('sender', 'receiver')

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
