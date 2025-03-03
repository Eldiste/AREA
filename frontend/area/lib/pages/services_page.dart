import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import '../services/workflow_service.dart';
import 'package:flutter/foundation.dart';

class ServicesPage extends StatefulWidget {
  final bool isDarkMode;
  const ServicesPage({super.key, required this.isDarkMode});

  @override
  State<ServicesPage> createState() => _ServicesPageState();
}

class _ServicesPageState extends State<ServicesPage> {
  final WorkflowService _workflowService = WorkflowService();
  List<String> connectedServices = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadConnectedServices();
  }

  Future<void> _loadConnectedServices() async {
    try {
      final services = await _workflowService.getConnectedServices();
      setState(() {
        connectedServices = services;
        isLoading = false;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading connected services: $e')),
        );
      }
      setState(() {
        isLoading = false;
      });
    }
  }

  Future<void> _connectService(String serviceName, String loginUrl) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token');

      if (token == null) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('You are not logged in')),
          );
        }
        return;
      }

      print('Base URL from env: ${dotenv.env['BASE_URL']}');

      final Uri url = Uri.parse(loginUrl).replace(
        queryParameters: {'access_token': token},
      );

      print('Complete URL to launch: ${url.toString()}');

      if (kIsWeb) {
        final result = await launchUrl(
          url,
          webOnlyWindowName: '_self',
        );
        if (!result && mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Failed to open $serviceName login page')),
          );
        }
      } else {
        try {
          final result = await launchUrl(
            url,
            mode: LaunchMode.inAppWebView,
            webViewConfiguration: const WebViewConfiguration(
              enableJavaScript: true,
              enableDomStorage: true,
            ),
          );

          if (!result) {
            final externalResult = await launchUrl(
              url,
              mode: LaunchMode.externalApplication,
            );

            if (!externalResult && mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                    content: Text('Failed to open $serviceName login page')),
              );
            }
          }
        } catch (launchError) {
          print('Error launching URL: $launchError');
          final defaultResult = await launchUrl(
            url,
            mode: LaunchMode.platformDefault,
          );

          if (!defaultResult && mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                  content:
                      Text('All attempts to open $serviceName login failed')),
            );
          }
        }
      }
    } catch (e) {
      print('Error in _connectService: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error connecting to $serviceName: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final backgroundColor = widget.isDarkMode ? Colors.black : Colors.white;
    final cardColor = widget.isDarkMode ? Colors.grey[900] : Colors.grey[100];
    final textColor = widget.isDarkMode ? Colors.amber : Colors.black;
    final subtitleColor =
        widget.isDarkMode ? Colors.grey[500] : Colors.grey[700];

    return Scaffold(
      body: Container(
        color: backgroundColor,
        padding: const EdgeInsets.all(16.0),
        child: ListView(
          children: [
            _buildServiceCard(
              icon: FontAwesomeIcons.discord,
              title: 'Discord',
              description:
                  'Integrate with Discord to manage messages, automate reactions, and handle server events seamlessly.',
              color: const Color(0xFF5865F2),
              loginUrl: '${dotenv.env['BASE_URL']}/oauth/discord/login',
              cardColor: cardColor,
              textColor: textColor,
              subtitleColor: subtitleColor,
              onConnect: () => _connectService(
                  'Discord', '${dotenv.env['BASE_URL']}/oauth/discord/login'),
            ),
            const SizedBox(height: 10),
            _buildServiceCard(
              icon: FontAwesomeIcons.spotify,
              title: 'Spotify',
              description:
                  'Connect with Spotify to monitor playlists, automate song management, and track playback activities.',
              color: const Color(0xFF1DB954),
              loginUrl: '${dotenv.env['BASE_URL']}/oauth/spotify/login',
              cardColor: cardColor,
              textColor: textColor,
              subtitleColor: subtitleColor,
              onConnect: () => _connectService(
                  'Spotify', '${dotenv.env['BASE_URL']}/oauth/spotify/login'),
            ),
            const SizedBox(height: 10),
            _buildServiceCard(
              icon: FontAwesomeIcons.github,
              title: 'GitHub',
              description:
                  'Stay in sync with GitHub to track pull requests, issues, and automate workflows for repositories.',
              color: const Color(0xFF333333),
              loginUrl: '${dotenv.env['BASE_URL']}/oauth/github/login',
              cardColor: cardColor,
              textColor: textColor,
              subtitleColor: subtitleColor,
              onConnect: () => _connectService(
                  'GitHub', '${dotenv.env['BASE_URL']}/oauth/github/login'),
            ),
            const SizedBox(height: 10),
            _buildServiceCard(
              icon: FontAwesomeIcons.google,
              title: 'Google',
              description:
                  'Connect with Google to integrate calendar events, automate tasks, and synchronize your data seamlessly.',
              color: const Color(0xFFDB4437),
              loginUrl: '${dotenv.env['BASE_URL']}/oauth/google/login',
              cardColor: cardColor,
              textColor: textColor,
              subtitleColor: subtitleColor,
              onConnect: () => _connectService(
                  'Google', '${dotenv.env['BASE_URL']}/oauth/google/login'),
            ),
            const SizedBox(height: 10),
            _buildServiceCard(
              icon: FontAwesomeIcons.microsoft,
              title: 'Outlook',
              description:
                  'Manage Outlook mails and calendar events through automation.',
              color: const Color(0xFF0072C6),
              loginUrl: '${dotenv.env['BASE_URL']}/oauth/outlook/login',
              cardColor: cardColor,
              textColor: textColor,
              subtitleColor: subtitleColor,
              onConnect: () => _connectService(
                'Outlook',
                '${dotenv.env['BASE_URL']}/oauth/outlook/login',
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildServiceCard({
    required IconData icon,
    required String title,
    required String description,
    required Color color,
    required String loginUrl,
    required Color? cardColor,
    required Color textColor,
    required Color? subtitleColor,
    required VoidCallback onConnect,
  }) {
    final bool isConnected = connectedServices.contains(title.toLowerCase());

    return Card(
      color: cardColor,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(10),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  backgroundColor: color,
                  child: Icon(icon, color: Colors.white),
                ),
                const SizedBox(width: 12),
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: textColor,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              description,
              style: TextStyle(
                fontSize: 14,
                color: subtitleColor,
              ),
            ),
            const SizedBox(height: 10),
            if (isConnected)
              const Padding(
                padding: EdgeInsets.only(top: 8.0),
                child: Chip(
                  label: Text('Connected'),
                  backgroundColor: Colors.green,
                  labelStyle: TextStyle(color: Colors.white),
                ),
              ),
            Center(
              child: ElevatedButton.icon(
                onPressed: onConnect,
                icon: FaIcon(icon, size: 18, color: Colors.white),
                label:
                    Text(isConnected ? 'Reconnect $title' : 'Connect $title'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: color,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 8,
                  ),
                  shape: const RoundedRectangleBorder(
                    borderRadius: BorderRadius.all(Radius.circular(8)),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
