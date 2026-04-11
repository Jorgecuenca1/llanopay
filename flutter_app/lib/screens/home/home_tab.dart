import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../blocs/auth/auth_bloc.dart';
import '../../blocs/auth/auth_state.dart';
import '../../services/api_service.dart';
import '../../config/api_config.dart';

class HomeTab extends StatefulWidget {
  const HomeTab({super.key});

  @override
  State<HomeTab> createState() => _HomeTabState();
}

class _HomeTabState extends State<HomeTab> {
  Map<String, dynamic>? _wallet;
  List<dynamic> _transactions = [];
  Map<String, dynamic>? _rewards;
  bool _loading = true;
  bool _balanceVisible = true;
  final _copFormat = NumberFormat('#,###', 'es_CO');

  @override
  void initState() {
    super.initState();
    _loadAll();
  }

  Future<void> _loadAll() async {
    setState(() => _loading = true);
    try {
      final api = context.read<ApiService>();
      final results = await Future.wait([
        api.get(ApiConfig.walletBalance),
        api.get(ApiConfig.walletTransactions, queryParameters: {'page_size': 5}),
        api.get('/global/rewards/'),
      ]);
      if (mounted) {
        setState(() {
          if (results[0].success) _wallet = results[0].data as Map<String, dynamic>;
          if (results[1].success) {
            final data = results[1].data;
            if (data is Map) {
              _transactions = (data['results'] as List?) ?? [];
            } else if (data is List) {
              _transactions = data;
            }
          }
          if (results[2].success) _rewards = results[2].data as Map<String, dynamic>?;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _loading = false);
    }
  }

  String _formatCOP(dynamic value) {
    final num = double.tryParse(value?.toString() ?? '0') ?? 0;
    return _copFormat.format(num.toInt());
  }

  String _txTypeLabel(String type) {
    const labels = {
      'DEPOSIT': 'Depósito',
      'WITHDRAWAL': 'Retiro',
      'TRANSFER_IN': 'Recibido',
      'TRANSFER_OUT': 'Enviado',
      'CRYPTO_DEPOSIT': 'Crypto',
      'LLO_PURCHASE': 'Compra LLO',
      'LLO_SALE': 'Venta LLO',
      'COMMISSION': 'Comisión',
      'MICROCREDIT_DISBURSEMENT': 'Crédito',
      'MICROCREDIT_PAYMENT': 'Pago crédito',
    };
    return labels[type] ?? type;
  }

  bool _isIncoming(String type) {
    return ['DEPOSIT', 'TRANSFER_IN', 'CRYPTO_DEPOSIT', 'LLO_PURCHASE', 'MICROCREDIT_DISBURSEMENT'].contains(type);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: BlocBuilder<AuthBloc, AuthState>(
          builder: (context, state) {
            final name = state is Authenticated
                ? state.user?.firstName ?? 'Usuario'
                : 'Usuario';
            return Text('Hola, $name!');
          },
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () => context.push('/notifications'),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadAll,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Balance card
              Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      theme.colorScheme.primary,
                      theme.colorScheme.primary.withAlpha(200),
                    ],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: theme.colorScheme.primary.withAlpha(77),
                      blurRadius: 16,
                      offset: const Offset(0, 6),
                    ),
                  ],
                ),
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: _loading
                      ? const Center(
                          child: CircularProgressIndicator(color: Colors.white),
                        )
                      : Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text('Saldo disponible',
                                    style: theme.textTheme.bodyMedium?.copyWith(color: Colors.white70)),
                                IconButton(
                                  icon: Icon(
                                      _balanceVisible ? Icons.visibility : Icons.visibility_off,
                                      color: Colors.white70, size: 20),
                                  onPressed: () => setState(() => _balanceVisible = !_balanceVisible),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Text(
                              _balanceVisible
                                  ? '\$ ${_formatCOP(_wallet?['balance_cop'])} COP'
                                  : '\$ ******** COP',
                              style: theme.textTheme.headlineMedium?.copyWith(
                                  color: Colors.white, fontWeight: FontWeight.w700),
                            ),
                            const SizedBox(height: 6),
                            Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                  decoration: BoxDecoration(
                                      color: const Color(0xFFF9A825),
                                      borderRadius: BorderRadius.circular(8)),
                                  child: Text('LLO',
                                      style: theme.textTheme.labelSmall
                                          ?.copyWith(color: Colors.black87, fontWeight: FontWeight.bold)),
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  _balanceVisible
                                      ? '${_formatCOP(_wallet?['balance_llo'])} SNC'
                                      : '****** SNC',
                                  style: theme.textTheme.titleMedium?.copyWith(
                                      color: const Color(0xFFF9A825), fontWeight: FontWeight.w600),
                                ),
                              ],
                            ),
                            if (_rewards != null) ...[
                              const SizedBox(height: 12),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                                decoration: BoxDecoration(
                                  color: Colors.white.withAlpha(40),
                                  borderRadius: BorderRadius.circular(20),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    const Icon(Icons.emoji_events,
                                        color: Color(0xFFFFD700), size: 16),
                                    const SizedBox(width: 6),
                                    Text(
                                      '${_rewards!['balance']} pts • ${_rewards!['tier']}',
                                      style: const TextStyle(
                                          color: Colors.white,
                                          fontWeight: FontWeight.w600,
                                          fontSize: 12),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ],
                        ),
                ),
              ),
              const SizedBox(height: 24),
              Text('Pagos & Transferencias',
                  style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              GridView.count(
                crossAxisCount: 4,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                mainAxisSpacing: 12,
                crossAxisSpacing: 8,
                childAspectRatio: 0.9,
                children: [
                  _QuickAction(
                    icon: Icons.send,
                    label: 'Enviar',
                    color: theme.colorScheme.primary,
                    onTap: () => context.push('/transfer/send'),
                  ),
                  _QuickAction(
                    icon: Icons.qr_code_2,
                    label: 'QR',
                    color: Colors.purple,
                    onTap: () => context.push('/qr'),
                  ),
                  _QuickAction(
                    icon: Icons.add_circle,
                    label: 'Recargar',
                    color: Colors.green.shade700,
                    onTap: () => context.push('/topup'),
                  ),
                  _QuickAction(
                    icon: Icons.mobile_friendly,
                    label: 'Recarga\nMóvil',
                    color: Colors.blue.shade700,
                    onTap: () => context.push('/mobile-topup'),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text('Productos & Servicios',
                  style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              GridView.count(
                crossAxisCount: 4,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                mainAxisSpacing: 12,
                crossAxisSpacing: 8,
                childAspectRatio: 0.9,
                children: [
                  _QuickAction(
                    icon: Icons.receipt_long,
                    label: 'Pagar\nServicios',
                    color: Colors.orange.shade700,
                    onTap: () => context.push('/bills'),
                  ),
                  _QuickAction(
                    icon: Icons.credit_card,
                    label: 'Tarjetas',
                    color: Colors.indigo,
                    onTap: () => context.push('/cards'),
                  ),
                  _QuickAction(
                    icon: Icons.toll,
                    label: 'Crypto',
                    color: const Color(0xFFF9A825),
                    onTap: () => context.push('/crypto/llanocoin'),
                  ),
                  _QuickAction(
                    icon: Icons.credit_score,
                    label: 'Crédito',
                    color: Colors.teal,
                    onTap: () => context.push('/microcredit'),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text('Recompensas',
                  style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              GridView.count(
                crossAxisCount: 4,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                mainAxisSpacing: 12,
                crossAxisSpacing: 8,
                childAspectRatio: 0.9,
                children: [
                  _QuickAction(
                    icon: Icons.emoji_events,
                    label: 'Mis\nPuntos',
                    color: Colors.amber.shade700,
                    onTap: () => context.push('/rewards'),
                  ),
                  _QuickAction(
                    icon: Icons.group_add,
                    label: 'Referidos',
                    color: Colors.pink.shade400,
                    onTap: () => context.push('/referrals'),
                  ),
                  _QuickAction(
                    icon: Icons.store,
                    label: 'Comercios',
                    color: Colors.deepOrange,
                    onTap: () => context.push('/marketplace'),
                  ),
                  _QuickAction(
                    icon: Icons.history,
                    label: 'Historial',
                    color: Colors.blueGrey,
                    onTap: () => context.push('/wallet/transactions'),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Movimientos recientes',
                      style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                  TextButton(
                    onPressed: () => context.push('/wallet/transactions'),
                    child: const Text('Ver todo'),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              if (_loading)
                const Center(child: Padding(padding: EdgeInsets.all(20), child: CircularProgressIndicator()))
              else if (_transactions.isEmpty)
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Center(
                      child: Column(
                        children: [
                          Icon(Icons.receipt_long,
                              size: 48, color: theme.colorScheme.onSurfaceVariant.withAlpha(100)),
                          const SizedBox(height: 8),
                          Text('Sin movimientos aún',
                              style: theme.textTheme.bodyMedium
                                  ?.copyWith(color: theme.colorScheme.onSurfaceVariant)),
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
                      final isIn = _isIncoming(type);
                      return ListTile(
                        leading: CircleAvatar(
                          backgroundColor:
                              (isIn ? Colors.green : Colors.red).withAlpha(30),
                          child: Icon(
                            isIn ? Icons.arrow_downward : Icons.arrow_upward,
                            color: isIn ? Colors.green : Colors.red,
                            size: 20,
                          ),
                        ),
                        title: Text(_txTypeLabel(type),
                            style: const TextStyle(fontWeight: FontWeight.w600)),
                        subtitle: Text(
                          tx['description']?.toString() ?? '',
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(fontSize: 12),
                        ),
                        trailing: Text(
                          '${isIn ? '+' : '-'}\$${_formatCOP(amount)} $currency',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: isIn ? Colors.green : Colors.red,
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

class _QuickAction extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _QuickAction({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Padding(
        padding: const EdgeInsets.all(4),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircleAvatar(
              radius: 24,
              backgroundColor: color.withAlpha(30),
              child: Icon(icon, color: color, size: 24),
            ),
            const SizedBox(height: 6),
            Text(label,
                textAlign: TextAlign.center,
                style: theme.textTheme.labelSmall
                    ?.copyWith(fontSize: 10, fontWeight: FontWeight.w600)),
          ],
        ),
      ),
    );
  }
}
