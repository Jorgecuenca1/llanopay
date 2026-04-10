/// API configuration for LlanoPay backend services.
class ApiConfig {
  ApiConfig._();

  /// Base URL for the API. Override via environment or build config.
  static String baseUrl = 'https://nova.corpofuturo.org/api/v1';

  /// WebSocket URL for real-time notifications.
  static String get wsUrl {
    final uri = Uri.parse(baseUrl);
    final wsScheme = uri.scheme == 'https' ? 'wss' : 'ws';
    return '$wsScheme://${uri.host}:${uri.port}';
  }

  // ──────────────────────────────────────────────
  // Auth Service
  // ──────────────────────────────────────────────
  static const String authRegister = '/auth/register/';
  static const String authLogin = '/auth/login/';
  static const String authRefreshToken = '/auth/token/refresh/';
  static const String authVerifyOTP = '/auth/verify-otp/';
  static const String authRequestOTP = '/auth/request-otp/';
  static const String authProfile = '/auth/profile/';
  static const String authChangePassword = '/auth/change-password/';
  static const String authLogout = '/auth/logout/';

  // ──────────────────────────────────────────────
  // Wallet Service
  // ──────────────────────────────────────────────
  static const String walletInfo = '/wallet/';
  static const String walletBalance = '/wallet/balance/';
  static const String walletTransactions = '/wallet/transactions/';
  static const String walletTopUp = '/wallet/top-up/';
  static const String walletWithdraw = '/wallet/withdraw/';

  // ──────────────────────────────────────────────
  // Crypto Service (Llanocoin)
  // ──────────────────────────────────────────────
  static const String cryptoDeposit = '/crypto/deposit/';
  static const String cryptoWithdraw = '/crypto/withdraw/';
  static const String cryptoExchangeRate = '/crypto/exchange-rate/';
  static const String cryptoBuyLlo = '/crypto/buy-llo/';
  static const String cryptoSellLlo = '/crypto/sell-llo/';
  static const String cryptoTransactions = '/crypto/transactions/';
  static const String cryptoLlanocoinInfo = '/crypto/llanocoin/';

  // ──────────────────────────────────────────────
  // Transfer Service
  // ──────────────────────────────────────────────
  static const String transferSend = '/transfers/send/';
  static const String transferHistory = '/transfers/history/';
  static const String transferDetail = '/transfers/'; // + {id}/
  static const String transferContacts = '/transfers/contacts/';
  static const String transferCalculateFee = '/transfers/calculate-fee/';

  // ──────────────────────────────────────────────
  // Marketplace Service
  // ──────────────────────────────────────────────
  static const String marketplaceMerchants = '/marketplace/merchants/';
  static const String marketplaceCategories = '/marketplace/categories/';
  static const String marketplacePromotions = '/marketplace/promotions/';
  static const String marketplaceReviews = '/marketplace/reviews/';
  static const String marketplaceSearch = '/marketplace/search/';
  static const String marketplaceNearby = '/marketplace/nearby/';

  // ──────────────────────────────────────────────
  // Microcredit Service
  // ──────────────────────────────────────────────
  static const String microcreditProfile = '/microcredit/profile/';
  static const String microcreditProducts = '/microcredit/products/';
  static const String microcreditRequest = '/microcredit/request/';
  static const String microcreditLoans = '/microcredit/loans/';
  static const String microcreditPayments = '/microcredit/payments/';
  static const String microcreditSimulate = '/microcredit/simulate/';

  // ──────────────────────────────────────────────
  // Notifications Service
  // ──────────────────────────────────────────────
  static const String notifications = '/notifications/';
  static const String notificationsMarkRead = '/notifications/mark-read/';
  static const String notificationsSettings = '/notifications/settings/';
  static const String notificationsWebSocket = '/ws/notifications/';
}
