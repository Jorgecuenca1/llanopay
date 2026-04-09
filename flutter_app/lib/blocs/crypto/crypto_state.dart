import 'package:equatable/equatable.dart';

abstract class CryptoState extends Equatable {
  const CryptoState();

  @override
  List<Object?> get props => [];
}

class CryptoInitial extends CryptoState {
  const CryptoInitial();
}

class CryptoLoading extends CryptoState {
  const CryptoLoading();
}

class DepositSubmitted extends CryptoState {
  final Map<String, dynamic> deposit;

  const DepositSubmitted({required this.deposit});

  @override
  List<Object?> get props => [deposit];
}

class DepositsLoaded extends CryptoState {
  final List<Map<String, dynamic>> deposits;

  const DepositsLoaded({required this.deposits});

  @override
  List<Object?> get props => [deposits];
}

class RatesLoaded extends CryptoState {
  final Map<String, dynamic> rates;

  const RatesLoaded({required this.rates});

  @override
  List<Object?> get props => [rates];
}

class LlanocoinBought extends CryptoState {
  final Map<String, dynamic> transaction;

  const LlanocoinBought({required this.transaction});

  @override
  List<Object?> get props => [transaction];
}

class LlanocoinSold extends CryptoState {
  final Map<String, dynamic> transaction;

  const LlanocoinSold({required this.transaction});

  @override
  List<Object?> get props => [transaction];
}

class LloTransactionsLoaded extends CryptoState {
  final List<Map<String, dynamic>> transactions;

  const LloTransactionsLoaded({required this.transactions});

  @override
  List<Object?> get props => [transactions];
}

class CryptoError extends CryptoState {
  final String message;

  const CryptoError({required this.message});

  @override
  List<Object?> get props => [message];
}
