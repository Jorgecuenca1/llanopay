import 'package:equatable/equatable.dart';

abstract class CryptoEvent extends Equatable {
  const CryptoEvent();

  @override
  List<Object?> get props => [];
}

class CryptoDepositSubmitted extends CryptoEvent {
  final String currency;
  final double amount;
  final String txHash;
  final String network;

  const CryptoDepositSubmitted({
    required this.currency,
    required this.amount,
    required this.txHash,
    required this.network,
  });

  @override
  List<Object?> get props => [currency, amount, txHash, network];
}

class DepositsLoadRequested extends CryptoEvent {
  const DepositsLoadRequested();
}

class RatesLoadRequested extends CryptoEvent {
  const RatesLoadRequested();
}

class LlanocoinBuyRequested extends CryptoEvent {
  final double amountCop;

  const LlanocoinBuyRequested({required this.amountCop});

  @override
  List<Object?> get props => [amountCop];
}

class LlanocoinSellRequested extends CryptoEvent {
  final double amountLlo;

  const LlanocoinSellRequested({required this.amountLlo});

  @override
  List<Object?> get props => [amountLlo];
}

class LloTransactionsLoadRequested extends CryptoEvent {
  const LloTransactionsLoadRequested();
}
