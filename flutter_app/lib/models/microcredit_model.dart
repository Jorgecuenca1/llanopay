/// User's credit profile / score for microcredit eligibility.
class CreditProfileModel {
  final int id;
  final int userId;
  final int creditScore;
  final double maxCreditAmount;
  final String riskLevel;
  final int totalLoans;
  final int activeLoans;
  final double totalRepaid;
  final bool isEligible;
  final DateTime? lastUpdated;

  const CreditProfileModel({
    required this.id,
    required this.userId,
    required this.creditScore,
    required this.maxCreditAmount,
    required this.riskLevel,
    this.totalLoans = 0,
    this.activeLoans = 0,
    this.totalRepaid = 0.0,
    this.isEligible = false,
    this.lastUpdated,
  });

  factory CreditProfileModel.fromJson(Map<String, dynamic> json) {
    return CreditProfileModel(
      id: json['id'] as int,
      userId: json['user_id'] as int? ?? json['user'] as int? ?? 0,
      creditScore: json['credit_score'] as int? ?? 0,
      maxCreditAmount: _toDouble(json['max_credit_amount']),
      riskLevel: json['risk_level'] as String? ?? 'unknown',
      totalLoans: json['total_loans'] as int? ?? 0,
      activeLoans: json['active_loans'] as int? ?? 0,
      totalRepaid: _toDouble(json['total_repaid']),
      isEligible: json['is_eligible'] as bool? ?? false,
      lastUpdated: json['last_updated'] != null
          ? DateTime.tryParse(json['last_updated'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'credit_score': creditScore,
      'max_credit_amount': maxCreditAmount,
      'risk_level': riskLevel,
      'total_loans': totalLoans,
      'active_loans': activeLoans,
      'total_repaid': totalRepaid,
      'is_eligible': isEligible,
      'last_updated': lastUpdated?.toIso8601String(),
    };
  }

  @override
  String toString() =>
      'CreditProfile(score: $creditScore, eligible: $isEligible)';
}

/// Microcredit product definition (loan type template).
class MicrocreditProductModel {
  final int id;
  final String name;
  final String? description;
  final double minAmount;
  final double maxAmount;
  final double interestRate;
  final int minTermDays;
  final int maxTermDays;
  final int minCreditScore;
  final bool isActive;

  const MicrocreditProductModel({
    required this.id,
    required this.name,
    this.description,
    required this.minAmount,
    required this.maxAmount,
    required this.interestRate,
    required this.minTermDays,
    required this.maxTermDays,
    this.minCreditScore = 0,
    this.isActive = true,
  });

  factory MicrocreditProductModel.fromJson(Map<String, dynamic> json) {
    return MicrocreditProductModel(
      id: json['id'] as int,
      name: json['name'] as String,
      description: json['description'] as String?,
      minAmount: _toDouble(json['min_amount']),
      maxAmount: _toDouble(json['max_amount']),
      interestRate: _toDouble(json['interest_rate']),
      minTermDays: json['min_term_days'] as int? ?? 30,
      maxTermDays: json['max_term_days'] as int? ?? 365,
      minCreditScore: json['min_credit_score'] as int? ?? 0,
      isActive: json['is_active'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'min_amount': minAmount,
      'max_amount': maxAmount,
      'interest_rate': interestRate,
      'min_term_days': minTermDays,
      'max_term_days': maxTermDays,
      'min_credit_score': minCreditScore,
      'is_active': isActive,
    };
  }

  @override
  String toString() =>
      'MicrocreditProduct(id: $id, name: $name, rate: $interestRate%)';
}

/// An active microcredit loan.
class MicrocreditModel {
  final int id;
  final int userId;
  final int productId;
  final String? productName;
  final double amount;
  final double interestRate;
  final int termDays;
  final double totalRepayment;
  final double amountPaid;
  final double amountPending;
  final String status;
  final DateTime requestedAt;
  final DateTime? approvedAt;
  final DateTime? disbursedAt;
  final DateTime? dueDate;

  const MicrocreditModel({
    required this.id,
    required this.userId,
    required this.productId,
    this.productName,
    required this.amount,
    required this.interestRate,
    required this.termDays,
    required this.totalRepayment,
    this.amountPaid = 0.0,
    this.amountPending = 0.0,
    required this.status,
    required this.requestedAt,
    this.approvedAt,
    this.disbursedAt,
    this.dueDate,
  });

  /// Progress ratio of repayment (0.0 to 1.0).
  double get repaymentProgress =>
      totalRepayment > 0 ? (amountPaid / totalRepayment).clamp(0.0, 1.0) : 0.0;

  /// Whether the loan is overdue.
  bool get isOverdue =>
      dueDate != null &&
      DateTime.now().isAfter(dueDate!) &&
      status != 'paid' &&
      status != 'closed';

  factory MicrocreditModel.fromJson(Map<String, dynamic> json) {
    return MicrocreditModel(
      id: json['id'] as int,
      userId: json['user_id'] as int? ?? json['user'] as int? ?? 0,
      productId: json['product_id'] as int? ?? json['product'] as int? ?? 0,
      productName: json['product_name'] as String?,
      amount: _toDouble(json['amount']),
      interestRate: _toDouble(json['interest_rate']),
      termDays: json['term_days'] as int? ?? 0,
      totalRepayment: _toDouble(json['total_repayment']),
      amountPaid: _toDouble(json['amount_paid']),
      amountPending: _toDouble(json['amount_pending']),
      status: json['status'] as String? ?? 'pending',
      requestedAt: DateTime.parse(json['requested_at'] as String),
      approvedAt: json['approved_at'] != null
          ? DateTime.tryParse(json['approved_at'] as String)
          : null,
      disbursedAt: json['disbursed_at'] != null
          ? DateTime.tryParse(json['disbursed_at'] as String)
          : null,
      dueDate: json['due_date'] != null
          ? DateTime.tryParse(json['due_date'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'product_id': productId,
      'product_name': productName,
      'amount': amount,
      'interest_rate': interestRate,
      'term_days': termDays,
      'total_repayment': totalRepayment,
      'amount_paid': amountPaid,
      'amount_pending': amountPending,
      'status': status,
      'requested_at': requestedAt.toIso8601String(),
      'approved_at': approvedAt?.toIso8601String(),
      'disbursed_at': disbursedAt?.toIso8601String(),
      'due_date': dueDate?.toIso8601String(),
    };
  }

  @override
  String toString() =>
      'Microcredit(id: $id, amount: $amount, status: $status)';
}

/// A single payment against a microcredit loan.
class MicrocreditPaymentModel {
  final int id;
  final int loanId;
  final double amount;
  final String currency;
  final String paymentMethod;
  final String? reference;
  final String status;
  final DateTime paidAt;

  const MicrocreditPaymentModel({
    required this.id,
    required this.loanId,
    required this.amount,
    required this.currency,
    required this.paymentMethod,
    this.reference,
    required this.status,
    required this.paidAt,
  });

  factory MicrocreditPaymentModel.fromJson(Map<String, dynamic> json) {
    return MicrocreditPaymentModel(
      id: json['id'] as int,
      loanId: json['loan_id'] as int? ?? json['loan'] as int? ?? 0,
      amount: _toDouble(json['amount']),
      currency: json['currency'] as String? ?? 'COP',
      paymentMethod: json['payment_method'] as String? ?? 'wallet',
      reference: json['reference'] as String?,
      status: json['status'] as String? ?? 'completed',
      paidAt: DateTime.parse(json['paid_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'loan_id': loanId,
      'amount': amount,
      'currency': currency,
      'payment_method': paymentMethod,
      'reference': reference,
      'status': status,
      'paid_at': paidAt.toIso8601String(),
    };
  }

  @override
  String toString() =>
      'MicrocreditPayment(id: $id, loan: $loanId, amount: $amount)';
}

// ── Helper ────────────────────────────────────────
double _toDouble(dynamic value) {
  if (value == null) return 0.0;
  if (value is double) return value;
  if (value is int) return value.toDouble();
  if (value is String) return double.tryParse(value) ?? 0.0;
  return 0.0;
}
