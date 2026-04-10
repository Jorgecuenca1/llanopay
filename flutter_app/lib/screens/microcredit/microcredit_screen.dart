import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';

import '../../config/theme.dart';
import '../../services/api_service.dart';
import '../../config/api_config.dart';

/// Main microcredit overview: credit score gauge, max credit, active loans.
class MicrocreditScreen extends StatefulWidget {
  const MicrocreditScreen({super.key});

  @override
  State<MicrocreditScreen> createState() => _MicrocreditScreenState();
}

class _MicrocreditScreenState extends State<MicrocreditScreen> {
  bool _loading = true;
  int _creditScore = 0;
  double _maxCredit = 0;
  int _activeLoanCount = 0;
  int _totalLoans = 0;
  List<dynamic> _loans = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final api = context.read<ApiService>();
    final results = await Future.wait([
      api.get(ApiConfig.microcreditProfile),
      api.get(ApiConfig.microcreditLoans),
    ]);
    if (mounted) {
      setState(() {
        _loading = false;
        if (results[0].success) {
          final p = results[0].data as Map<String, dynamic>;
          _creditScore = (p['credit_score'] as num? ?? 0).toInt();
          _maxCredit = double.tryParse(p['max_credit_amount']?.toString() ?? '0') ?? 0;
          _activeLoanCount = (p['active_loans'] as num? ?? 0).toInt();
          _totalLoans = (p['total_loans'] as num? ?? 0).toInt();
        }
        if (results[1].success) {
          final d = results[1].data;
          _loans = d is Map ? (d['results'] as List? ?? []) : (d as List? ?? []);
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final copFormat = NumberFormat.currency(
      locale: 'es_CO',
      symbol: '\$',
      decimalDigits: 0,
    );

    final int creditScore = _creditScore;
    final double maxCredit = _maxCredit;
    final activeLoans = _loans.where((l) => (l as Map)['status'] == 'ACTIVE' || l['status'] == 'DISBURSED').toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Microcredito'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: _loading ? const Center(child: CircularProgressIndicator()) : RefreshIndicator(
        onRefresh: _load,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // -- Credit score gauge --
            Center(
              child: SizedBox(
                width: 200,
                height: 200,
                child: CustomPaint(
                  painter: _CreditScoreGaugePainter(
                    score: creditScore,
                    maxScore: 1000,
                  ),
                  child: Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          '$creditScore',
                          style: GoogleFonts.montserrat(
                            fontSize: 42,
                            fontWeight: FontWeight.w800,
                            color: _scoreColor(creditScore),
                          ),
                        ),
                        Text(
                          'puntos',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),

            const SizedBox(height: 8),

            Center(
              child: Text(
                'Tu perfil crediticio',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: LlanoPayTheme.textSecondary,
                    ),
              ),
            ),

            const SizedBox(height: 20),

            // -- Max credit available --
            Card(
              child: Padding(
                padding: const EdgeInsets.all(18),
                child: Row(
                  children: [
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        color: LlanoPayTheme.secondaryGold.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: const Icon(
                        Icons.account_balance,
                        color: LlanoPayTheme.secondaryGoldDark,
                        size: 26,
                      ),
                    ),
                    const SizedBox(width: 14),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Credito maximo disponible',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${copFormat.format(maxCredit)} COP',
                          style: GoogleFonts.montserrat(
                            fontSize: 22,
                            fontWeight: FontWeight.w800,
                            color: LlanoPayTheme.primaryGreen,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // -- Request credit button --
            SizedBox(
              height: 52,
              child: ElevatedButton.icon(
                onPressed: () => context.push('/microcredit/request'),
                icon: const Icon(Icons.add_circle_outline),
                label: const Text('Solicitar Credito'),
              ),
            ),

            const SizedBox(height: 28),

            // -- Available products --
            Text(
              'Productos disponibles',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 12),

            _buildProductCard(
              context,
              icon: Icons.flash_on,
              iconColor: LlanoPayTheme.secondaryGold,
              title: 'Microcredito Express',
              subtitle: 'Hasta \$500.000 - 30 dias',
              interestRate: '2.5% mensual',
              onTap: () => context.push('/microcredit/request'),
            ),
            const SizedBox(height: 8),
            _buildProductCard(
              context,
              icon: Icons.agriculture,
              iconColor: LlanoPayTheme.primaryGreen,
              title: 'Credito Llanero',
              subtitle: 'Hasta \$2.000.000 - 90 dias',
              interestRate: '1.8% mensual',
              onTap: () => context.push('/microcredit/request'),
            ),
            const SizedBox(height: 8),
            _buildProductCard(
              context,
              icon: Icons.toll,
              iconColor: LlanoPayTheme.accentBrown,
              title: 'Credito con Colateral LLO',
              subtitle: 'Hasta \$5.000.000 - 180 dias',
              interestRate: '1.2% mensual',
              onTap: () => context.push('/microcredit/request'),
            ),

            const SizedBox(height: 28),

            // -- Active loans --
            Text(
              'Creditos activos',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 12),

            if (activeLoans.isEmpty)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(28),
                  child: Center(
                    child: Column(
                      children: [
                        Icon(
                          Icons.credit_score_outlined,
                          size: 48,
                          color: LlanoPayTheme.textSecondary.withOpacity(0.4),
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'Sin creditos activos',
                          style:
                              Theme.of(context).textTheme.bodyMedium?.copyWith(
                                    color: LlanoPayTheme.textSecondary,
                                  ),
                        ),
                      ],
                    ),
                  ),
                ),
              )
            else
              ...activeLoans.map((loan) {
                return Card(
                  margin: const EdgeInsets.only(bottom: 8),
                  child: ListTile(
                    leading: const Icon(Icons.credit_card,
                        color: LlanoPayTheme.primaryGreen),
                    title: Text(loan['product'] as String? ?? 'Credito'),
                    subtitle: Text(
                      '${copFormat.format(loan['amount'])} - ${loan['status']}',
                    ),
                    trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                  ),
                );
              }),

            const SizedBox(height: 24),
          ],
        ),
      ),
    ),
    );
  }

  Widget _buildProductCard(
    BuildContext context, {
    required IconData icon,
    required Color iconColor,
    required String title,
    required String subtitle,
    required String interestRate,
    required VoidCallback onTap,
  }) {
    return Card(
      child: ListTile(
        onTap: onTap,
        leading: CircleAvatar(
          backgroundColor: iconColor.withOpacity(0.1),
          child: Icon(icon, color: iconColor),
        ),
        title: Text(
          title,
          style: Theme.of(context).textTheme.titleMedium,
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(subtitle),
            Text(
              'Tasa: $interestRate',
              style: Theme.of(context).textTheme.labelSmall?.copyWith(
                    color: LlanoPayTheme.primaryGreen,
                  ),
            ),
          ],
        ),
        trailing: const Icon(Icons.arrow_forward_ios, size: 16),
        isThreeLine: true,
      ),
    );
  }

