import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:llanopay/widgets/balance_card.dart';
import 'package:llanopay/widgets/llanopay_button.dart';
import 'package:llanopay/widgets/empty_state.dart';
import 'package:llanopay/widgets/quick_action_button.dart';
import 'package:llanopay/widgets/credit_score_gauge.dart';
import 'package:llanopay/widgets/notification_badge.dart';

void main() {
  group('BalanceCard', () {
    testWidgets('muestra saldos COP y LLO', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: BalanceCard(
              balanceCop: 1500000,
              balanceLlo: 25.5,
            ),
          ),
        ),
      );

      expect(find.text('Mi Billetera'), findsOneWidget);
      expect(find.text('Pesos Colombianos'), findsOneWidget);
      expect(find.text('Llanocoin'), findsOneWidget);
    });

    testWidgets('oculta saldos al pulsar icono de ojo',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: BalanceCard(
              balanceCop: 1500000,
              balanceLlo: 25.5,
            ),
          ),
        ),
      );

      // Tap the visibility toggle
      await tester.tap(find.byIcon(Icons.visibility));
      await tester.pump();

      expect(find.byIcon(Icons.visibility_off), findsOneWidget);
      expect(find.textContaining('******'), findsWidgets);
    });
  });

  group('LlanoPayButton', () {
    testWidgets('muestra texto del boton primario',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: LlanoPayButton(
              text: 'Continuar',
              onPressed: () {},
            ),
          ),
        ),
      );

      expect(find.text('Continuar'), findsOneWidget);
    });

    testWidgets('muestra indicador de carga', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: LlanoPayButton(
              text: 'Enviando',
              isLoading: true,
            ),
          ),
        ),
      );

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      expect(find.text('Enviando'), findsNothing);
    });

    testWidgets('boton secundario renderiza OutlinedButton',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: LlanoPayButton(
              text: 'Cancelar',
              isSecondary: true,
              onPressed: () {},
            ),
          ),
        ),
      );

      expect(find.byType(OutlinedButton), findsOneWidget);
    });
  });

  group('EmptyState', () {
    testWidgets('muestra titulo y subtitulo', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: EmptyState(
              icon: Icons.inbox,
              title: 'Sin transacciones',
              subtitle: 'Tus movimientos apareceran aqui',
            ),
          ),
        ),
      );

      expect(find.text('Sin transacciones'), findsOneWidget);
      expect(find.text('Tus movimientos apareceran aqui'), findsOneWidget);
    });

    testWidgets('muestra boton de accion cuando se proporciona',
        (WidgetTester tester) async {
      bool tapped = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: EmptyState(
              icon: Icons.inbox,
              title: 'Sin datos',
              actionLabel: 'Recargar',
              onAction: () => tapped = true,
            ),
          ),
        ),
      );

      expect(find.text('Recargar'), findsOneWidget);
      await tester.tap(find.text('Recargar'));
      expect(tapped, isTrue);
    });
  });

  group('QuickActionButton', () {
    testWidgets('muestra icono y etiqueta', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: QuickActionButton(
              icon: Icons.send,
              label: 'Enviar',
              onTap: () {},
            ),
          ),
        ),
      );

      expect(find.text('Enviar'), findsOneWidget);
      expect(find.byIcon(Icons.send), findsOneWidget);
    });
  });

  group('CreditScoreGauge', () {
    testWidgets('muestra puntaje y etiqueta', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: CreditScoreGauge(score: 750),
          ),
        ),
      );

      expect(find.text('750'), findsOneWidget);
      expect(find.text('Excelente'), findsOneWidget);
      expect(find.text('Puntaje Crediticio'), findsOneWidget);
    });
  });

  group('NotificationBadge', () {
    testWidgets('muestra contador de no leidas', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: NotificationBadge(
              unreadCount: 5,
              onTap: () {},
            ),
          ),
        ),
      );

      expect(find.text('5'), findsOneWidget);
      expect(find.byIcon(Icons.notifications_outlined), findsOneWidget);
    });

    testWidgets('no muestra badge cuando el conteo es cero',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: NotificationBadge(
              unreadCount: 0,
              onTap: () {},
            ),
          ),
        ),
      );

      expect(find.text('0'), findsNothing);
    });
  });
}
