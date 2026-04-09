import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../config/theme.dart';

/// Glassmorphism-style card showing COP and LLO balances.
///
/// Features a green gradient background, gold accent for LLO,
/// and an eye toggle to show/hide balance amounts.
class BalanceCard extends StatefulWidget {
  /// Balance in Colombian Pesos.
  final double balanceCop;

  /// Balance in Llanocoin.
  final double balanceLlo;

  /// Optional callback when the card is tapped.
  final VoidCallback? onTap;

  const BalanceCard({
    super.key,
    required this.balanceCop,
    required this.balanceLlo,
    this.onTap,
  });

  @override
  State<BalanceCard> createState() => _BalanceCardState();
}

class _BalanceCardState extends State<BalanceCard> {
  bool _isBalanceVisible = true;

  static final _copFormatter = NumberFormat.currency(
    locale: 'es_CO',
    symbol: '\$',
    decimalDigits: 0,
  );

  static final _lloFormatter = NumberFormat.currency(
    locale: 'es_CO',
    symbol: '',
    decimalDigits: 4,
  );

  void _toggleVisibility() {
    setState(() {
      _isBalanceVisible = !_isBalanceVisible;
    });
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: widget.onTap,
      child: Container(
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
              color: LlanoPayTheme.primaryGreen.withValues(alpha: 0.4),
              blurRadius: 16,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(20),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header row
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Mi Billetera',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            color: Colors.white70,
                          ),
                    ),
                    IconButton(
                      onPressed: _toggleVisibility,
                      icon: Icon(
                        _isBalanceVisible
                            ? Icons.visibility
                            : Icons.visibility_off,
                        color: Colors.white70,
                        size: 22,
                      ),
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(),
                    ),
                  ],
                ),
                const SizedBox(height: 12),

                // COP Balance
                Text(
                  _isBalanceVisible
                      ? _copFormatter.format(widget.balanceCop)
                      : '\$ ******',
                  style: Theme.of(context).textTheme.displaySmall?.copyWith(
                        color: Colors.white,
                        fontWeight: FontWeight.w700,
                      ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Pesos Colombianos',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.white60,
                      ),
                ),

                const SizedBox(height: 20),
                Container(
                  height: 1,
                  color: Colors.white24,
                ),
                const SizedBox(height: 16),

                // LLO Balance
                Row(
                  children: [
                    Container(
                      width: 32,
                      height: 32,
                      decoration: BoxDecoration(
                        color: LlanoPayTheme.secondaryGold,
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: LlanoPayTheme.secondaryGold
                                .withValues(alpha: 0.4),
                            blurRadius: 8,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: const Center(
                        child: Text(
                          'L',
                          style: TextStyle(
                            color: Colors.black87,
                            fontWeight: FontWeight.w800,
                            fontSize: 16,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _isBalanceVisible
                              ? '${_lloFormatter.format(widget.balanceLlo)} LLO'
                              : '****** LLO',
                          style:
                              Theme.of(context).textTheme.titleLarge?.copyWith(
                                    color: LlanoPayTheme.secondaryGold,
                                    fontWeight: FontWeight.w700,
                                  ),
                        ),
                        Text(
                          'Llanocoin',
                          style:
                              Theme.of(context).textTheme.bodySmall?.copyWith(
                                    color: Colors.white54,
                                  ),
                        ),
                      ],
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