  static Color _scoreColor(int score) {
    if (score >= 750) return LlanoPayTheme.success;
    if (score >= 500) return LlanoPayTheme.secondaryGold;
    return LlanoPayTheme.error;
  }
}

/// Custom painter for the credit score gauge (semi-circular).
class _CreditScoreGaugePainter extends CustomPainter {
  final int score;
  final int maxScore;

  _CreditScoreGaugePainter({
    required this.score,
    required this.maxScore,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height * 0.6);
    final radius = size.width * 0.4;
    const startAngle = math.pi * 0.8;
    const sweepAngle = math.pi * 1.4;

    // Background arc
    final bgPaint = Paint()
      ..color = LlanoPayTheme.divider
      ..style = PaintingStyle.stroke
      ..strokeWidth = 12
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      startAngle,
      sweepAngle,
      false,
      bgPaint,
    );

    // Score arc
    final progress = (score / maxScore).clamp(0.0, 1.0);
    final scoreAngle = sweepAngle * progress;

    Color scoreColor;
    if (score >= 750) {
      scoreColor = LlanoPayTheme.success;
    } else if (score >= 500) {
      scoreColor = LlanoPayTheme.secondaryGold;
    } else {
      scoreColor = LlanoPayTheme.error;
    }

    final scorePaint = Paint()
      ..color = scoreColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = 12
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      startAngle,
      scoreAngle,
      false,
      scorePaint,
    );
  }

  @override
  bool shouldRepaint(covariant _CreditScoreGaugePainter oldDelegate) {
    return oldDelegate.score != score || oldDelegate.maxScore != maxScore;
  }
}
