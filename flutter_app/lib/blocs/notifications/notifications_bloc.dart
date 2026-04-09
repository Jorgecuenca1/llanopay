import 'package:flutter_bloc/flutter_bloc.dart';

import '../../repositories/notification_repository.dart';
import 'notifications_event.dart';
import 'notifications_state.dart';

class NotificationsBloc extends Bloc<NotificationsEvent, NotificationsState> {
  final NotificationRepository notificationsRepository;

  NotificationsBloc({required this.notificationsRepository})
      : super(const NotificationsInitial()) {
    on<NotificationsLoadRequested>(_onNotificationsLoadRequested);
    on<NotificationMarkRead>(_onNotificationMarkRead);
    on<NotificationsMarkAllRead>(_onNotificationsMarkAllRead);
    on<UnreadCountRequested>(_onUnreadCountRequested);
    on<RealTimeNotificationReceived>(_onRealTimeNotificationReceived);
  }

  Future<void> _onNotificationsLoadRequested(
    NotificationsLoadRequested event,
    Emitter<NotificationsState> emit,
  ) async {
    emit(const NotificationsLoading());
    try {
      final notifications = await notificationsRepository.getNotifications();
      final unreadCount = await notificationsRepository.getUnreadCount();
      emit(NotificationsLoaded(
        notifications: notifications,
        unreadCount: unreadCount,
      ));
    } catch (e) {
      emit(NotificationsError(message: e.toString()));
    }
  }

  Future<void> _onNotificationMarkRead(
    NotificationMarkRead event,
    Emitter<NotificationsState> emit,
  ) async {
    try {
      await notificationsRepository.markAsRead(ids: event.ids);
      final notifications = await notificationsRepository.getNotifications();
      final unreadCount = await notificationsRepository.getUnreadCount();
      emit(NotificationsLoaded(
        notifications: notifications,
        unreadCount: unreadCount,
      ));
    } catch (e) {
      emit(NotificationsError(message: e.toString()));
    }
  }

  Future<void> _onNotificationsMarkAllRead(
    NotificationsMarkAllRead event,
    Emitter<NotificationsState> emit,
  ) async {
    try {
      await notificationsRepository.markAllAsRead();
      final notifications = await notificationsRepository.getNotifications();
      emit(NotificationsLoaded(
        notifications: notifications,
        unreadCount: 0,
      ));
    } catch (e) {
      emit(NotificationsError(message: e.toString()));
    }
  }

  Future<void> _onUnreadCountRequested(
    UnreadCountRequested event,
    Emitter<NotificationsState> emit,
  ) async {
    try {
      final count = await notificationsRepository.getUnreadCount();
      emit(UnreadCountLoaded(count: count));
    } catch (e) {
      emit(NotificationsError(message: e.toString()));
    }
  }

  Future<void> _onRealTimeNotificationReceived(
    RealTimeNotificationReceived event,
    Emitter<NotificationsState> emit,
  ) async {
    final currentState = state;
    if (currentState is NotificationsLoaded) {
      final updatedNotifications = [
        event.notification,
        ...currentState.notifications,
      ];
      emit(NotificationsLoaded(
        notifications: updatedNotifications,
        unreadCount: currentState.unreadCount + 1,
      ));
    } else {
      final notifications = await notificationsRepository.getNotifications();
      final unreadCount = await notificationsRepository.getUnreadCount();
      emit(NotificationsLoaded(
        notifications: notifications,
        unreadCount: unreadCount,
      ));
    }
  }
}
