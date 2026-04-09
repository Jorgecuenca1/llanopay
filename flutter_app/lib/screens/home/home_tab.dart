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
  bool _loading = true;
  bool _balanceVisible = true;
  final _copFormat = NumberFormat('#,###', 'es_CO');

  @override
  void initState() {
    super.initState();
    _loadWallet();
  }

  Future<void> _loadWallet() async {
    setState(() => _loading = true);
    try {
      final api = context.read<ApiService>();
      final response = await api.get(ApiConfig.walletBalance);
      if (response.success && response.data != null) {
        setState(() {
          _wallet = response.data as Map<String, dynamic>;
          _loading = false;
        });
      } else {
        setState(() => _loading = false);
      }
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  String _formatCOP(dynamic value) {
    final num = double.tryParse(value?.toString() ?? '0') ?? 0;
    return _copFormat.format(num.toInt());
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
        onRefresh: _loadWallet,
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
                                Text(
                                  'Saldo disponible',
                                  style: theme.textTheme.bodyMedium?.copyWith(
                                    color: Colors.white70,
                                  ),
                                ),
                                IconButton(
                                  icon: Icon(
                                    _balanceVisible
                                        ? Icons.visibility
                                        : Icons.visibility_off,
                                    color: Colors.white70,
                                    size: 20,
                                  ),
                                  onPressed: () => setState(
                                      () => _balanceVisible = !_balanceVisible),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Text(
                              _balanceVisible
                                  ? '\$ ${_formatCOP(_wallet?['balance_cop'])} COP'
                                  : '\$ ******** COP',
                              style: theme.textTheme.headlineMedium?.copyWith(
                                color: Colors.white,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                            const SizedBox(height: 6),
                            Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 8, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFFF9A825),
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Text(
                                    'LLO',
                                    style:
                                        theme.textTheme.labelSmall?.copyWith(
                                      color: Colors.black87,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  _balanceVisible
                                      ? '${_formatCOP(_wallet?['balance_llo'])} Llanocoin'
                                      : '****** Llanocoin',
                                  style: theme.textTheme.titleMedium?.copyWith(
                                    color: const Color(0xFFF9A825),
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                            if (_wallet?['llo_cop_equivalent'] != null) ...[
                              const SizedBox(height: 4),
                              Text(
                                _balanceVisible
                                    ? '~ \$ ${_formatCOP(_wallet?['llo_cop_equivalent'])} COP en LLO'
                                    : '',
                                style: theme.textTheme.bodySmall?.copyWith(
                                  color: Colors.white54,
                                ),
                              ),
                            ],
                          ],
                        ),
                ),
              ),
              const SizedBox(height: 24),
              // Quick actions
              Text('Acciones rapidas',
                  style: theme.textTheme.titleLarge
                      ?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _QuickAction(
                    icon: Icons.send,
                    label: 'Enviar',
                    color: theme.colorScheme.primary,
                    onTap: () => context.push('/transfer/send'),
                  ),
                  _QuickAction(
                    icon: Icons.download,
                    label: 'Depositar',
                    color: Colors.blue.shade700,
                    onTap: () => context.push('/crypto/deposit'),
                  ),
                  _QuickAction(
                    icon: Icons.toll,
                    label: 'Llanocoin',
                    color: const Color(0xFFF9A825),
                    onTap: () => context.push('/crypto/llanocoin'),
                  ),
                  _QuickAction(
                    icon: Icons.credit_score,
                    label: 'Credito',
                    color: Colors.orange.shade700,
                    onTap: () => context.push('/microcredit'),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              Text('Movimientos recientes',
                  style: theme.textTheme.titleLarge
                      ?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
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
                        Text(
                          'Sin movimientos aun',
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Tus transacciones apareceran aqui',
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant
                                .withAlpha(150),
                          ),
                        ),
                      ],
                    ),
                  ),
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
        padding: const EdgeInsets.all(8),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircleAvatar(
              radius: 26,
              backgroundColor: color.withAlpha(30),
              child: Icon(icon, color: color),
            ),
            const SizedBox(height: 8),
            Text(label, style: theme.textTheme.labelMedium),
          ],
        ),
      ),
    );
  }
}
