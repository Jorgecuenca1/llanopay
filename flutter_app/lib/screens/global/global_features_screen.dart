import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../services/api_service.dart';

/// Universal screen that handles all global features (topup, qr, mobile-topup,
/// bills, cards, rewards, referrals).
class GlobalFeatureScreen extends StatefulWidget {
  final String feature;
  const GlobalFeatureScreen({super.key, required this.feature});

  @override
  State<GlobalFeatureScreen> createState() => _GlobalFeatureScreenState();
}

class _GlobalFeatureScreenState extends State<GlobalFeatureScreen> {
  bool _loading = true;
  String? _error;
  dynamic _data;
  final _copFormat = NumberFormat('#,###', 'es_CO');

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  String _title() {
    switch (widget.feature) {
      case 'topup':
        return 'Recargar Saldo';
      case 'qr':
        return 'Pagos QR';
      case 'mobile-topup':
        return 'Recargas Móvil';
      case 'bills':
        return 'Pagar Servicios';
      case 'cards':
        return 'Tarjetas Virtuales';
      case 'rewards':
        return 'Mis Puntos';
      case 'referrals':
        return 'Referidos';
      default:
        return 'SuperNova';
    }
  }

  String _formatCOP(dynamic v) {
    final n = double.tryParse(v?.toString() ?? '0') ?? 0;
    return _copFormat.format(n.toInt());
  }

  Future<void> _loadData() async {
    setState(() => _loading = true);
    try {
      final api = context.read<ApiService>();
      String endpoint;
      switch (widget.feature) {
        case 'topup':
          endpoint = '/global/wallet/topup/';
          break;
        case 'qr':
          endpoint = '/global/qr/list/';
          break;
        case 'mobile-topup':
          endpoint = '/global/mobile-topup/';
          break;
        case 'bills':
          endpoint = '/global/bills/';
          break;
        case 'cards':
          endpoint = '/global/cards/';
          break;
        case 'rewards':
          endpoint = '/global/rewards/';
          break;
        case 'referrals':
          endpoint = '/global/referral/code/';
          break;
        default:
          endpoint = '/wallet/balance/';
      }
      final r = await api.get(endpoint);
      if (mounted) {
        setState(() {
          _loading = false;
          if (r.success) {
            _data = r.data;
          } else {
            _error = r.message ?? 'Error al cargar';
          }
        });
      }
    } catch (e) {
      if (mounted) setState(() {
        _loading = false;
        _error = e.toString();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_title()),
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
        actions: [
          if (['topup', 'qr', 'mobile-topup', 'bills', 'cards'].contains(widget.feature))
            IconButton(icon: const Icon(Icons.add), onPressed: _showCreateDialog),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!, style: const TextStyle(color: Colors.red)))
              : _buildContent(),
    );
  }

  Widget _buildContent() {
    switch (widget.feature) {
      case 'rewards':
        return _buildRewards();
      case 'referrals':
        return _buildReferrals();
      case 'cards':
        return _buildCards();
      default:
        return _buildList();
    }
  }

  Widget _buildRewards() {
    final d = _data as Map<String, dynamic>? ?? {};
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            decoration: BoxDecoration(
              gradient: const LinearGradient(colors: [Color(0xFFFFD700), Color(0xFFF9A825)]),
              borderRadius: BorderRadius.circular(20),
            ),
            padding: const EdgeInsets.all(24),
            child: Column(
              children: [
                const Icon(Icons.emoji_events, size: 64, color: Colors.white),
                const SizedBox(height: 12),
                Text('${d['balance'] ?? 0} puntos',
                    style: const TextStyle(fontSize: 36, color: Colors.white, fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                  decoration: BoxDecoration(
                      color: Colors.white.withAlpha(60), borderRadius: BorderRadius.circular(20)),
                  child: Text('Tier ${d['tier'] ?? 'BRONZE'}',
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  _statRow('Total ganado', '${d['lifetime_earned'] ?? 0} puntos'),
                  const Divider(),
                  _statRow('Total canjeado', '${d['lifetime_redeemed'] ?? 0} puntos'),
                  const Divider(),
                  _statRow('Conversión', '100 pts = \$1,000 COP'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: _showRedeemDialog,
            icon: const Icon(Icons.swap_horiz),
            label: const Text('Canjear puntos'),
            style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16)),
          ),
        ],
      ),
    );
  }

