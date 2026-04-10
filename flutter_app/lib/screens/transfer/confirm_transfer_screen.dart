import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../config/api_config.dart';
import '../../services/api_service.dart';

/// Confirmation screen before executing a transfer.
class ConfirmTransferScreen extends StatefulWidget {
  final Map<String, dynamic> transferData;

  const ConfirmTransferScreen({super.key, required this.transferData});

  @override
  State<ConfirmTransferScreen> createState() => _ConfirmTransferScreenState();
}

class _ConfirmTransferScreenState extends State<ConfirmTransferScreen>
    with SingleTickerProviderStateMixin {
  bool _isLoading = false;
  bool _showSuccess = false;
  String? _errorMessage;
  late final AnimationController _successAnimController;
  late final Animation<double> _successAnimation;

  final _copFormat = NumberFormat.currency(
    locale: 'es_CO',
    symbol: '\$',
    decimalDigits: 0,
  );

  @override
  void initState() {
    super.initState();
    _successAnimController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );
    _successAnimation = CurvedAnimation(
      parent: _successAnimController,
      curve: Curves.elasticOut,
    );
  }

  @override
  void dispose() {
    _successAnimController.dispose();
    super.dispose();
  }

  String _formatPhone(String raw) {
    var p = raw.replaceAll(RegExp(r'[\s\-\(\)]'), '');
    if (p.startsWith('57') && !p.startsWith('+')) p = '+$p';
    if (p.startsWith('3') && p.length == 10) p = '+57$p';
    if (!p.startsWith('+')) p = '+$p';
    return p;
  }

  Future<void> _confirm() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final apiService = context.read<ApiService>();
      final phone = _formatPhone(widget.transferData['phone'] as String);
      final amount = (widget.transferData['amount'] as num).toDouble();
      final currency = widget.transferData['currency'] as String? ?? 'COP';
      final description = widget.transferData['description'] as String? ?? '';

      final response = await apiService.post(
        ApiConfig.transferSend,
        data: {
          'receiver_phone': phone,
          'amount': amount.toString(),
          'currency': currency,
          if (description.isNotEmpty) 'description': description,
        },
      );

      if (!mounted) return;

      if (response.success) {
        final data = response.data as Map<String, dynamic>;
        final otpRequired = data['otp_required'] == true;

        if (otpRequired) {
          // Show OTP dialog
          final transfer = data['transfer'] as Map<String, dynamic>;
          final transferId = transfer['id'] as String;
          await _showOTPDialog(apiService, transferId);
        } else {
          setState(() {
            _isLoading = false;
            _showSuccess = true;
          });
          _successAnimController.forward();
        }
      } else {
        setState(() {
          _isLoading = false;
          _errorMessage = response.message ??
              response.errors?.values.first?.toString() ??
              'Error al realizar la transferencia';
        });
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _errorMessage = 'Error de conexion: ${e.toString()}';
      });
    }
  }

  Future<void> _showOTPDialog(ApiService apiService, String transferId) async {
    setState(() => _isLoading = false);
    final otpController = TextEditingController();

    final result = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        title: const Text('Confirmar con OTP'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Esta transferencia requiere confirmacion con codigo OTP. '
              'Ingresa el codigo enviado a tu telefono.',
              style: TextStyle(fontSize: 13),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: otpController,
              keyboardType: TextInputType.number,
              maxLength: 6,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 24,
                letterSpacing: 8,
                fontWeight: FontWeight.bold,
              ),
              decoration: const InputDecoration(
                hintText: '000000',
                counterText: '',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(ctx).pop(true),
            child: const Text('Confirmar'),
          ),
        ],
      ),
    );

    if (result != true) return;

    setState(() => _isLoading = true);

    final confirmResp = await apiService.post(
      ApiConfig.transferConfirm,
      data: {
        'transfer_id': transferId,
        'otp_code': otpController.text.trim(),
      },
    );

    if (!mounted) return;

    if (confirmResp.success) {
      setState(() {
        _isLoading = false;
        _showSuccess = true;
      });
      _successAnimController.forward();
    } else {
      setState(() {
        _isLoading = false;
        _errorMessage = confirmResp.message ?? 'Codigo OTP invalido';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_showSuccess) return _buildSuccessScreen();

    final theme = Theme.of(context);
    final phone = widget.transferData['phone'] as String? ?? '';
    final amount = (widget.transferData['amount'] as num?)?.toDouble() ?? 0;
    final currency = widget.transferData['currency'] as String? ?? 'COP';
    final commission =
        (widget.transferData['commission'] as num?)?.toDouble() ?? 0;
    final description = widget.transferData['description'] as String? ?? '';
    final total = amount + commission;

    final maskedPhone = phone.length > 4
        ? '${'*' * (phone.length - 4)}${phone.substring(phone.length - 4)}'
        : phone;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Confirmar envio'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 8),
            Center(
              child: Container(
                width: 72,
                height: 72,
                decoration: BoxDecoration(
                  color: theme.colorScheme.primary.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.send,
                  color: theme.colorScheme.primary,
                  size: 36,
                ),
              ),
            ),
            const SizedBox(height: 24),
            Center(
              child: Text(
                'Resumen de la transferencia',
                style: theme.textTheme.headlineSmall,
              ),
            ),
            const SizedBox(height: 28),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    _summaryRow('Destinatario', maskedPhone),
                    const Divider(height: 24),
                    _summaryRow(
                      'Monto',
                      currency == 'COP'
                          ? '${_copFormat.format(amount)} COP'
                          : '${amount.toStringAsFixed(2)} LLO',
                    ),
                    const Divider(height: 24),
                    _summaryRow(
                      'Comision',
                      commission == 0
                          ? 'Gratis'
                          : '${_copFormat.format(commission)} COP',
                    ),
                    const Divider(height: 24),
                    _summaryRow(
                      'Total',
                      currency == 'COP'
                          ? '${_copFormat.format(total)} COP'
                          : '${amount.toStringAsFixed(2)} LLO',
                      isBold: true,
                    ),
                    if (description.isNotEmpty) ...[
                      const Divider(height: 24),
                      _summaryRow('Descripcion', description),
                    ],
                  ],
                ),
              ),
            ),
            if (_errorMessage != null) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline, color: Colors.red, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _errorMessage!,
                        style: const TextStyle(color: Colors.red, fontSize: 13),
                      ),
                    ),
                  ],
                ),
              ),
            ],
            const SizedBox(height: 32),
            SizedBox(
              height: 52,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _confirm,
                child: _isLoading
                    ? const SizedBox(
                        width: 24,
                        height: 24,
                        child: CircularProgressIndicator(
                          color: Colors.white,
                          strokeWidth: 2.5,
                        ),
                      )
                    : const Text('Confirmar'),
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 52,
              child: OutlinedButton(
                onPressed: _isLoading ? null : () => context.pop(),
                child: const Text('Cancelar'),
              ),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildSuccessScreen() {
    final theme = Theme.of(context);
    final amount = (widget.transferData['amount'] as num?)?.toDouble() ?? 0;
    final currency = widget.transferData['currency'] as String? ?? 'COP';

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ScaleTransition(
                  scale: _successAnimation,
                  child: Container(
                    width: 100,
                    height: 100,
                    decoration: BoxDecoration(
                      color: theme.colorScheme.primary,
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.check,
                      color: Colors.white,
                      size: 56,
                    ),
                  ),
                ),
                const SizedBox(height: 32),
                Text(
                  'Envio exitoso!',
                  style: theme.textTheme.displaySmall?.copyWith(
                    color: theme.colorScheme.primary,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  currency == 'COP'
                      ? '${_copFormat.format(amount)} COP enviados'
                      : '${amount.toStringAsFixed(2)} LLO enviados',
                  style: theme.textTheme.bodyLarge?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
                const SizedBox(height: 48),
                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: ElevatedButton(
                    onPressed: () => context.go('/home'),
                    child: const Text('Volver al inicio'),
                  ),
                ),
                const SizedBox(height: 12),
                TextButton(
                  onPressed: () => context.go('/wallet'),
                  child: const Text('Ver movimientos'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _summaryRow(String label, String value, {bool isBold = false}) {
    final theme = Theme.of(context);
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: Text(
            label,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: isBold
                ? theme.textTheme.titleMedium?.copyWith(
                    color: theme.colorScheme.primary,
                  )
                : theme.textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
            textAlign: TextAlign.end,
          ),
        ),
      ],
    );
  }
}
