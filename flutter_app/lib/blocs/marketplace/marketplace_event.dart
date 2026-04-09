import 'package:equatable/equatable.dart';

abstract class MarketplaceEvent extends Equatable {
  const MarketplaceEvent();

  @override
  List<Object?> get props => [];
}

class CategoriesLoadRequested extends MarketplaceEvent {
  const CategoriesLoadRequested();
}

class MerchantsLoadRequested extends MarketplaceEvent {
  final Map<String, dynamic>? filters;

  const MerchantsLoadRequested({this.filters});

  @override
  List<Object?> get props => [filters];
}

class MerchantDetailRequested extends MarketplaceEvent {
  final String slug;

  const MerchantDetailRequested({required this.slug});

  @override
  List<Object?> get props => [slug];
}

class MerchantPaymentRequested extends MarketplaceEvent {
  final String merchantId;
  final double amount;
  final String currency;

  const MerchantPaymentRequested({
    required this.merchantId,
    required this.amount,
    required this.currency,
  });

  @override
  List<Object?> get props => [merchantId, amount, currency];
}

class ReviewSubmitted extends MarketplaceEvent {
  final String merchantId;
  final int rating;
  final String? comment;

  const ReviewSubmitted({
    required this.merchantId,
    required this.rating,
    this.comment,
  });

  @override
  List<Object?> get props => [merchantId, rating, comment];
}

class NearbyMerchantsRequested extends MarketplaceEvent {
  final double lat;
  final double lng;
  final double? radius;

  const NearbyMerchantsRequested({
    required this.lat,
    required this.lng,
    this.radius,
  });

  @override
  List<Object?> get props => [lat, lng, radius];
}
