import 'package:flutter/material.dart';

import '../config/theme.dart';

/// Circular icon button with a label below, used for dashboard quick actions.
///
/// Typical actions: Enviar, Recibir, Crypto, Llanocoin.
class QuickActionButton extends StatelessWidget {
  /// Icon displayed inside the circular button.
  final IconData icon;

  /// Label displayed below the button.
  final String label;

  /// Background color for the circular button.
  /// Defaults to [LlanoPayTheme.primaryGreen].
  final Color? backgroundColor;

  /// Icon color. Defaults to [Colors.white].
  final Color? iconColor;

  /// Callback when the button is pressed.
  final VoidCallback? onTap;

  const QuickActionButton({
    super.key,
    required this.icon,
    required this.label,
    this.backgroundColor,
    this.iconColor,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final bgColor = backgroundColor ?? LlanoPayTheme.primaryGreen;
    final fgColor = iconColor ?? Colors.white;

    return GestureDetector(
      onTap: onTap,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: bgColor,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: bgColor.withValues(alpha: 0.3),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Icon(
              icon,
              color: fgColor,
              size: 26,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            label,
            style: Theme.of(context).textTheme.labelMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
            textAlign: TextAlign.center,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}
