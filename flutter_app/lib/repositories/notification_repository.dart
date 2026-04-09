import '../config/api_config.dart';
import '../services/api_service.dart';

/// Repository for notification operations.
class NotificationRepository {
  final ApiService apiService;

  NotificationRepository({required this.apiService});

  /// Fetch notifications, optionally filtered by read status.
  Future<List<Map<String, dynamic>>> getNotifications({
    bool? isRead,
  }) async {
    final queryParameters = <String, dynamic>{};
    if (isRead != null) {
      queryParameters['is_read'] = isRead;
    }
    final response = await apiService.get(
      ApiConfig.notifications,
      queryParameters: queryParameters.isNotEmpty ? queryParameters : null,
    );
    final data = response.data;
    if (data is List) {
      return data.cast<Map<String, dynamic>>();
    }
    final results = (data as Map<String, dynamic>)['results'] as List?;
    return results?.cast<Map<String, dynamic>>() ?? [];
  }

  /// Mark specific notifications as read by their [ids].
  Future<Map<String, dynamic>> markAsRead({
    required List<String> ids,
  }) async {
    final response = await apiService.post(
      ApiConfig.notificationsMarkRead,
      data: {
        'ids': ids,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  /// Mark all notifications as read.
  Future<Map<String, dynamic>> markAllAsRead() async {
    final response = await apiService.post(
      ApiConfig.notificationsMarkRead,
      data: {
        'all': true,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  /// Fetch the count of unread notifications.
  Future<int> getUnreadCount() async {
    final response = await apiService.get(
      ApiConfig.notifications,
      queryParameters: {'is_read': false, 'page_size': 1},
    );
    final data = response.data;
    if (data is Map<String, dynamic>) {
      return (data['count'] as int?) ?? 0;
    }
    return (data as List?)?.length ?? 0;
  }

  /// Register a device token for push notifications.
  Future<Map<String, dynamic>> registerDeviceToken({
    required String token,
    required String platform,
  }) async {
    final response = await apiService.post(
      ApiConfig.notificationsSettings,
      data: {
        'device_token': token,
        'platform': platform,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  /// Fetch notification settings/preferences.
  Future<Map<String, dynamic>> getSettings() async {
    final response = await apiService.get(ApiConfig.notificationsSettings);
    return response.data as Map<String, dynamic>;
  }
}
