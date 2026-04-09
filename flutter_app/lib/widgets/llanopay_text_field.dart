import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../config/theme.dart';

/// Styled text field for LlanoPay forms.
///
/// Supports rounded borders, prefix icons, error text, and built-in
/// formatters for phone numbers and COP currency amounts.
class LlanoPayTextField extends StatelessWidget {
  /// Text editing controller.
  final TextEditingController? controller;

  /// Label text displayed above the field when focused.
  final String? label;

  /// Hint text displayed when the field is empty.
  final String? hint;

  /// Prefix icon displayed at the start of the field.
  final IconData? prefixIcon;

  /// Suffix widget (e.g., visibility toggle).
  final Widget? suffix;

  /// Error text displayed below the field.
  final String? errorText;

  /// Whether the text is obscured (for passwords).
  final bool obscureText;

  /// Keyboard type.
  final TextInputType? keyboardType;

  /// Whether to format as a Colombian phone number.
  final bool isPhoneNumber;

  /// Whether to format as a COP currency amount with thousands separator.
  final bool isCurrency;

  /// Maximum number of lines.
  final int maxLines;

  /// Whether the field is enabled.
  final bool enabled;

  /// Callback on text change.
  final ValueChanged<String>? onChanged;

  /// Callback on field submission.
  final ValueChanged<String>? onSubmitted;

  /// Focus node.
  final FocusNode? focusNode;

  /// Text input action.
  final TextInputAction? textInputAction;

  const LlanoPayTextField({
    super.key,
    this.controller,
    this.label,
    this.hint,
    this.prefixIcon,
    this.suffix,
    this.errorText,
    this.obscureText = false,
    this.keyboardType,
    this.isPhoneNumber = false,
    this.isCurrency = false,
    this.maxLines = 1,
    this.enabled = true,
    this.onChanged,
    this.onSubmitted,
    this.focusNode,
    this.textInputAction,
  });

  @override
  Widget build(BuildContext context) {
    final inputFormatters = <TextInputFormatter>[];

    TextInputType? effectiveKeyboardType = keyboardType;

    if (isPhoneNumber) {
      effectiveKeyboardType = TextInputType.phone;
      inputFormatters.addAll([
        FilteringTextInputFormatter.digitsOnly,
        LengthLimitingTextInputFormatter(10),
        _PhoneNumberFormatter(),
      ]);
    } else if (isCurrency) {
      effectiveKeyboardType = TextInputType.number;
      inputFormatters.addAll([
        FilteringTextInputFormatter.digitsOnly,
        _CopCurrencyFormatter(),
      ]);
    }

    return TextField(
      controller: controller,
      focusNode: focusNode,
      obscureText: obscureText,
      keyboardType: effectiveKeyboardType,
      textInputAction: textInputAction,
      maxLines: maxLines,
      enabled: enabled,
      inputFormatters: inputFormatters,
      onChanged: onChanged,
      onSubmitted: onSubmitted,
      style: Theme.of(context).textTheme.bodyLarge,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        errorText: errorText,
        prefixIcon: prefixIcon != null
            ? Icon(prefixIcon, color: LlanoPayTheme.textSecondary)
            : null,
        suffixIcon: suffix,
        filled: true,
        fillColor: enabled
            ? LlanoPayTheme.surfaceWhite
            : LlanoPayTheme.backgroundLight,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(LlanoPayTheme.inputRadius),
          borderSide: const BorderSide(color: LlanoPayTheme.divider),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(LlanoPayTheme.inputRadius),
          borderSide: const BorderSide(color: LlanoPayTheme.divider),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(LlanoPayTheme.inputRadius),
          borderSide: const BorderSide(
            color: LlanoPayTheme.primaryGreen,
            width: 2,
          ),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(LlanoPayTheme.inputRadius),
          borderSide: const BorderSide(color: LlanoPayTheme.error),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(LlanoPayTheme.inputRadius),
          borderSide: const BorderSide(
            color: LlanoPayTheme.error,
            width: 2,
          ),
        ),
      ),
    );
  }
}

/// Formats a phone number as 3XX XXX XXXX (Colombian mobile format).
class _PhoneNumberFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    final digits = newValue.text.replaceAll(RegExp(r'\D'), '');
    final buffer = StringBuffer();

    for (int i = 0; i < digits.length; i++) {
      if (i == 3 || i == 6) {
        buffer.write(' ');
      }
      buffer.write(digits[i]);
    }

    final formatted = buffer.toString();
    return TextEditingValue(
      text: formatted,
      selection: TextSelection.collapsed(offset: formatted.length),
    );
  }
}

/// Formats a number with COP-style thousands separators (dots).
class _CopCurrencyFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    final digits = newValue.text.replaceAll(RegExp(r'\D'), '');
    if (digits.isEmpty) {
      return const TextEditingValue(
        text: '',
        selection: TextSelection.collapsed(offset: 0),
      );
    }

    final number = int.parse(digits);
    final formatted = _formatWithDots(number);

    return TextEditingValue(
      text: formatted,
      selection: TextSelection.collapsed(offset: formatted.length),
    );
  }

  String _formatWithDots(int number) {
    final str = number.toString();
    final buffer = StringBuffer();
    final remainder = str.length % 3;

    for (int i = 0; i < str.length; i++) {
      if (i > 0 && (i - remainder) % 3 == 0 && remainder != 0 ||
          i > 0 && i % 3 == 0 && remainder == 0) {
        buffer.write('.');
      }
      buffer.write(str[i]);
    }

    return buffer.toString();
  }
}
