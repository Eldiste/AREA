import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'route_manager.dart';

void main() async {
  await dotenv.load(fileName: ".env");
  runApp(const AreaApp());
}

class AreaApp extends StatelessWidget {
  const AreaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'AREA',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        primaryColor: const Color(0xFF1C2942),
      ),
      routerConfig: RouteManager.router,
      debugShowCheckedModeBanner: false,
    );
  }
}
