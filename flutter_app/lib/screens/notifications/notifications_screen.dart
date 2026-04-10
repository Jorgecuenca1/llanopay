import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../services/api_service.dart';
import '../../config/api_config.dart';

/// Notifications screen loading from API.
class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  bool _loading = true;
  List<dynamic> _notifications = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final api = context.read<ApiService>();
    final r = await api.get(ApiConfig.notifications);
    if (mounted) {
      setState(() {
        _loading = false;
        if (r.success) {
          final d = r.data;
          _notifications = d is Map ? (d['results'] as List? ?? []) : (d as List? ?? []);
        }
      });
    }
  }

  Future<void> _markAllAsRead() async {
    final api = context.read<ApiService>();
    await api.post(ApiConfig.notificationsMarkAllRead);
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Marcadas como leidas')),
      );
      _load();
    }
  }

  IconData _typeIcon(String? type) {
    switch (type) {
      case 'TRANSFER_RECEIVED':
      case 'TRANSFER_SENT':
        return Icons.swap_horiz;
      case 'PROMOTION':
        return Icons.local_offer;
      case 'OTP_CODE':
        return Icons.security;
      case 'CRYPTO_DEPOSIT':
        return Icons.currency_bitcoin;
      case 'LOAN_APPROVED':
      case 'LOAN_PAYMENT_DUE':
        return Icons.credit_score;
      case 'MERCHANT_PAYMENT':
        return Icons.store;
      default:
        return Icons.notifications;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Notificaciones'),
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
        actions: [
          if (_notifications.any((n) => n['is_read'] == false))
            IconButton(
              icon: const Icon(Icons.done_all),
              onPressed: _markAllAsRead,
              tooltip: 'Marcar todo como leido',
            ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _load,
        child: _loading
            ? const Center(child: CircularProgressIndicator())
            : _notifications.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.notifications_none, size: 64, color: Theme.of(context).colorScheme.onSurfaceVariant),
                        const SizedBox(height: 16),
                        const Text('Sin notificaciones'),
                      ],
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(8),
                    itemCount: _notifications.length,
                    itemBuilder: (ctx, i) {
                      final n = _notifications[i] as Map<String, dynamic>;
                      final isRead = n['is_read'] == true;
                      final created = n['created_at']?.toString();
                      String when = '';
                      if (created != null) {
                        try {
                          when = DateFormat('dd/MM/yyyy HH:mm').format(DateTime.parse(created));
                        } catch (_) {}
                      }
                      return Card(
                        color: isRead ? null : Theme.of(context).colorScheme.primaryContainer.withAlpha(60),
                        child: ListTile(
                          leading: CircleAvatar(
                            backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                            child: Icon(_typeIcon(n['notification_type']?.toString()),
                                color: Theme.of(context).colorScheme.primary),
                          ),
                          title: Text(n['title']?.toString() ?? '',
                              style: TextStyle(
                                  fontWeight: isRead ? FontWeight.normal : FontWeight.bold)),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(n['message']?.toString() ?? ''),
                              const SizedBox(height: 4),
                              Text(when,
                                  style: const TextStyle(fontSize: 11, color: Colors.grey)),
                            ],
                          ),
                          trailing: isRead
                              ? null
                              : Container(
                                  width: 10,
                                  height: 10,
                                  decoration: const BoxDecoration(
                                      color: Colors.red, shape: BoxShape.circle),
                                ),
                        ),
                      );
                    },
                  ),
      ),
    );
  }
}
