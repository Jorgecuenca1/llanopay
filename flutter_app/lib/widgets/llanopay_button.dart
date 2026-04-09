import 'package:flutter/material.dart';

import '../config/theme.dart';

/// Branded button for LlanoPay.
///
/// Supports primary (filled green) and secondary (outlined green) styles,
/// a loading state with a progress indicator, and a full-width option.
class LlanoPayButton extends StatelessWidget {
  /// Button label text.
  final String text;

  /// Callback when the button is pressed.
  final VoidCallback? onPressed;

  /// Whether the button shows a loading indicator.
  final bool isLoading;

  /// Whether this is a secondary (outlined) button.
  final bool isSecondary;

  /// Whether the button stretches to full width.
  final bool fullWidth;

  /// Optional leading icon.
  final IconData? icon;

  const LlanoPayButton({
    super.key,
    required this.text,
    this.onPressed,
    this.isLoading = false,
    this.isSecondary = false,
    this.fullWidth = true,
    this.icon,
  });

  @override
  Widget build(BuildContext context) {
    final child = _buildChild(context);

    Widget button;
    if (isSecondary) {
      button = OutlinedButton(
        onPressed: isLoading ? null : onPressed,
        style: OutlinedButton.styleFrom(
          foregroundColor: LlanoPayTheme.primaryGreen,
          side: const BorderSide(
            color: LlanoPayTheme.primaryGreen,
            width: 1.5,
          ),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(LlanoPayTheme.buttonRadius),
          ),
        ),
        child: child,
      );
    } else {
      button = ElevatedButton(
        onPressed: isLoading ? null : onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: LlanoPayTheme.primaryGreen,
          foregroundColor: Colors.white,
          disabledBackgroundColor:
              LlanoPayTheme.primaryGreen.withValues(alpha: 0.6),
          disabledForegroundColor: Colors.white70,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(LlanoPayTheme.buttonRadius),
          ),
          elevation: 2,
        ),
        child: child,
      );
    }

    if (fullWidth) {
      return SizedBox(
        width: double.infinity,
        height: 50,
        child: button,
      );
    }

    return button;
  }

  Widget _buildChild(BuildContext context) {
    if (isLoading) {
      return SizedBox(
        width: 22,
        height: 22,
        child: CircularProgressIndicator(
          strokeWidth: 2.5,
          valueColor: AlwaysStoppedAnimation<Color>(
            isSecondary ? LlanoPayTheme.primaryGreen : Colors.white,
          ),
        ),
      );
    }

    if (icon != null) {
      return Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 20),
          const SizedBox(width: 8),
          Text(text),
        ],
      );
    }

    return Text(text);
  }
}
