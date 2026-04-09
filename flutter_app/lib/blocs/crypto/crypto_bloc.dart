import 'package:flutter_bloc/flutter_bloc.dart';

import '../../repositories/crypto_repository.dart';
import 'crypto_event.dart';
import 'crypto_state.dart';

class CryptoBloc extends Bloc<CryptoEvent, CryptoState> {
  final CryptoRepository cryptoRepository;

  CryptoBloc({required this.cryptoRepository}) : super(const CryptoInitial()) {
    on<CryptoDepositSubmitted>(_onCryptoDepositSubmitted);
    on<DepositsLoadRequested>(_onDepositsLoadRequested);
    on<RatesLoadRequested>(_onRatesLoadRequested);
    on<LlanocoinBuyRequested>(_onLlanocoinBuyRequested);
    on<LlanocoinSellRequested>(_onLlanocoinSellRequested);
    on<LloTransactionsLoadRequested>(_onLloTransactionsLoadRequested);
  }

  Future<void> _onCryptoDepositSubmitted(
    CryptoDepositSubmitted event,
    Emitter<CryptoState> emit,
  ) async {
    emit(const CryptoLoading());
    try {
      final deposit = await cryptoRepository.submitDeposit(
        currency: event.currency,
        amount: event.amount,
        txHash: event.txHash,
        network: event.network,
      );
      emit(DepositSubmitted(deposit: deposit));
    } catch (e) {
      emit(CryptoError(message: e.toString()));
    }
  }

  Future<void> _onDepositsLoadRequested(
    DepositsLoadRequested event,
    Emitter<CryptoState> emit,
  ) async {
    emit(const CryptoLoading());
    try {
      final deposits = await cryptoRepository.getDeposits();
      emit(DepositsLoaded(deposits: deposits));
    } catch (e) {
      emit(CryptoError(message: e.toString()));
    }
  }

  Future<void> _onRatesLoadRequested(
    RatesLoadRequested event,
    Emitter<CryptoState> emit,
  ) async {
    emit(const CryptoLoading());
    try {
      final rates = await cryptoRepository.getRates();
      emit(RatesLoaded(rates: rates));
    } catch (e) {
      emit(CryptoError(message: e.toString()));
    }
  }

  Future<void> _onLlanocoinBuyRequested(
    LlanocoinBuyRequested event,
    Emitter<CryptoState> emit,
  ) async {
    emit(const CryptoLoading());
    try {
      final transaction = await cryptoRepository.buyLlanocoin(
        amountCop: event.amountCop,
      );
      emit(LlanocoinBought(transaction: transaction));
    } catch (e) {
      emit(CryptoError(message: e.toString()));
    }
  }

  Future<void> _onLlanocoinSellRequested(
    LlanocoinSellRequested event,
    Emitter<CryptoState> emit,
  ) async {
    emit(const CryptoLoading());
    try {
      final transaction = await cryptoRepository.sellLlanocoin(
        amountLlo: event.amountLlo,
      );
      emit(LlanocoinSold(transaction: transaction));
    } catch (e) {
      emit(CryptoError(message: e.toString()));
    }
  }

  Future<void> _onLloTransactionsLoadRequested(
    LloTransactionsLoadRequested event,
    Emitter<CryptoState> emit,
  ) async {
    emit(const CryptoLoading());
    try {
      final transactions = await cryptoRepository.getLloTransactions();
      emit(LloTransactionsLoaded(transactions: transactions));
    } catch (e) {
      emit(CryptoError(message: e.toString()));
    }
  }
}
