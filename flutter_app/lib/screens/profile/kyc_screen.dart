import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:image_picker/image_picker.dart';

import '../../config/theme.dart';

/// KYC (Know Your Customer) identity verification screen.
/// Steps: 1. Document front, 2. Document back, 3. Selfie.
class KYCScreen extends StatefulWidget {
  const KYCScreen({super.key});

  @override
  State<KYCScreen> createState() => _KYCScreenState();
}

class _KYCScreenState extends State<KYCScreen> {
  final ImagePicker _picker = ImagePicker();

  int _currentStep = 0;
  String? _docFrontPath;
  String? _docBackPath;
  String? _selfiePath;
  bool _isUploading = false;
  String _kycStatus = 'none'; // none, pending, verified

  static const List<Map<String, dynamic>> _steps = [
    {
      'title': 'Frente del documento',
      'subtitle': 'Toma una foto clara del frente de tu documento de identidad',
      'icon': Icons.credit_card,
    },
    {
      'title': 'Reverso del documento',
      'subtitle':
          'Toma una foto clara del reverso de tu documento de identidad',
      'icon': Icons.credit_card,
    },
    {
      'title': 'Selfie de verificacion',
      'subtitle':
          'Toma una selfie sosteniendo tu documento junto a tu rostro',
      'icon': Icons.face,
    },
  ];

