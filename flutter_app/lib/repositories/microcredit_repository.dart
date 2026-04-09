import '../config/api_config.dart';
import '../services/api_service.dart';

/// Repository for microcredit and credit scoring operations.
class MicrocreditRepository {
  final ApiService apiService;

  MicrocreditRepository({required this.apiService});

  /// Fetch the user's credit profile and score.
  Future<Map<String, dynamic>> getCreditProfile() async {
    final response = await apiService.get(ApiConfig.microcreditProfile);
    return response.data as Map<String, dynamic>;
  }

  /// Fetch available microcredit products.
  Future<List<Map<String, dynamic>>> getProducts() async {
    final response = await apiService.get(ApiConfig.microcreditProducts);
    final data = response.data;
    if (data is List) {
      return data.cast<Map<String, dynamic>>();
    }
    final results = (data as Map<String, dynamic>)['results'] as List?;
    return results?.cast<Map<String, dynamic>>() ?? [];
  }

  /// Request a new microcredit loan.
  Future<Map<String, dynamic>> requestMicrocredit({
    required String productId,
    required double amount,
  }) async {
    final response = await apiService.post(
      ApiConfig.microcreditRequest,
      data: {
        'product': productId,
        'amount': amount,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  /// Fetch the user's microcredit loan history.
  Future<List<Map<String, dynamic>>> getMicrocredits() async {
    final response = await apiService.get(ApiConfig.microcreditLoans);
    final data = response.data;
    if (data is List) {
      return data.cast<Map<String, dynamic>>();
    }
    final results = (data as Map<String, dynamic>)['results'] as List?;
    return results?.cast<Map<String, dynamic>>() ?? [];
  }

  /// Fetch a single microcredit loan by its [id].
  Future<Map<String, dynamic>> getMicrocredit(String id) async {
    final response = await apiService.get(
      '${ApiConfig.microcreditLoans}$id/',
    );
    return response.data as Map<String, dynamic>;
  }

  /// Make a payment on an active microcredit loan.
  Future<Map<String, dynamic>> makePayment({
    required String microcreditId,
    required double amount,
  }) async {
    final response = await apiService.post(
      ApiConfig.microcreditPayments,
      data: {
        'microcredit': microcreditId,
        'amount': amount,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  /// Request a recalculation of the user's credit score.
  Future<Map<String, dynamic>> recalculateScore() async {
    final response = await apiService.post(
      '${ApiConfig.microcreditProfile}recalculate/',
    );
    return response.data as Map<String, dynamic>;
  }

  /// Simulate a microcredit loan to preview payments.
  Future<Map<String, dynamic>> simulate({
    required String productId,
    required double amount,
  }) async {
    final response = await apiService.post(
      ApiConfig.microcreditSimulate,
      data: {
        'product': productId,
        'amount': amount,
      },
    );
    return response.data as Map<String, dynamic>;
  }
}
