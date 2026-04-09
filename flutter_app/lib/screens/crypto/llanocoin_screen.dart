import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';

import '../../config/theme.dart';

/// Llanocoin (LLO) management screen: buy, sell, view balance and history.
class LlanocoinScreen extends StatefulWidget {
  const LlanocoinScreen({super.key});

  @override
  State<LlanocoinScreen> createState() => _LlanocoinScreenState();
}

class _LlanocoinScreenState extends State<LlanocoinScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController;
  final _buyAmountController = TextEditingController();
  final _sellAmountController = TextEditingController();

  final _copFormat = NumberFormat.currency(
    locale: 'es_CO',
    symbol: '\$',
    decimalDigits: 0,
  );

  static const double _exchangeRate = 1000; // 1 LLO = 1,000 COP
  static const double _currentLloBalance = 0;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _buyAmountController.dispose();
    _sellAmountController.dispose();
    super.dispose();
  }

  double get _buyPreviewLlo {
    final cop = double.tryParse(
            _buyAmountController.text.replaceAll(RegExp(r'[^0-9.]'), '')) ??
        0;
    return cop / _exchangeRate;
  }

  double get _sellPreviewCop {
    final llo = double.tryParse(
            _sellAmountController.text.replaceAll(RegExp(r'[^0-9.]'), '')) ??
        0;
    return llo * _exchangeRate;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Llanocoin'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: LlanoPayTheme.secondaryGold,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white60,
          labelStyle: GoogleFonts.montserrat(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
          tabs: const [
            Tab(text: 'Comprar'),
            Tab(text: 'Vender'),
            Tab(text: 'Historial'),
          ],
        ),
      ),
      body: Column(
        children: [
          // -- Balance & exchange rate header --
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  LlanoPayTheme.primaryGreen,
                  LlanoPayTheme.primaryGreenLight,
                ],
              ),
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        color: LlanoPayTheme.secondaryGold,
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color:
                                LlanoPayTheme.secondaryGold.withOpacity(0.4),
                            blurRadius: 12,
                          ),
                        ],
                      ),
                      child: const Icon(
                        Icons.toll,
                        color: Colors.white,
                        size: 22,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      '${_currentLloBalance.toStringAsFixed(2)} LLO',
                      style: GoogleFonts.montserrat(
                        color: Colors.white,
                        fontSize: 26,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 14,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    '1 LLO = ${_copFormat.format(_exchangeRate)} COP',
                    style: GoogleFonts.nunito(
                      color: Colors.white,
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // -- Tab views --
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildBuyTab(),
                _buildSellTab(),
                _buildHistoryTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBuyTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'Comprar Llanocoin',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          Text(
            'Usa pesos colombianos para comprar LLO',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: LlanoPayTheme.textSecondary,
                ),
          ),
          const SizedBox(height: 24),

          // Amount in COP
          TextFormField(
            controller: _buyAmountController,
            keyboardType: TextInputType.number,
            style: GoogleFonts.montserrat(
              fontSize: 24,
              fontWeight: FontWeight.w700,
            ),
            textAlign: TextAlign.center,
            decoration: const InputDecoration(
              labelText: 'Monto en COP',
              hintText: '0',
              prefixText: '\$ ',
              suffixText: 'COP',
            ),
            onChanged: (_) => setState(() {}),
          ),
          const SizedBox(height: 20),

          // Preview
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: LlanoPayTheme.secondaryGold.withOpacity(0.1),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: LlanoPayTheme.secondaryGold.withOpacity(0.3),
              ),
            ),
            child: Column(
              children: [
                const Icon(
                  Icons.arrow_downward,
                  color: LlanoPayTheme.secondaryGoldDark,
                ),
                const SizedBox(height: 8),
                Text(
                  'Recibiras',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 4),
                Text(
                  '${_buyPreviewLlo.toStringAsFixed(2)} LLO',
                  style: GoogleFonts.montserrat(
                    fontSize: 28,
                    fontWeight: FontWeight.w800,
                    color: LlanoPayTheme.secondaryGoldDark,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 28),

          SizedBox(
            height: 52,
            child: ElevatedButton.icon(
              onPressed: _buyPreviewLlo > 0
                  ? () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Compra de Llanocoin en proceso'),
                          backgroundColor: LlanoPayTheme.success,
                        ),
                      );
                    }
                  : null,
              icon: const Icon(Icons.shopping_cart),
              label: const Text('Comprar LLO'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSellTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'Vender Llanocoin',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          Text(
            'Convierte tus LLO a pesos colombianos',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: LlanoPayTheme.textSecondary,
                ),
          ),
          const SizedBox(height: 24),

          // Amount in LLO
          TextFormField(
            controller: _sellAmountController,
            keyboardType: TextInputType.number,
            style: GoogleFonts.montserrat(
              fontSize: 24,
              fontWeight: FontWeight.w700,
            ),
            textAlign: TextAlign.center,
            decoration: const InputDecoration(
              labelText: 'Cantidad de LLO',
              hintText: '0.00',
              suffixText: 'LLO',
            ),
            onChanged: (_) => setState(() {}),
          ),
          const SizedBox(height: 20),

          // Preview
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: LlanoPayTheme.primaryGreen.withOpacity(0.08),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: LlanoPayTheme.primaryGreen.withOpacity(0.2),
              ),
            ),
            child: Column(
              children: [
                const Icon(
                  Icons.arrow_downward,
                  color: LlanoPayTheme.primaryGreen,
                ),
                const SizedBox(height: 8),
                Text(
                  'Recibiras',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 4),
                Text(
                  '${_copFormat.format(_sellPreviewCop)} COP',
                  style: GoogleFonts.montserrat(
                    fontSize: 28,
                    fontWeight: FontWeight.w800,
                    color: LlanoPayTheme.primaryGreen,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 28),

          SizedBox(
            height: 52,
            child: ElevatedButton.icon(
              onPressed: _sellPreviewCop > 0
                  ? () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Venta de Llanocoin en proceso'),
                          backgroundColor: LlanoPayTheme.success,
                        ),
                      );
                    }
                  : null,
              style: ElevatedButton.styleFrom(
                backgroundColor: LlanoPayTheme.secondaryGoldDark,
              ),
              icon: const Icon(Icons.sell_outlined),
              label: const Text('Vender LLO'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHistoryTab() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.history,
            size: 56,
            color: LlanoPayTheme.textSecondary.withOpacity(0.4),
          ),
          const SizedBox(height: 12),
          Text(
            'Sin transacciones de Llanocoin',
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: LlanoPayTheme.textSecondary,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Tus compras y ventas de LLO apareceran aqui',
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ),
    );
  }
}
