import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../services/storage_service.dart';

// ── Screen placeholder imports ──────────────────
// These will be replaced with real screen imports as they are built.
import '../screens/splash_screen.dart';
import '../screens/auth/login_screen.dart';
import '../screens/auth/register_screen.dart';
import '../screens/auth/verify_otp_screen.dart';
import '../screens/home/home_screen.dart';
import '../screens/home/home_tab.dart';
import '../screens/wallet/wallet_tab.dart';
import '../screens/transfer/transfer_tab.dart';
import '../screens/marketplace/marketplace_tab.dart';
import '../screens/profile/profile_tab.dart';
import '../screens/wallet/transaction_list_screen.dart';
import '../screens/crypto/crypto_deposit_screen.dart';
import '../screens/crypto/llanocoin_screen.dart';
import '../screens/transfer/send_transfer_screen.dart';
import '../screens/transfer/confirm_transfer_screen.dart';
import '../screens/marketplace/merchant_detail_screen.dart';
import '../screens/microcredit/microcredit_screen.dart';
import '../screens/microcredit/microcredit_request_screen.dart';
import '../screens/notifications/notifications_screen.dart';
import '../screens/profile/kyc_screen.dart';

/// Application router configuration.
class AppRouter {
  AppRouter._();

  static final _rootNavigatorKey = GlobalKey<NavigatorState>();
  static final _shellNavigatorKey = GlobalKey<NavigatorState>();

  static final StorageService _storageService = StorageService();

  static final GoRouter router = GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/splash',
    debugLogDiagnostics: true,
    redirect: _authRedirect,
    routes: [
      // ── Splash ───────────────────────────────
      GoRoute(
        path: '/splash',
        name: 'splash',
        builder: (context, state) => const SplashScreen(),
      ),

      // ── Auth routes ──────────────────────────
      GoRoute(
        path: '/login',
        name: 'login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/register',
        name: 'register',
        builder: (context, state) => const RegisterScreen(),
      ),
      GoRoute(
        path: '/verify-otp',
        name: 'verify-otp',
        builder: (context, state) {
          final extra = state.extra as Map<String, dynamic>? ?? {};
          return VerifyOTPScreen(
            phone: extra['phone'] as String? ?? '',
            purpose: extra['purpose'] as String? ?? 'registration',
          );
        },
      ),

      // ── Main app (ShellRoute with BottomNav) ─
      ShellRoute(
        navigatorKey: _shellNavigatorKey,
        builder: (context, state, child) => HomeScreen(child: child),
        routes: [
          GoRoute(
            path: '/home',
            name: 'home',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: HomeTab(),
            ),
          ),
          GoRoute(
            path: '/wallet',
            name: 'wallet',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: WalletTab(),
            ),
          ),
          GoRoute(
            path: '/transfer',
            name: 'transfer',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: TransferTab(),
            ),
          ),
          GoRoute(
            path: '/marketplace',
            name: 'marketplace',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: MarketplaceTab(),
            ),
          ),
          GoRoute(
            path: '/profile',
            name: 'profile',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: ProfileTab(),
            ),
          ),
        ],
      ),

      // ── Wallet detail routes ─────────────────
      GoRoute(
        path: '/wallet/transactions',
        name: 'wallet-transactions',
        builder: (context, state) => const TransactionListScreen(),
      ),

      // ── Crypto routes ────────────────────────
      GoRoute(
        path: '/crypto/deposit',
        name: 'crypto-deposit',
        builder: (context, state) => const CryptoDepositScreen(),
      ),
      GoRoute(
        path: '/crypto/llanocoin',
        name: 'crypto-llanocoin',
        builder: (context, state) => const LlanocoinScreen(),
      ),

      // ── Transfer detail routes ───────────────
      GoRoute(
        path: '/transfer/send',
        name: 'transfer-send',
        builder: (context, state) => const SendTransferScreen(),
      ),
      GoRoute(
        path: '/transfer/confirm',
        name: 'transfer-confirm',
        builder: (context, state) {
          final extra = state.extra as Map<String, dynamic>? ?? {};
          return ConfirmTransferScreen(transferData: extra);
        },
      ),

      // ── Marketplace detail routes ────────────
      GoRoute(
        path: '/marketplace/:slug',
        name: 'merchant-detail',
        builder: (context, state) {
          final slug = state.pathParameters['slug']!;
          return MerchantDetailScreen(slug: slug);
        },
      ),

      // ── Microcredit routes ───────────────────
      GoRoute(
        path: '/microcredit',
        name: 'microcredit',
        builder: (context, state) => const MicrocreditScreen(),
      ),
      GoRoute(
        path: '/microcredit/request',
        name: 'microcredit-request',
        builder: (context, state) => const MicrocreditRequestScreen(),
      ),

      // ── Notifications ────────────────────────
      GoRoute(
        path: '/notifications',
        name: 'notifications',
        builder: (context, state) => const NotificationsScreen(),
      ),

      // ── Profile sub-routes ───────────────────
      GoRoute(
        path: '/profile/kyc',
        name: 'profile-kyc',
        builder: (context, state) => const KYCScreen(),
      ),
    ],
  );

  /// Redirect unauthenticated users to login.
  static Future<String?> _authRedirect(
    BuildContext context,
    GoRouterState state,
  ) async {
    final isLoggedIn = await _storageService.isLoggedIn();
    final currentPath = state.matchedLocation;

    // Public routes that don't require authentication.
    const publicPaths = {'/splash', '/login', '/register', '/verify-otp'};
    final isPublicRoute = publicPaths.contains(currentPath);

    if (!isLoggedIn && !isPublicRoute) {
      return '/login';
    }

    if (isLoggedIn && (currentPath == '/login' || currentPath == '/register')) {
      return '/home';
    }

    return null;
  }
}
