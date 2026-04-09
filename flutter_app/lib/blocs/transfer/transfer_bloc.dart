import 'package:flutter_bloc/flutter_bloc.dart';

import '../../repositories/transfer_repository.dart';
import 'transfer_event.dart';
import 'transfer_state.dart';

class TransferBloc extends Bloc<TransferEvent, TransferState> {
  final TransferRepository transferRepository;

  TransferBloc({required this.transferRepository})
      : super(const TransferInitial()) {
    on<TransferInitiated>(_onTransferInitiated);
    on<TransferConfirmed>(_onTransferConfirmed);
    on<TransfersLoadRequested>(_onTransfersLoadRequested);
    on<TransferDetailRequested>(_onTransferDetailRequested);
    on<LimitsLoadRequested>(_onLimitsLoadRequested);
  }

  Future<void> _onTransferInitiated(
    TransferInitiated event,
    Emitter<TransferState> emit,
  ) async {
    emit(const TransferLoading());
    try {
      final result = await transferRepository.initiateTransfer(
        receiverPhone: event.receiverPhone,
        amount: event.amount,
        currency: event.currency,
        description: event.description,
      );
      final transfer = result['transfer'] as Map<String, dynamic>;
      final requiresOTP = result['requires_otp'] as bool? ?? false;
      emit(TransferCreated(transfer: transfer, requiresOTP: requiresOTP));
    } catch (e) {
      emit(TransferError(message: e.toString()));
    }
  }

  Future<void> _onTransferConfirmed(
    TransferConfirmed event,
    Emitter<TransferState> emit,
  ) async {
    emit(const TransferLoading());
    try {
      final transfer = await transferRepository.confirmTransfer(
        transferId: event.transferId,
        otpCode: event.otpCode,
      );
      emit(TransferCompleted(transfer: transfer));
    } catch (e) {
      emit(TransferError(message: e.toString()));
    }
  }

  Future<void> _onTransfersLoadRequested(
    TransfersLoadRequested event,
    Emitter<TransferState> emit,
  ) async {
    emit(const TransferLoading());
    try {
      final transfers = await transferRepository.getTransfers();
      emit(TransfersLoaded(transfers: transfers));
    } catch (e) {
      emit(TransferError(message: e.toString()));
    }
  }

  Future<void> _onTransferDetailRequested(
    TransferDetailRequested event,
    Emitter<TransferState> emit,
  ) async {
    emit(const TransferLoading());
    try {
      final transfer = await transferRepository.getTransferDetail(event.id);
      emit(TransferDetailLoaded(transfer: transfer));
    } catch (e) {
      emit(TransferError(message: e.toString()));
    }
  }

  Future<void> _onLimitsLoadRequested(
    LimitsLoadRequested event,
    Emitter<TransferState> emit,
  ) async {
    emit(const TransferLoading());
    try {
      final limits = await transferRepository.getLimits();
      emit(LimitsLoaded(limits: limits));
    } catch (e) {
      emit(TransferError(message: e.toString()));
    }
  }
}
