import 'package:flutter_bloc/flutter_bloc.dart';

import '../../services/auth_service.dart';
import '../../services/storage_service.dart';
import '../../models/user_model.dart';
import 'auth_event.dart';
import 'auth_state.dart';

class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final AuthService authService;
  final StorageService storageService;

  AuthBloc({
    required this.authService,
    required this.storageService,
  }) : super(const AuthInitial()) {
    on<AppStarted>(_onAppStarted);
    on<LoginRequested>(_onLoginRequested);
    on<RegisterRequested>(_onRegisterRequested);
    on<VerifyOTPRequested>(_onVerifyOTPRequested);
    on<RequestOTPRequested>(_onRequestOTPRequested);
    on<LogoutRequested>(_onLogoutRequested);
    on<ProfileLoadRequested>(_onProfileLoadRequested);
    on<ProfileUpdateRequested>(_onProfileUpdateRequested);
  }

  Future<void> _onAppStarted(
    AppStarted event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());
    try {
      final token = await storageService.getToken();
      if (token != null) {
        final response = await authService.getProfile();
        if (response.success && response.data != null) {
          emit(Authenticated(user: response.data!, token: token));
        } else {
          emit(const Unauthenticated());
        }
      } else {
        emit(const Unauthenticated());
      }
    } catch (e) {
      emit(const Unauthenticated());
    }
  }

  Future<void> _onLoginRequested(
    LoginRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());
    try {
      final response = await authService.login(
        phone: event.phone,
        password: event.password,
      );
      if (response.success && response.data != null) {
        final data = response.data as Map<String, dynamic>;
        final token = data['access'] as String? ?? '';
        final cachedUser = await storageService.getUser();
        emit(Authenticated(user: cachedUser, token: token));
      } else {
        emit(AuthError(message: response.message ?? 'Error de autenticación'));
      }
    } catch (e) {
      emit(AuthError(message: e.toString()));
    }
  }

  Future<void> _onRegisterRequested(
    RegisterRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());
    try {
      await authService.register(
        phone: event.phone,
        documentType: event.docType,
        documentNumber: event.docNumber,
        firstName: event.firstName,
        lastName: event.lastName,
        password: event.password,
      );
      emit(const RegistrationSuccess());
    } catch (e) {
      emit(AuthError(message: e.toString()));
    }
  }

  Future<void> _onVerifyOTPRequested(
    VerifyOTPRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());
    try {
      await authService.verifyOTP(
        phone: event.phone,
        code: event.code,
        purpose: event.purpose,
      );
      emit(const OTPVerified());
    } catch (e) {
      emit(AuthError(message: e.toString()));
    }
  }

  Future<void> _onRequestOTPRequested(
    RequestOTPRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());
    try {
      await authService.requestOTP(
        phone: event.phone,
        purpose: event.purpose,
      );
      emit(OTPSent(phone: event.phone, purpose: event.purpose));
    } catch (e) {
      emit(AuthError(message: e.toString()));
    }
  }

  Future<void> _onLogoutRequested(
    LogoutRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());
    try {
      await authService.logout();
      emit(const Unauthenticated());
    } catch (e) {
      await storageService.clearAll();
      emit(const Unauthenticated());
    }
  }

  Future<void> _onProfileLoadRequested(
    ProfileLoadRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());
    try {
      final response = await authService.getProfile();
      if (response.success && response.data != null) {
        emit(ProfileLoaded(user: response.data!));
      } else {
        emit(AuthError(message: response.message ?? 'Error al cargar perfil'));
      }
    } catch (e) {
      emit(AuthError(message: e.toString()));
    }
  }

  Future<void> _onProfileUpdateRequested(
    ProfileUpdateRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());
    try {
      final response = await authService.updateProfile(event.data);
      if (response.success && response.data != null) {
        emit(ProfileUpdated(user: response.data!));
      } else {
        emit(AuthError(message: response.message ?? 'Error al actualizar'));
      }
    } catch (e) {
      emit(AuthError(message: e.toString()));
    }
  }
}
