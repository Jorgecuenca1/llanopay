import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import '../../services/api_service.dart';
import '../../config/api_config.dart';

/// Marketplace tab listing merchants and promotions from the API.
class MarketplaceTab extends StatefulWidget {
  const MarketplaceTab({super.key});

  @override
  State<MarketplaceTab> createState() => _MarketplaceTabState();
}

class _MarketplaceTabState extends State<MarketplaceTab> {
  bool _loading = true;
  List<dynamic> _merchants = [];
  List<dynamic> _categories = [];
  String? _selectedCategory;
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() => _loading = true);
    try {
      final api = context.read<ApiService>();
      final params = <String, dynamic>{'page_size': 20};
      if (_selectedCategory != null) params['category'] = _selectedCategory;
      if (_searchController.text.isNotEmpty) params['search'] = _searchController.text;

      final results = await Future.wait([
        api.get(ApiConfig.marketplaceMerchants, queryParameters: params),
        api.get(ApiConfig.marketplaceCategories),
      ]);
      if (mounted) {
        setState(() {
          if (results[0].success) {
            final d = results[0].data;
            _merchants = d is Map ? (d['results'] as List? ?? []) : (d as List? ?? []);
          }
          if (results[1].success) {
            final d = results[1].data;
            _categories = d is Map ? (d['results'] as List? ?? []) : (d as List? ?? []);
          }
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Marketplace'),
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(12),
              child: TextField(
                controller: _searchController,
                decoration: InputDecoration(
                  hintText: 'Buscar comercios...',
                  prefixIcon: const Icon(Icons.search),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  contentPadding: const EdgeInsets.symmetric(vertical: 0, horizontal: 16),
                ),
                onSubmitted: (_) => _loadData(),
              ),
            ),
            if (_categories.isNotEmpty)
              SizedBox(
                height: 44,
                child: ListView(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  children: [
                    Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: ChoiceChip(
                        label: const Text('Todos'),
                        selected: _selectedCategory == null,
                        onSelected: (_) {
                          setState(() => _selectedCategory = null);
                          _loadData();
                        },
                      ),
                    ),
                    ..._categories.map((c) {
                      final cat = c as Map<String, dynamic>;
                      final slug = cat['slug']?.toString();
                      return Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: ChoiceChip(
                          label: Text(cat['name']?.toString() ?? ''),
                          selected: _selectedCategory == slug,
                          onSelected: (_) {
                            setState(() => _selectedCategory = slug);
                            _loadData();
                          },
                        ),
                      );
                    }),
                  ],
                ),
              ),
            const SizedBox(height: 8),
            Expanded(
              child: _loading
                  ? const Center(child: CircularProgressIndicator())
                  : _merchants.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.store, size: 64, color: theme.colorScheme.onSurfaceVariant),
                              const SizedBox(height: 16),
                              Text('No se encontraron comercios',
                                  style: theme.textTheme.bodyLarge),
                            ],
                          ),
                        )
                      : ListView.builder(
                          padding: const EdgeInsets.all(12),
                          itemCount: _merchants.length,
                          itemBuilder: (ctx, i) {
                            final m = _merchants[i] as Map<String, dynamic>;
                            return Card(
                              margin: const EdgeInsets.only(bottom: 8),
                              child: ListTile(
                                leading: CircleAvatar(
                                  backgroundColor: theme.colorScheme.primaryContainer,
                                  child: Icon(Icons.store, color: theme.colorScheme.primary),
                                ),
                                title: Text(m['business_name']?.toString() ?? '',
                                    style: const TextStyle(fontWeight: FontWeight.w600)),
                                subtitle: Text(
                                  '${m['category']?['name'] ?? ''} • ${m['city'] ?? ''}',
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                                trailing: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    const Icon(Icons.star, color: Colors.amber, size: 16),
                                    Text(' ${(m['rating'] as num? ?? 0).toStringAsFixed(1)}'),
                                  ],
                                ),
                                onTap: () => context.push('/marketplace/${m['slug']}'),
                              ),
                            );
                          },
                        ),
            ),
          ],
        ),
      ),
    );
  }
}
