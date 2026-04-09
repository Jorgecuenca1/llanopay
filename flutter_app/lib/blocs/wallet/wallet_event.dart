import 'package:equatable/equatable.dart';

abstract class WalletEvent extends Equatable {
  const WalletEvent();

  @override
  List<Object?> get props => [];
}

class WalletLoadRequested extends WalletEvent {
  const WalletLoadRequested();
}

class TransactionsLoadRequested extends WalletEvent {
  final Map<String, dynamic>? filters;

  const TransactionsLoadRequested({this.filters});

  @override
  List<Object?> get props => [filters];
}

class TransactionDetailRequested extends WalletEvent {
  final String id;

  const TransactionDetailRequested({required this.id});

  @override
  List<Object?> get props => [id];
}

class BalanceSummaryRequested extends WalletEvent {
  const BalanceSummaryRequested();
}
