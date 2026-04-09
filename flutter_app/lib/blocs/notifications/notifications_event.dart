import 'package:equatable/equatable.dart';

abstract class NotificationsEvent extends Equatable {
  const NotificationsEvent();

  @override
  List<Object?> get props => [];
}

class NotificationsLoadRequested extends NotificationsEvent {
  const NotificationsLoadRequested();
}

class NotificationMarkRead extends NotificationsEvent {
  final List<String> ids;

  const NotificationMarkRead({required this.ids});

  @override
  List<Object?> get props => [ids];
}

class NotificationsMarkAllRead extends NotificationsEvent {
  const NotificationsMarkAllRead();
}

class UnreadCountRequested extends NotificationsEvent {
  const UnreadCountRequested();
}

class RealTimeNotificationReceived extends NotificationsEvent {
  final Map<String, dynamic> notification;

  const RealTimeNotificationReceived({required this.notification});

  @override
  List<Object?> get props => [notification];
}
