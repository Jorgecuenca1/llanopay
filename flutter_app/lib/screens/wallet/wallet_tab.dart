import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Wallet tab showing balances and transaction shortcuts.
class WalletTab extends StatelessWidget {
  const WalletTab({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Billetera')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // COP Balance card
            Card(
              child: ListTile(
                leading: CircleAvatar(
                  backgroundColor: theme.colorScheme.primary,
                  child: const Text('COP', style: TextStyle(color: Colors.white, fontSize: 12)),
                ),
                title: const Text('Pesos Colombianos'),
                subtitle: const Text('\$ 0'),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () => context.push('/wallet/transactions'),
              ),
            ),
            const SizedBox(height: 8),
            // LLO Balance card
            Card(
              child: ListTile(
                leading: CircleAvatar(
                  backgroundColor: theme.colorScheme.secondary,
                  child: const Text('LLO', style: TextStyle(color: Colors.black, fontSize: 12)),
                ),
                title: const Text('Llanocoin'),
                subtitle: const Text('0.00 LLO'),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () => context.push('/crypto/llanocoin'),
              ),
            ),
            const SizedBox(height: 24),
            // Actions
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => context.push('/crypto/deposit'),
                    icon: const Icon(Icons.add),
                    label: const Text('Recargar'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {},
                    icon: const Icon(Icons.arrow_downward),
                    label: const Text('Retirar'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
