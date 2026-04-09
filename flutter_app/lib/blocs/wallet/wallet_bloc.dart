import 'package:flutter_bloc/flutter_bloc.dart';

import '../../repositories/wallet_repository.dart';
import 'wallet_event.dart';
import 'wallet_state.dart';

class WalletBloc extends Bloc<WalletEvent, WalletState> {
  final WalletRepository walletRepository;

  WalletBloc({required this.walletRepository}) : super(const WalletInitial()) {
    on<WalletLoadRequested>(_onWalletLoadRequested);
    on<TransactionsLoadRequested>(_onTransactionsLoadRequested);
    on<TransactionDetailRequested>(_onTransactionDetailRequested);
    on<BalanceSummaryRequested>(_onBalanceSummaryRequested);
  }

  Future<void> _onWalletLoadRequested(
    WalletLoadRequested event,
    Emitter<WalletState> emit,
  ) async {
    emit(const WalletLoading());
    try {
      final wallet = await walletRepository.getWallet();
      final balanceSummary = await walletRepository.getBalanceSummary();
      emit(WalletLoaded(wallet: wallet, balanceSummary: balanceSummary));
    } catch (e) {
      emit(WalletError(message: e.toString()));
    }
  }

  Future<void> _onTransactionsLoadRequested(
    TransactionsLoadRequested event,
    Emitter<WalletState> emit,
  ) async {
    emit(const WalletLoading());
    try {
      final transactions = await walletRepository.getTransactions(
        filters: event.filters,
      );
      emit(TransactionsLoaded(transactions: transactions));
    } catch (e) {
      emit(WalletError(message: e.toString()));
    }
  }

  Future<void> _onTransactionDetailRequested(
    TransactionDetailRequested event,
    Emitter<WalletState> emit,
  ) async {
    emit(const WalletLoading());
    try {
      final transaction = await walletRepository.getTransactionDetail(event.id);
      emit(TransactionDetailLoaded(transaction: transaction));
    } catch (e) {
      emit(WalletError(message: e.toString()));
    }
  }

  Future<void> _onBalanceSummaryRequested(
    BalanceSummaryRequested event,
    Emitter<WalletState> emit,
  ) async {
    emit(const WalletLoading());
    try {
      final wallet = await walletRepository.getWallet();
      final balanceSummary = await walletRepository.getBalanceSummary();
      emit(WalletLoaded(wallet: wallet, balanceSummary: balanceSummary));
    } catch (e) {
      emit(WalletError(message: e.toString()));
    }
  }
}
