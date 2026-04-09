import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';

import '../../config/theme.dart';

/// Screen for requesting a new microcredit loan.
class MicrocreditRequestScreen extends StatefulWidget {
  const MicrocreditRequestScreen({super.key});

  @override
  State<MicrocreditRequestScreen> createState() =>
      _MicrocreditRequestScreenState();
}

class _MicrocreditRequestScreenState extends State<MicrocreditRequestScreen> {
  bool _isLoading = false;

  // Product selection
  int _selectedProductIndex = 0;

  static const List<Map<String, dynamic>> _products = [
    {
      'name': 'Microcredito Express',
      'icon': Icons.flash_on,
      'color': LlanoPayTheme.secondaryGold,
      'min': 50000.0,
      'max': 500000.0,
      'terms': [15, 30],
      'rate': 0.025, // 2.5% monthly
      'requires_collateral': false,
    },
    {
      'name': 'Credito Llanero',
      'icon': Icons.agriculture,
      'color': LlanoPayTheme.primaryGreen,
      'min': 100000.0,
      'max': 2000000.0,
      'terms': [30, 60, 90],
      'rate': 0.018, // 1.8% monthly
      'requires_collateral': false,
    },
    {
      'name': 'Credito Colateral LLO',
      'icon': Icons.toll,
      'color': LlanoPayTheme.accentBrown,
      'min': 200000.0,
      'max': 5000000.0,
      'terms': [30, 60, 90, 180],
      'rate': 0.012, // 1.2% monthly
      'requires_collateral': true,
    },
  ];

  late double _amount;
  late int _selectedTerm;

  final _copFormat = NumberFormat.currency(
    locale: 'es_CO',
    symbol: '\$',
    decimalDigits: 0,
  );

  @override
  void initState() {
    super.initState();
    _amount = (_products[0]['min'] as double);
    _selectedTerm = (_products[0]['terms'] as List<int>).first;
  }

  Map<String, dynamic> get _selectedProduct => _products[_selectedProductIndex];
  double get _minAmount => _selectedProduct['min'] as double;
  double get _maxAmount => _selectedProduct['max'] as double;
  double get _monthlyRate => _selectedProduct['rate'] as double;
  bool get _requiresCollateral =>
      _selectedProduct['requires_collateral'] as bool;

  double get _totalInterest {
    final months = _selectedTerm / 30;
    return _amount * _monthlyRate * months;
  }

  double get _totalToRepay => _amount + _totalInterest;

  double get _lloCollateral {
    // 120% collateral in LLO (1 LLO = 1000 COP)
    return (_totalToRepay * 1.2) / 1000;
  }

  void _onProductChanged(int index) {
    setState(() {
      _selectedProductIndex = index;
      final product = _products[index];
      _amount = product['min'] as double;
      _selectedTerm = (product['terms'] as List<int>).first;
    });
  }

