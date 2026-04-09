import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../config/theme.dart';

/// Notifications screen grouped by date with mark-all-read and swipe-to-read.
class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  // Placeholder notifications
  final List<Map<String, dynamic>> _notifications = [
    {
      'id': '1',
      'type': 'transfer',
      'title': 'Transferencia recibida',
      'message': 'Recibiste \$50.000 COP de +57 300***1234',
      'time': DateTime.now().subtract(const Duration(minutes: 15)),
      'read': false,
    },
    {
      'id': '2',
      'type': 'promo',
      'title': 'Promocion disponible',
      'message': '10% de descuento en comercios aliados este fin de semana',
      'time': DateTime.now().subtract(const Duration(hours: 2)),
      'read': false,
    },
    {
      'id': '3',
      'type': 'security',
      'title': 'Inicio de sesion exitoso',
      'message': 'Se inicio sesion desde un nuevo dispositivo',
      'time': DateTime.now().subtract(const Duration(hours: 5)),
      'read': true,
    },
    {
      'id': '4',
      'type': 'crypto',
      'title': 'Deposito confirmado',
      'message':
          'Tu deposito de 50 USDT ha sido verificado y acreditado',
      'time': DateTime.now().subtract(const Duration(days: 1)),
      'read': true,
    },
    {
      'id': '5',
      'type': 'system',
      'title': 'Bienvenido a LlanoPay',
      'message':
          'Tu cuenta ha sido creada exitosamente. Verifica tu identidad para aumentar tus limites.',
      'time': DateTime.now().subtract(const Duration(days: 2)),
      'read': true,
    },
    {
      'id': '6',
      'type': 'transfer',
      'title': 'Envio exitoso',
      'message': 'Enviaste \$25.000 COP a +57 311***5678',
      'time': DateTime.now().subtract(const Duration(days: 2)),
      'read': true,
    },
  ];

  void _markAllAsRead() {
    setState(() {
      for (final n in _notifications) {
        n['read'] = true;
      }
    });
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Todas las notificaciones marcadas como leidas'),
        backgroundColor: LlanoPayTheme.success,
      ),
    );
  }

  void _markAsRead(String id) {
    setState(() {
      final n = _notifications.firstWhere((n) => n['id'] == id);
      n['read'] = true;
    });
  }

  IconData _typeIcon(String type) {
    switch (type) {
      case 'transfer':
        return Icons.swap_horiz;
      case 'promo':
        return Icons.local_offer;
      case 'security':
        return Icons.security;
      case 'crypto':
        return Icons.currency_bitcoin;
      case 'system':
        return Icons.info_outline;
      default:
        return Icons.notifications;
    }
  }

  Color _typeColor(String type) {
    switch (type) {
      case 'transfer':
        return LlanoPayTheme.primaryGreen;
      case 'promo':
        return LlanoPayTheme.secondaryGold;
      case 'security':
        return LlanoPayTheme.error;
      case 'crypto':
        return const Color(0xFF6C63FF);
      case 'system':
        return LlanoPayTheme.accentBrown;
      default:
        return LlanoPayTheme.textSecondary;
    }
  }

  String _timeAgo(DateTime time) {
    final diff = DateTime.now().difference(time);
    if (diff.inMinutes < 60) {
      return 'Hace ${diff.inMinutes} min';
    } else if (diff.inHours < 24) {
      return 'Hace ${diff.inHours} h';
    } else {
      return 'Hace ${diff.inDays} d';
    }
  }

  Map<String, List<Map<String, dynamic>>> _groupByDate() {
    final grouped = <String, List<Map<String, dynamic>>>{};
    for (final n in _notifications) {
      final time = n['time'] as DateTime;
      final now = DateTime.now();
      String label;
      if (time.year == now.year &&
          time.month == now.month &&
          time.day == now.day) {
        label = 'Hoy';
      } else if (time.year == now.year &&
          time.month == now.month &&
          time.day == now.day - 1) {
        label = 'Ayer';
      } else {
        label = '${time.day}/${time.month}/${time.year}';
      }
      grouped.putIfAbsent(label, () => []).add(n);
    }
    return grouped;
  }

  @override
  Widget build(BuildContext context) {
    final hasUnread = _notifications.any((n) => !(n['read'] as bool));
    final grouped = _groupByDate();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Notificaciones'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
        actions: [
          if (hasUnread)
            TextButton(
              onPressed: _markAllAsRead,
              child: Text(
                'Marcar todo como leido',
                style: GoogleFonts.nunito(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
        ],
      ),
      body: _notifications.isEmpty
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.notifications_off_outlined,
                    size: 56,
                    color: LlanoPayTheme.textSecondary.withOpacity(0.4),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Sin notificaciones',
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                          color: LlanoPayTheme.textSecondary,
                        ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Las alertas de transacciones y novedades apareceran aqui',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: LlanoPayTheme.textSecondary,
                        ),
                  ),
                ],
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.only(bottom: 24),
              itemCount: grouped.length,
              itemBuilder: (context, groupIndex) {
                final dateLabel = grouped.keys.elementAt(groupIndex);
                final items = grouped[dateLabel]!;

                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Date header
                    Padding(
                      padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
                      child: Text(
                        dateLabel,
                        style:
                            Theme.of(context).textTheme.titleSmall?.copyWith(
                                  color: LlanoPayTheme.textSecondary,
                                ),
                      ),
                    ),
                    // Notification items
                    ...items.map((n) => _buildNotificationTile(n)),
                  ],
                );
              },
            ),
    );
  }

  Widget _buildNotificationTile(Map<String, dynamic> notification) {
    final id = notification['id'] as String;
    final type = notification['type'] as String;
    final title = notification['title'] as String;
    final message = notification['message'] as String;
    final time = notification['time'] as DateTime;
    final isRead = notification['read'] as bool;
    final color = _typeColor(type);

    return Dismissible(
      key: Key(id),
      direction: DismissDirection.startToEnd,
      onDismissed: (_) => _markAsRead(id),
      background: Container(
        color: LlanoPayTheme.primaryGreen.withOpacity(0.1),
        alignment: Alignment.centerLeft,
        padding: const EdgeInsets.only(left: 20),
        child: const Icon(
          Icons.mark_email_read,
          color: LlanoPayTheme.primaryGreen,
        ),
      ),
      child: Container(
        color:
            isRead ? null : LlanoPayTheme.primaryGreen.withOpacity(0.04),
        child: ListTile(
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 4,
          ),
          leading: Container(
            width: 42,
            height: 42,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              _typeIcon(type),
              color: color,
              size: 22,
            ),
          ),
          title: Row(
            children: [
              Expanded(
                child: Text(
                  title,
                  style:
                      Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight:
                                isRead ? FontWeight.w500 : FontWeight.w700,
                          ),
                ),
              ),
              if (!isRead)
                Container(
                  width: 8,
                  height: 8,
                  decoration: const BoxDecoration(
                    color: LlanoPayTheme.primaryGreen,
                    shape: BoxShape.circle,
                  ),
                ),
            ],
          ),
          subtitle: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 2),
              Text(
                message,
                style: Theme.of(context).textTheme.bodySmall,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 4),
              Text(
                _timeAgo(time),
                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                      color: LlanoPayTheme.textSecondary,
                    ),
              ),
            ],
          ),
          onTap: () {
            if (!isRead) _markAsRead(id);
          },
        ),
      ),
    );
  }
}
