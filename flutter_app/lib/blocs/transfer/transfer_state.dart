import 'package:equatable/equatable.dart';

abstract class TransferState extends Equatable {
  const TransferState();

  @override
  List<Object?> get props => [];
}

class TransferInitial extends TransferState {
  const TransferInitial();
}

class TransferLoading extends TransferState {
  const TransferLoading();
}

class TransferCreated extends TransferState {
  final Map<String, dynamic> transfer;
  final bool requiresOTP;

  const TransferCreated({
    required this.transfer,
    required this.requiresOTP,
  });

  @override
  List<Object?> get props => [transfer, requiresOTP];
}

class TransferCompleted extends TransferState {
  final Map<String, dynamic> transfer;

  const TransferCompleted({required this.transfer});

  @override
  List<Object?> get props => [transfer];
}

class TransfersLoaded extends TransferState {
  final List<Map<String, dynamic>> transfers;

  const TransfersLoaded({required this.transfers});

  @override
  List<Object?> get props => [transfers];
}

class TransferDetailLoaded extends TransferState {
  final Map<String, dynamic> transfer;

  const TransferDetailLoaded({required this.transfer});

  @override
  List<Object?> get props => [transfer];
}

class LimitsLoaded extends TransferState {
  final Map<String, dynamic> limits;

  const LimitsLoaded({required this.limits});

  @override
  List<Object?> get props => [limits];
}

class TransferError extends TransferState {
  final String message;

  const TransferError({required this.message});

  @override
  List<Object?> get props => [message];
}
