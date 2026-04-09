import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import '../config/api_config.dart';
import 'storage_service.dart';

/// Real-time notification service over WebSocket.
class WebSocketService {
  final StorageService storageService;

  WebSocketChannel? _channel;
  StreamController<Map<String, dynamic>>? _controller;
  Timer? _reconnectTimer;
  bool _isDisposed = false;
  bool _isConnected = false;

  static const int _reconnectDelaySeconds = 5;
  static const int _maxReconnectAttempts = 10;
  int _reconnectAttempts = 0;

  WebSocketService({required this.storageService});

  /// Stream of incoming notification payloads.
  Stream<Map<String, dynamic>> get notifications {
    _controller ??= StreamController<Map<String, dynamic>>.broadcast();
    return _controller!.stream;
  }

  /// Whether the WebSocket is currently connected.
  bool get isConnected => _isConnected;

  /// Open the WebSocket connection, attaching JWT auth.
  Future<void> connect() async {
    if (_isDisposed) return;

    final token = await storageService.getToken();
    if (token == null) return;

    final wsUrl =
        '${ApiConfig.wsUrl}${ApiConfig.notificationsWebSocket}?token=$token';

    try {
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      _isConnected = true;
      _reconnectAttempts = 0;

      _controller ??= StreamController<Map<String, dynamic>>.broadcast();

      _channel!.stream.listen(
        _onData,
        onError: _onError,
        onDone: _onDone,
        cancelOnError: false,
      );
    } catch (e) {
      _isConnected = false;
      _scheduleReconnect();
    }
  }

  /// Send a message through the WebSocket.
  void send(Map<String, dynamic> data) {
    if (_isConnected && _channel != null) {
      _channel!.sink.add(jsonEncode(data));
    }
  }

  /// Gracefully close the connection and release resources.
  void dispose() {
    _isDisposed = true;
    _reconnectTimer?.cancel();
    _channel?.sink.close();
    _controller?.close();
    _channel = null;
    _controller = null;
    _isConnected = false;
  }

  /// Disconnect without disposing; allows reconnection.
  void disconnect() {
    _reconnectTimer?.cancel();
    _channel?.sink.close();
    _channel = null;
    _isConnected = false;
  }

  // ── Internal handlers ─────────────────────────

  void _onData(dynamic rawData) {
    try {
      final decoded = jsonDecode(rawData as String) as Map<String, dynamic>;
      _controller?.add(decoded);
    } catch (_) {
      // Discard malformed messages.
    }
  }

  void _onError(Object error) {
    _isConnected = false;
    _scheduleReconnect();
  }

  void _onDone() {
    _isConnected = false;
    _scheduleReconnect();
  }

  void _scheduleReconnect() {
    if (_isDisposed) return;
    if (_reconnectAttempts >= _maxReconnectAttempts) return;

    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(
      Duration(seconds: _reconnectDelaySeconds * (_reconnectAttempts + 1)),
      () {
        _reconnectAttempts++;
        connect();
      },
    );
  }
}
