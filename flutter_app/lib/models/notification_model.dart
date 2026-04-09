/// In-app notification.
class NotificationModel {
  final int id;
  final String notificationType;
  final String title;
  final String message;
  final Map<String, dynamic>? data;
  final bool isRead;
  final DateTime createdAt;

  const NotificationModel({
    required this.id,
    required this.notificationType,
    required this.title,
    required this.message,
    this.data,
    this.isRead = false,
    required this.createdAt,
  });

  factory NotificationModel.fromJson(Map<String, dynamic> json) {
    return NotificationModel(
      id: json['id'] as int,
      notificationType: json['notification_type'] as String? ?? 'general',
      title: json['title'] as String? ?? '',
      message: json['message'] as String? ?? '',
      data: json['data'] != null
          ? Map<String, dynamic>.from(json['data'] as Map)
          : null,
      isRead: json['is_read'] as bool? ?? false,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'notification_type': notificationType,
      'title': title,
      'message': message,
      'data': data,
      'is_read': isRead,
      'created_at': createdAt.toIso8601String(),
    };
  }

  /// Return a copy with [isRead] set to true.
  NotificationModel markAsRead() {
    return NotificationModel(
      id: id,
      notificationType: notificationType,
      title: title,
      message: message,
      data: data,
      isRead: true,
      createdAt: createdAt,
    );
  }

  @override
  String toString() =>
      'Notification(id: $id, type: $notificationType, read: $isRead)';
}
