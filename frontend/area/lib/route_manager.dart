import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'pages/login_page.dart';
import 'pages/home_page.dart';
import 'pages/profile_page.dart';
import 'utils/auth_utils.dart';

class RouteManager {
  static final GoRouter router = GoRouter(
    initialLocation: '/login',
    redirect: _guardRoutes,
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginPage(),
      ),
      GoRoute(
        path: '/home',
        builder: (context, state) => const HomePage(),
        routes: [
          GoRoute(
            path: 'profile',
            builder: (context, state) {
              final isDarkMode = state.extra as bool? ?? false;
              return ProfilePage(isDarkMode: isDarkMode);
            },
          ),
        ],
      ),
    ],
  );

  static Future<String?> _guardRoutes(
      BuildContext context, GoRouterState state) async {
    final token = await AuthUtils.getAuthToken();
    final isLoggedIn = token != null;
    final isLoginPage = state.location == '/login';

    // If not logged in and not on login page, redirect to login
    if (!isLoggedIn && !isLoginPage) {
      return '/login';
    }

    // If logged in and on login page, redirect to home
    if (isLoggedIn && isLoginPage) {
      return '/home';
    }

    // Allow the navigation to proceed
    return null;
  }
}
