import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../models/user_model.dart';

/// Unified storage service combining secure storage (tokens) and
/// shared preferences (non-sensitive data).
class StorageService {
  static const _accessTokenKey = 'access_token';
  static const _refreshTokenKey = 'refresh_token';
  static const _userKey = 'cached_user';
  static const _onboardingKey = 'onboarding_complete';

  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
  );

  // ── Token management (secure) ─────────────────

  Future<void> saveToken(String token) async {
    await _secureStorage.write(key: _accessTokenKey, value: token);
  }

  Future<String?> getToken() async {
    return _secureStorage.read(key: _accessTokenKey);
  }

  Future<void> clearToken() async {
    await _secureStorage.delete(key: _accessTokenKey);
  }

  Future<void> saveRefreshToken(String token) async {
    await _secureStorage.write(key: _refreshTokenKey, value: token);
  }

  Future<String?> getRefreshToken() async {
    return _secureStorage.read(key: _refreshTokenKey);
  }

  Future<void> clearRefreshToken() async {
    await _secureStorage.delete(key: _refreshTokenKey);
  }

  // ── User cache (shared preferences) ──────────

  Future<void> saveUser(UserModel user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_userKey, jsonEncode(user.toJson()));
  }

  Future<UserModel?> getUser() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_userKey);
    if (raw == null) return null;
    try {
      return UserModel.fromJson(jsonDecode(raw) as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }

  Future<void> clearUser() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_userKey);
  }

  // ── Auth state ────────────────────────────────

  Future<bool> isLoggedIn() async {
    final token = await getToken();
    return token != null && token.isNotEmpty;
  }

  // ── Onboarding ────────────────────────────────

  Future<void> setOnboardingComplete() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_onboardingKey, true);
  }

  Future<bool> isOnboardingComplete() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_onboardingKey) ?? false;
  }

  // ── Clear all ─────────────────────────────────

  Future<void> clearAll() async {
    await _secureStorage.deleteAll();
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_userKey);
    // Keep onboarding flag across logouts.
  }
}
