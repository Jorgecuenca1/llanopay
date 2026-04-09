import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../config/theme.dart';

/// Circular gauge displaying the user's credit score (0-1000).
///
/// Color transitions: red (0-300), orange (300-500),
/// yellow (500-700), green (700-1000).
class CreditScoreGauge extends StatelessWidget {
  /// The credit score value (0-1000).
  final int score;

  /// Diameter of the gauge. Defaults to 200.
  final double size;

  /// Optional label below the score. Defaults to "Puntaje Crediticio".
  final String? label;

  const CreditScoreGauge({
    super.key,
    required this.score,
    this.size = 200,
    this.label,
  });

  Color get _scoreColor {
    if (score < 300) return const Color(0xFFD32F2F); // Red
    if (score < 500) return const Color(0xFFFF9800); // Orange
    if (score < 700) return const Color(0xFFFDD835); // Yellow
    return LlanoPayTheme.success; // Green
  }

  String get _scoreLabel {
    if (score < 300) return 'Bajo';
    if (score < 500) return 'Regular';
    if (score < 700) return 'Bueno';
    return 'Excelente';
  }

  @override
  Widget build(BuildContext context) {
    final normalizedScore = score.clamp(0, 1000);

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          width: size,
          height: size,
          child: CustomPaint(
            painter: _GaugePainter(
              score: normalizedScore,
              scoreColor: _scoreColor,
            ),
            child: Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    '$normalizedScore',
                    style: Theme.of(context)
                        .textTheme
                        .displayMedium
                        ?.copyWith(
                          color: _scoreColor,
                          fontWeight: FontWeight.w800,
                        ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    _scoreLabel,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: _scoreColor,
                          fontWeight: FontWeight.w600,
                        ),
                  ),
                ],
              ),
            ),
          ),
        ),
        const SizedBox(height: 12),
        Text(
          label ?? 'Puntaje Crediticio',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: LlanoPayTheme.textSecondary,
              ),
        ),
      ],
    );
  }
}

class _GaugePainter extends CustomPainter {
  final int score;
  final Color scoreColor;

  _GaugePainter({
    required this.score,
    required this.scoreColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width / 2) - 16;
    const startAngle = math.pi * 0.75; // 135 degrees
    const totalSweep = math.pi * 1.5; // 270 degrees

    // Background track
    final trackPaint = Paint()
      ..color = LlanoPayTheme.divider
      ..style = PaintingStyle.stroke
      ..strokeWidth = 12
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      startAngle,
      totalSweep,
      false,
      trackPaint,
    );

    // Score arc
    final sweepAngle = totalSweep * (score / 1000);
    final scorePaint = Paint()
      ..color = scoreColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = 12
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      startAngle,
      sweepAngle,
      false,
      scorePaint,
    );

    // Tick marks at color boundaries (300, 500, 700)
    final tickPaint = Paint()
      ..color = LlanoPayTheme.textSecondary.withValues(alpha: 0.3)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5;

    for (final boundary in [300, 500, 700]) {
      final tickAngle = startAngle + (totalSweep * (boundary / 1000));
      final innerPoint = Offset(
        center.dx + (radius - 10) * math.cos(tickAngle),
        center.dy + (radius - 10) * math.sin(tickAngle),
      );
      final outerPoint = Offset(
        center.dx + (radius + 10) * math.cos(tickAngle),
        center.dy + (radius + 10) * math.sin(tickAngle),
      );
      canvas.drawLine(innerPoint, outerPoint, tickPaint);
    }
  }

  @override
  bool shouldRepaint(_GaugePainter oldDelegate) {
    return oldDelegate.score != score || oldDelegate.scoreColor != scoreColor;
  }
}
