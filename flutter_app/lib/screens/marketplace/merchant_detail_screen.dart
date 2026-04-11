import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';

import '../../config/theme.dart';
import '../../services/api_service.dart';
import '../../config/api_config.dart';

/// Detail screen for a specific marketplace merchant - loads real data from API.
class MerchantDetailScreen extends StatefulWidget {
  final String slug;

  const MerchantDetailScreen({super.key, required this.slug});

  @override
  State<MerchantDetailScreen> createState() => _MerchantDetailScreenState();
}

class _MerchantDetailScreenState extends State<MerchantDetailScreen> {
  bool _loading = true;
  Map<String, dynamic>? _merchant;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final api = context.read<ApiService>();
    final r = await api.get('${ApiConfig.marketplaceMerchants}${widget.slug}/');
    if (mounted) {
      setState(() {
        _loading = false;
        if (r.success) {
          _merchant = r.data as Map<String, dynamic>;
        } else {
          _error = r.message ?? 'Error al cargar el comercio';
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Cargando...'),
          leading: IconButton(
              icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
        ),
        body: const Center(child: CircularProgressIndicator()),
      );
    }
    if (_error != null || _merchant == null) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Error'),
          leading: IconButton(
              icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
        ),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.grey),
              const SizedBox(height: 16),
              Text(_error ?? 'Comercio no encontrado'),
            ],
          ),
        ),
      );
    }

    final merchant = _merchant!;
    final copFormat = NumberFormat.currency(
      locale: 'es_CO',
      symbol: '\$',
      decimalDigits: 0,
    );
    final acceptsLlo = merchant['accepts_llo'] == true;
    final acceptsCop = merchant['accepts_cop'] == true;
    final cat = merchant['category'] as Map<String, dynamic>?;
    final rating = (merchant['rating'] as num?)?.toDouble() ?? 0.0;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Detalle del Comercio'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Container(
              height: 200,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    LlanoPayTheme.primaryGreen,
                    LlanoPayTheme.primaryGreenLight.withOpacity(0.7),
                  ],
                ),
              ),
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      width: 72,
                      height: 72,
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(20),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.15),
                            blurRadius: 12,
                          ),
                        ],
                      ),
                      child: const Icon(
                        Icons.store,
                        color: LlanoPayTheme.primaryGreen,
                        size: 40,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      merchant['business_name']?.toString() ?? '',
                      style: GoogleFonts.montserrat(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      _ratingStars(rating, context),
                      const SizedBox(width: 8),
                      Text(
                        rating.toStringAsFixed(1),
                        style: GoogleFonts.montserrat(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        '(${merchant['total_sales'] ?? 0} ventas)',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      const Spacer(),
                      if (cat != null)
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: LlanoPayTheme.primaryGreen.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            cat['name']?.toString() ?? '',
                            style: GoogleFonts.nunito(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: LlanoPayTheme.primaryGreen,
                            ),
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Text(
                        'Acepta: ',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      if (acceptsCop) _badge('COP', LlanoPayTheme.primaryGreen),
                      const SizedBox(width: 6),
                      if (acceptsLlo)
                        _badge('SuperNova Coin', LlanoPayTheme.secondaryGoldDark),
                    ],
                  ),
                  const SizedBox(height: 20),
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Información',
                              style: Theme.of(context).textTheme.titleMedium),
                          const SizedBox(height: 12),
                          if (merchant['address'] != null)
                            _infoRow(Icons.location_on_outlined,
                                merchant['address'].toString()),
                          if (merchant['city'] != null) ...[
                            const SizedBox(height: 10),
                            _infoRow(Icons.location_city,
                                '${merchant['city']}, ${merchant['department'] ?? ''}'),
                          ],
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  SizedBox(
                    height: 52,
                    child: ElevatedButton.icon(
                      onPressed: () =>
                          _showPayDialog(context, merchant, acceptsLlo, acceptsCop),
                      icon: const Icon(Icons.payment),
                      label: const Text('Pagar a este comercio'),
                    ),
                  ),
                  const SizedBox(height: 24),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showPayDialog(BuildContext context, Map<String, dynamic> merchant,
      bool acceptsLlo, bool acceptsCop) {
    final amountController = TextEditingController();
    String currency = acceptsCop ? 'COP' : 'LLO';

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setSt) => AlertDialog(
          title: Text('Pagar a ${merchant['business_name']}'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: amountController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Monto',
                  prefixText: '\$ ',
                ),
              ),
              const SizedBox(height: 12),
              if (acceptsCop && acceptsLlo)
                DropdownButtonFormField<String>(
                  value: currency,
                  decoration: const InputDecoration(labelText: 'Moneda'),
                  items: [
                    if (acceptsCop)
                      const DropdownMenuItem(value: 'COP', child: Text('COP - Pesos')),
                    if (acceptsLlo)
                      const DropdownMenuItem(
                          value: 'LLO', child: Text('LLO - SuperNova Coin')),
                  ],
                  onChanged: (v) => setSt(() => currency = v ?? 'COP'),
                ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancelar'),
            ),
            ElevatedButton(
              onPressed: () async {
                final amount = amountController.text.trim();
                if (amount.isEmpty) return;
                Navigator.pop(ctx);
                await _payMerchant(merchant['id']?.toString() ?? '', amount, currency);
              },
              child: const Text('Pagar'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _payMerchant(String merchantId, String amount, String currency) async {
    final api = context.read<ApiService>();
    final r = await api.post('/marketplace/payments/', data: {
      'merchant': merchantId,
      'amount': amount,
      'currency': currency,
    });
    if (!mounted) return;
    if (r.success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Pago exitoso!'),
          backgroundColor: Colors.green,
        ),
      );
      context.pop();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(r.message ?? 'Error al pagar'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Widget _badge(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        label,
        style: GoogleFonts.montserrat(
          fontSize: 11,
          fontWeight: FontWeight.w700,
          color: color,
        ),
      ),
    );
  }

  Widget _ratingStars(double rating, BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(5, (index) {
        if (index < rating.floor()) {
          return const Icon(Icons.star,
              size: 16, color: LlanoPayTheme.secondaryGold);
        } else if (index < rating) {
          return const Icon(Icons.star_half,
              size: 16, color: LlanoPayTheme.secondaryGold);
        }
        return Icon(Icons.star_border,
            size: 16, color: LlanoPayTheme.secondaryGold.withOpacity(0.5));
      }),
    );
  }

  Widget _infoRow(IconData icon, String text) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 20, color: LlanoPayTheme.textSecondary),
        const SizedBox(width: 10),
        Expanded(child: Text(text)),
      ],
    );
  }
}
