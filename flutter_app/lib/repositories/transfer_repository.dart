import '../config/api_config.dart';
import '../services/api_service.dart';

/// Repository for peer-to-peer transfer operations.
class TransferRepository {
  final ApiService apiService;

  TransferRepository({required this.apiService});

  /// Initiate a transfer to another user.
  ///
  /// Returns the created transfer and whether OTP confirmation is required.
  Future<Map<String, dynamic>> initiateTransfer({
    required String receiverPhone,
    required double amount,
    required String currency,
    String? description,
  }) async {
    final response = await apiService.post(
      ApiConfig.transferSend,
      data: {
        'receiver_phone': receiverPhone,
        'amount': amount,
        'currency': currency,
        if (description != null) 'description': description,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  /// Confirm a pending transfer with an OTP code.
  Future<Map<String, dynamic>> confirmTransfer({
    required String transferId,
    required String otpCode,
  }) async {
    final response = await apiService.post(
      '${ApiConfig.transferDetail}$transferId/confirm/',
      data: {
        'otp_code': otpCode,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  /// Fetch paginated transfer history with optional filters.
  ///
  /// Supported filters: `status`, `currency`, `date_from`, `date_to`,
  /// `page`, `page_size`.
  Future<List<Map<String, dynamic>>> getTransfers({
    Map<String, dynamic>? filters,
  }) async {
    final response = await apiService.get(
      ApiConfig.transferHistory,
      queryParameters: filters,
    );
    final data = response.data;
    if (data is List) {
      return data.cast<Map<String, dynamic>>();
    }
    final results = (data as Map<String, dynamic>)['results'] as List?;
    return results?.cast<Map<String, dynamic>>() ?? [];
  }

  /// Fetch a single transfer by its [id].
  Future<Map<String, dynamic>> getTransferDetail(String id) async {
    final response = await apiService.get(
      '${ApiConfig.transferDetail}$id/',
    );
    return response.data as Map<String, dynamic>;
  }

  /// Fetch the user's current transfer limits.
  Future<Map<String, dynamic>> getLimits() async {
    final response = await apiService.get(
      '${ApiConfig.transferDetail}limits/',
    );
    return response.data as Map<String, dynamic>;
  }

  /// Update the user's transfer limits.
  Future<Map<String, dynamic>> updateLimits({
    required Map<String, dynamic> data,
  }) async {
    final response = await apiService.patch(
      '${ApiConfig.transferDetail}limits/',
      data: data,
    );
    return response.data as Map<String, dynamic>;
  }

  /// Calculate the fee for a transfer.
  Future<Map<String, dynamic>> calculateFee({
    required double amount,
    required String currency,
  }) async {
    final response = await apiService.post(
      ApiConfig.transferCalculateFee,
      data: {
        'amount': amount,
        'currency': currency,
      },
    );
    return response.data as Map<String, dynamic>;
  }
}
