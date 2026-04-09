import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../config/theme.dart';

/// Full marketplace screen with search, category filters, and merchant grid.
class MarketplaceScreen extends StatefulWidget {
  const MarketplaceScreen({super.key});

  @override
  State<MarketplaceScreen> createState() => _MarketplaceScreenState();
}

class _MarketplaceScreenState extends State<MarketplaceScreen> {
  final _searchController = TextEditingController();
  String _selectedCategory = 'Todos';
  String _selectedDepartment = 'Todos';

  static const List<String> _categories = [
    'Todos',
    'Restaurantes',
    'Tiendas',
    'Servicios',
    'Salud',
    'Transporte',
    'Educacion',
    'Entretenimiento',
  ];

  static const List<String> _departments = [
    'Todos',
    'Meta',
    'Casanare',
    'Arauca',
    'Vichada',
    'Guainia',
    'Guaviare',
  ];

  // Placeholder merchants
  static const List<Map<String, dynamic>> _merchants = [
    {
      'name': 'Restaurante El Llanero',
      'category': 'Restaurantes',
      'city': 'Villavicencio',
      'department': 'Meta',
      'rating': 4.5,
      'accepts_llo': true,
      'slug': 'restaurante-el-llanero',
    },
    {
      'name': 'Tienda Campesina',
      'category': 'Tiendas',
      'city': 'Yopal',
      'department': 'Casanare',
      'rating': 4.2,
      'accepts_llo': true,
      'slug': 'tienda-campesina',
    },
    {
      'name': 'Clinica del Llano',
      'category': 'Salud',
      'city': 'Villavicencio',
      'department': 'Meta',
      'rating': 4.8,
      'accepts_llo': false,
      'slug': 'clinica-del-llano',
    },
    {
      'name': 'Mototaxi Express',
      'category': 'Transporte',
      'city': 'Acacias',
      'department': 'Meta',
      'rating': 3.9,
      'accepts_llo': true,
      'slug': 'mototaxi-express',
    },
    {
      'name': 'Panaderia La Espiga',
      'category': 'Tiendas',
      'city': 'Granada',
      'department': 'Meta',
      'rating': 4.6,
      'accepts_llo': true,
      'slug': 'panaderia-la-espiga',
    },
    {
      'name': 'Taller Mecanico San Jose',
      'category': 'Servicios',
      'city': 'Arauca',
      'department': 'Arauca',
      'rating': 4.0,
      'accepts_llo': false,
      'slug': 'taller-mecanico-san-jose',
    },
  ];

