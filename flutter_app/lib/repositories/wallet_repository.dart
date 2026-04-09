import '../config/api_config.dart';
import '../services/api_service.dart';

/// Repository for wallet and transaction operations.
class WalletRepository {
  final ApiService apiService;

  WalletRepository({required this.apiService});

  /// Fetch the user's wallet information.
  Future<Map<String, dynamic>> getWallet() async {
    final response = await apiService.get(ApiConfig.walletInfo);
    return response.data as Map<String, dynamic>;
  }

  /// Fetch the balance summary (COP + LLO balances, recent activity).
  Future<Map<String, dynamic>> getBalanceSummary() async {
    final response = await apiService.get(ApiConfig.walletBalance);
    return response.data as Map<String, dynamic>;
  }

  /// Fetch paginated transaction history with optional filters.
  ///
  /// Supported filters: `type`, `currency`, `date_from`, `date_to`,
  /// `page`, `page_size`.
  Future<List<Map<String, dynamic>>> getTransactions({
    Map<String, dynamic>? filters,
  }) async {
    final response = await apiService.get(
      ApiConfig.walletTransactions,
      queryParameters: filters,
    );
    final data = response.data;
    if (data is List) {
      return data.cast<Map<String, dynamic>>();
    }
    // Handle paginated response envelope.
    final results = (data as Map<String, dynamic>)['results'] as List?;
    return results?.cast<Map<String, dynamic>>() ?? [];
  }

  /// Fetch a single transaction by its [id].
  Future<Map<String, dynamic>> getTransactionDetail(String id) async {
    final response = await apiService.get(
      '${ApiConfig.walletTransactions}$id/',
    );
    return response.data as Map<String, dynamic>;
  }
}
