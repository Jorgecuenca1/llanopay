import 'dart:async';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:pin_code_fields/pin_code_fields.dart';

/// OTP verification screen.
class VerifyOTPScreen extends StatefulWidget {
  final String phone;
  final String purpose;

  const VerifyOTPScreen({
    super.key,
    required this.phone,
    this.purpose = 'registration',
  });

  @override
  State<VerifyOTPScreen> createState() => _VerifyOTPScreenState();
}

class _VerifyOTPScreenState extends State<VerifyOTPScreen> {
  final _otpController = TextEditingController();
  Timer? _timer;
  int _secondsRemaining = 60;
  bool _canResend = false;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _startCountdown();
  }

  @override
  void dispose() {
    _otpController.dispose();
    _timer?.cancel();
    super.dispose();
  }

  void _startCountdown() {
    setState(() {
      _secondsRemaining = 60;
      _canResend = false;
    });
    _timer?.cancel();
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_secondsRemaining == 0) {
        timer.cancel();
        if (mounted) setState(() => _canResend = true);
      } else {
        if (mounted) setState(() => _secondsRemaining--);
      }
    });
  }

  Future<void> _verifyOTP(String code) async {
    if (code.length < 6) return;
    setState(() => _isLoading = true);

    // TODO: Integrate with AuthService.verifyOTP
    await Future.delayed(const Duration(seconds: 1));

    if (!mounted) return;
    setState(() => _isLoading = false);

    if (widget.purpose == 'registration') {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Cuenta verificada exitosamente'),
          backgroundColor: Theme.of(context).colorScheme.primary,
        ),
      );
      context.go('/login');
    } else {
      context.pop(true);
    }
  }

  void _resendOTP() {
    // TODO: Integrate with AuthService.requestOTP
    _startCountdown();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final maskedPhone = widget.phone.length > 4
        ? '${'*' * (widget.phone.length - 4)}${widget.phone.substring(widget.phone.length - 4)}'
        : widget.phone;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Verificacion'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 28),
          child: Column(
            children: [
              const SizedBox(height: 40),
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: theme.colorScheme.primary.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.sms_outlined,
                  color: theme.colorScheme.primary,
                  size: 40,
                ),
              ),
              const SizedBox(height: 28),
              Text(
                'Ingresa el codigo enviado a tu celular',
                style: theme.textTheme.titleLarge,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(
                'Enviamos un codigo de 6 digitos a $maskedPhone',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 36),
              PinCodeTextField(
                appContext: context,
                length: 6,
                controller: _otpController,
                keyboardType: TextInputType.number,
                animationType: AnimationType.fade,
                pinTheme: PinTheme(
                  shape: PinCodeFieldShape.box,
                  borderRadius: BorderRadius.circular(12),
                  fieldHeight: 56,
                  fieldWidth: 46,
                  activeFillColor: theme.colorScheme.surface,
                  inactiveFillColor: theme.colorScheme.surfaceContainerHighest,
                  selectedFillColor: theme.colorScheme.surface,
                  activeColor: theme.colorScheme.primary,
                  inactiveColor: theme.colorScheme.outline,
                  selectedColor: theme.colorScheme.secondary,
                ),
                enableActiveFill: true,
                onCompleted: _verifyOTP,
                onChanged: (_) {},
              ),
              const SizedBox(height: 24),
              if (_isLoading)
                Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: CircularProgressIndicator(
                    color: theme.colorScheme.primary,
                  ),
                ),
              if (!_canResend)
                Text(
                  'Reenviar codigo en $_secondsRemaining s',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                )
              else
                TextButton.icon(
                  onPressed: _resendOTP,
                  icon: const Icon(Icons.refresh),
                  label: const Text('Reenviar codigo'),
                ),
              const Spacer(),
              SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton(
                  onPressed:
                      _isLoading ? null : () => _verifyOTP(_otpController.text),
                  child: const Text('Verificar'),
                ),
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }
}
