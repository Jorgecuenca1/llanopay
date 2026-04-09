import 'package:flutter/material.dart';

import '../config/theme.dart';

/// Centered empty state widget displayed when lists or screens have no data.
///
/// Shows an icon placeholder, a title, an optional subtitle,
/// and an optional action button.
class EmptyState extends StatelessWidget {
  /// Icon to display as the illustration placeholder.
  final IconData icon;

  /// Main title text.
  final String title;

  /// Optional subtitle / description.
  final String? subtitle;

  /// Optional action button label.
  final String? actionLabel;

  /// Callback for the action button.
  final VoidCallback? onAction;

  /// Icon size. Defaults to 80.
  final double iconSize;

  const EmptyState({
    super.key,
    required this.icon,
    required this.title,
    this.subtitle,
    this.actionLabel,
    this.onAction,
    this.iconSize = 80,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 48),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Illustration placeholder
            Container(
              width: iconSize + 40,
              height: iconSize + 40,
              decoration: BoxDecoration(
                color: LlanoPayTheme.primaryGreen.withValues(alpha: 0.08),
                shape: BoxShape.circle,
              ),
              child: Icon(
                icon,
                size: iconSize,
                color: LlanoPayTheme.primaryGreen.withValues(alpha: 0.4),
              ),
            ),
            const SizedBox(height: 24),

            // Title
            Text(
              title,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
              textAlign: TextAlign.center,
            ),

            // Subtitle
            if (subtitle != null) ...[
              const SizedBox(height: 8),
              Text(
                subtitle!,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: LlanoPayTheme.textSecondary,
                    ),
                textAlign: TextAlign.center,
              ),
            ],

            // Action button
            if (actionLabel != null && onAction != null) ...[
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: onAction,
                style: ElevatedButton.styleFrom(
                  backgroundColor: LlanoPayTheme.primaryGreen,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 32,
                    vertical: 14,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius:
                        BorderRadius.circular(LlanoPayTheme.buttonRadius),
                  ),
                ),
                child: Text(actionLabel!),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
