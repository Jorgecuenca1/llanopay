import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

import 'config/theme.dart';
import 'config/router.dart';
import 'services/api_service.dart';
import 'services/auth_service.dart';
import 'services/storage_service.dart';
import 'services/websocket_service.dart';
import 'blocs/auth/auth_bloc.dart';
import 'blocs/auth/auth_event.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  final storageService = StorageService();
  final apiService = ApiService(storageService: storageService);
  final authService = AuthService(
    apiService: apiService,
    storageService: storageService,
  );
  final websocketService = WebSocketService(storageService: storageService);

  runApp(
    LlanoPayApp(
      storageService: storageService,
      apiService: apiService,
      authService: authService,
      websocketService: websocketService,
    ),
  );
}

class LlanoPayApp extends StatelessWidget {
  final StorageService storageService;
  final ApiService apiService;
  final AuthService authService;
  final WebSocketService websocketService;

  const LlanoPayApp({
    super.key,
    required this.storageService,
    required this.apiService,
    required this.authService,
    required this.websocketService,
  });

  @override
  Widget build(BuildContext context) {
    return MultiRepositoryProvider(
      providers: [
        RepositoryProvider<StorageService>.value(value: storageService),
        RepositoryProvider<ApiService>.value(value: apiService),
        RepositoryProvider<AuthService>.value(value: authService),
        RepositoryProvider<WebSocketService>.value(value: websocketService),
      ],
      child: BlocProvider(
        create: (_) => AuthBloc(
          authService: authService,
          storageService: storageService,
        )..add(const AppStarted()),
        child: MaterialApp.router(
          title: 'SuperNova',
          debugShowCheckedModeBanner: false,
          theme: LlanoPayTheme.lightTheme,
          routerConfig: AppRouter.router,
          locale: const Locale('es', 'CO'),
          supportedLocales: const [
            Locale('es', 'CO'),
            Locale('es'),
            Locale('en'),
          ],
          localizationsDelegates: const [
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
        ),
      ),
    );
  }
}
