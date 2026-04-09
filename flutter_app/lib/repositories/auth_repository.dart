import '../config/api_config.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';

/// Repository for authentication and user profile operations.
class AuthRepository {
  final ApiService apiService;
  final StorageService storageService;

  AuthRepository({
    required this.apiService,
    required this.storageService,
  });

  /// Register a new user account.
  Future<Map<String, dynamic>> register({
    required String phone,
    required String docType,
    required String docNumber,
    required String firstName,
    required String lastName,
    required String password,
  }) async {
    final response = await apiService.post(
      ApiConfig.authRegister,
      data: {
        'phone': phone,
        'doc_type': docType,
        'doc_number': docNumber,
        'first_name': firstName,
        'last_name': lastName,
        'password': password,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  /// Verify OTP code for registration or password reset.
  Future<Map<String, dynamic>> verifyOTP({
    required String phone,
    required String code,
    required String purpose,
  }) async {
    final response = await apiService.post(
      ApiConfig.authVerifyOTP,
      data: {
        'phone': phone,
        'code': code,
        'purpose': purpose,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  /// Login with phone and password. Saves tokens on success.
  Future<Map<String, dynamic>> login({
    required String phone,
    required String password,
  }) async {
    final response = await apiService.post(
      ApiConfig.authLogin,
      data: {
        'phone': phone,
        'password': password,
      },
    );
    final data = response.data as Map<String, dynamic>;

    // Persist authentication tokens.
    final token = data['token'] as String?;
    final refreshToken = data['refresh_token'] as String?;
    if (token != null) {
      await storageService.saveToken(token);
    }
    if (refreshToken != null) {
      await storageService.saveRefreshToken(refreshToken);
    }

    return data;
  }

  /// Request a new OTP for the given phone and purpose.
  Future<Map<String, dynamic>> requestOTP({
    required String phone,
    required String purpose,
  }) async {
    final response = await apiService.post(
      ApiConfig.authRequestOTP,
      data: {
        'phone': phone,
        'purpose': purpose,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  /// Fetch the authenticated user's profile.
  Future<Map<String, dynamic>> getProfile() async {
    final response = await apiService.get(ApiConfig.authProfile);
    return response.data as Map<String, dynamic>;
  }

  /// Update the authenticated user's profile.
  Future<Map<String, dynamic>> updateProfile({
    required Map<String, dynamic> data,
  }) async {
    final response = await apiService.patch(
      ApiConfig.authProfile,
      data: data,
    );
    return response.data as Map<String, dynamic>;
  }

  /// Change the authenticated user's password.
  Future<Map<String, dynamic>> changePassword({
    required String currentPassword,
    required String newPassword,
  }) async {
    final response = await apiService.post(
      ApiConfig.authChangePassword,
      data: {
        'current_password': currentPassword,
        'new_password': newPassword,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  /// Logout and clear persisted tokens.
  Future<void> logout() async {
    try {
      await apiService.post(ApiConfig.authLogout);
    } finally {
      await storageService.clearToken();
      await storageService.clearRefreshToken();
    }
  }
}
