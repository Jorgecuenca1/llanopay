import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Registration screen for new LlanoPay users.
class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _phoneController = TextEditingController();
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _documentController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  String _documentType = 'CC';
  bool _obscurePassword = true;
  bool _obscureConfirm = true;
  bool _acceptedTerms = false;
  bool _isLoading = false;

  static const _documentTypes = {
    'CC': 'Cedula de Ciudadania',
    'CE': 'Cedula de Extranjeria',
    'TI': 'Tarjeta de Identidad',
    'NIT': 'NIT',
    'PA': 'Pasaporte',
  };

  @override
  void dispose() {
    _phoneController.dispose();
    _firstNameController.dispose();
    _lastNameController.dispose();
    _documentController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _handleRegister() async {
    if (!_formKey.currentState!.validate()) return;

    if (!_acceptedTerms) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Debes aceptar los terminos y condiciones'),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
      return;
    }

    setState(() => _isLoading = true);

    // TODO: Integrate with AuthService.register
    await Future.delayed(const Duration(seconds: 1));

    if (!mounted) return;
    setState(() => _isLoading = false);
    context.push('/verify-otp', extra: {
      'phone': _phoneController.text.trim(),
      'purpose': 'registration',
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Crear Cuenta'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Registrate en LlanoPay',
                style: theme.textTheme.headlineMedium,
              ),
              const SizedBox(height: 8),
              Text(
                'Completa tus datos para crear tu billetera digital',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 28),
              TextFormField(
                controller: _phoneController,
                keyboardType: TextInputType.phone,
                decoration: const InputDecoration(
                  labelText: 'Numero de celular',
                  hintText: '+57 300 000 0000',
                  prefixIcon: Icon(Icons.phone_android),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'Ingresa tu numero de celular';
                  }
                  if (value.trim().length < 10) return 'Numero invalido';
                  return null;
                },
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: _documentType,
                decoration: const InputDecoration(
                  labelText: 'Tipo de documento',
                  prefixIcon: Icon(Icons.badge_outlined),
                ),
                items: _documentTypes.entries
                    .map((e) => DropdownMenuItem(
                          value: e.key,
                          child: Text(e.value),
                        ))
                    .toList(),
                onChanged: (v) {
                  if (v != null) setState(() => _documentType = v);
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _documentController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Numero de documento',
                  prefixIcon: Icon(Icons.numbers),
                ),
                validator: (v) => v == null || v.trim().isEmpty
                    ? 'Ingresa tu numero de documento'
                    : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _firstNameController,
                textCapitalization: TextCapitalization.words,
                decoration: const InputDecoration(
                  labelText: 'Nombres',
                  prefixIcon: Icon(Icons.person_outline),
                ),
                validator: (v) =>
                    v == null || v.trim().isEmpty ? 'Ingresa tus nombres' : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _lastNameController,
                textCapitalization: TextCapitalization.words,
                decoration: const InputDecoration(
                  labelText: 'Apellidos',
                  prefixIcon: Icon(Icons.person_outline),
                ),
                validator: (v) =>
                    v == null || v.trim().isEmpty ? 'Ingresa tus apellidos' : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _passwordController,
                obscureText: _obscurePassword,
                decoration: InputDecoration(
                  labelText: 'Contrasena',
                  prefixIcon: const Icon(Icons.lock_outline),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _obscurePassword
                          ? Icons.visibility_off
                          : Icons.visibility,
                    ),
                    onPressed: () {
                      setState(() => _obscurePassword = !_obscurePassword);
                    },
                  ),
                ),
                validator: (v) {
                  if (v == null || v.isEmpty) return 'Ingresa una contrasena';
                  if (v.length < 8) return 'Minimo 8 caracteres';
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _confirmPasswordController,
                obscureText: _obscureConfirm,
                decoration: InputDecoration(
                  labelText: 'Confirmar contrasena',
                  prefixIcon: const Icon(Icons.lock_outline),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _obscureConfirm
                          ? Icons.visibility_off
                          : Icons.visibility,
                    ),
                    onPressed: () {
                      setState(() => _obscureConfirm = !_obscureConfirm);
                    },
                  ),
                ),
                validator: (v) {
                  if (v != _passwordController.text) {
                    return 'Las contrasenas no coinciden';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 20),
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Checkbox(
                    value: _acceptedTerms,
                    activeColor: theme.colorScheme.primary,
                    onChanged: (v) {
                      setState(() => _acceptedTerms = v ?? false);
                    },
                  ),
                  Expanded(
                    child: GestureDetector(
                      onTap: () {
                        setState(() => _acceptedTerms = !_acceptedTerms);
                      },
                      child: Padding(
                        padding: const EdgeInsets.only(top: 12),
                        child: Text.rich(
                          TextSpan(
                            text: 'Acepto los ',
                            style: theme.textTheme.bodySmall,
                            children: [
                              TextSpan(
                                text: 'Terminos y Condiciones',
                                style: TextStyle(
                                  color: theme.colorScheme.primary,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                              const TextSpan(text: ' y la '),
                              TextSpan(
                                text: 'Politica de Privacidad',
                                style: TextStyle(
                                  color: theme.colorScheme.primary,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              SizedBox(
                height: 52,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _handleRegister,
                  child: _isLoading
                      ? const SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(
                            color: Colors.white,
                            strokeWidth: 2.5,
                          ),
                        )
                      : const Text('Crear Cuenta'),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text('Ya tienes cuenta? ', style: theme.textTheme.bodyMedium),
                  TextButton(
                    onPressed: () => context.pop(),
                    child: const Text('Iniciar Sesion'),
                  ),
                ],
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}
