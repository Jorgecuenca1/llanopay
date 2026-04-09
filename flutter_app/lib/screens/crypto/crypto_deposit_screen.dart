import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:qr_flutter/qr_flutter.dart';

/// Screen for depositing crypto funds into the LlanoPay wallet.
class CryptoDepositScreen extends StatefulWidget {
  const CryptoDepositScreen({super.key});

  @override
  State<CryptoDepositScreen> createState() => _CryptoDepositScreenState();
}

class _CryptoDepositScreenState extends State<CryptoDepositScreen> {
  final _txHashController = TextEditingController();
  final _amountController = TextEditingController();

  String _selectedCurrency = 'USDT';
  String _selectedNetwork = 'TRC20';
  bool _isVerifying = false;

  static const Map<String, List<String>> _networks = {
    'USDT': ['TRC20', 'ERC20', 'BEP20'],
    'ETH': ['ERC20'],
    'BTC': ['Bitcoin'],
  };

  static const Map<String, String> _walletAddresses = {
    'USDT_TRC20': 'TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7',
    'USDT_ERC20': '0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18',
    'USDT_BEP20': '0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18',
    'ETH_ERC20': '0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18',
    'BTC_Bitcoin': 'bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq',
  };

  String get _currentAddress {
    return _walletAddresses['${_selectedCurrency}_$_selectedNetwork'] ?? '';
  }

  @override
  void dispose() {
    _txHashController.dispose();
    _amountController.dispose();
    super.dispose();
  }

  Future<void> _onVerify() async {
    if (_txHashController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Ingresa el hash de la transaccion'),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
      return;
    }
    if (_amountController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Ingresa el monto enviado'),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
      return;
    }

    setState(() => _isVerifying = true);

    // TODO: Integrate with CryptoService
    await Future.delayed(const Duration(seconds: 2));

    if (!mounted) return;
    setState(() => _isVerifying = false);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Text(
            'Deposito en verificacion. Te notificaremos cuando se confirme.'),
        backgroundColor: Theme.of(context).colorScheme.primary,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final availableNetworks = _networks[_selectedCurrency] ?? [];

    return Scaffold(
      appBar: AppBar(
        title: const Text('Depositar Crypto'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Selecciona la criptomoneda',
              style: theme.textTheme.titleMedium,
            ),
            const SizedBox(height: 12),
            Row(
              children: ['USDT', 'ETH', 'BTC'].map((currency) {
                final isSelected = _selectedCurrency == currency;
                return Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    child: ChoiceChip(
                      label: Text(currency),
                      selected: isSelected,
                      onSelected: (selected) {
                        if (selected) {
                          setState(() {
                            _selectedCurrency = currency;
                            _selectedNetwork = _networks[currency]!.first;
                          });
                        }
                      },
                      selectedColor: theme.colorScheme.primary,
                      labelStyle: TextStyle(
                        color: isSelected ? Colors.white : null,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 20),
            Text('Red', style: theme.textTheme.titleMedium),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _selectedNetwork,
              decoration: const InputDecoration(
                prefixIcon: Icon(Icons.lan_outlined),
              ),
              items: availableNetworks
                  .map((net) => DropdownMenuItem(value: net, child: Text(net)))
                  .toList(),
              onChanged: (v) {
                if (v != null) setState(() => _selectedNetwork = v);
              },
            ),
            const SizedBox(height: 24),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    Text('Direccion de deposito',
                        style: theme.textTheme.titleMedium),
                    const SizedBox(height: 16),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: QrImageView(
                        data: _currentAddress,
                        version: QrVersions.auto,
                        size: 180,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.surfaceContainerHighest,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Row(
                        children: [
                          Expanded(
                            child: Text(
                              _currentAddress,
                              style: const TextStyle(
                                fontSize: 12,
                                fontFamily: 'monospace',
                              ),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          IconButton(
                            icon: Icon(
                              Icons.copy,
                              size: 20,
                              color: theme.colorScheme.primary,
                            ),
                            onPressed: () {
                              Clipboard.setData(
                                ClipboardData(text: _currentAddress),
                              );
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: const Text('Direccion copiada'),
                                  backgroundColor: theme.colorScheme.primary,
                                ),
                              );
                            },
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: theme.colorScheme.secondary.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: theme.colorScheme.secondary.withOpacity(0.3),
                ),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(
                    Icons.warning_amber_rounded,
                    color: theme.colorScheme.secondary,
                    size: 22,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Envia solo $_selectedCurrency por la red $_selectedNetwork a esta direccion. '
                      'Enviar otra criptomoneda o usar otra red puede resultar en la perdida de fondos.',
                      style: theme.textTheme.bodySmall,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            TextFormField(
              controller: _txHashController,
              decoration: const InputDecoration(
                labelText: 'Hash de la transaccion',
                hintText: '0x...',
                prefixIcon: Icon(Icons.tag),
              ),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _amountController,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: 'Monto enviado',
                hintText: '0.00',
                prefixIcon: const Icon(Icons.attach_money),
                suffixText: _selectedCurrency,
              ),
            ),
            const SizedBox(height: 28),
            SizedBox(
              height: 52,
              child: ElevatedButton.icon(
                onPressed: _isVerifying ? null : _onVerify,
                icon: _isVerifying
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          color: Colors.white,
                          strokeWidth: 2,
                        ),
                      )
                    : const Icon(Icons.verified_outlined),
                label: Text(
                  _isVerifying ? 'Verificando...' : 'Verificar Deposito',
                ),
              ),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}
