import 'package:equatable/equatable.dart';

import '../../models/user_model.dart';

abstract class AuthState extends Equatable {
  const AuthState();

  @override
  List<Object?> get props => [];
}

class AuthInitial extends AuthState {
  const AuthInitial();
}

class AuthLoading extends AuthState {
  const AuthLoading();
}

class Authenticated extends AuthState {
  final UserModel? user;
  final String token;

  const Authenticated({
    this.user,
    required this.token,
  });

  @override
  List<Object?> get props => [user, token];
}

class Unauthenticated extends AuthState {
  const Unauthenticated();
}

class OTPSent extends AuthState {
  final String phone;
  final String purpose;

  const OTPSent({
    required this.phone,
    required this.purpose,
  });

  @override
  List<Object?> get props => [phone, purpose];
}

class OTPVerified extends AuthState {
  const OTPVerified();
}

class RegistrationSuccess extends AuthState {
  const RegistrationSuccess();
}

class AuthError extends AuthState {
  final String message;

  const AuthError({required this.message});

  @override
  List<Object?> get props => [message];
}

class ProfileLoaded extends AuthState {
  final UserModel user;

  const ProfileLoaded({required this.user});

  @override
  List<Object?> get props => [user];
}

class ProfileUpdated extends AuthState {
  final UserModel user;

  const ProfileUpdated({required this.user});

  @override
  List<Object?> get props => [user];
}
