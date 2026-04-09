/// Peer-to-peer transfer between wallets.
class TransferModel {
  final int id;
  final int sender;
  final int receiver;
  final double amount;
  final String currency;
  final double commissionAmount;
  final String? description;
  final String reference;
  final String status;
  final DateTime createdAt;

  /// Optional expanded sender/receiver info returned by the API.
  final String? senderName;
  final String? senderPhone;
  final String? receiverName;
  final String? receiverPhone;

  const TransferModel({
    required this.id,
    required this.sender,
    required this.receiver,
    required this.amount,
    required this.currency,
    required this.commissionAmount,
    this.description,
    required this.reference,
    required this.status,
    required this.createdAt,
    this.senderName,
    this.senderPhone,
    this.receiverName,
    this.receiverPhone,
  });

  /// Net amount the receiver gets after commission.
  double get netAmount => amount - commissionAmount;

  factory TransferModel.fromJson(Map<String, dynamic> json) {
    return TransferModel(
      id: json['id'] as int,
      sender: json['sender'] is int
          ? json['sender'] as int
          : (json['sender'] as Map<String, dynamic>)['id'] as int,
      receiver: json['receiver'] is int
          ? json['receiver'] as int
          : (json['receiver'] as Map<String, dynamic>)['id'] as int,
      amount: _toDouble(json['amount']),
      currency: json['currency'] as String? ?? 'COP',
      commissionAmount: _toDouble(json['commission_amount']),
      description: json['description'] as String?,
      reference: json['reference'] as String? ?? '',
      status: json['status'] as String? ?? 'completed',
      createdAt: DateTime.parse(json['created_at'] as String),
      senderName: _extractName(json['sender']),
      senderPhone: _extractPhone(json['sender']),
      receiverName: _extractName(json['receiver']),
      receiverPhone: _extractPhone(json['receiver']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'sender': sender,
      'receiver': receiver,
      'amount': amount,
      'currency': currency,
      'commission_amount': commissionAmount,
      'description': description,
      'reference': reference,
      'status': status,
      'created_at': createdAt.toIso8601String(),
    };
  }

  @override
  String toString() =>
      'TransferModel(id: $id, amount: $amount $currency, $status)';
}

// ── Helpers ───────────────────────────────────────

String? _extractName(dynamic field) {
  if (field is Map<String, dynamic>) {
    final first = field['first_name'] as String? ?? '';
    final last = field['last_name'] as String? ?? '';
    final full = '$first $last'.trim();
    return full.isNotEmpty ? full : null;
  }
  return null;
}

String? _extractPhone(dynamic field) {
  if (field is Map<String, dynamic>) {
    return field['phone_number'] as String?;
  }
  return null;
}

double _toDouble(dynamic value) {
  if (value == null) return 0.0;
  if (value is double) return value;
  if (value is int) return value.toDouble();
  if (value is String) return double.tryParse(value) ?? 0.0;
  return 0.0;
}
