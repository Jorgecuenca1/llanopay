import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../blocs/auth/auth_bloc.dart';
import '../../blocs/auth/auth_event.dart';
import '../../blocs/auth/auth_state.dart';
import '../../config/theme.dart';

/// User profile screen with settings menu and logout.
class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Mi Perfil'),
      ),
      body: BlocListener<AuthBloc, AuthState>(
        listener: (context, state) {
          if (state is Unauthenticated) {
            context.go('/auth/login');
          }
        },
        child: BlocBuilder<AuthBloc, AuthState>(
          builder: (context, state) {
            String firstName = 'Usuario';
            String lastName = '';
            String phone = '+57 ---';
            String docType = '';
            String docNumber = '';
            String verificationStatus = 'Sin verificar';

            if (state is Authenticated && state.user != null) {
              firstName = state.user!.firstName;
              lastName = state.user!.lastName;
              phone = state.user!.phoneNumber;
              docType = state.user!.documentType ?? '';
              docNumber = state.user!.documentNumber ?? '';
              verificationStatus = state.user!.isVerified ? 'Verificado' : 'Sin verificar';
            }

            return ListView(
              padding: const EdgeInsets.all(16),
              children: [
                const SizedBox(height: 8),

                // -- Avatar & info --
                Center(
                  child: Column(
                    children: [
                      CircleAvatar(
                        radius: 48,
                        backgroundColor:
                            LlanoPayTheme.primaryGreen.withOpacity(0.1),
                        child: const Icon(
                          Icons.person,
                          size: 48,
                          color: LlanoPayTheme.primaryGreen,
                        ),
                      ),
                      const SizedBox(height: 14),
                      Text(
                        '$firstName $lastName',
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        phone,
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: LlanoPayTheme.textSecondary,
                            ),
                      ),
                      if (docType.isNotEmpty && docNumber.isNotEmpty) ...[
                        const SizedBox(height: 2),
                        Text(
                          '$docType $docNumber',
                          style:
                              Theme.of(context).textTheme.bodySmall?.copyWith(
                                    color: LlanoPayTheme.textSecondary,
                                  ),
                        ),
                      ],
                      const SizedBox(height: 10),

                      // Verification badge
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 14,
                          vertical: 5,
                        ),
                        decoration: BoxDecoration(
                          color: _verificationColor(verificationStatus)
                              .withOpacity(0.1),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              _verificationIcon(verificationStatus),
                              size: 16,
                              color:
                                  _verificationColor(verificationStatus),
                            ),
                            const SizedBox(width: 6),
                            Text(
                              _verificationLabel(verificationStatus),
                              style: GoogleFonts.montserrat(
                                fontSize: 12,
                                fontWeight: FontWeight.w600,
                                color:
                                    _verificationColor(verificationStatus),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 28),

                // -- Menu items --
                _ProfileMenuItem(
                  icon: Icons.edit_outlined,
                  title: 'Editar Perfil',
                  subtitle: 'Actualiza tu informacion personal',
                  onTap: () => context.push('/profile/edit'),
                ),
                _ProfileMenuItem(
                  icon: Icons.verified_user_outlined,
                  title: 'Verificacion KYC',
                  subtitle: 'Verifica tu identidad',
                  onTap: () => context.push('/profile/kyc'),
                ),
                _ProfileMenuItem(
                  icon: Icons.speed_outlined,
                  title: 'Limites de Transferencia',
                  subtitle: 'Consulta tus limites diarios y mensuales',
                  onTap: () {},
                ),
                _ProfileMenuItem(
                  icon: Icons.credit_score_outlined,
                  title: 'Microcredito',
                  subtitle: 'Solicita tu credito digital',
                  onTap: () => context.push('/microcredit'),
                ),
                _ProfileMenuItem(
                  icon: Icons.security_outlined,
                  title: 'Seguridad',
                  subtitle: 'Contrasena y autenticacion biometrica',
                  onTap: () {},
                ),
                _ProfileMenuItem(
                  icon: Icons.info_outline,
                  title: 'Sobre LlanoPay',
                  subtitle: 'Version 1.0.0 - Tu billetera del llano',
                  onTap: () {},
                ),

                const SizedBox(height: 24),

                // -- Logout button --
                SizedBox(
                  height: 52,
                  child: OutlinedButton.icon(
                    onPressed: () {
                      showDialog(
                        context: context,
                        builder: (ctx) => AlertDialog(
                          title: const Text('Cerrar Sesion'),
                          content: const Text(
                            'Estas seguro que deseas cerrar sesion?',
                          ),
                          actions: [
                            TextButton(
                              onPressed: () => Navigator.pop(ctx),
                              child: const Text('Cancelar'),
                            ),
                            ElevatedButton(
                              onPressed: () {
                                Navigator.pop(ctx);
                                context
                                    .read<AuthBloc>()
                                    .add(const LogoutRequested());
                              },
                              style: ElevatedButton.styleFrom(
                                backgroundColor: LlanoPayTheme.error,
                              ),
                              child: const Text('Cerrar Sesion'),
                            ),
                          ],
                        ),
                      );
                    },
                    icon: const Icon(Icons.logout, color: LlanoPayTheme.error),
                    label: const Text(
                      'Cerrar Sesion',
                      style: TextStyle(color: LlanoPayTheme.error),
                    ),
                    style: OutlinedButton.styleFrom(
                      side: const BorderSide(color: LlanoPayTheme.error),
                    ),
                  ),
                ),

                const SizedBox(height: 24),
              ],
            );
          },
        ),
      ),
    );
  }

  Color _verificationColor(String status) {
    switch (status.toLowerCase()) {
      case 'verified':
      case 'verificado':
        return LlanoPayTheme.success;
      case 'pending':
      case 'pendiente':
        return LlanoPayTheme.secondaryGold;
      case 'rejected':
      case 'rechazado':
        return LlanoPayTheme.error;
      default:
        return LlanoPayTheme.textSecondary;
    }
  }

  IconData _verificationIcon(String status) {
    switch (status.toLowerCase()) {
      case 'verified':
      case 'verificado':
        return Icons.verified;
      case 'pending':
      case 'pendiente':
        return Icons.hourglass_bottom;
      case 'rejected':
      case 'rechazado':
        return Icons.cancel;
      default:
        return Icons.warning_amber;
    }
  }

  String _verificationLabel(String status) {
    switch (status.toLowerCase()) {
      case 'verified':
        return 'Verificado';
      case 'pending':
        return 'En revision';
      case 'rejected':
        return 'Rechazado';
      default:
        return 'Sin verificar';
    }
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
        leading: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: LlanoPayTheme.primaryGreen.withOpacity(0.08),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(
            icon,
            color: LlanoPayTheme.primaryGreen,
            size: 22,
          ),
        ),
        title: Text(
          title,
          style: Theme.of(context).textTheme.titleMedium,
        ),
        subtitle: Text(
          subtitle,
          style: Theme.of(context).textTheme.bodySmall,
        ),
        trailing: const Icon(Icons.arrow_forward_ios, size: 16),
        onTap: onTap,
      ),
    );
  }
}
