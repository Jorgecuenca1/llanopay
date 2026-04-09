import 'package:flutter/material.dart';

import '../config/theme.dart';

/// Card widget for displaying a merchant in the marketplace list.
///
/// Shows the merchant logo/image, business name, category, rating,
/// city, and accepted payment badges (COP/LLO).
class MerchantCard extends StatelessWidget {
  /// Merchant business name.
  final String name;

  /// Category label (e.g., "Restaurante", "Tienda").
  final String category;

  /// Average rating (0.0 - 5.0).
  final double rating;

  /// City name.
  final String city;

  /// URL for the merchant's logo or image. Null shows a placeholder.
  final String? imageUrl;

  /// Whether the merchant accepts COP payments.
  final bool acceptsCop;

  /// Whether the merchant accepts LLO (Llanocoin) payments.
  final bool acceptsLlo;

  /// Callback when the card is tapped.
  final VoidCallback? onTap;

  const MerchantCard({
    super.key,
    required this.name,
    required this.category,
    required this.rating,
    required this.city,
    this.imageUrl,
    this.acceptsCop = true,
    this.acceptsLlo = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(LlanoPayTheme.cardRadius),
      ),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              // Merchant image / placeholder
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: _buildImage(),
              ),
              const SizedBox(width: 12),

              // Merchant info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Name
                    Text(
                      name,
                      style:
                          Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.w600,
                              ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),

                    // Category chip
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: LlanoPayTheme.primaryGreenLight
                            .withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        category,
                        style:
                            Theme.of(context).textTheme.labelSmall?.copyWith(
                                  color: LlanoPayTheme.primaryGreenDark,
                                  fontWeight: FontWeight.w600,
                                ),
                      ),
                    ),
                    const SizedBox(height: 6),

                    // Rating and city
                    Row(
                      children: [
                        ..._buildStars(),
                        const SizedBox(width: 4),
                        Text(
                          rating.toStringAsFixed(1),
                          style:
                              Theme.of(context).textTheme.labelSmall?.copyWith(
                                    fontWeight: FontWeight.w600,
                                  ),
                        ),
                        const SizedBox(width: 8),
                        Icon(
                          Icons.location_on,
                          size: 14,
                          color: LlanoPayTheme.textSecondary,
                        ),
                        const SizedBox(width: 2),
                        Flexible(
                          child: Text(
                            city,
                            style: Theme.of(context).textTheme.labelSmall,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),

                    // Payment badges
                    Row(
                      children: [
                        if (acceptsCop) _buildBadge(context, 'COP', false),
                        if (acceptsCop && acceptsLlo)
                          const SizedBox(width: 6),
                        if (acceptsLlo) _buildBadge(context, 'LLO', true),
                      ],
                    ),
                  ],
                ),
              ),

              // Arrow
              const Icon(
                Icons.chevron_right,
                color: LlanoPayTheme.textSecondary,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildImage() {
    if (imageUrl != null && imageUrl!.isNotEmpty) {
      return Image.network(
        imageUrl!,
        width: 64,
        height: 64,
        fit: BoxFit.cover,
        errorBuilder: (_, __, ___) => _buildPlaceholder(),
      );
    }
    return _buildPlaceholder();
  }

  Widget _buildPlaceholder() {
    return Container(
      width: 64,
      height: 64,
      color: LlanoPayTheme.backgroundLight,
      child: const Icon(
        Icons.storefront,
        color: LlanoPayTheme.primaryGreen,
        size: 32,
      ),
    );
  }

  List<Widget> _buildStars() {
    final stars = <Widget>[];
    final fullStars = rating.floor();
    final hasHalf = (rating - fullStars) >= 0.5;

    for (int i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.add(const Icon(
          Icons.star,
          size: 14,
          color: LlanoPayTheme.secondaryGold,
        ));
      } else if (i == fullStars && hasHalf) {
        stars.add(const Icon(
          Icons.star_half,
          size: 14,
          color: LlanoPayTheme.secondaryGold,
        ));
      } else {
        stars.add(const Icon(
          Icons.star_border,
          size: 14,
          color: LlanoPayTheme.secondaryGold,
        ));
      }
    }
    return stars;
  }

  Widget _buildBadge(BuildContext context, String label, bool isLlo) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: isLlo
            ? LlanoPayTheme.secondaryGold.withValues(alpha: 0.15)
            : LlanoPayTheme.primaryGreen.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: isLlo
              ? LlanoPayTheme.secondaryGold
              : LlanoPayTheme.primaryGreen,
          width: 1,
        ),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: isLlo
                  ? LlanoPayTheme.secondaryGoldDark
                  : LlanoPayTheme.primaryGreenDark,
              fontWeight: FontWeight.w700,
              fontSize: 10,
            ),
      ),
    );
  }
}
