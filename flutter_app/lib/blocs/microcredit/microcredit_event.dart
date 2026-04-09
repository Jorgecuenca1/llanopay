import 'package:equatable/equatable.dart';

abstract class MicrocreditEvent extends Equatable {
  const MicrocreditEvent();

  @override
  List<Object?> get props => [];
}

class CreditProfileLoadRequested extends MicrocreditEvent {
  const CreditProfileLoadRequested();
}

class ProductsLoadRequested extends MicrocreditEvent {
  const ProductsLoadRequested();
}

class MicrocreditRequested extends MicrocreditEvent {
  final String productId;
  final double amount;

  const MicrocreditRequested({
    required this.productId,
    required this.amount,
  });

  @override
  List<Object?> get props => [productId, amount];
}

class MicrocreditsLoadRequested extends MicrocreditEvent {
  const MicrocreditsLoadRequested();
}

class PaymentSubmitted extends MicrocreditEvent {
  final String microcreditId;
  final double amount;

  const PaymentSubmitted({
    required this.microcreditId,
    required this.amount,
  });

  @override
  List<Object?> get props => [microcreditId, amount];
}

class ScoreRecalculateRequested extends MicrocreditEvent {
  const ScoreRecalculateRequested();
}
