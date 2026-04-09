import 'package:flutter_bloc/flutter_bloc.dart';

import '../../repositories/marketplace_repository.dart';
import 'marketplace_event.dart';
import 'marketplace_state.dart';

class MarketplaceBloc extends Bloc<MarketplaceEvent, MarketplaceState> {
  final MarketplaceRepository marketplaceRepository;

  MarketplaceBloc({required this.marketplaceRepository})
      : super(const MarketplaceInitial()) {
    on<CategoriesLoadRequested>(_onCategoriesLoadRequested);
    on<MerchantsLoadRequested>(_onMerchantsLoadRequested);
    on<MerchantDetailRequested>(_onMerchantDetailRequested);
    on<MerchantPaymentRequested>(_onMerchantPaymentRequested);
    on<ReviewSubmitted>(_onReviewSubmitted);
    on<NearbyMerchantsRequested>(_onNearbyMerchantsRequested);
  }

  Future<void> _onCategoriesLoadRequested(
    CategoriesLoadRequested event,
    Emitter<MarketplaceState> emit,
  ) async {
    emit(const MarketplaceLoading());
    try {
      final categories = await marketplaceRepository.getCategories();
      emit(CategoriesLoaded(categories: categories));
    } catch (e) {
      emit(MarketplaceError(message: e.toString()));
    }
  }

  Future<void> _onMerchantsLoadRequested(
    MerchantsLoadRequested event,
    Emitter<MarketplaceState> emit,
  ) async {
    emit(const MarketplaceLoading());
    try {
      final merchants = await marketplaceRepository.getMerchants(
        filters: event.filters,
      );
      emit(MerchantsLoaded(merchants: merchants));
    } catch (e) {
      emit(MarketplaceError(message: e.toString()));
    }
  }

  Future<void> _onMerchantDetailRequested(
    MerchantDetailRequested event,
    Emitter<MarketplaceState> emit,
  ) async {
    emit(const MarketplaceLoading());
    try {
      final merchant = await marketplaceRepository.getMerchant(
        event.slug,
      );
      emit(MerchantDetailLoaded(merchant: merchant));
    } catch (e) {
      emit(MarketplaceError(message: e.toString()));
    }
  }

  Future<void> _onMerchantPaymentRequested(
    MerchantPaymentRequested event,
    Emitter<MarketplaceState> emit,
  ) async {
    emit(const MarketplaceLoading());
    try {
      await marketplaceRepository.payMerchant(
        merchantId: event.merchantId,
        amount: event.amount,
        currency: event.currency,
      );
      emit(const PaymentCompleted());
    } catch (e) {
      emit(MarketplaceError(message: e.toString()));
    }
  }

  Future<void> _onReviewSubmitted(
    ReviewSubmitted event,
    Emitter<MarketplaceState> emit,
  ) async {
    emit(const MarketplaceLoading());
    try {
      await marketplaceRepository.submitReview(
        merchantId: event.merchantId,
        rating: event.rating,
        comment: event.comment,
      );
      emit(const ReviewSubmittedState());
    } catch (e) {
      emit(MarketplaceError(message: e.toString()));
    }
  }

  Future<void> _onNearbyMerchantsRequested(
    NearbyMerchantsRequested event,
    Emitter<MarketplaceState> emit,
  ) async {
    emit(const MarketplaceLoading());
    try {
      final merchants = await marketplaceRepository.getNearbyMerchants(
        lat: event.lat,
        lng: event.lng,
        radius: event.radius ?? 5.0,
      );
      emit(NearbyMerchantsLoaded(merchants: merchants));
    } catch (e) {
      emit(MarketplaceError(message: e.toString()));
    }
  }
}
