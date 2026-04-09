import 'package:dio/dio.dart';

import '../config/api_config.dart';
import 'storage_service.dart';

/// Structured API response wrapper.
class ApiResponse<T> {
  final bool success;
  final T? data;
  final String? message;
  final int? statusCode;
  final Map<String, dynamic>? errors;

  const ApiResponse({
    required this.success,
    this.data,
    this.message,
    this.statusCode,
    this.errors,
  });
}

/// Dio-based HTTP client with JWT authentication and token refresh.
class ApiService {
  late final Dio _dio;
  final StorageService storageService;
  bool _isRefreshing = false;

  ApiService({required this.storageService}) {
    _dio = Dio(
      BaseOptions(
        baseUrl: ApiConfig.baseUrl,
        connectTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 30),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    _dio.interceptors.addAll([
      _authInterceptor(),
      _tokenRefreshInterceptor(),
      LogInterceptor(
        requestBody: true,
        responseBody: true,
        logPrint: (obj) => print('[API] $obj'),
      ),
    ]);
  }

  // ── Interceptors ──────────────────────────────

  /// Attaches the Bearer token to every request.
  InterceptorsWrapper _authInterceptor() {
    return InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await storageService.getToken();
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
    );
  }

  /// Automatically refreshes the JWT when a 401 is received.
  InterceptorsWrapper _tokenRefreshInterceptor() {
    return InterceptorsWrapper(
      onError: (error, handler) async {
        if (error.response?.statusCode == 401 && !_isRefreshing) {
          _isRefreshing = true;
          try {
            final refreshToken = await storageService.getRefreshToken();
            if (refreshToken == null) {
              await storageService.clearAll();
              _isRefreshing = false;
              return handler.reject(error);
            }

            final refreshDio = Dio(
              BaseOptions(baseUrl: ApiConfig.baseUrl),
            );

            final response = await refreshDio.post(
              ApiConfig.authRefreshToken,
              data: {'refresh': refreshToken},
            );

            if (response.statusCode == 200) {
              final newAccess = response.data['access'] as String;
              final newRefresh =
                  response.data['refresh'] as String? ?? refreshToken;

              await storageService.saveToken(newAccess);
              await storageService.saveRefreshToken(newRefresh);

              // Retry the original request with the new token.
              error.requestOptions.headers['Authorization'] =
                  'Bearer $newAccess';
              final retryResponse = await _dio.fetch(error.requestOptions);
              _isRefreshing = false;
              return handler.resolve(retryResponse);
            }
          } catch (_) {
            await storageService.clearAll();
          }
          _isRefreshing = false;
        }
        handler.next(error);
      },
    );
  }

  // ── HTTP Methods ──────────────────────────────

  Future<ApiResponse<dynamic>> get(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    return _request(() => _dio.get(path, queryParameters: queryParameters));
  }

  Future<ApiResponse<dynamic>> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  }) async {
    return _request(
      () => _dio.post(path, data: data, queryParameters: queryParameters),
    );
  }

  Future<ApiResponse<dynamic>> put(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  }) async {
    return _request(
      () => _dio.put(path, data: data, queryParameters: queryParameters),
    );
  }

  Future<ApiResponse<dynamic>> patch(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  }) async {
    return _request(
      () => _dio.patch(path, data: data, queryParameters: queryParameters),
    );
  }

  Future<ApiResponse<dynamic>> delete(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  }) async {
    return _request(
      () => _dio.delete(path, data: data, queryParameters: queryParameters),
    );
  }

  /// Upload files with multipart form data.
  Future<ApiResponse<dynamic>> upload(
    String path, {
    required FormData formData,
  }) async {
    return _request(() => _dio.post(path, data: formData));
  }

  // ── Internal ──────────────────────────────────

  Future<ApiResponse<dynamic>> _request(
    Future<Response<dynamic>> Function() request,
  ) async {
    try {
      final response = await request();
      return ApiResponse(
        success: true,
        data: response.data,
        statusCode: response.statusCode,
      );
    } on DioException catch (e) {
      return _handleDioError(e);
    } catch (e) {
      return ApiResponse(
        success: false,
        message: 'Error inesperado: $e',
      );
    }
  }

  ApiResponse<dynamic> _handleDioError(DioException error) {
    String message;
    Map<String, dynamic>? errors;
    final statusCode = error.response?.statusCode;

    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        message = 'Tiempo de espera agotado. Verifica tu conexion.';
        break;
      case DioExceptionType.connectionError:
        message = 'Sin conexion a internet.';
        break;
      case DioExceptionType.badResponse:
        final data = error.response?.data;
        if (data is Map<String, dynamic>) {
          message = data['detail'] as String? ??
              data['message'] as String? ??
              'Error del servidor.';
          errors = data['errors'] as Map<String, dynamic>?;
        } else {
          message = 'Error del servidor ($statusCode).';
        }
        break;
      case DioExceptionType.cancel:
        message = 'Solicitud cancelada.';
        break;
      default:
        message = 'Error de conexion.';
    }

    return ApiResponse(
      success: false,
      message: message,
      statusCode: statusCode,
      errors: errors,
    );
  }
}
