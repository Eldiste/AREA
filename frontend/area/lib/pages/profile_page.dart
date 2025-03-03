import 'package:area/utils/auth_utils.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:area/services/workflow_service.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class ProfilePage extends StatefulWidget {
  final bool isDarkMode;
  const ProfilePage({super.key, required this.isDarkMode});

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  late bool _isDarkMode;
  final WorkflowService _workflowService = WorkflowService();
  List<String> connectedServices = [];
  String userEmail = '';
  bool isLoading = true;

  // Define service info
  final List<Map<String, dynamic>> services = [
    {
      'name': 'Discord',
      'icon': FontAwesomeIcons.discord,
      'color': const Color(0xFF5865F2),
    },
    {
      'name': 'Spotify',
      'icon': FontAwesomeIcons.spotify,
      'color': const Color(0xFF1DB954),
    },
    {
      'name': 'GitHub',
      'icon': FontAwesomeIcons.github,
      'color': const Color(0xFF333333),
    },
    {
      'name': 'Google',
      'icon': FontAwesomeIcons.google,
      'color': const Color(0xFFDB4437),
    },
    {
      'name': 'Outlook',
      'icon': FontAwesomeIcons.microsoft,
      'color': const Color(0xFF0072C6),
    },
  ];

  @override
  void initState() {
    super.initState();
    _isDarkMode = widget.isDarkMode;
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      // Load connected services
      final services = await _workflowService.getConnectedServices();

      // Load user email
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token');
      final response = await http.get(
        Uri.parse('${dotenv.env['BASE_URL']}/auth/user/email'),
        headers: {
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          connectedServices = services;
          userEmail = data['email'];
          isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading data: $e')),
        );
      }
    }
  }

  void _toggleDarkMode() {
    setState(() {
      _isDarkMode = !_isDarkMode;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _isDarkMode ? Colors.black : Colors.white,
      appBar: AppBar(
        automaticallyImplyLeading: false,
        backgroundColor:
            _isDarkMode ? Colors.grey[900] : const Color(0xFF1C2942),
        title: Text(
          'Profile',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: _isDarkMode ? Colors.amber : Colors.white,
          ),
        ),
        centerTitle: true,
        leading: Padding(
          padding: const EdgeInsets.only(left: 8.0),
          child: Switch(
            value: _isDarkMode,
            onChanged: (value) {
              _toggleDarkMode();
            },
            activeColor: Colors.white,
            inactiveThumbColor: Colors.grey[400],
            inactiveTrackColor:
                _isDarkMode ? Colors.grey[700] : Colors.grey[300],
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(
              Icons.logout,
              color: Colors.white,
            ),
            onPressed: () async {
              await AuthUtils.removeAuthToken();
              if (context.mounted) {
                context.go('/login');
              }
            },
          ),
        ],
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              child: Center(
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      const SizedBox(height: 20),
                      Icon(
                        Icons.account_circle,
                        size: 100,
                        color: _isDarkMode
                            ? Colors.amber
                            : const Color(0xFF1C2942),
                      ),
                      const SizedBox(height: 20),
                      Text(
                        userEmail,
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: _isDarkMode
                              ? Colors.amber
                              : const Color(0xFF1C2942),
                        ),
                      ),
                      const SizedBox(height: 40),
                      Text(
                        'Connected Services',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: _isDarkMode
                              ? Colors.amber
                              : const Color(0xFF1C2942),
                        ),
                      ),
                      const SizedBox(height: 20),
                      Wrap(
                        spacing: 20,
                        runSpacing: 20,
                        children: services.map((service) {
                          final isConnected = connectedServices.contains(
                              service['name'].toString().toLowerCase());
                          return Column(
                            children: [
                              Container(
                                width: 60,
                                height: 60,
                                decoration: BoxDecoration(
                                  color: service['color'],
                                  shape: BoxShape.circle,
                                  border: Border.all(
                                    color: isConnected
                                        ? Colors.green
                                        : Colors.grey,
                                    width: 3,
                                  ),
                                ),
                                child: Icon(
                                  service['icon'],
                                  color: Colors.white,
                                  size: 30,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                service['name'],
                                style: TextStyle(
                                  color: _isDarkMode
                                      ? Colors.amber
                                      : const Color(0xFF1C2942),
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Text(
                                isConnected ? 'Connected' : 'Not Connected',
                                style: TextStyle(
                                  color:
                                      isConnected ? Colors.green : Colors.grey,
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          );
                        }).toList(),
                      ),
                      const SizedBox(height: 40),
                      ElevatedButton(
                        onPressed: () {
                          context.pop();
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: _isDarkMode
                              ? Colors.amber
                              : const Color(0xFF1C2942),
                        ),
                        child: const Text(
                          'Back',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
    );
  }
}
