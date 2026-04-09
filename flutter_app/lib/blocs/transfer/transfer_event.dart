import 'package:equatable/equatable.dart';

abstract class TransferEvent extends Equatable {
  const TransferEvent();

  @override
  List<Object?> get props => [];
}

class TransferInitiated extends TransferEvent {
  final String receiverPhone;
  final double amount;
  final String currency;
  final String? description;

  const TransferInitiated({
    required this.receiverPhone,
    required this.amount,
    required this.currency,
    this.description,
  });

  @override
  List<Object?> get props => [receiverPhone, amount, currency, description];
}

class TransferConfirmed extends TransferEvent {
  final String transferId;
  final String otpCode;

  const TransferConfirmed({
    required this.transferId,
    required this.otpCode,
  });

  @override
  List<Object?> get props => [transferId, otpCode];
}

class TransfersLoadRequested extends TransferEvent {
  const TransfersLoadRequested();
}

class TransferDetailRequested extends TransferEvent {
  final String id;

  const TransferDetailRequested({required this.id});

  @override
  List<Object?> get props => [id];
}

class LimitsLoadRequested extends TransferEvent {
  const LimitsLoadRequested();
}
