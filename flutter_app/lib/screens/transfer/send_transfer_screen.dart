import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

/// Screen for sending COP or LLO to another user.
class SendTransferScreen extends StatefulWidget {
  const SendTransferScreen({super.key});

  @override
  State<SendTransferScreen> createState() => _SendTransferScreenState();
}

class _SendTransferScreenState extends State<SendTransferScreen> {
  final _formKey = GlobalKey<FormState>();
  final _phoneController = TextEditingController();
  final _amountController = TextEditingController();
  final _descriptionController = TextEditingController();

  String _currency = 'COP';
  final _copFormat = NumberFormat.currency(
    locale: 'es_CO',
    symbol: '\$',
    decimalDigits: 0,
  );

  @override
  void dispose() {
    _phoneController.dispose();
    _amountController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  double get _parsedAmount {
    final text = _amountController.text.replaceAll(RegExp(r'[^0-9.]'), '');
    return double.tryParse(text) ?? 0;
  }

  double get _commission {
    final amount = _parsedAmount;
    if (_currency == 'COP') {
      if (amount <= 50000) return 0;
      return amount * 0.005; // 0.5%
    }
    return 0; // LLO transfers are free
  }

  void _onSend() {
    if (!(_formKey.currentState?.validate() ?? false)) return;

    context.push(
      '/transfer/confirm',
      extra: {
        'phone': _phoneController.text.trim(),
        'amount': _parsedAmount,
        'currency': _currency,
        'commission': _commission,
        'description': _descriptionController.text.trim(),
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Enviar dinero'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextFormField(
                controller: _phoneController,
                keyboardType: TextInputType.phone,
                decoration: InputDecoration(
                  labelText: 'Celular del destinatario',
                  hintText: '+57 300 000 0000',
                  prefixIcon: const Icon(Icons.person_search),
                  suffixIcon: IconButton(
                    icon: const Icon(Icons.contacts),
                    onPressed: () {
                      // TODO: Contact picker
                    },
                    tooltip: 'Seleccionar contacto',
                  ),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'Ingresa el numero del destinatario';
                  }
                  if (value.trim().length < 10) return 'Numero invalido';
                  return null;
                },
              ),
              const SizedBox(height: 24),
              // Currency toggle
              Row(
                children: [
                  Text('Moneda:', style: theme.textTheme.titleMedium),
                  const SizedBox(width: 16),
                  Expanded(
                    child: SegmentedButton<String>(
                      selected: {_currency},
                      onSelectionChanged: (s) {
                        setState(() => _currency = s.first);
                      },
                      segments: const [
                        ButtonSegment(
                          value: 'COP',
                          label: Text('COP'),
                          icon: Icon(Icons.attach_money, size: 18),
                        ),
                        ButtonSegment(
                          value: 'LLO',
                          label: Text('LLO'),
                          icon: Icon(Icons.toll, size: 18),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              TextFormField(
                controller: _amountController,
                keyboardType: TextInputType.number,
                textAlign: TextAlign.center,
                style: theme.textTheme.displaySmall,
                inputFormatters: [
                  FilteringTextInputFormatter.allow(RegExp(r'[0-9.]')),
                ],
                decoration: InputDecoration(
                  labelText: 'Monto a enviar',
                  hintText: _currency == 'COP' ? '0' : '0.00',
                  prefixText: _currency == 'COP' ? '\$ ' : '',
                  suffixText: _currency,
                ),
                onChanged: (_) => setState(() {}),
                validator: (value) {
                  final amount = double.tryParse(
                      value?.replaceAll(RegExp(r'[^0-9.]'), '') ?? '');
                  if (amount == null || amount <= 0) {
                    return 'Ingresa un monto valido';
                  }
                  if (_currency == 'COP' && amount < 1000) {
                    return 'El monto minimo es \$1.000 COP';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              if (_parsedAmount > 0)
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.secondary.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Comision:', style: theme.textTheme.bodyMedium),
                      Text(
                        _commission == 0
                            ? 'Gratis'
                            : '${_copFormat.format(_commission)} COP',
                        style: theme.textTheme.titleMedium?.copyWith(
                          color: _commission == 0
                              ? theme.colorScheme.primary
                              : theme.colorScheme.tertiary,
                        ),
                      ),
                    ],
                  ),
                ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _descriptionController,
                maxLength: 100,
                decoration: const InputDecoration(
                  labelText: 'Descripcion (opcional)',
                  hintText: 'Ej: Pago almuerzo',
                  prefixIcon: Icon(Icons.note_outlined),
                ),
              ),
              const SizedBox(height: 28),
              SizedBox(
                height: 52,
                child: ElevatedButton.icon(
                  onPressed: _onSend,
                  icon: const Icon(Icons.send),
                  label: const Text('Enviar'),
                ),
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }
}
