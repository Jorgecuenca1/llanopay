/// Crypto deposit (COP -> wallet or external source -> LLO).
class CryptoDepositModel {
  final int id;
  final double amount;
  final String currency;
  final String depositMethod;
  final String? externalReference;
  final String status;
  final DateTime createdAt;
  final DateTime? confirmedAt;

  const CryptoDepositModel({
    required this.id,
    required this.amount,
    required this.currency,
    required this.depositMethod,
    this.externalReference,
    required this.status,
    required this.createdAt,
    this.confirmedAt,
  });

  factory CryptoDepositModel.fromJson(Map<String, dynamic> json) {
    return CryptoDepositModel(
      id: json['id'] as int,
      amount: _toDouble(json['amount']),
      currency: json['currency'] as String? ?? 'COP',
      depositMethod: json['deposit_method'] as String? ?? 'bank_transfer',
      externalReference: json['external_reference'] as String?,
      status: json['status'] as String? ?? 'pending',
      createdAt: DateTime.parse(json['created_at'] as String),
      confirmedAt: json['confirmed_at'] != null
          ? DateTime.tryParse(json['confirmed_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'amount': amount,
      'currency': currency,
      'deposit_method': depositMethod,
      'external_reference': externalReference,
      'status': status,
      'created_at': createdAt.toIso8601String(),
      'confirmed_at': confirmedAt?.toIso8601String(),
    };
  }

  @override
  String toString() =>
      'CryptoDepositModel(id: $id, amount: $amount $currency, $status)';
}

/// Exchange rate between COP and LLO.
class ExchangeRateModel {
  final double buyRate;
  final double sellRate;
  final double midRate;
  final String baseCurrency;
  final String quoteCurrency;
  final DateTime updatedAt;

  const ExchangeRateModel({
    required this.buyRate,
    required this.sellRate,
    required this.midRate,
    required this.baseCurrency,
    required this.quoteCurrency,
    required this.updatedAt,
  });

  factory ExchangeRateModel.fromJson(Map<String, dynamic> json) {
    return ExchangeRateModel(
      buyRate: _toDouble(json['buy_rate']),
      sellRate: _toDouble(json['sell_rate']),
      midRate: _toDouble(json['mid_rate']),
      baseCurrency: json['base_currency'] as String? ?? 'COP',
      quoteCurrency: json['quote_currency'] as String? ?? 'LLO',
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'buy_rate': buyRate,
      'sell_rate': sellRate,
      'mid_rate': midRate,
      'base_currency': baseCurrency,
      'quote_currency': quoteCurrency,
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  @override
  String toString() =>
      'ExchangeRate(buy: $buyRate, sell: $sellRate, $baseCurrency/$quoteCurrency)';
}

/// A Llanocoin (LLO) transaction.
class LlanocoinTransactionModel {
  final int id;
  final String transactionType;
  final double amountLlo;
  final double amountCop;
  final double exchangeRate;
  final String status;
  final String? reference;
  final DateTime createdAt;

  const LlanocoinTransactionModel({
    required this.id,
    required this.transactionType,
    required this.amountLlo,
    required this.amountCop,
    required this.exchangeRate,
    required this.status,
    this.reference,
    required this.createdAt,
  });

  factory LlanocoinTransactionModel.fromJson(Map<String, dynamic> json) {
    return LlanocoinTransactionModel(
      id: json['id'] as int,
      transactionType: json['transaction_type'] as String,
      amountLlo: _toDouble(json['amount_llo']),
      amountCop: _toDouble(json['amount_cop']),
      exchangeRate: _toDouble(json['exchange_rate']),
      status: json['status'] as String? ?? 'completed',
      reference: json['reference'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'transaction_type': transactionType,
      'amount_llo': amountLlo,
      'amount_cop': amountCop,
      'exchange_rate': exchangeRate,
      'status': status,
      'reference': reference,
      'created_at': createdAt.toIso8601String(),
    };
  }

  @override
  String toString() =>
      'LlanocoinTx(id: $id, type: $transactionType, LLO: $amountLlo)';
}

// ── Helper ────────────────────────────────────────
double _toDouble(dynamic value) {
  if (value == null) return 0.0;
  if (value is double) return value;
  if (value is int) return value.toDouble();
  if (value is String) return double.tryParse(value) ?? 0.0;
  return 0.0;
}
