import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';

import '../../config/theme.dart';

/// Detail screen for a specific marketplace merchant.
class MerchantDetailScreen extends StatelessWidget {
  final String slug;

  const MerchantDetailScreen({super.key, required this.slug});

  // Placeholder merchant data (in real app, fetched from API)
  Map<String, dynamic> get _merchant => {
        'name': 'Restaurante El Llanero',
        'category': 'Restaurantes',
        'city': 'Villavicencio',
        'department': 'Meta',
        'address': 'Cra 30 #25-10, Villavicencio, Meta',
        'phone': '+57 311 000 0000',
        'rating': 4.5,
        'review_count': 23,
        'accepts_cop': true,
        'accepts_llo': true,
        'whatsapp': '+573110000000',
        'description':
            'Autentica comida llanera. Mamona, carne a la llanera, y los mejores jugos del llano.',
        'promotions': [
          {
            'title': '10% dcto pagando con LLO',
            'expires': '2026-04-01',
          },
        ],
        'reviews': [
          {
            'user': 'Juan P.',
            'rating': 5,
            'comment': 'Excelente mamona, totalmente recomendado!',
            'date': '2026-02-20',
          },
          {
            'user': 'Maria L.',
            'rating': 4,
            'comment': 'Muy buena comida, el servicio puede mejorar.',
            'date': '2026-02-15',
          },
        ],
      };

  @override
  Widget build(BuildContext context) {
    final merchant = _merchant;
    final copFormat = NumberFormat.currency(
      locale: 'es_CO',
      symbol: '\$',
      decimalDigits: 0,
    );

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
            // -- Cover image / logo --
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
                      merchant['name'] as String,
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
                  // -- Rating & category --
                  Row(
                    children: [
                      _ratingStars(
                          (merchant['rating'] as num).toDouble(), context),
                      const SizedBox(width: 8),
                      Text(
                        '${merchant['rating']}',
                        style: GoogleFonts.montserrat(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        '(${merchant['review_count']} resenas)',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      const Spacer(),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color:
                              LlanoPayTheme.primaryGreen.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          merchant['category'] as String,
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

                  // -- Accepts badges --
                  Row(
                    children: [
                      Text(
                        'Acepta: ',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      if (merchant['accepts_cop'] == true)
                        _badge('COP', LlanoPayTheme.primaryGreen),
                      const SizedBox(width: 6),
                      if (merchant['accepts_llo'] == true)
                        _badge('LLO', LlanoPayTheme.secondaryGoldDark),
                    ],
                  ),

                  const SizedBox(height: 20),

                  // -- Info card --
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Informacion',
                            style:
                                Theme.of(context).textTheme.titleMedium,
                          ),
                          const SizedBox(height: 12),
                          _infoRow(Icons.location_on_outlined,
                              merchant['address'] as String),
                          const SizedBox(height: 10),
                          _infoRow(Icons.phone_outlined,
                              merchant['phone'] as String),
                          const SizedBox(height: 10),
                          _infoRow(Icons.location_city,
                              '${merchant['city']}, ${merchant['department']}'),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 16),

                  // -- Description --
                  if ((merchant['description'] as String).isNotEmpty) ...[
                    Text(
                      merchant['description'] as String,
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                    const SizedBox(height: 20),
                  ],

                  // -- Active promotions --
                  if ((merchant['promotions'] as List).isNotEmpty) ...[
                    Text(
                      'Promociones activas',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 12),
                    ...(merchant['promotions'] as List).map((promo) {
                      return Card(
                        color: LlanoPayTheme.secondaryGold.withOpacity(0.1),
                        child: ListTile(
                          leading: const Icon(
                            Icons.local_offer,
                            color: LlanoPayTheme.secondaryGoldDark,
                          ),
                          title: Text(
                            promo['title'] as String,
                            style: Theme.of(context)
                                .textTheme
                                .titleMedium
                                ?.copyWith(
                                  color: LlanoPayTheme.secondaryGoldDark,
                                ),
                          ),
                          subtitle: Text(
                            'Valido hasta ${promo['expires']}',
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        ),
                      );
                    }),
                    const SizedBox(height: 20),
                  ],

                  // -- Reviews section --
                  Text(
                    'Resenas',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 12),
                  ...(merchant['reviews'] as List).map((review) {
                    return Card(
                      margin: const EdgeInsets.only(bottom: 8),
                      child: Padding(
                        padding: const EdgeInsets.all(14),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                CircleAvatar(
                                  radius: 16,
                                  backgroundColor: LlanoPayTheme.primaryGreen
                                      .withOpacity(0.1),
                                  child: Text(
                                    (review['user'] as String)
                                        .substring(0, 1),
                                    style: GoogleFonts.montserrat(
                                      color: LlanoPayTheme.primaryGreen,
                                      fontWeight: FontWeight.w700,
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        review['user'] as String,
                                        style: Theme.of(context)
                                            .textTheme
                                            .titleMedium,
                                      ),
                                      Text(
                                        review['date'] as String,
                                        style: Theme.of(context)
                                            .textTheme
                                            .labelSmall,
                                      ),
                                    ],
                                  ),
                                ),
                                _ratingStars(
                                    (review['rating'] as num).toDouble(),
                                    context),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Text(
                              review['comment'] as String,
                              style:
                                  Theme.of(context).textTheme.bodyMedium,
                            ),
                          ],
                        ),
                      ),
                    );
                  }),

                  const SizedBox(height: 24),

                  // -- Action buttons --
                  SizedBox(
                    height: 52,
                    child: ElevatedButton.icon(
                      onPressed: () {
                        _showPayDialog(context, copFormat);
                      },
                      icon: const Icon(Icons.payment),
                      label: const Text('Pagar'),
                    ),
                  ),

                  const SizedBox(height: 12),

                  // -- WhatsApp button --
                  SizedBox(
                    height: 52,
                    child: OutlinedButton.icon(
                      onPressed: () {
                        // Launch WhatsApp URL
                        final whatsapp = merchant['whatsapp'] as String;
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text(
                                'Abriendo WhatsApp: $whatsapp'),
                            backgroundColor: LlanoPayTheme.success,
                          ),
                        );
                      },
                      icon: const Icon(Icons.chat, color: Color(0xFF25D366)),
                      label: const Text(
                        'WhatsApp',
                        style: TextStyle(color: Color(0xFF25D366)),
                      ),
                      style: OutlinedButton.styleFrom(
                        side: const BorderSide(color: Color(0xFF25D366)),
                      ),
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

  void _showPayDialog(BuildContext context, NumberFormat copFormat) {
    final amountController = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Pagar al comercio'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextFormField(
              controller: amountController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: 'Monto',
                prefixText: '\$ ',
                suffixText: 'COP',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Pago procesado exitosamente'),
                  backgroundColor: LlanoPayTheme.success,
                ),
              );
            },
            child: const Text('Pagar'),
          ),
        ],
      ),
    );
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