  Widget _buildReferrals() {
    final d = _data as Map<String, dynamic>? ?? {};
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(colors: [
                Theme.of(context).colorScheme.primary,
                Theme.of(context).colorScheme.primary.withAlpha(200),
              ]),
              borderRadius: BorderRadius.circular(20),
            ),
            padding: const EdgeInsets.all(24),
            child: Column(
              children: [
                const Icon(Icons.group_add, size: 48, color: Colors.white),
                const SizedBox(height: 12),
                const Text('Tu código de referido',
                    style: TextStyle(color: Colors.white70, fontSize: 14)),
                const SizedBox(height: 8),
                Text(d['code']?.toString() ?? '------',
                    style: const TextStyle(
                        fontSize: 36, color: Colors.white, fontWeight: FontWeight.bold, letterSpacing: 4)),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      children: [
                        const Icon(Icons.people, color: Colors.green, size: 32),
                        const SizedBox(height: 8),
                        Text('${d['total_referrals'] ?? 0}',
                            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                        const Text('Referidos'),
                      ],
                    ),
                  ),
                ),
              ),
              Expanded(
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      children: [
                        const Icon(Icons.attach_money, color: Colors.amber, size: 32),
                        const SizedBox(height: 8),
                        Text('\$${_formatCOP(d['total_earned'])}',
                            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                        const Text('Ganado'),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Card(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Column(
                children: [
                  Text('Cómo funciona', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  SizedBox(height: 12),
                  ListTile(
                    leading: CircleAvatar(child: Text('1')),
                    title: Text('Comparte tu código'),
                    subtitle: Text('Envíalo a tus amigos'),
                  ),
                  ListTile(
                    leading: CircleAvatar(child: Text('2')),
                    title: Text('Tu amigo se registra'),
                    subtitle: Text('Y usa tu código de referido'),
                  ),
                  ListTile(
                    leading: CircleAvatar(child: Text('3')),
                    title: Text('Ambos ganan \$5,000 COP'),
                    subtitle: Text('Bono de bienvenida automático'),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCards() {
    final d = _data;
    final list = d is Map ? (d['results'] as List? ?? []) : (d as List? ?? []);
    if (list.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.credit_card, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            const Text('No tienes tarjetas virtuales', style: TextStyle(fontSize: 16)),
            const SizedBox(height: 16),
            ElevatedButton.icon(
                onPressed: _showCreateDialog,
                icon: const Icon(Icons.add),
                label: const Text('Crear tarjeta')),
          ],
        ),
      );
    }
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: list.length,
      itemBuilder: (ctx, i) {
        final card = list[i] as Map<String, dynamic>;
        return Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: Container(
            decoration: BoxDecoration(
              gradient: const LinearGradient(colors: [Color(0xFF1B5E20), Color(0xFF388E3C)]),
              borderRadius: BorderRadius.circular(16),
            ),
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: const [
                    Text('SuperNova',
                        style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
                    Icon(Icons.credit_card, color: Colors.white, size: 28),
                  ],
                ),
                const SizedBox(height: 24),
                Text(card['masked_number']?.toString() ?? '****',
                    style: const TextStyle(
                        color: Colors.white, fontSize: 20, letterSpacing: 2, fontFamily: 'monospace')),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('TITULAR',
                            style: TextStyle(color: Colors.white60, fontSize: 10)),
                        Text(card['card_holder_name']?.toString() ?? '',
                            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
                      ],
                    ),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('EXPIRA',
                            style: TextStyle(color: Colors.white60, fontSize: 10)),
                        Text(
                            '${card['expiry_month'].toString().padLeft(2, '0')}/${card['expiry_year'].toString().substring(2)}',
                            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
                      ],
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildList() {
    final d = _data;
    final list = d is Map ? (d['results'] as List? ?? []) : (d as List? ?? []);
    if (list.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.inbox, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            const Text('Sin registros', style: TextStyle(fontSize: 16)),
            const SizedBox(height: 16),
            ElevatedButton.icon(
                onPressed: _showCreateDialog,
                icon: const Icon(Icons.add),
                label: const Text('Crear nuevo')),
          ],
        ),
      );
    }
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: list.length,
      itemBuilder: (ctx, i) {
        final item = list[i] as Map<String, dynamic>;
        return Card(
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: Theme.of(context).colorScheme.primary.withAlpha(30),
              child: Icon(_iconForFeature(), color: Theme.of(context).colorScheme.primary),
            ),
            title: Text(_titleForItem(item)),
            subtitle: Text(_subtitleForItem(item)),
            trailing: Text('\$${_formatCOP(item['amount'])}',
                style: const TextStyle(fontWeight: FontWeight.bold)),
          ),
        );
      },
    );
  }

  IconData _iconForFeature() {
    switch (widget.feature) {
      case 'topup':
        return Icons.add_circle;
      case 'qr':
        return Icons.qr_code;
      case 'mobile-topup':
        return Icons.mobile_friendly;
      case 'bills':
        return Icons.receipt_long;
      default:
        return Icons.payment;
    }
  }

  String _titleForItem(Map<String, dynamic> item) {
    if (widget.feature == 'qr') return item['code']?.toString() ?? '';
    if (widget.feature == 'mobile-topup') return item['phone_number']?.toString() ?? '';
    if (widget.feature == 'bills') return item['company']?.toString() ?? '';
    return item['method_display']?.toString() ?? item['description']?.toString() ?? '';
  }

  String _subtitleForItem(Map<String, dynamic> item) {
    return '${item['status']} • ${item['created_at']?.toString().substring(0, 10) ?? ''}';
  }

  Widget _statRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }

  void _showCreateDialog() {
    switch (widget.feature) {
      case 'topup':
        _showTopupDialog();
        break;
      case 'mobile-topup':
        _showMobileTopupDialog();
        break;
      case 'bills':
        _showBillDialog();
        break;
      case 'cards':
        _createCard();
        break;
      case 'qr':
        _showQRDialog();
        break;
    }
  }

  void _showTopupDialog() {
    final amountCtrl = TextEditingController();
    String method = 'CARD';
    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setSt) => AlertDialog(
          title: const Text('Recargar saldo'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: amountCtrl,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Monto COP'),
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: method,
                decoration: const InputDecoration(labelText: 'Método'),
                items: const [
                  DropdownMenuItem(value: 'CARD', child: Text('Tarjeta')),
                  DropdownMenuItem(value: 'BANK', child: Text('Banco')),
                  DropdownMenuItem(value: 'CASH', child: Text('Efectivo')),
                ],
                onChanged: (v) => setSt(() => method = v ?? 'CARD'),
              ),
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
            ElevatedButton(
              onPressed: () async {
                Navigator.pop(ctx);
                final api = context.read<ApiService>();
                final r = await api.post('/global/wallet/topup/',
                    data: {'amount': amountCtrl.text, 'currency': 'COP', 'method': method});
                if (r.success) {
                  ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Recarga exitosa!')));
                  _loadData();
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text(r.message ?? 'Error')));
                }
              },
              child: const Text('Recargar'),
            ),
          ],
        ),
      ),
    );
  }

  void _showMobileTopupDialog() {
    final phoneCtrl = TextEditingController();
    final amountCtrl = TextEditingController();
    String operator = 'Claro';
    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setSt) => AlertDialog(
          title: const Text('Recargar celular'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(controller: phoneCtrl, decoration: const InputDecoration(labelText: 'Número')),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  value: operator,
                  decoration: const InputDecoration(labelText: 'Operador'),
                  items: ['Claro', 'Movistar', 'Tigo', 'WOM']
                      .map((o) => DropdownMenuItem(value: o, child: Text(o)))
                      .toList(),
                  onChanged: (v) => setSt(() => operator = v ?? 'Claro'),
                ),
                const SizedBox(height: 12),
                TextField(
                    controller: amountCtrl,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(labelText: 'Monto COP')),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
            ElevatedButton(
              onPressed: () async {
                Navigator.pop(ctx);
                final api = context.read<ApiService>();
                final r = await api.post('/global/mobile-topup/', data: {
                  'phone_number': phoneCtrl.text,
                  'operator': operator,
                  'amount': amountCtrl.text,
                  'currency': 'COP',
                  'country_code': 'CO',
                });
                if (r.success) {
                  ScaffoldMessenger.of(context)
                      .showSnackBar(const SnackBar(content: Text('Recarga enviada!')));
                  _loadData();
                } else {
                  ScaffoldMessenger.of(context)
                      .showSnackBar(SnackBar(content: Text(r.message ?? 'Error')));
                }
              },
              child: const Text('Recargar'),
            ),
          ],
        ),
      ),
    );
  }

  void _showBillDialog() {
    final companyCtrl = TextEditingController();
    final accountCtrl = TextEditingController();
    final amountCtrl = TextEditingController();
    String category = 'ELECTRICITY';
    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setSt) => AlertDialog(
          title: const Text('Pagar servicio'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                DropdownButtonFormField<String>(
                  value: category,
                  decoration: const InputDecoration(labelText: 'Tipo'),
                  items: const [
                    DropdownMenuItem(value: 'ELECTRICITY', child: Text('Electricidad')),
                    DropdownMenuItem(value: 'WATER', child: Text('Agua')),
                    DropdownMenuItem(value: 'GAS', child: Text('Gas')),
                    DropdownMenuItem(value: 'INTERNET', child: Text('Internet')),
                    DropdownMenuItem(value: 'TV', child: Text('TV')),
                    DropdownMenuItem(value: 'PHONE', child: Text('Teléfono')),
                  ],
                  onChanged: (v) => setSt(() => category = v ?? 'ELECTRICITY'),
                ),
                const SizedBox(height: 12),
                TextField(
                    controller: companyCtrl,
                    decoration: const InputDecoration(labelText: 'Empresa')),
                const SizedBox(height: 12),
                TextField(
                    controller: accountCtrl,
                    decoration: const InputDecoration(labelText: 'Cuenta/Contrato')),
                const SizedBox(height: 12),
                TextField(
                    controller: amountCtrl,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(labelText: 'Monto COP')),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
            ElevatedButton(
              onPressed: () async {
                Navigator.pop(ctx);
                final api = context.read<ApiService>();
                final r = await api.post('/global/bills/', data: {
                  'category': category,
                  'company': companyCtrl.text,
                  'account_number': accountCtrl.text,
                  'amount': amountCtrl.text,
                  'currency': 'COP',
                });
                if (r.success) {
                  ScaffoldMessenger.of(context)
                      .showSnackBar(const SnackBar(content: Text('Pago realizado!')));
                  _loadData();
                } else {
                  ScaffoldMessenger.of(context)
                      .showSnackBar(SnackBar(content: Text(r.message ?? 'Error')));
                }
              },
              child: const Text('Pagar'),
            ),
          ],
        ),
      ),
    );
  }

  void _createCard() async {
    final api = context.read<ApiService>();
    final r = await api.post('/global/cards/', data: {'currency': 'USD', 'spending_limit': '1000'});
    if (r.success) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Tarjeta creada!')));
      _loadData();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(r.message ?? 'Error')));
    }
  }

  void _showQRDialog() {
    final amountCtrl = TextEditingController();
    final descCtrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Generar QR para cobrar'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
                controller: amountCtrl,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Monto (opcional)')),
            const SizedBox(height: 12),
            TextField(controller: descCtrl, decoration: const InputDecoration(labelText: 'Descripción')),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(ctx);
              final api = context.read<ApiService>();
              final data = <String, dynamic>{'currency': 'COP', 'description': descCtrl.text};
              if (amountCtrl.text.isNotEmpty) data['amount'] = amountCtrl.text;
              final r = await api.post('/global/qr/', data: data);
              if (r.success) {
                final qr = r.data as Map<String, dynamic>;
                showDialog(
                  context: context,
                  builder: (_) => AlertDialog(
                    title: const Text('Tu QR'),
                    content: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.qr_code_2, size: 120),
                        const SizedBox(height: 12),
                        SelectableText(qr['code']?.toString() ?? '',
                            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                      ],
                    ),
                    actions: [
                      TextButton(onPressed: () => Navigator.pop(context), child: const Text('OK')),
                    ],
                  ),
                );
                _loadData();
              } else {
                ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(r.message ?? 'Error')));
              }
            },
            child: const Text('Generar'),
          ),
        ],
      ),
    );
  }

  void _showRedeemDialog() {
    final ctrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Canjear puntos'),
        content: TextField(
          controller: ctrl,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(
              labelText: 'Puntos a canjear', helperText: '100 pts = \$1,000 COP'),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(ctx);
              final api = context.read<ApiService>();
              final r = await api.post('/global/rewards/redeem/', data: {'points': ctrl.text});
              if (r.success) {
                ScaffoldMessenger.of(context)
                    .showSnackBar(const SnackBar(content: Text('Canje exitoso!')));
                _loadData();
              } else {
                ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(r.message ?? 'Error')));
              }
            },
            child: const Text('Canjear'),
          ),
        ],
      ),
    );
  }
}
