import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Shell screen that provides bottom navigation for main tabs.
class HomeScreen extends StatelessWidget {
  final Widget child;

  const HomeScreen({super.key, required this.child});

  static const _tabs = [
    _TabConfig(
      path: '/home',
      icon: Icons.home_outlined,
      activeIcon: Icons.home,
      label: 'Inicio',
    ),
    _TabConfig(
      path: '/wallet',
      icon: Icons.account_balance_wallet_outlined,
      activeIcon: Icons.account_balance_wallet,
      label: 'Billetera',
    ),
    _TabConfig(
      path: '/transfer',
      icon: Icons.send_outlined,
      activeIcon: Icons.send,
      label: 'Enviar',
    ),
    _TabConfig(
      path: '/marketplace',
      icon: Icons.store_outlined,
      activeIcon: Icons.store,
      label: 'Comercios',
    ),
    _TabConfig(
      path: '/profile',
      icon: Icons.person_outline,
      activeIcon: Icons.person,
      label: 'Perfil',
    ),
  ];

  int _currentIndex(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;
    for (int i = 0; i < _tabs.length; i++) {
      if (location == _tabs[i].path) return i;
    }
    return 0;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final index = _currentIndex(context);

    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: index,
        onDestinationSelected: (i) => context.go(_tabs[i].path),
        backgroundColor: theme.colorScheme.surface,
        indicatorColor: theme.colorScheme.primary.withOpacity(0.12),
        labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
        destinations: _tabs
            .map(
              (tab) => NavigationDestination(
                icon: Icon(tab.icon),
                selectedIcon: Icon(tab.activeIcon, color: theme.colorScheme.primary),
                label: tab.label,
              ),
            )
            .toList(),
      ),
    );
  }
}

class _TabConfig {
  final String path;
  final IconData icon;
  final IconData activeIcon;
  final String label;

  const _TabConfig({
    required this.path,
    required this.icon,
    required this.activeIcon,
    required this.label,
  });
}
