import 'package:equatable/equatable.dart';

abstract class AuthEvent extends Equatable {
  const AuthEvent();

  @override
  List<Object?> get props => [];
}

class AppStarted extends AuthEvent {
  const AppStarted();
}

class LoginRequested extends AuthEvent {
  final String phone;
  final String password;

  const LoginRequested({
    required this.phone,
    required this.password,
  });

  @override
  List<Object?> get props => [phone, password];
}

class RegisterRequested extends AuthEvent {
  final String phone;
  final String docType;
  final String docNumber;
  final String firstName;
  final String lastName;
  final String password;

  const RegisterRequested({
    required this.phone,
    required this.docType,
    required this.docNumber,
    required this.firstName,
    required this.lastName,
    required this.password,
  });

  @override
  List<Object?> get props => [phone, docType, docNumber, firstName, lastName, password];
}

class VerifyOTPRequested extends AuthEvent {
  final String phone;
  final String code;
  final String purpose;

  const VerifyOTPRequested({
    required this.phone,
    required this.code,
    required this.purpose,
  });

  @override
  List<Object?> get props => [phone, code, purpose];
}

class RequestOTPRequested extends AuthEvent {
  final String phone;
  final String purpose;

  const RequestOTPRequested({
    required this.phone,
    required this.purpose,
  });

  @override
  List<Object?> get props => [phone, purpose];
}

class LogoutRequested extends AuthEvent {
  const LogoutRequested();
}

class ProfileLoadRequested extends AuthEvent {
  const ProfileLoadRequested();
}

class ProfileUpdateRequested extends AuthEvent {
  final Map<String, dynamic> data;

  const ProfileUpdateRequested({required this.data});

  @override
  List<Object?> get props => [data];
}
