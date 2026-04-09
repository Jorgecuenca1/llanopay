import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Profile tab showing user info and settings.
class ProfileTab extends StatelessWidget {
  const ProfileTab({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Mi Perfil')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // User avatar and name
          Center(
            child: Column(
              children: [
                CircleAvatar(
                  radius: 40,
                  backgroundColor: theme.colorScheme.primaryContainer,
                  child: Icon(
                    Icons.person,
                    size: 40,
                    color: theme.colorScheme.primary,
                  ),
                ),
                const SizedBox(height: 12),
                Text('Usuario LlanoPay', style: theme.textTheme.headlineSmall),
                const SizedBox(height: 4),
                Text(
                  '+57 ---',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          // Menu items
          _ProfileMenuItem(
            icon: Icons.verified_user_outlined,
            title: 'Verificacion KYC',
            subtitle: 'Verifica tu identidad',
            onTap: () => context.push('/profile/kyc'),
          ),
          _ProfileMenuItem(
            icon: Icons.credit_score_outlined,
            title: 'Microcredito',
            subtitle: 'Solicita tu credito',
            onTap: () => context.push('/microcredit'),
          ),
          _ProfileMenuItem(
            icon: Icons.notifications_outlined,
            title: 'Notificaciones',
            subtitle: 'Configura tus alertas',
            onTap: () => context.push('/notifications'),
          ),
          _ProfileMenuItem(
            icon: Icons.security_outlined,
            title: 'Seguridad',
            subtitle: 'Contrasena y biometricos',
            onTap: () {},
          ),
          _ProfileMenuItem(
            icon: Icons.help_outline,
            title: 'Ayuda',
            subtitle: 'Preguntas frecuentes',
            onTap: () {},
          ),
          const SizedBox(height: 16),
          OutlinedButton.icon(
            onPressed: () {
              // TODO: Integrate with AuthService.logout
              context.go('/login');
            },
            icon: const Icon(Icons.logout, color: Colors.red),
            label: const Text('Cerrar Sesion', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }
}

class _ProfileMenuItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  const _ProfileMenuItem({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(icon),
        title: Text(title),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.arrow_forward_ios, size: 16),
        onTap: onTap,
      ),
    );
  }
}
