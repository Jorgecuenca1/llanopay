import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';

import '../../blocs/auth/auth_bloc.dart';
import '../../blocs/auth/auth_state.dart';
import '../../blocs/wallet/wallet_bloc.dart';
import '../../blocs/wallet/wallet_event.dart';
import '../../blocs/wallet/wallet_state.dart';
import '../../config/theme.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
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

  @override
  void initState() {
    super.initState();
    context.read<WalletBloc>().add(const WalletLoadRequested());
  }

  @override
  Widget build(BuildContext context) {
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
          Stack(
            children: [
              IconButton(
                icon: const Icon(Icons.notifications_outlined),
                onPressed: () => context.push('/notifications'),
              ),
              Positioned(
                right: 10,
                top: 10,
                child: Container(
                  width: 10,
                  height: 10,
                  decoration: const BoxDecoration(
                    color: LlanoPayTheme.error,
                    shape: BoxShape.circle,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
      body: RefreshIndicator(
        color: LlanoPayTheme.primaryGreen,
        onRefresh: () async {
          context.read<WalletBloc>().add(const WalletLoadRequested());
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // -- Balance Card (Glassmorphism) --
              _buildBalanceCard(),

              const SizedBox(height: 24),

              // -- Quick Actions --
              _buildQuickActions(),

              const SizedBox(height: 28),

              // -- Active Promotions --
              Text(
                'Promociones activas',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 12),
              _buildPromotionsCarousel(),

              const SizedBox(height: 28),

              // -- Recent Transactions --
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Transacciones recientes',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  TextButton(
                    onPressed: () => context.go('/home/wallet'),
                    child: const Text('Ver todas'),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              _buildRecentTransactions(),

              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildBalanceCard() {
    return BlocBuilder<WalletBloc, WalletState>(
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
          width: double.infinity,
          padding: const EdgeInsets.all(24),
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
                color: LlanoPayTheme.primaryGreen.withOpacity(0.35),
                blurRadius: 20,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(20),
            child: BackdropFilter(
              filter: ImageFilter.blur(sigmaX: 0, sigmaY: 0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Saldo disponible',
                        style: GoogleFonts.nunito(
                          color: Colors.white70,
                          fontSize: 14,
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          'LlanoPay',
                          style: GoogleFonts.montserrat(
                            color: Colors.white,
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),

                  // COP balance
                  state is WalletLoading
                      ? const SizedBox(
                          height: 36,
                          width: 120,
                          child: LinearProgressIndicator(
                            color: Colors.white24,
                            backgroundColor: Colors.white10,
                          ),
                        )
                      : Text(
                          '${_copFormat.format(copBalance)} COP',
                          style: GoogleFonts.montserrat(
                            color: Colors.white,
                            fontSize: 30,
                            fontWeight: FontWeight.w800,
                          ),
                        ),

                  const SizedBox(height: 8),

                  // LLO balance
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 3,
                        ),
                        decoration: BoxDecoration(
                          color: LlanoPayTheme.secondaryGold.withOpacity(0.3),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          'LLO',
                          style: GoogleFonts.montserrat(
                            color: LlanoPayTheme.secondaryGold,
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '${_lloFormat.format(lloBalance)} Llanocoin',
                        style: GoogleFonts.nunito(
                          color: Colors.white.withOpacity(0.9),
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildQuickActions() {
    final actions = [
      {
        'icon': Icons.send,
        'label': 'Enviar',
        'color': LlanoPayTheme.primaryGreen,
        'onTap': () => context.go('/home/send'),
      },
      {
        'icon': Icons.qr_code,
        'label': 'Recibir',
        'color': LlanoPayTheme.secondaryGold,
        'onTap': () => context.push('/wallet/receive'),
      },
      {
        'icon': Icons.currency_bitcoin,
        'label': 'Depositar\nCrypto',
        'color': const Color(0xFF6C63FF),
        'onTap': () => context.push('/crypto/deposit'),
      },
      {
        'icon': Icons.toll,
        'label': 'Llanocoin',
        'color': LlanoPayTheme.accentBrown,
        'onTap': () => context.push('/crypto/llanocoin'),
      },
    ];

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: actions.map((action) {
        return GestureDetector(
          onTap: action['onTap'] as VoidCallback,
          child: Column(
            children: [
              Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(
                  color: (action['color'] as Color).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Icon(
                  action['icon'] as IconData,
                  color: action['color'] as Color,
                  size: 26,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                action['label'] as String,
                style: Theme.of(context).textTheme.labelMedium,
                textAlign: TextAlign.center,
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildPromotionsCarousel() {
    // Placeholder promotions
    final promotions = [
      {
        'title': 'Primer envio gratis',
        'subtitle': 'Envia dinero sin comision',
        'color': LlanoPayTheme.primaryGreen,
      },
      {
        'title': 'Gana Llanocoin',
        'subtitle': 'Recibe 5 LLO por cada referido',
        'color': LlanoPayTheme.secondaryGoldDark,
      },
      {
        'title': 'Paga en comercios',
        'subtitle': '10% dcto en comercios aliados',
        'color': LlanoPayTheme.accentBrown,
      },
    ];

    return SizedBox(
      height: 130,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: promotions.length,
        separatorBuilder: (_, __) => const SizedBox(width: 12),
        itemBuilder: (context, index) {
          final promo = promotions[index];
          return Container(
            width: 260,
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  (promo['color'] as Color),
                  (promo['color'] as Color).withOpacity(0.7),
                ],
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                const Icon(
                  Icons.local_offer_outlined,
                  color: Colors.white70,
                  size: 28,
                ),
                const SizedBox(height: 12),
                Text(
                  promo['title'] as String,
                  style: GoogleFonts.montserrat(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  promo['subtitle'] as String,
                  style: GoogleFonts.nunito(
                    color: Colors.white70,
                    fontSize: 13,
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildRecentTransactions() {
    return BlocBuilder<WalletBloc, WalletState>(
      builder: (context, state) {
        if (state is WalletLoading) {
          return const Center(
            child: Padding(
              padding: EdgeInsets.all(32),
              child: CircularProgressIndicator(
                color: LlanoPayTheme.primaryGreen,
              ),
            ),
          );
        }

        // Use real transactions from loaded state, or show placeholder
        if (state is WalletLoaded) {
          final transactions =
              (state.balanceSummary['recent_transactions'] as List<dynamic>?)
                      ?.take(5)
                      .toList() ??
                  [];

          if (transactions.isEmpty) {
            return _buildEmptyTransactions();
          }

          return Column(
            children: transactions.map((tx) {
              final txMap = tx as Map<String, dynamic>;
              return _buildTransactionTile(txMap);
            }).toList(),
          );
        }

        return _buildEmptyTransactions();
      },
    );
  }

  Widget _buildEmptyTransactions() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 40),
      child: Column(
        children: [
          Icon(
            Icons.receipt_long_outlined,
            size: 48,
            color: LlanoPayTheme.textSecondary.withOpacity(0.4),
          ),
          const SizedBox(height: 12),
          Text(
            'Sin transacciones recientes',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: LlanoPayTheme.textSecondary,
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildTransactionTile(Map<String, dynamic> tx) {
    final type = tx['type'] as String? ?? 'transfer';
    final amount = (tx['amount'] as num?)?.toDouble() ?? 0;
    final description = tx['description'] as String? ?? '';
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
      default:
        icon = Icons.swap_horiz;
        iconColor = LlanoPayTheme.primaryGreen;
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
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
          description.isNotEmpty ? description : type,
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
