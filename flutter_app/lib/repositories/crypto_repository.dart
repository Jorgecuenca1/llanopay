import '../config/api_config.dart';
import '../services/api_service.dart';

/// Repository for cryptocurrency and Llanocoin operations.
class CryptoRepository {
  final ApiService apiService;

  CryptoRepository({required this.apiService});

  /// Submit a crypto deposit proof.
  Future<Map<String, dynamic>> submitDeposit({
    required String currency,
    required double amount,
    required String txHash,
    required String network,
  }) async {
    final response = await apiService.post(
      ApiConfig.cryptoDeposit,
      data: {
        'currency': currency,
        'amount': amount,
        'tx_hash': txHash,
        'network': network,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  /// Fetch the user's crypto deposit history.
  Future<List<Map<String, dynamic>>> getDeposits() async {
    final response = await apiService.get(ApiConfig.cryptoDeposit);
    final data = response.data;
    if (data is List) {
      return data.cast<Map<String, dynamic>>();
    }
    final results = (data as Map<String, dynamic>)['results'] as List?;
    return results?.cast<Map<String, dynamic>>() ?? [];
  }

  /// Fetch current exchange rates for supported crypto currencies.
  Future<Map<String, dynamic>> getRates() async {
    final response = await apiService.get(ApiConfig.cryptoExchangeRate);
    return response.data as Map<String, dynamic>;
  }

  /// Buy Llanocoin (LLO) using COP balance.
  Future<Map<String, dynamic>> buyLlanocoin({
    required double amountCop,
  }) async {
    final response = await apiService.post(
      ApiConfig.cryptoBuyLlo,
      data: {
        'amount_cop': amountCop,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  /// Sell Llanocoin (LLO) to COP balance.
  Future<Map<String, dynamic>> sellLlanocoin({
    required double amountLlo,
  }) async {
    final response = await apiService.post(
      ApiConfig.cryptoSellLlo,
      data: {
        'amount_llo': amountLlo,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  /// Fetch Llanocoin transaction history.
  Future<List<Map<String, dynamic>>> getLloTransactions() async {
    final response = await apiService.get(ApiConfig.cryptoTransactions);
    final data = response.data;
    if (data is List) {
      return data.cast<Map<String, dynamic>>();
    }
    final results = (data as Map<String, dynamic>)['results'] as List?;
    return results?.cast<Map<String, dynamic>>() ?? [];
  }

  /// Fetch Llanocoin metadata (total supply, price, etc.).
  Future<Map<String, dynamic>> getLlanocoinInfo() async {
    final response = await apiService.get(ApiConfig.cryptoLlanocoinInfo);
    return response.data as Map<String, dynamic>;
  }
}
