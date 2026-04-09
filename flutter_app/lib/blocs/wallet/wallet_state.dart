import 'package:equatable/equatable.dart';

abstract class WalletState extends Equatable {
  const WalletState();

  @override
  List<Object?> get props => [];
}

class WalletInitial extends WalletState {
  const WalletInitial();
}

class WalletLoading extends WalletState {
  const WalletLoading();
}

class WalletLoaded extends WalletState {
  final Map<String, dynamic> wallet;
  final Map<String, dynamic> balanceSummary;

  const WalletLoaded({
    required this.wallet,
    required this.balanceSummary,
  });

  @override
  List<Object?> get props => [wallet, balanceSummary];
}

class TransactionsLoaded extends WalletState {
  final List<Map<String, dynamic>> transactions;

  const TransactionsLoaded({required this.transactions});

  @override
  List<Object?> get props => [transactions];
}

class TransactionDetailLoaded extends WalletState {
  final Map<String, dynamic> transaction;

  const TransactionDetailLoaded({required this.transaction});

  @override
  List<Object?> get props => [transaction];
}

class WalletError extends WalletState {
  final String message;

  const WalletError({required this.message});

  @override
  List<Object?> get props => [message];
}
