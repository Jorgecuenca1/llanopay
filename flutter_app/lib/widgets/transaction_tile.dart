import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../config/theme.dart';

/// A list tile displaying a single transaction.
///
/// Shows a colored icon by type, description, relative/formatted date,
/// amount with sign and color, and an optional status chip.
class TransactionTile extends StatelessWidget {
  /// Transaction description / title.
  final String description;

  /// Transaction amount (positive for income, negative for expense).
  final double amount;

  /// Currency code: 'COP' or 'LLO'.
  final String currency;

  /// Transaction type: 'income', 'expense', 'transfer_in', 'transfer_out',
  /// 'crypto_buy', 'crypto_sell', 'payment', etc.
  final String type;

  /// Transaction status: 'completed', 'pending', 'failed', 'cancelled'.
  final String status;

  /// ISO 8601 date string of the transaction.
  final String date;

  /// Callback when the tile is tapped.
  final VoidCallback? onTap;

  const TransactionTile({
    super.key,
    required this.description,
    required this.amount,
    required this.currency,
    required this.type,
    required this.status,
    required this.date,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isIncome = amount >= 0;
    final amountColor =
        isIncome ? LlanoPayTheme.success : LlanoPayTheme.error;

    return ListTile(
      onTap: onTap,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      leading: _buildIcon(),
      title: Text(
        description,
        style: Theme.of(context).textTheme.titleMedium,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
      ),
      subtitle: Row(
        children: [
          Flexible(
            child: Text(
              _formatDate(),
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
          if (status != 'completed') ...[
            const SizedBox(width: 8),
            _buildStatusChip(context),
          ],
        ],
      ),
      trailing: Text(
        _formatAmount(),
        style: Theme.of(context).textTheme.titleMedium?.copyWith(
              color: amountColor,
              fontWeight: FontWeight.w700,
            ),
      ),
    );
  }

  Widget _buildIcon() {
    final isIncome = amount >= 0;
    final Color bgColor;
    final IconData iconData;

    switch (type) {
      case 'transfer_in':
        bgColor = LlanoPayTheme.success;
        iconData = Icons.call_received;
        break;
      case 'transfer_out':
        bgColor = LlanoPayTheme.error;
        iconData = Icons.call_made;
        break;
      case 'crypto_buy':
        bgColor = LlanoPayTheme.secondaryGold;
        iconData = Icons.currency_bitcoin;
        break;
      case 'crypto_sell':
        bgColor = LlanoPayTheme.secondaryGoldDark;
        iconData = Icons.currency_bitcoin;
        break;
      case 'payment':
        bgColor = LlanoPayTheme.accentBrown;
        iconData = Icons.storefront;
        break;
      case 'microcredit':
        bgColor = LlanoPayTheme.primaryGreenLight;
        iconData = Icons.account_balance;
        break;
      default:
        bgColor =
            isIncome ? LlanoPayTheme.success : LlanoPayTheme.error;
        iconData = isIncome ? Icons.arrow_downward : Icons.arrow_upward;
    }

    return CircleAvatar(
      radius: 20,
      backgroundColor: bgColor.withValues(alpha: 0.15),
      child: Icon(iconData, color: bgColor, size: 20),
    );
  }

  Widget _buildStatusChip(BuildContext context) {
    final Color chipColor;
    final String label;

    switch (status) {
      case 'pending':
        chipColor = LlanoPayTheme.secondaryGold;
        label = 'Pendiente';
        break;
      case 'failed':
        chipColor = LlanoPayTheme.error;
        label = 'Fallida';
        break;
      case 'cancelled':
        chipColor = LlanoPayTheme.textSecondary;
        label = 'Cancelada';
        break;
      default:
        chipColor = LlanoPayTheme.success;
        label = status;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: chipColor.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: chipColor,
              fontWeight: FontWeight.w600,
            ),
      ),
    );
  }

  String _formatAmount() {
    final prefix = amount >= 0 ? '+' : '';
    if (currency == 'LLO') {
      final formatter = NumberFormat.currency(
        locale: 'es_CO',
        symbol: '',
        decimalDigits: 4,
      );
      return '$prefix${formatter.format(amount)} LLO';
    }
    final formatter = NumberFormat.currency(
      locale: 'es_CO',
      symbol: '\$',
      decimalDigits: 0,
    );
    return '$prefix${formatter.format(amount)}';
  }

  String _formatDate() {
    try {
      final dateTime = DateTime.parse(date);
      final now = DateTime.now();
      final difference = now.difference(dateTime);

      if (difference.inMinutes < 1) {
        return 'Ahora mismo';
      } else if (difference.inMinutes < 60) {
        return 'hace ${difference.inMinutes} min';
      } else if (difference.inHours < 24) {
        final hours = difference.inHours;
        return 'hace $hours ${hours == 1 ? 'hora' : 'horas'}';
      } else if (difference.inDays < 7) {
        final days = difference.inDays;
        return 'hace $days ${days == 1 ? 'dia' : 'dias'}';
      } else {
        return DateFormat('MMM d, yyyy', 'es_CO').format(dateTime);
      }
    } catch (_) {
      return date;
    }
  }
}
