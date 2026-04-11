import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../services/api_service.dart';
import '../../config/api_config.dart';

/// Wallet tab showing real balances and transaction shortcuts.
class WalletTab extends StatefulWidget {
  const WalletTab({super.key});

  @override
  State<WalletTab> createState() => _WalletTabState();
}

class _WalletTabState extends State<WalletTab> {
  Map<String, dynamic>? _wallet;
  List<dynamic> _transactions = [];
  bool _loading = true;
  final _copFormat = NumberFormat('#,###', 'es_CO');

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final api = context.read<ApiService>();
    final results = await Future.wait([
      api.get(ApiConfig.walletBalance),
      api.get(ApiConfig.walletTransactions, queryParameters: {'page_size': 10}),
    ]);
    if (mounted) {
      setState(() {
        _loading = false;
        if (results[0].success) _wallet = results[0].data as Map<String, dynamic>;
        if (results[1].success) {
          final d = results[1].data;
          _transactions = d is Map ? (d['results'] as List? ?? []) : (d as List? ?? []);
        }
      });
    }
  }

  String _fmtCop(dynamic v) {
    final n = double.tryParse(v?.toString() ?? '0') ?? 0;
    return _copFormat.format(n.toInt());
  }

  String _fmtSnc(dynamic v) {
    final n = double.tryParse(v?.toString() ?? '0') ?? 0;
    return n.toStringAsFixed(2);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cop = _wallet?['balance_cop'];
    final llo = _wallet?['balance_llo'];
    final lloCop = _wallet?['llo_cop_equivalent'];

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mi Billetera'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _load,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _load,
        child: _loading
            ? const Center(child: CircularProgressIndicator())
            : SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // COP Balance card
                    Card(
                      elevation: 2,
                      child: ListTile(
                        contentPadding: const EdgeInsets.all(16),
                        leading: CircleAvatar(
                          radius: 26,
                          backgroundColor: theme.colorScheme.primary,
                          child: const Text('COP',
                              style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold)),
                        ),
                        title: const Text('Pesos Colombianos',
                            style: TextStyle(fontWeight: FontWeight.w600)),
                        subtitle: Text('\$ ${_fmtCop(cop)}',
                            style: const TextStyle(
                                fontSize: 22,
                                fontWeight: FontWeight.bold,
                                color: Colors.green)),
                        trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                        onTap: () => context.push('/wallet/transactions'),
                      ),
                    ),
                    const SizedBox(height: 12),
                    // SuperNova Coin Balance card
                    Card(
                      elevation: 2,
                      child: ListTile(
                        contentPadding: const EdgeInsets.all(16),
                        leading: CircleAvatar(
                          radius: 26,
                          backgroundColor: const Color(0xFFF9A825),
                          child: const Text('SNC',
                              style: TextStyle(
                                  color: Colors.black,
                                  fontSize: 11,
                                  fontWeight: FontWeight.bold)),
                        ),
                        title: const Text('SuperNova Coin',
                            style: TextStyle(fontWeight: FontWeight.w600)),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('${_fmtSnc(llo)} SNC',
                                style: const TextStyle(
                                    fontSize: 22,
                                    fontWeight: FontWeight.bold,
                                    color: Color(0xFFF57F17))),
                            if (lloCop != null)
                              Text('≈ \$ ${_fmtCop(lloCop)} COP',
                                  style: const TextStyle(
                                      fontSize: 12, color: Colors.grey)),
                          ],
                        ),
                        trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                        onTap: () => context.push('/crypto/llanocoin'),
                      ),
                    ),
                    const SizedBox(height: 16),
                    // Actions row
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () => context.push('/topup'),
                            icon: const Icon(Icons.add_circle_outline),
                            label: const Text('Recargar'),
                            style: OutlinedButton.styleFrom(
                                padding:
                                    const EdgeInsets.symmetric(vertical: 14)),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () => context.push('/transfer/send'),
                            icon: const Icon(Icons.send),
                            label: const Text('Enviar'),
                            style: OutlinedButton.styleFrom(
                                padding:
                                    const EdgeInsets.symmetric(vertical: 14)),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Movimientos recientes',
                            style: TextStyle(
                                fontSize: 16, fontWeight: FontWeight.bold)),
                        TextButton(
                            onPressed: () =>
                                context.push('/wallet/transactions'),
                            child: const Text('Ver todo')),
                      ],
                    ),
                    const SizedBox(height: 8),
                    if (_transactions.isEmpty)
                      Card(
                        child: Padding(
                          padding: const EdgeInsets.all(24),
                          child: Center(
                            child: Column(
                              children: [
                                Icon(Icons.receipt_long,
                                    size: 48,
                                    color: theme.colorScheme.onSurfaceVariant
                                        .withAlpha(100)),
                                const SizedBox(height: 8),
                                Text('Sin movimientos aún',
                                    style: theme.textTheme.bodyMedium),
                              ],
                            ),
                          ),
                        ),
                      )
                    else
                      Card(
                        child: Column(
                          children: _transactions.map<Widget>((tx) {
                            final type = tx['transaction_type']?.toString() ?? '';
                            final amount = tx['amount']?.toString() ?? '0';
                            final currency = tx['currency']?.toString() ?? 'COP';
                            final isIn = [
                              'DEPOSIT',
                              'TRANSFER_IN',
                              'CRYPTO_DEPOSIT',
                              'LLO_PURCHASE',
                              'MICROCREDIT_DISBURSEMENT'
                            ].contains(type);
                            final names = {
                              'DEPOSIT': 'Depósito',
                              'WITHDRAWAL': 'Retiro',
                              'TRANSFER_IN': 'Recibido',
                              'TRANSFER_OUT': 'Enviado',
                              'CRYPTO_DEPOSIT': 'Crypto',
                              'LLO_PURCHASE': 'Compra SNC',
                              'LLO_SALE': 'Venta SNC',
                              'COMMISSION': 'Comisión',
                              'MICROCREDIT_DISBURSEMENT': 'Crédito',
                              'MICROCREDIT_PAYMENT': 'Pago crédito',
                            };
                            final displayCurrency = currency == 'LLO' ? 'SNC' : currency;
                            return ListTile(
                              dense: true,
                              leading: CircleAvatar(
                                backgroundColor:
                                    (isIn ? Colors.green : Colors.red)
                                        .withAlpha(30),
                                child: Icon(
                                  isIn
                                      ? Icons.arrow_downward
                                      : Icons.arrow_upward,
                                  color: isIn ? Colors.green : Colors.red,
                                  size: 18,
                                ),
                              ),
                              title: Text(names[type] ?? type),
                              subtitle: Text(
                                tx['description']?.toString() ?? '',
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                              trailing: Text(
                                '${isIn ? '+' : '-'}\$${_fmtCop(amount)} $displayCurrency',
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: isIn ? Colors.green : Colors.red,
                                  fontSize: 13,
                                ),
                              ),
                            );
                          }).toList(),
                        ),
                      ),
                  ],
                ),
              ),
      ),
    );
  }
}
