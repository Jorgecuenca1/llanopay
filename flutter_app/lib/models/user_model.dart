/// User profile model for LlanoPay.
class UserModel {
  final int id;
  final String phoneNumber;
  final String documentType;
  final String documentNumber;
  final String firstName;
  final String lastName;
  final String? email;
  final bool isVerified;
  final bool isMerchant;
  final String? profilePicture;
  final String? city;
  final String? department;
  final DateTime? createdAt;

  const UserModel({
    required this.id,
    required this.phoneNumber,
    required this.documentType,
    required this.documentNumber,
    required this.firstName,
    required this.lastName,
    this.email,
    this.isVerified = false,
    this.isMerchant = false,
    this.profilePicture,
    this.city,
    this.department,
    this.createdAt,
  });

  /// Full display name.
  String get fullName => '$firstName $lastName';

  /// Create from JSON map.
  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] as int,
      phoneNumber: json['phone_number'] as String,
      documentType: json['document_type'] as String? ?? 'CC',
      documentNumber: json['document_number'] as String? ?? '',
      firstName: json['first_name'] as String? ?? '',
      lastName: json['last_name'] as String? ?? '',
      email: json['email'] as String?,
      isVerified: json['is_verified'] as bool? ?? false,
      isMerchant: json['is_merchant'] as bool? ?? false,
      profilePicture: json['profile_picture'] as String?,
      city: json['city'] as String?,
      department: json['department'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String)
          : null,
    );
  }

  /// Serialize to JSON map.
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'phone_number': phoneNumber,
      'document_type': documentType,
      'document_number': documentNumber,
      'first_name': firstName,
      'last_name': lastName,
      'email': email,
      'is_verified': isVerified,
      'is_merchant': isMerchant,
      'profile_picture': profilePicture,
      'city': city,
      'department': department,
      'created_at': createdAt?.toIso8601String(),
    };
  }

  /// Copy with overrides.
  UserModel copyWith({
    int? id,
    String? phoneNumber,
    String? documentType,
    String? documentNumber,
    String? firstName,
    String? lastName,
    String? email,
    bool? isVerified,
    bool? isMerchant,
    String? profilePicture,
    String? city,
    String? department,
    DateTime? createdAt,
  }) {
    return UserModel(
      id: id ?? this.id,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      documentType: documentType ?? this.documentType,
      documentNumber: documentNumber ?? this.documentNumber,
      firstName: firstName ?? this.firstName,
      lastName: lastName ?? this.lastName,
      email: email ?? this.email,
      isVerified: isVerified ?? this.isVerified,
      isMerchant: isMerchant ?? this.isMerchant,
      profilePicture: profilePicture ?? this.profilePicture,
      city: city ?? this.city,
      department: department ?? this.department,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  String toString() => 'UserModel(id: $id, phone: $phoneNumber, name: $fullName)';
}
