import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

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

  Future<void> _confirm() async {
    setState(() => _isLoading = true);

    // TODO: Integrate with TransferService
    await Future.delayed(const Duration(seconds: 2));

    if (!mounted) return;
    setState(() {
      _isLoading = false;
      _showSuccess = true;
    });
    _successAnimController.forward();
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