  Future<void> _submitRequest() async {
    setState(() => _isLoading = true);

    // Simulate API call
    await Future.delayed(const Duration(seconds: 2));

    if (!mounted) return;
    setState(() => _isLoading = false);

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Solicitud de credito enviada exitosamente'),
        backgroundColor: LlanoPayTheme.success,
      ),
    );
    context.pop();
  }

  @override
  Widget build(BuildContext context) {
    final availableTerms = _selectedProduct['terms'] as List<int>;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Solicitar Credito'),
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
            Text(
              'Selecciona un producto',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 12),

            // -- Product selection cards --
            SizedBox(
              height: 110,
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                itemCount: _products.length,
                separatorBuilder: (_, __) => const SizedBox(width: 10),
                itemBuilder: (context, index) {
                  final product = _products[index];
                  final isSelected = index == _selectedProductIndex;
                  final color = product['color'] as Color;

                  return GestureDetector(
                    onTap: () => _onProductChanged(index),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 200),
                      width: 150,
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: isSelected
                            ? color.withOpacity(0.1)
                            : LlanoPayTheme.surfaceWhite,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(
                          color: isSelected ? color : LlanoPayTheme.divider,
                          width: isSelected ? 2 : 1,
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Icon(
                            product['icon'] as IconData,
                            color: color,
                            size: 28,
                          ),
                          const Spacer(),
                          Text(
                            product['name'] as String,
                            style: GoogleFonts.montserrat(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: isSelected
                                  ? color
                                  : LlanoPayTheme.textPrimary,
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),

            const SizedBox(height: 28),

            // -- Amount slider --
            Text(
              'Monto solicitado',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            Center(
              child: Text(
                _copFormat.format(_amount),
                style: GoogleFonts.montserrat(
                  fontSize: 32,
                  fontWeight: FontWeight.w800,
                  color: LlanoPayTheme.primaryGreen,
                ),
              ),
            ),
            Slider(
              value: _amount,
              min: _minAmount,
              max: _maxAmount,
              divisions: ((_maxAmount - _minAmount) / 50000).round(),
              activeColor: LlanoPayTheme.primaryGreen,
              inactiveColor: LlanoPayTheme.divider,
              onChanged: (value) {
                setState(() => _amount = value);
              },
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  _copFormat.format(_minAmount),
                  style: Theme.of(context).textTheme.labelSmall,
                ),
                Text(
                  _copFormat.format(_maxAmount),
                  style: Theme.of(context).textTheme.labelSmall,
                ),
              ],
            ),

            const SizedBox(height: 24),

            // -- Term selection --
            Text(
              'Plazo',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            SegmentedButton<int>(
              selected: {_selectedTerm},
              onSelectionChanged: (selection) {
                setState(() => _selectedTerm = selection.first);
              },
              segments: availableTerms
                  .map(
                    (term) => ButtonSegment(
                      value: term,
                      label: Text('$term dias'),
                    ),
                  )
                  .toList(),
            ),

            const SizedBox(height: 24),

            // -- Simulation preview --
            Card(
              child: Padding(
                padding: const EdgeInsets.all(18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Simulacion',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 16),
                    _simRow(
                      'Monto solicitado',
                      _copFormat.format(_amount),
                    ),
                    const Divider(height: 20),
                    _simRow(
                      'Tasa de interes',
                      '${(_monthlyRate * 100).toStringAsFixed(1)}% mensual',
                    ),
                    const Divider(height: 20),
                    _simRow(
                      'Plazo',
                      '$_selectedTerm dias',
                    ),
                    const Divider(height: 20),
                    _simRow(
                      'Intereses estimados',
                      _copFormat.format(_totalInterest),
                    ),
                    const Divider(height: 20),
                    _simRow(
                      'Total a pagar',
                      '${_copFormat.format(_totalToRepay)} COP',
                      isBold: true,
                    ),
                  ],
                ),
              ),
            ),

            // -- LLO collateral info --
            if (_requiresCollateral) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: LlanoPayTheme.secondaryGold.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: LlanoPayTheme.secondaryGold.withOpacity(0.3),
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(
                          Icons.toll,
                          color: LlanoPayTheme.secondaryGoldDark,
                          size: 22,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Colateral en Llanocoin requerido',
                          style: Theme.of(context)
                              .textTheme
                              .titleMedium
                              ?.copyWith(
                                color: LlanoPayTheme.secondaryGoldDark,
                              ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Text(
                      'Este producto requiere un colateral del 120% en LLO que sera bloqueado hasta que pagues el credito.',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    const SizedBox(height: 10),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'LLO requerido:',
                          style: Theme.of(context).textTheme.bodyMedium,
                        ),
                        Text(
                          '${_lloCollateral.toStringAsFixed(2)} LLO',
                          style: GoogleFonts.montserrat(
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                            color: LlanoPayTheme.secondaryGoldDark,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],

            const SizedBox(height: 28),

            // -- Submit button --
            SizedBox(
              height: 52,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _submitRequest,
                child: _isLoading
                    ? const SizedBox(
                        width: 24,
                        height: 24,
                        child: CircularProgressIndicator(
                          color: Colors.white,
                          strokeWidth: 2.5,
                        ),
                      )
                    : const Text('Solicitar'),
              ),
            ),

            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _simRow(String label, String value, {bool isBold = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: LlanoPayTheme.textSecondary,
              ),
        ),
        Text(
          value,
          style: isBold
              ? GoogleFonts.montserrat(
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                  color: LlanoPayTheme.primaryGreen,
                )
              : Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
        ),
      ],
    );
  }
}
