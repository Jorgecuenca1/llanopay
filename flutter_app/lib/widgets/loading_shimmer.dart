import 'package:flutter/material.dart';
import 'package:shimmer/shimmer.dart';

import '../config/theme.dart';

/// Shimmer loading placeholder widgets for various LlanoPay UI patterns.
class LoadingShimmer extends StatelessWidget {
  final Widget child;

  const LoadingShimmer({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return Shimmer.fromColors(
      baseColor: LlanoPayTheme.divider,
      highlightColor: LlanoPayTheme.backgroundLight,
      child: child,
    );
  }

  /// Shimmer placeholder for a list of transaction tiles.
  static Widget listShimmer({int itemCount = 5}) {
    return LoadingShimmer(
      child: ListView.separated(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: itemCount,
        separatorBuilder: (_, __) => const Divider(height: 1),
        itemBuilder: (_, __) => const _ListItemShimmer(),
      ),
    );
  }

  /// Shimmer placeholder for a single card (e.g., merchant card).
  static Widget cardShimmer() {
    return LoadingShimmer(
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Card(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(LlanoPayTheme.cardRadius),
          ),
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                // Image placeholder
                Container(
                  width: 64,
                  height: 64,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        width: double.infinity,
                        height: 14,
                        color: Colors.white,
                      ),
                      const SizedBox(height: 8),
                      Container(
                        width: 100,
                        height: 10,
                        color: Colors.white,
                      ),
                      const SizedBox(height: 8),
                      Container(
                        width: 140,
                        height: 10,
                        color: Colors.white,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// Shimmer placeholder for the balance card.
  static Widget balanceShimmer() {
    return LoadingShimmer(
      child: Container(
        width: double.infinity,
        margin: const EdgeInsets.symmetric(horizontal: 16),
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 100,
              height: 12,
              color: Colors.white,
            ),
            const SizedBox(height: 16),
            Container(
              width: 200,
              height: 28,
              color: Colors.white,
            ),
            const SizedBox(height: 8),
            Container(
              width: 120,
              height: 10,
              color: Colors.white,
            ),
            const SizedBox(height: 20),
            Container(
              height: 1,
              color: Colors.white,
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Container(
                  width: 32,
                  height: 32,
                  decoration: const BoxDecoration(
                    color: Colors.white,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 12),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      width: 140,
                      height: 16,
                      color: Colors.white,
                    ),
                    const SizedBox(height: 4),
                    Container(
                      width: 80,
                      height: 10,
                      color: Colors.white,
                    ),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

/// Internal shimmer placeholder for a single list item.
class _ListItemShimmer extends StatelessWidget {
  const _ListItemShimmer();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          // Circle avatar placeholder
          Container(
            width: 40,
            height: 40,
            decoration: const BoxDecoration(
              color: Colors.white,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 12),
          // Text lines
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: double.infinity,
                  height: 14,
                  color: Colors.white,
                ),
                const SizedBox(height: 6),
                Container(
                  width: 100,
                  height: 10,
                  color: Colors.white,
                ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          // Amount placeholder
          Container(
            width: 80,
            height: 14,
            color: Colors.white,
          ),
        ],
      ),
    );
  }
}
