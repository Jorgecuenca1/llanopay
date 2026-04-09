import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// LlanoPay visual identity inspired by Colombia's Llanos Orientales.
///
/// - Primary green (#2E7D32): the vast llano grasslands.
/// - Secondary gold (#F9A825): the legendary llano sunrise.
/// - Accent brown (#795548): the warm earth of the plains.
class LlanoPayTheme {
  LlanoPayTheme._();

  // ── Brand Colors ──────────────────────────────
  static const Color primaryGreen = Color(0xFF2E7D32);
  static const Color primaryGreenLight = Color(0xFF60AD5E);
  static const Color primaryGreenDark = Color(0xFF005005);

  static const Color secondaryGold = Color(0xFFF9A825);
  static const Color secondaryGoldLight = Color(0xFFFFD95A);
  static const Color secondaryGoldDark = Color(0xFFC17900);

  static const Color accentBrown = Color(0xFF795548);
  static const Color accentBrownLight = Color(0xFFA98274);
  static const Color accentBrownDark = Color(0xFF4B2C20);

  // ── Neutral Colors ────────────────────────────
  static const Color backgroundLight = Color(0xFFF5F5F0);
  static const Color surfaceWhite = Color(0xFFFFFFFF);
  static const Color textPrimary = Color(0xFF212121);
  static const Color textSecondary = Color(0xFF757575);
  static const Color divider = Color(0xFFE0E0E0);
  static const Color error = Color(0xFFD32F2F);
  static const Color success = Color(0xFF388E3C);

  // ── Radii ─────────────────────────────────────
  static const double cardRadius = 16.0;
  static const double buttonRadius = 12.0;
  static const double inputRadius = 12.0;

  // ── Light Theme ───────────────────────────────
  static ThemeData get lightTheme {
    final textTheme = _buildTextTheme();

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      colorScheme: const ColorScheme.light(
        primary: primaryGreen,
        onPrimary: Colors.white,
        primaryContainer: primaryGreenLight,
        onPrimaryContainer: primaryGreenDark,
        secondary: secondaryGold,
        onSecondary: Colors.black,
        secondaryContainer: secondaryGoldLight,
        onSecondaryContainer: secondaryGoldDark,
        tertiary: accentBrown,
        onTertiary: Colors.white,
        tertiaryContainer: accentBrownLight,
        onTertiaryContainer: accentBrownDark,
        error: error,
        onError: Colors.white,
        surface: surfaceWhite,
        onSurface: textPrimary,
        surfaceContainerHighest: backgroundLight,
        onSurfaceVariant: textSecondary,
        outline: divider,
      ),
      scaffoldBackgroundColor: backgroundLight,
      textTheme: textTheme,
      appBarTheme: AppBarTheme(
        backgroundColor: primaryGreen,
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: GoogleFonts.montserrat(
          fontSize: 18,
          fontWeight: FontWeight.w600,
          color: Colors.white,
        ),
      ),
      cardTheme: CardThemeData(
        elevation: 2,
        shadowColor: Colors.black12,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(cardRadius),
        ),
        clipBehavior: Clip.antiAlias,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryGreen,
          foregroundColor: Colors.white,
          elevation: 2,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(buttonRadius),
          ),
          textStyle: GoogleFonts.montserrat(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: primaryGreen,
          side: const BorderSide(color: primaryGreen, width: 1.5),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(buttonRadius),
          ),
          textStyle: GoogleFonts.montserrat(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: primaryGreen,
          textStyle: GoogleFonts.nunito(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surfaceWhite,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(inputRadius),
          borderSide: const BorderSide(color: divider),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(inputRadius),
          borderSide: const BorderSide(color: divider),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(inputRadius),
          borderSide: const BorderSide(color: primaryGreen, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(inputRadius),
          borderSide: const BorderSide(color: error),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(inputRadius),
          borderSide: const BorderSide(color: error, width: 2),
        ),
        labelStyle: GoogleFonts.nunito(color: textSecondary),
        hintStyle: GoogleFonts.nunito(color: textSecondary),
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: surfaceWhite,
        selectedItemColor: primaryGreen,
        unselectedItemColor: textSecondary,
        type: BottomNavigationBarType.fixed,
        elevation: 8,
      ),
      floatingActionButtonTheme: const FloatingActionButtonThemeData(
        backgroundColor: secondaryGold,
        foregroundColor: Colors.black,
      ),
      chipTheme: ChipThemeData(
        backgroundColor: backgroundLight,
        selectedColor: primaryGreenLight,
        labelStyle: GoogleFonts.nunito(fontSize: 13),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
      ),
      dividerTheme: const DividerThemeData(
        color: divider,
        thickness: 1,
        space: 1,
      ),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(buttonRadius),
        ),
      ),
    );
  }

  // ── Text Theme ────────────────────────────────
  static TextTheme _buildTextTheme() {
    return TextTheme(
      // Headings — Montserrat
      displayLarge: GoogleFonts.montserrat(
        fontSize: 32,
        fontWeight: FontWeight.w700,
        color: textPrimary,
      ),
      displayMedium: GoogleFonts.montserrat(
        fontSize: 28,
        fontWeight: FontWeight.w700,
        color: textPrimary,
      ),
      displaySmall: GoogleFonts.montserrat(
        fontSize: 24,
        fontWeight: FontWeight.w600,
        color: textPrimary,
      ),
      headlineLarge: GoogleFonts.montserrat(
        fontSize: 22,
        fontWeight: FontWeight.w600,
        color: textPrimary,
      ),
      headlineMedium: GoogleFonts.montserrat(
        fontSize: 20,
        fontWeight: FontWeight.w600,
        color: textPrimary,
      ),
      headlineSmall: GoogleFonts.montserrat(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: textPrimary,
      ),
      titleLarge: GoogleFonts.montserrat(
        fontSize: 16,
        fontWeight: FontWeight.w600,
        color: textPrimary,
      ),
      titleMedium: GoogleFonts.montserrat(
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: textPrimary,
      ),
      titleSmall: GoogleFonts.montserrat(
        fontSize: 12,
        fontWeight: FontWeight.w600,
        color: textSecondary,
      ),
      // Body — Nunito
      bodyLarge: GoogleFonts.nunito(
        fontSize: 16,
        fontWeight: FontWeight.w400,
        color: textPrimary,
      ),
      bodyMedium: GoogleFonts.nunito(
        fontSize: 14,
        fontWeight: FontWeight.w400,
        color: textPrimary,
      ),
      bodySmall: GoogleFonts.nunito(
        fontSize: 12,
        fontWeight: FontWeight.w400,
        color: textSecondary,
      ),
      // Labels — Nunito
      labelLarge: GoogleFonts.nunito(
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: textPrimary,
      ),
      labelMedium: GoogleFonts.nunito(
        fontSize: 12,
        fontWeight: FontWeight.w500,
        color: textSecondary,
      ),
      labelSmall: GoogleFonts.nunito(
        fontSize: 10,
        fontWeight: FontWeight.w500,
        color: textSecondary,
      ),
    );
  }
}
