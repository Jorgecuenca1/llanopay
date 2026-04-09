import '../config/api_config.dart';
import '../services/api_service.dart';

/// Repository for marketplace and merchant operations.
class MarketplaceRepository {
  final ApiService apiService;

  MarketplaceRepository({required this.apiService});

  /// Fetch all available marketplace categories.
  Future<List<Map<String, dynamic>>> getCategories() async {
    final response = await apiService.get(ApiConfig.marketplaceCategories);
    final data = response.data;
    if (data is List) {
      return data.cast<Map<String, dynamic>>();
    }
    final results = (data as Map<String, dynamic>)['results'] as List?;
    return results?.cast<Map<String, dynamic>>() ?? [];
  }

  /// Fetch merchants with optional filters.
  ///
  /// Supported filters: `category`, `search`, `accepts_llo`,
  /// `city`, `page`, `page_size`.
  Future<List<Map<String, dynamic>>> getMerchants({
    Map<String, dynamic>? filters,
  }) async {
    final response = await apiService.get(
      ApiConfig.marketplaceMerchants,
      queryParameters: filters,
    );
    final data = response.data;
    if (data is List) {
      return data.cast<Map<String, dynamic>>();
    }
    final results = (data as Map<String, dynamic>)['results'] as List?;
    return results?.cast<Map<String, dynamic>>() ?? [];
  }

  /// Fetch a single merchant by its [slug].
  Future<Map<String, dynamic>> getMerchant(String slug) async {
    final response = await apiService.get(
      '${ApiConfig.marketplaceMerchants}$slug/',
    );
    return response.data as Map<String, dynamic>;
  }

  /// Pay a merchant from the user's wallet.
  Future<Map<String, dynamic>> payMerchant({
    required String merchantId,
    required double amount,
    required String currency,
  }) async {
    final response = await apiService.post(
      '${ApiConfig.marketplaceMerchants}$merchantId/pay/',
      data: {
        'amount': amount,
        'currency': currency,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  /// Submit a review for a merchant.
  Future<Map<String, dynamic>> submitReview({
    required String merchantId,
    required int rating,
    String? comment,
  }) async {
    final response = await apiService.post(
      ApiConfig.marketplaceReviews,
      data: {
        'merchant': merchantId,
        'rating': rating,
        if (comment != null) 'comment': comment,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  /// Fetch nearby merchants by geographic coordinates.
  Future<List<Map<String, dynamic>>> getNearbyMerchants({
    required double lat,
    required double lng,
    double radius = 5.0,
  }) async {
    final response = await apiService.get(
      ApiConfig.marketplaceNearby,
      queryParameters: {
        'lat': lat,
        'lng': lng,
        'radius': radius,
      },
    );
    final data = response.data;
    if (data is List) {
      return data.cast<Map<String, dynamic>>();
    }
    final results = (data as Map<String, dynamic>)['results'] as List?;
    return results?.cast<Map<String, dynamic>>() ?? [];
  }

  /// Search merchants by query string.
  Future<List<Map<String, dynamic>>> searchMerchants(String query) async {
    final response = await apiService.get(
      ApiConfig.marketplaceSearch,
      queryParameters: {'q': query},
    );
    final data = response.data;
    if (data is List) {
      return data.cast<Map<String, dynamic>>();
    }
    final results = (data as Map<String, dynamic>)['results'] as List?;
    return results?.cast<Map<String, dynamic>>() ?? [];
  }
}
