import 'package:flutter/material.dart';
import 'package:flutter_login/flutter_login.dart';
import 'package:go_router/go_router.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class LoginPage extends StatelessWidget {
  const LoginPage({super.key});

  Duration get loginTime => const Duration(milliseconds: 1000);

  Future<String?> _authUser(LoginData data) async {
    try {
      final response = await http.post(
        Uri.parse('${dotenv.env['BASE_URL']}/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username_or_email': data.name,
          'password': data.password,
        }),
      );

      if (response.statusCode == 200) {
        // Save the token
        final token = jsonDecode(response.body)['access_token'];
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('auth_token', token);
        return null; // Return null means success
      } else {
        final error = jsonDecode(response.body)['detail'];
        return error ?? 'Authentication failed';
      }
    } catch (e) {
      return 'Connection error occurred';
    }
  }

  Future<String?> _signupUser(SignupData data) async {
    if (data.name == null || data.password == null) {
      return 'Invalid data provided';
    }

    try {
      // Register the user
      final registerResponse = await http.post(
        Uri.parse('${dotenv.env['BASE_URL']}/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': data.name,
          'email': data.name, // Using email as username for simplicity
          'password': data.password,
        }),
      );

      if (registerResponse.statusCode == 200) {
        // After successful registration, automatically login the user
        final loginResponse = await http.post(
          Uri.parse('${dotenv.env['BASE_URL']}/auth/login'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({
            'username_or_email': data.name,
            'password': data.password,
          }),
        );

        if (loginResponse.statusCode == 200) {
          // Save the token
          final token = jsonDecode(loginResponse.body)['access_token'];
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString('auth_token', token);
          return null; // Return null means success
        } else {
          return 'Login after registration failed';
        }
      } else {
        final error = jsonDecode(registerResponse.body)['detail'];
        return error ?? 'Registration failed';
      }
    } catch (e) {
      return 'Connection error occurred';
    }
  }

  Future<String?> _recoverPassword(String email) async {
    // Implement password recovery if backend supports it
    return 'Password recovery not implemented';
  }

  @override
  Widget build(BuildContext context) {
    return FlutterLogin(
      title: 'AREA',
      onLogin: _authUser,
      onSignup: _signupUser,
      onRecoverPassword: _recoverPassword,
      onSubmitAnimationCompleted: () {
        context.go('/home');
      },
      theme: LoginTheme(
        primaryColor: const Color(0xFF1C2942),
        accentColor: const Color(0xFF3B556D),
        errorColor: Colors.deepOrange,
        titleStyle: const TextStyle(
          color: Colors.white,
          fontWeight: FontWeight.bold,
          fontSize: 36,
        ),
      ),
    );
  }
}
