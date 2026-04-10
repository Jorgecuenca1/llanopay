/// API configuration for SuperNova backend services.
class ApiConfig {
  ApiConfig._();

  /// Base URL for the API.
  static String baseUrl = 'https://nova.jorgecuenca.com/api/v1';

  /// WebSocket URL for real-time notifications.
  static String get wsUrl {
    final uri = Uri.parse(baseUrl);
    final wsScheme = uri.scheme == 'https' ? 'wss' : 'ws';
    final port = uri.hasPort ? ':${uri.port}' : '';
    return '$wsScheme://${uri.host}$port';
  }

  // ── Auth ──
  static const String authRegister = '/auth/register/';
  static const String authLogin = '/auth/login/';
  static const String authRefreshToken = '/auth/token/refresh/';
  static const String authVerifyOTP = '/auth/verify-otp/';
  static const String authRequestOTP = '/auth/request-otp/';
  static const String authProfile = '/auth/profile/';
  static const String authChangePassword = '/auth/change-password/';
  static const String authLogout = '/auth/logout/';

  // ── Wallet ──
  static const String walletInfo = '/wallet/';
  static const String walletBalance = '/wallet/balance/';
  static const String walletTransactions = '/wallet/transactions/';

  // ── Crypto ──
  static const String cryptoDeposits = '/crypto/deposits/';
  static const String cryptoDepositsList = '/crypto/deposits/list/';
  static const String cryptoWithdrawals = '/crypto/withdrawals/';
  static const String cryptoRates = '/crypto/rates/';
  static const String cryptoBuyLlo = '/crypto/llanocoin/buy/';
  static const String cryptoSellLlo = '/crypto/llanocoin/sell/';
  static const String cryptoLloTransactions = '/crypto/llanocoin/transactions/';

  // Aliases for backwards compat
  static const String cryptoDeposit = cryptoDeposits;
  static const String cryptoWithdraw = cryptoWithdrawals;
  static const String cryptoExchangeRate = cryptoRates;
  static const String cryptoTransactions = cryptoLloTransactions;
  static const String cryptoLlanocoinInfo = cryptoLloTransactions;

  // ── Transfers ──
  static const String transferSend = '/transfers/send/';
  static const String transferConfirm = '/transfers/confirm/';
  static const String transferList = '/transfers/list/';
  static const String transferLimits = '/transfers/limits/';
  static String transferDetail(String id) => '/transfers/$id/';

  // Aliases for backwards compat
  static const String transferHistory = transferList;
  static const String transferContacts = transferList;
  static const String transferCalculateFee = transferLimits;

  // ── Marketplace ──
  static const String marketplaceMerchants = '/marketplace/merchants/';
  static const String marketplaceCategories = '/marketplace/categories/';
  static const String marketplaceNearby = '/marketplace/merchants/nearby/';
  static const String marketplacePayments = '/marketplace/payments/';
  static const String marketplaceReviews = '/marketplace/reviews/';
  static const String marketplacePromotions = '/marketplace/promotions/';
  static const String marketplaceSearch = marketplaceMerchants;

  // ── Microcredit ──
  static const String microcreditProfile = '/microcredit/profile/';
  static const String microcreditProducts = '/microcredit/products/';
  static const String microcreditRequest = '/microcredit/request/';
  static const String microcreditLoans = '/microcredit/loans/';
  static const String microcreditPayments = '/microcredit/pay/';
  static const String microcreditSimulate = '/microcredit/profile/';

  // ── Notifications ──
  static const String notifications = '/notifications/';
  static const String notificationsMarkRead = '/notifications/mark-read/';
  static const String notificationsMarkAllRead = '/notifications/mark-all-read/';
  static const String notificationsUnreadCount = '/notifications/unread-count/';
  static const String notificationsDeviceToken = '/notifications/device-token/';
  static const String notificationsSettings = notificationsDeviceToken;
  static const String notificationsWebSocket = '/ws/notifications/';
}
