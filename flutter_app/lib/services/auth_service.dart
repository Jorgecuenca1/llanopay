import '../config/api_config.dart';
import '../models/user_model.dart';
import 'api_service.dart';
import 'storage_service.dart';

/// Authentication and user profile service.
class AuthService {
  final ApiService apiService;
  final StorageService storageService;

  AuthService({
    required this.apiService,
    required this.storageService,
  });

  // ── Registration & OTP ────────────────────────

  /// Register a new user account.
  Future<ApiResponse<dynamic>> register({
    required String phone,
    required String documentType,
    required String documentNumber,
    required String firstName,
    required String lastName,
    required String password,
  }) async {
    final response = await apiService.post(
      ApiConfig.authRegister,
      data: {
        'phone_number': phone,
        'document_type': documentType,
        'document_number': documentNumber,
        'first_name': firstName,
        'last_name': lastName,
        'password': password,
      },
    );
    return response;
  }

  /// Verify an OTP code.
  Future<ApiResponse<dynamic>> verifyOTP({
    required String phone,
    required String code,
    required String purpose,
  }) async {
    final response = await apiService.post(
      ApiConfig.authVerifyOTP,
      data: {
        'phone_number': phone,
        'code': code,
        'purpose': purpose,
      },
    );
    return response;
  }

  /// Request an OTP code for the given purpose.
  Future<ApiResponse<dynamic>> requestOTP({
    required String phone,
    required String purpose,
  }) async {
    final response = await apiService.post(
      ApiConfig.authRequestOTP,
      data: {
        'phone_number': phone,
        'purpose': purpose,
      },
    );
    return response;
  }

  // ── Login / Logout ────────────────────────────

  /// Authenticate and store tokens.
  Future<ApiResponse<dynamic>> login({
    required String phone,
    required String password,
  }) async {
    final response = await apiService.post(
      ApiConfig.authLogin,
      data: {
        'phone_number': phone,
        'password': password,
      },
    );

    if (response.success && response.data != null) {
      final data = response.data as Map<String, dynamic>;
      final access = data['access'] as String?;
      final refresh = data['refresh'] as String?;
      final userJson = data['user'] as Map<String, dynamic>?;

      if (access != null) await storageService.saveToken(access);
      if (refresh != null) await storageService.saveRefreshToken(refresh);
      if (userJson != null) {
        final user = UserModel.fromJson(userJson);
        await storageService.saveUser(user);
      }
    }

    return response;
  }

  /// Clear local session and notify backend.
  Future<void> logout() async {
    try {
      final refreshToken = await storageService.getRefreshToken();
      if (refreshToken != null) {
        await apiService.post(
          ApiConfig.authLogout,
          data: {'refresh': refreshToken},
        );
      }
    } catch (_) {
      // Ignore errors during logout — always clear local state.
    } finally {
      await storageService.clearAll();
    }
  }

  // ── Profile ───────────────────────────────────

  /// Fetch the authenticated user's profile.
  Future<ApiResponse<UserModel>> getProfile() async {
    final response = await apiService.get(ApiConfig.authProfile);

    if (response.success && response.data != null) {
      final user = UserModel.fromJson(response.data as Map<String, dynamic>);
      await storageService.saveUser(user);
      return ApiResponse<UserModel>(
        success: true,
        data: user,
        statusCode: response.statusCode,
      );
    }

    return ApiResponse<UserModel>(
      success: false,
      message: response.message,
      statusCode: response.statusCode,
      errors: response.errors,
    );
  }

  /// Update profile fields.
  Future<ApiResponse<UserModel>> updateProfile(
    Map<String, dynamic> data,
  ) async {
    final response = await apiService.patch(
      ApiConfig.authProfile,
      data: data,
    );

    if (response.success && response.data != null) {
      final user = UserModel.fromJson(response.data as Map<String, dynamic>);
      await storageService.saveUser(user);
      return ApiResponse<UserModel>(
        success: true,
        data: user,
        statusCode: response.statusCode,
      );
    }

    return ApiResponse<UserModel>(
      success: false,
      message: response.message,
      statusCode: response.statusCode,
      errors: response.errors,
    );
  }

  /// Change the user's password.
  Future<ApiResponse<dynamic>> changePassword({
    required String oldPassword,
    required String newPassword,
  }) async {
    return apiService.post(
      ApiConfig.authChangePassword,
      data: {
        'old_password': oldPassword,
        'new_password': newPassword,
      },
    );
  }

  // ── Token helpers ─────────────────────────────

  /// Whether the user has a stored access token.
  Future<bool> isAuthenticated() => storageService.isLoggedIn();

  /// Retrieve the locally cached user, if any.
  Future<UserModel?> getCachedUser() => storageService.getUser();
}
