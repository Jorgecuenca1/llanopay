import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';

import '../../blocs/wallet/wallet_bloc.dart';
import '../../blocs/wallet/wallet_event.dart';
import '../../blocs/wallet/wallet_state.dart';
import '../../config/theme.dart';

class WalletScreen extends StatefulWidget {
  const WalletScreen({super.key});

  @override
  State<WalletScreen> createState() => _WalletScreenState();
}

class _WalletScreenState extends State<WalletScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController;
  final _copFormat = NumberFormat.currency(
    locale: 'es_CO',
    symbol: '\$',
    decimalDigits: 0,
  );
  final _lloFormat = NumberFormat.currency(
    locale: 'es_CO',
    symbol: '',
    decimalDigits: 2,
  );

  String? _currentFilter;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _tabController.addListener(_onTabChanged);
    context.read<WalletBloc>().add(const WalletLoadRequested());
    context.read<WalletBloc>().add(const TransactionsLoadRequested());
  }

  @override
  void dispose() {
    _tabController.removeListener(_onTabChanged);
    _tabController.dispose();
    super.dispose();
  }

  void _onTabChanged() {
    if (!_tabController.indexIsChanging) return;
    Map<String, dynamic>? filters;
    switch (_tabController.index) {
      case 1:
        filters = {'direction': 'income'};
        _currentFilter = 'income';
        break;
      case 2:
        filters = {'direction': 'expense'};
        _currentFilter = 'expense';
        break;
      default:
        _currentFilter = null;
    }
    context
        .read<WalletBloc>()
        .add(TransactionsLoadRequested(filters: filters));
  }

  Future<void> _onRefresh() async {
    context.read<WalletBloc>().add(const WalletLoadRequested());
    context.read<WalletBloc>().add(
          TransactionsLoadRequested(
            filters: _currentFilter != null
                ? {'direction': _currentFilter}
                : null,
          ),
        );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Billetera'),
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
            Tab(text: 'Todas'),
            Tab(text: 'Entradas'),
            Tab(text: 'Salidas'),
          ],
        ),
      ),
      body: RefreshIndicator(
        color: LlanoPayTheme.primaryGreen,
        onRefresh: _onRefresh,
        child: CustomScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          slivers: [
            // -- Balance Card --
            SliverToBoxAdapter(
              child: _buildBalanceCard(),
            ),

            // -- Transactions List --
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(16, 20, 16, 8),
                child: Text(
                  'Movimientos',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ),
            ),
            _buildTransactionsList(),
          ],
        ),
      ),
    );
  }

  Widget _buildBalanceCard() {
    return BlocBuilder<WalletBloc, WalletState>(
      buildWhen: (prev, curr) => curr is WalletLoaded || curr is WalletLoading,
      builder: (context, state) {
        double copBalance = 0;
        double lloBalance = 0;

        if (state is WalletLoaded) {
          copBalance =
              (state.wallet['balance_cop'] as num?)?.toDouble() ?? 0;
          lloBalance =
              (state.wallet['balance_llo'] as num?)?.toDouble() ?? 0;
        }

        return Container(
          margin: const EdgeInsets.all(16),
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            gradient: const LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                LlanoPayTheme.primaryGreen,
                LlanoPayTheme.primaryGreenDark,
              ],
            ),
            boxShadow: [
              BoxShadow(
                color: LlanoPayTheme.primaryGreen.withOpacity(0.3),
                blurRadius: 16,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Saldo total',
                style: GoogleFonts.nunito(
                  color: Colors.white70,
                  fontSize: 14,
                ),
              ),
              const SizedBox(height: 8),
              state is WalletLoading
                  ? const SizedBox(
                      height: 32,
                      width: 140,
                      child: LinearProgressIndicator(
                        color: Colors.white24,
                        backgroundColor: Colors.white10,
                      ),
                    )
                  : Text(
                      '${_copFormat.format(copBalance)} COP',
                      style: GoogleFonts.montserrat(
                        color: Colors.white,
                        fontSize: 28,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 6,
                ),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(
                      Icons.toll,
                      color: LlanoPayTheme.secondaryGold,
                      size: 18,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      '${_lloFormat.format(lloBalance)} LLO',
                      style: GoogleFonts.montserrat(
                        color: Colors.white,
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      '= ${_copFormat.format(lloBalance * 1000)} COP',
                      style: GoogleFonts.nunito(
                        color: Colors.white60,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildTransactionsList() {
    return BlocBuilder<WalletBloc, WalletState>(
      buildWhen: (prev, curr) =>
          curr is TransactionsLoaded || curr is WalletLoading || curr is WalletError,
      builder: (context, state) {
        if (state is WalletLoading) {
          return const SliverFillRemaining(
            child: Center(
              child: CircularProgressIndicator(
                color: LlanoPayTheme.primaryGreen,
              ),
            ),
          );
        }

        if (state is TransactionsLoaded) {
          final transactions = state.transactions;

          if (transactions.isEmpty) {
            return SliverFillRemaining(
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.receipt_long_outlined,
                      size: 56,
                      color: LlanoPayTheme.textSecondary.withOpacity(0.4),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'No hay movimientos',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            color: LlanoPayTheme.textSecondary,
                          ),
                    ),
                  ],
                ),
              ),
            );
          }

          return SliverList(
            delegate: SliverChildBuilderDelegate(
              (context, index) {
                final tx = transactions[index];
                return _buildTransactionTile(tx);
              },
              childCount: transactions.length,
            ),
          );
        }

        if (state is WalletError) {
          return SliverFillRemaining(
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, size: 48, color: LlanoPayTheme.error),
                  const SizedBox(height: 12),
                  Text(state.message),
                  const SizedBox(height: 12),
                  TextButton(
                    onPressed: _onRefresh,
                    child: const Text('Reintentar'),
                  ),
                ],
              ),
            ),
          );
        }

        return const SliverToBoxAdapter(child: SizedBox.shrink());
      },
    );
  }

  Widget _buildTransactionTile(Map<String, dynamic> tx) {
    final type = tx['type'] as String? ?? 'transfer';
    final amount = (tx['amount'] as num?)?.toDouble() ?? 0;
    final description = tx['description'] as String? ?? type;
    final date = tx['created_at'] as String? ?? '';
    final isIncome = amount >= 0;

    IconData icon;
    Color iconColor;
    switch (type) {
      case 'deposit':
        icon = Icons.arrow_downward;
        iconColor = LlanoPayTheme.success;
        break;
      case 'withdrawal':
        icon = Icons.arrow_upward;
        iconColor = LlanoPayTheme.error;
        break;
      case 'crypto_deposit':
        icon = Icons.currency_bitcoin;
        iconColor = const Color(0xFF6C63FF);
        break;
      case 'purchase':
        icon = Icons.store;
        iconColor = LlanoPayTheme.accentBrown;
        break;
      case 'microcredit':
        icon = Icons.credit_score;
        iconColor = LlanoPayTheme.secondaryGoldDark;
        break;
      default:
        icon = Icons.swap_horiz;
        iconColor = LlanoPayTheme.primaryGreen;
    }

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: ListTile(
        onTap: () {
          final id = tx['id']?.toString();
          if (id != null) {
            context.push('/wallet/transaction/$id');
          }
        },
        leading: Container(
          width: 42,
          height: 42,
          decoration: BoxDecoration(
            color: iconColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(icon, color: iconColor, size: 22),
        ),
        title: Text(
          description,
          style: Theme.of(context).textTheme.titleMedium,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Text(
          date.isNotEmpty
              ? DateFormat('dd MMM yyyy, hh:mm a', 'es_CO')
                  .format(DateTime.tryParse(date) ?? DateTime.now())
              : '',
          style: Theme.of(context).textTheme.bodySmall,
        ),
        trailing: Text(
          '${isIncome ? '+' : ''}${_copFormat.format(amount)}',
          style: GoogleFonts.montserrat(
            fontSize: 14,
            fontWeight: FontWeight.w700,
            color: isIncome ? LlanoPayTheme.success : LlanoPayTheme.error,
          ),
        ),
      ),
    );
  }
}
