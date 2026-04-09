import 'package:equatable/equatable.dart';

abstract class MarketplaceState extends Equatable {
  const MarketplaceState();

  @override
  List<Object?> get props => [];
}

class MarketplaceInitial extends MarketplaceState {
  const MarketplaceInitial();
}

class MarketplaceLoading extends MarketplaceState {
  const MarketplaceLoading();
}

class CategoriesLoaded extends MarketplaceState {
  final List<Map<String, dynamic>> categories;

  const CategoriesLoaded({required this.categories});

  @override
  List<Object?> get props => [categories];
}

class MerchantsLoaded extends MarketplaceState {
  final List<Map<String, dynamic>> merchants;

  const MerchantsLoaded({required this.merchants});

  @override
  List<Object?> get props => [merchants];
}

class MerchantDetailLoaded extends MarketplaceState {
  final Map<String, dynamic> merchant;

  const MerchantDetailLoaded({required this.merchant});

  @override
  List<Object?> get props => [merchant];
}

class PaymentCompleted extends MarketplaceState {
  const PaymentCompleted();
}

class ReviewSubmittedState extends MarketplaceState {
  const ReviewSubmittedState();
}

class NearbyMerchantsLoaded extends MarketplaceState {
  final List<Map<String, dynamic>> merchants;

  const NearbyMerchantsLoaded({required this.merchants});

  @override
  List<Object?> get props => [merchants];
}

class MarketplaceError extends MarketplaceState {
  final String message;

  const MarketplaceError({required this.message});

  @override
  List<Object?> get props => [message];
}
