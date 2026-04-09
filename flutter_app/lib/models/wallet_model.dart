/// Wallet model containing COP and LLO balances.
class WalletModel {
  final int id;
  final double balanceCop;
  final double balanceLlo;
  final bool isActive;
  final DateTime createdAt;

  const WalletModel({
    required this.id,
    required this.balanceCop,
    required this.balanceLlo,
    required this.isActive,
    required this.createdAt,
  });

  factory WalletModel.fromJson(Map<String, dynamic> json) {
    return WalletModel(
      id: json['id'] as int,
      balanceCop: _toDouble(json['balance_cop']),
      balanceLlo: _toDouble(json['balance_llo']),
      isActive: json['is_active'] as bool? ?? true,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'balance_cop': balanceCop,
      'balance_llo': balanceLlo,
      'is_active': isActive,
      'created_at': createdAt.toIso8601String(),
    };
  }

  @override
  String toString() =>
      'WalletModel(id: $id, COP: $balanceCop, LLO: $balanceLlo)';
}

/// A single transaction within the wallet.
class TransactionModel {
  final int id;
  final String transactionType;
  final double amount;
  final String currency;
  final double balanceAfter;
  final String reference;
  final String? description;
  final String status;
  final DateTime createdAt;

  const TransactionModel({
    required this.id,
    required this.transactionType,
    required this.amount,
    required this.currency,
    required this.balanceAfter,
    required this.reference,
    this.description,
    required this.status,
    required this.createdAt,
  });

  factory TransactionModel.fromJson(Map<String, dynamic> json) {
    return TransactionModel(
      id: json['id'] as int,
      transactionType: json['transaction_type'] as String,
      amount: _toDouble(json['amount']),
      currency: json['currency'] as String? ?? 'COP',
      balanceAfter: _toDouble(json['balance_after']),
      reference: json['reference'] as String? ?? '',
      description: json['description'] as String?,
      status: json['status'] as String? ?? 'completed',
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'transaction_type': transactionType,
      'amount': amount,
      'currency': currency,
      'balance_after': balanceAfter,
      'reference': reference,
      'description': description,
      'status': status,
      'created_at': createdAt.toIso8601String(),
    };
  }

  /// Whether the transaction represents money coming in.
  bool get isCredit =>
      transactionType == 'deposit' ||
      transactionType == 'transfer_in' ||
      transactionType == 'cashback';

  @override
  String toString() =>
      'TransactionModel(id: $id, type: $transactionType, amount: $amount $currency)';
}

/// Aggregated balance summary.
class BalanceSummary {
  final double balanceCop;
  final double balanceLlo;
  final double lloCopEquivalent;

  const BalanceSummary({
    required this.balanceCop,
    required this.balanceLlo,
    required this.lloCopEquivalent,
  });

  /// Total balance in COP including LLO equivalent.
  double get totalCop => balanceCop + lloCopEquivalent;

  factory BalanceSummary.fromJson(Map<String, dynamic> json) {
    return BalanceSummary(
      balanceCop: _toDouble(json['balance_cop']),
      balanceLlo: _toDouble(json['balance_llo']),
      lloCopEquivalent: _toDouble(json['llo_cop_equivalent']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'balance_cop': balanceCop,
      'balance_llo': balanceLlo,
      'llo_cop_equivalent': lloCopEquivalent,
    };
  }
}

// ── Helper ────────────────────────────────────────
double _toDouble(dynamic value) {
  if (value == null) return 0.0;
  if (value is double) return value;
  if (value is int) return value.toDouble();
  if (value is String) return double.tryParse(value) ?? 0.0;
  return 0.0;
}
