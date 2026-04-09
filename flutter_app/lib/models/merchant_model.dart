/// Marketplace merchant profile.
class MerchantModel {
  final int id;
  final String name;
  final String slug;
  final String? description;
  final String? logoUrl;
  final String? coverImageUrl;
  final String? address;
  final String? city;
  final String? department;
  final double? latitude;
  final double? longitude;
  final String? phoneNumber;
  final MerchantCategoryModel? category;
  final double averageRating;
  final int totalReviews;
  final bool acceptsLlo;
  final bool isActive;
  final double? cashbackPercent;
  final DateTime? createdAt;

  const MerchantModel({
    required this.id,
    required this.name,
    required this.slug,
    this.description,
    this.logoUrl,
    this.coverImageUrl,
    this.address,
    this.city,
    this.department,
    this.latitude,
    this.longitude,
    this.phoneNumber,
    this.category,
    this.averageRating = 0.0,
    this.totalReviews = 0,
    this.acceptsLlo = true,
    this.isActive = true,
    this.cashbackPercent,
    this.createdAt,
  });

  factory MerchantModel.fromJson(Map<String, dynamic> json) {
    return MerchantModel(
      id: json['id'] as int,
      name: json['name'] as String,
      slug: json['slug'] as String,
      description: json['description'] as String?,
      logoUrl: json['logo_url'] as String?,
      coverImageUrl: json['cover_image_url'] as String?,
      address: json['address'] as String?,
      city: json['city'] as String?,
      department: json['department'] as String?,
      latitude: _toDoubleOrNull(json['latitude']),
      longitude: _toDoubleOrNull(json['longitude']),
      phoneNumber: json['phone_number'] as String?,
      category: json['category'] != null
          ? MerchantCategoryModel.fromJson(
              json['category'] as Map<String, dynamic>)
          : null,
      averageRating: _toDouble(json['average_rating']),
      totalReviews: json['total_reviews'] as int? ?? 0,
      acceptsLlo: json['accepts_llo'] as bool? ?? true,
      isActive: json['is_active'] as bool? ?? true,
      cashbackPercent: _toDoubleOrNull(json['cashback_percent']),
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'slug': slug,
      'description': description,
      'logo_url': logoUrl,
      'cover_image_url': coverImageUrl,
      'address': address,
      'city': city,
      'department': department,
      'latitude': latitude,
      'longitude': longitude,
      'phone_number': phoneNumber,
      'category': category?.toJson(),
      'average_rating': averageRating,
      'total_reviews': totalReviews,
      'accepts_llo': acceptsLlo,
      'is_active': isActive,
      'cashback_percent': cashbackPercent,
      'created_at': createdAt?.toIso8601String(),
    };
  }

  @override
  String toString() => 'MerchantModel(id: $id, name: $name, slug: $slug)';
}

/// Category for marketplace merchants.
class MerchantCategoryModel {
  final int id;
  final String name;
  final String slug;
  final String? icon;
  final String? description;

  const MerchantCategoryModel({
    required this.id,
    required this.name,
    required this.slug,
    this.icon,
    this.description,
  });

  factory MerchantCategoryModel.fromJson(Map<String, dynamic> json) {
    return MerchantCategoryModel(
      id: json['id'] as int,
      name: json['name'] as String,
      slug: json['slug'] as String,
      icon: json['icon'] as String?,
      description: json['description'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'slug': slug,
      'icon': icon,
      'description': description,
    };
  }

  @override
  String toString() => 'MerchantCategory(id: $id, name: $name)';
}

/// User review for a merchant.
class MerchantReviewModel {
  final int id;
  final int merchantId;
  final int userId;
  final String? userName;
  final int rating;
  final String? comment;
  final DateTime createdAt;

  const MerchantReviewModel({
    required this.id,
    required this.merchantId,
    required this.userId,
    this.userName,
    required this.rating,
    this.comment,
    required this.createdAt,
  });

  factory MerchantReviewModel.fromJson(Map<String, dynamic> json) {
    return MerchantReviewModel(
      id: json['id'] as int,
      merchantId: json['merchant_id'] as int? ?? json['merchant'] as int? ?? 0,
      userId: json['user_id'] as int? ?? json['user'] as int? ?? 0,
      userName: json['user_name'] as String?,
      rating: json['rating'] as int? ?? 0,
      comment: json['comment'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'merchant_id': merchantId,
      'user_id': userId,
      'user_name': userName,
      'rating': rating,
      'comment': comment,
      'created_at': createdAt.toIso8601String(),
    };
  }
}

/// Merchant promotion / discount offer.
class PromotionModel {
  final int id;
  final int merchantId;
  final String title;
  final String? description;
  final double discountPercent;
  final double? minPurchase;
  final String? promoCode;
  final bool lloOnly;
  final DateTime startDate;
  final DateTime endDate;
  final bool isActive;

  const PromotionModel({
    required this.id,
    required this.merchantId,
    required this.title,
    this.description,
    required this.discountPercent,
    this.minPurchase,
    this.promoCode,
    this.lloOnly = false,
    required this.startDate,
    required this.endDate,
    this.isActive = true,
  });

  /// Whether the promotion is currently valid.
  bool get isCurrentlyValid {
    final now = DateTime.now();
    return isActive && now.isAfter(startDate) && now.isBefore(endDate);
  }

  factory PromotionModel.fromJson(Map<String, dynamic> json) {
    return PromotionModel(
      id: json['id'] as int,
      merchantId: json['merchant_id'] as int? ?? json['merchant'] as int? ?? 0,
      title: json['title'] as String,
      description: json['description'] as String?,
      discountPercent: _toDouble(json['discount_percent']),
      minPurchase: _toDoubleOrNull(json['min_purchase']),
      promoCode: json['promo_code'] as String?,
      lloOnly: json['llo_only'] as bool? ?? false,
      startDate: DateTime.parse(json['start_date'] as String),
      endDate: DateTime.parse(json['end_date'] as String),
      isActive: json['is_active'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'merchant_id': merchantId,
      'title': title,
      'description': description,
      'discount_percent': discountPercent,
      'min_purchase': minPurchase,
      'promo_code': promoCode,
      'llo_only': lloOnly,
      'start_date': startDate.toIso8601String(),
      'end_date': endDate.toIso8601String(),
      'is_active': isActive,
    };
  }
}

// ── Helpers ───────────────────────────────────────

double _toDouble(dynamic value) {
  if (value == null) return 0.0;
  if (value is double) return value;
  if (value is int) return value.toDouble();
  if (value is String) return double.tryParse(value) ?? 0.0;
  return 0.0;
}

double? _toDoubleOrNull(dynamic value) {
  if (value == null) return null;
  if (value is double) return value;
  if (value is int) return value.toDouble();
  if (value is String) return double.tryParse(value);
  return null;
}