  Future<void> _pickImage(ImageSource source) async {
    try {
      final XFile? image = await _picker.pickImage(
        source: source,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );

      if (image == null) return;

      setState(() {
        switch (_currentStep) {
          case 0:
            _docFrontPath = image.path;
            break;
          case 1:
            _docBackPath = image.path;
            break;
          case 2:
            _selfiePath = image.path;
            break;
        }
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error al capturar imagen: $e'),
            backgroundColor: LlanoPayTheme.error,
          ),
        );
      }
    }
  }

  String? get _currentFilePath {
    switch (_currentStep) {
      case 0:
        return _docFrontPath;
      case 1:
        return _docBackPath;
      case 2:
        return _selfiePath;
      default:
        return null;
    }
  }

  bool get _allPhotosReady =>
      _docFrontPath != null && _docBackPath != null && _selfiePath != null;

  void _nextStep() {
    if (_currentFilePath == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Debes tomar o seleccionar una foto primero'),
          backgroundColor: LlanoPayTheme.error,
        ),
      );
      return;
    }

    if (_currentStep < 2) {
      setState(() => _currentStep++);
    } else {
      _submitKYC();
    }
  }

  Future<void> _submitKYC() async {
    if (!_allPhotosReady) return;

    setState(() => _isUploading = true);

    // Simulate upload
    await Future.delayed(const Duration(seconds: 3));

    if (!mounted) return;

    setState(() {
      _isUploading = false;
      _kycStatus = 'pending';
    });

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content:
            Text('Documentos enviados. Tu verificacion esta en revision.'),
        backgroundColor: LlanoPayTheme.success,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final step = _steps[_currentStep];

    return Scaffold(
      appBar: AppBar(
        title: const Text('Verificacion KYC'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: _kycStatus == 'pending'
          ? _buildPendingView()
          : SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // -- Step progress bar --
                  Row(
                    children: List.generate(3, (index) {
                      final isActive = index == _currentStep;
                      final isComplete = (index == 0 && _docFrontPath != null && _currentStep > 0) ||
                          (index == 1 && _docBackPath != null && _currentStep > 1) ||
                          (index == 2 && _selfiePath != null);

                      return Expanded(
                        child: Container(
                          margin:
                              EdgeInsets.only(right: index < 2 ? 8 : 0),
                          height: 4,
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(2),
                            color: isComplete
                                ? LlanoPayTheme.success
                                : isActive
                                    ? LlanoPayTheme.primaryGreen
                                    : LlanoPayTheme.divider,
                          ),
                        ),
                      );
                    }),
                  ),

                  const SizedBox(height: 8),

                  Text(
                    'Paso ${_currentStep + 1} de 3',
                    style: Theme.of(context).textTheme.labelMedium,
                  ),

                  const SizedBox(height: 28),

                  // -- Step icon --
                  Center(
                    child: Container(
                      width: 80,
                      height: 80,
                      decoration: BoxDecoration(
                        color:
                            LlanoPayTheme.primaryGreen.withOpacity(0.1),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        step['icon'] as IconData,
                        color: LlanoPayTheme.primaryGreen,
                        size: 40,
                      ),
                    ),
                  ),

                  const SizedBox(height: 20),

                  Text(
                    step['title'] as String,
                    style: Theme.of(context).textTheme.headlineSmall,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    step['subtitle'] as String,
                    style:
                        Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: LlanoPayTheme.textSecondary,
                            ),
                    textAlign: TextAlign.center,
                  ),

                  const SizedBox(height: 32),

                  // -- Photo preview / placeholder --
                  Container(
                    height: 200,
                    decoration: BoxDecoration(
                      color: LlanoPayTheme.backgroundLight,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: _currentFilePath != null
                            ? LlanoPayTheme.success
                            : LlanoPayTheme.divider,
                        width: 2,
                      ),
                    ),
                    child: _currentFilePath != null
                        ? Stack(
                            alignment: Alignment.center,
                            children: [
                              const Icon(
                                Icons.check_circle,
                                color: LlanoPayTheme.success,
                                size: 56,
                              ),
                              Positioned(
                                bottom: 12,
                                child: Text(
                                  'Foto capturada',
                                  style: GoogleFonts.nunito(
                                    color: LlanoPayTheme.success,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                            ],
                          )
                        : Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(
                                  Icons.add_a_photo_outlined,
                                  size: 48,
                                  color: LlanoPayTheme.textSecondary
                                      .withOpacity(0.4),
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  'Toma o selecciona una foto',
                                  style: Theme.of(context)
                                      .textTheme
                                      .bodyMedium
                                      ?.copyWith(
                                        color: LlanoPayTheme.textSecondary,
                                      ),
                                ),
                              ],
                            ),
                          ),
                  ),

                  const SizedBox(height: 20),

                  // -- Camera / Gallery buttons --
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () =>
                              _pickImage(ImageSource.camera),
                          icon: const Icon(Icons.camera_alt),
                          label: const Text('Camara'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () =>
                              _pickImage(ImageSource.gallery),
                          icon: const Icon(Icons.photo_library),
                          label: const Text('Galeria'),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 28),

                  // -- Upload progress --
                  if (_isUploading) ...[
                    const LinearProgressIndicator(
                      color: LlanoPayTheme.primaryGreen,
                      backgroundColor: LlanoPayTheme.divider,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'Subiendo documentos...',
                      style: Theme.of(context).textTheme.bodySmall,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),
                  ],

                  // -- Next / Submit button --
                  SizedBox(
                    height: 52,
                    child: ElevatedButton(
                      onPressed: _isUploading ? null : _nextStep,
                      child: Text(
                        _currentStep < 2
                            ? 'Siguiente'
                            : 'Enviar verificacion',
                      ),
                    ),
                  ),

                  if (_currentStep > 0) ...[
                    const SizedBox(height: 12),
                    SizedBox(
                      height: 52,
                      child: OutlinedButton(
                        onPressed: _isUploading
                            ? null
                            : () => setState(() => _currentStep--),
                        child: const Text('Anterior'),
                      ),
                    ),
                  ],

                  const SizedBox(height: 24),
                ],
              ),
            ),
    );
  }

  Widget _buildPendingView() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                color: LlanoPayTheme.secondaryGold.withOpacity(0.15),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.hourglass_bottom,
                color: LlanoPayTheme.secondaryGoldDark,
                size: 48,
              ),
            ),
            const SizedBox(height: 24),
            Text(
              'Verificacion en proceso',
              style: Theme.of(context).textTheme.headlineSmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            Text(
              'Tus documentos estan siendo revisados. Este proceso puede tomar hasta 24 horas. Te notificaremos cuando se complete.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: LlanoPayTheme.textSecondary,
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: () => context.pop(),
                child: const Text('Entendido'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
