import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Transfer tab showing recent transfers and send action.
class TransferTab extends StatelessWidget {
  const TransferTab({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Transferencias')),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.swap_horiz,
              size: 64,
              color: theme.colorScheme.onSurfaceVariant,
            ),
            const SizedBox(height: 16),
            Text(
              'Envia y recibe dinero al instante',
              style: theme.textTheme.bodyLarge?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () => context.push('/transfer/send'),
              icon: const Icon(Icons.send),
              label: const Text('Enviar Dinero'),
            ),
          ],
        ),
      ),
    );
  }
}