  List<Map<String, dynamic>> get _filteredMerchants {
    return _merchants.where((m) {
      final matchesCategory =
          _selectedCategory == 'Todos' || m['category'] == _selectedCategory;
      final matchesDepartment = _selectedDepartment == 'Todos' ||
          m['department'] == _selectedDepartment;
      final matchesSearch = _searchController.text.isEmpty ||
          (m['name'] as String)
              .toLowerCase()
              .contains(_searchController.text.toLowerCase());
      return matchesCategory && matchesDepartment && matchesSearch;
    }).toList();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final merchants = _filteredMerchants;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Comercios'),
      ),
      body: RefreshIndicator(
        color: LlanoPayTheme.primaryGreen,
        onRefresh: () async {
          // Placeholder refresh
          await Future.delayed(const Duration(milliseconds: 500));
        },
        child: CustomScrollView(
          slivers: [
            // -- Search bar --
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
                child: TextField(
                  controller: _searchController,
                  onChanged: (_) => setState(() {}),
                  decoration: InputDecoration(
                    hintText: 'Buscar comercios...',
                    prefixIcon: const Icon(Icons.search),
                    suffixIcon: _searchController.text.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.clear),
                            onPressed: () {
                              _searchController.clear();
                              setState(() {});
                            },
                          )
                        : null,
                  ),
                ),
              ),
            ),

            // -- Category chips --
            SliverToBoxAdapter(
              child: SizedBox(
                height: 56,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 10,
                  ),
                  itemCount: _categories.length,
                  separatorBuilder: (_, __) => const SizedBox(width: 8),
                  itemBuilder: (context, index) {
                    final cat = _categories[index];
                    final isSelected = _selectedCategory == cat;
                    return ChoiceChip(
                      label: Text(cat),
                      selected: isSelected,
                      onSelected: (selected) {
                        setState(() {
                          _selectedCategory = selected ? cat : 'Todos';
                        });
                      },
                      selectedColor: LlanoPayTheme.primaryGreen,
                      labelStyle: TextStyle(
                        color: isSelected
                            ? Colors.white
                            : LlanoPayTheme.textPrimary,
                        fontWeight: FontWeight.w600,
                        fontSize: 13,
                      ),
                    );
                  },
                ),
              ),
            ),

            // -- Department filter --
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: DropdownButtonFormField<String>(
                  value: _selectedDepartment,
                  decoration: const InputDecoration(
                    labelText: 'Departamento',
                    prefixIcon: Icon(Icons.location_on_outlined),
                    contentPadding: EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 10,
                    ),
                  ),
                  items: _departments
                      .map(
                        (dep) => DropdownMenuItem(
                          value: dep,
                          child: Text(dep),
                        ),
                      )
                      .toList(),
                  onChanged: (value) {
                    if (value != null) {
                      setState(() => _selectedDepartment = value);
                    }
                  },
                ),
              ),
            ),

            const SliverToBoxAdapter(child: SizedBox(height: 12)),

            // -- Merchant grid --
            if (merchants.isEmpty)
              SliverFillRemaining(
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.store_mall_directory_outlined,
                        size: 56,
                        color:
                            LlanoPayTheme.textSecondary.withOpacity(0.4),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'No se encontraron comercios',
                        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                              color: LlanoPayTheme.textSecondary,
                            ),
                      ),
                    ],
                  ),
                ),
              )
            else
              SliverPadding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                sliver: SliverGrid(
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    mainAxisSpacing: 12,
                    crossAxisSpacing: 12,
                    childAspectRatio: 0.78,
                  ),
                  delegate: SliverChildBuilderDelegate(
                    (context, index) {
                      final merchant = merchants[index];
                      return _buildMerchantCard(merchant);
                    },
                    childCount: merchants.length,
                  ),
                ),
              ),

            const SliverToBoxAdapter(child: SizedBox(height: 24)),
          ],
        ),
      ),
    );
  }

  Widget _buildMerchantCard(Map<String, dynamic> merchant) {
    final name = merchant['name'] as String;
    final category = merchant['category'] as String;
    final city = merchant['city'] as String;
    final rating = (merchant['rating'] as num).toDouble();
    final acceptsLlo = merchant['accepts_llo'] as bool;
    final slug = merchant['slug'] as String;

    return GestureDetector(
      onTap: () => context.push('/marketplace/$slug'),
      child: Card(
        clipBehavior: Clip.antiAlias,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Logo placeholder
            Container(
              height: 80,
              width: double.infinity,
              color: LlanoPayTheme.primaryGreen.withOpacity(0.08),
              child: Center(
                child: Icon(
                  _categoryIcon(category),
                  size: 36,
                  color: LlanoPayTheme.primaryGreen.withOpacity(0.6),
                ),
              ),
            ),

            Padding(
              padding: const EdgeInsets.all(10),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    name,
                    style: GoogleFonts.montserrat(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      const Icon(
                        Icons.star,
                        size: 14,
                        color: LlanoPayTheme.secondaryGold,
                      ),
                      const SizedBox(width: 2),
                      Text(
                        rating.toStringAsFixed(1),
                        style: Theme.of(context).textTheme.labelSmall,
                      ),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Text(
                          category,
                          style: Theme.of(context).textTheme.labelSmall,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    city,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      _badge('COP', LlanoPayTheme.primaryGreen),
                      if (acceptsLlo) ...[
                        const SizedBox(width: 4),
                        _badge('LLO', LlanoPayTheme.secondaryGoldDark),
                      ],
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _badge(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        label,
        style: GoogleFonts.montserrat(
          fontSize: 9,
          fontWeight: FontWeight.w700,
          color: color,
        ),
      ),
    );
  }

  IconData _categoryIcon(String category) {
    switch (category) {
      case 'Restaurantes':
        return Icons.restaurant;
      case 'Tiendas':
        return Icons.storefront;
      case 'Servicios':
        return Icons.build;
      case 'Salud':
        return Icons.local_hospital;
      case 'Transporte':
        return Icons.directions_car;
      case 'Educacion':
        return Icons.school;
      case 'Entretenimiento':
        return Icons.sports_esports;
      default:
        return Icons.store;
    }
  }
}
