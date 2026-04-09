import 'package:equatable/equatable.dart';

abstract class MicrocreditState extends Equatable {
  const MicrocreditState();

  @override
  List<Object?> get props => [];
}

class MicrocreditInitial extends MicrocreditState {
  const MicrocreditInitial();
}

class MicrocreditLoading extends MicrocreditState {
  const MicrocreditLoading();
}

class CreditProfileLoaded extends MicrocreditState {
  final Map<String, dynamic> profile;

  const CreditProfileLoaded({required this.profile});

  @override
  List<Object?> get props => [profile];
}

class ProductsLoaded extends MicrocreditState {
  final List<Map<String, dynamic>> products;

  const ProductsLoaded({required this.products});

  @override
  List<Object?> get props => [products];
}

class MicrocreditCreated extends MicrocreditState {
  final Map<String, dynamic> microcredit;

  const MicrocreditCreated({required this.microcredit});

  @override
  List<Object?> get props => [microcredit];
}

class MicrocreditsLoaded extends MicrocreditState {
  final List<Map<String, dynamic>> microcredits;

  const MicrocreditsLoaded({required this.microcredits});

  @override
  List<Object?> get props => [microcredits];
}

class PaymentCompletedState extends MicrocreditState {
  const PaymentCompletedState();
}

class ScoreRecalculated extends MicrocreditState {
  final Map<String, dynamic> profile;

  const ScoreRecalculated({required this.profile});

  @override
  List<Object?> get props => [profile];
}

class MicrocreditError extends MicrocreditState {
  final String message;

  const MicrocreditError({required this.message});

  @override
  List<Object?> get props => [message];
}
