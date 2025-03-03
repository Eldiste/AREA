import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class DashboardPage extends StatefulWidget {
  final bool isDarkMode;
  const DashboardPage({super.key, required this.isDarkMode});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  int totalWorkflows = 0;
  List<dynamic> activeAreas = [];
  Map<int, String> actionNames = {};
  Map<int, String> reactionNames = {};
  bool isLoading = true;
  bool _mounted = true;

  @override
  void initState() {
    super.initState();
    fetchAllData();
  }

  @override
  void dispose() {
    _mounted = false;
    super.dispose();
  }

  Future<List<dynamic>> _fetchData(String endpoint, String errorMessage) async {
    if (!_mounted) return [];
    final ctx = context;

    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token');

      final response = await http.get(
        Uri.parse('${dotenv.env['BASE_URL']}/api/$endpoint'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (!_mounted) return [];

      if (response.statusCode == 200) {
        return json.decode(response.body) as List<dynamic>;
      } else {
        throw Exception('$errorMessage: ${response.statusCode}');
      }
    } catch (e) {
      if (!_mounted) return [];
      if (ctx.mounted) {
        ScaffoldMessenger.of(ctx).showSnackBar(
          SnackBar(content: Text('$errorMessage: $e')),
        );
      }
      return [];
    }
  }

  Future<void> fetchAllData() async {
    if (!_mounted) return;
    setState(() => isLoading = true);

    await Future.wait([
      fetchDashboardData(),
      fetchActions(),
      fetchReactions(),
    ]);

    if (_mounted) {
      setState(() => isLoading = false);
    }
  }

  Future<void> fetchActions() async {
    final data = await _fetchData('actions', 'Failed to load actions');
    if (_mounted && data.isNotEmpty) {
      setState(() {
        actionNames = {
          for (var action in data) action['id'] as int: action['name'] as String
        };
      });
    }
  }

  Future<void> fetchReactions() async {
    final data = await _fetchData('reactions', 'Failed to load reactions');
    if (_mounted && data.isNotEmpty) {
      setState(() {
        reactionNames = {
          for (var reaction in data)
            reaction['id'] as int: reaction['name'] as String
        };
      });
    }
  }

  Future<void> fetchDashboardData() async {
    final data = await _fetchData('areas', 'Failed to load areas');
    if (_mounted && data.isNotEmpty) {
      setState(() {
        activeAreas = data.map((area) {
          area['trigger_config'] ??= {};
          area['action_config'] ??= {};
          area['reaction_config'] ??= {};
          return area;
        }).toList();
        totalWorkflows = activeAreas.length;
      });
    }
  }

  String getActionName(int id) {
    return actionNames[id] ?? "Action #$id";
  }

  String getReactionName(int id) {
    return reactionNames[id] ?? "Reaction #$id";
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: widget.isDarkMode ? Colors.black : Colors.white,
      padding: const EdgeInsets.all(16.0),
      child: isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildHeader(),
                  const SizedBox(height: 20),
                  _buildStatistics(),
                  const SizedBox(height: 20),
                  _buildWorkflowsList(),
                ],
              ),
            ),
    );
  }

  Widget _buildHeader() {
    return Text(
      'Dashboard Overview',
      style: TextStyle(
        fontSize: 28,
        fontWeight: FontWeight.bold,
        color: widget.isDarkMode ? Colors.amber : const Color(0xFF1C2942),
      ),
    );
  }

  Widget _buildStatistics() {
    return Card(
      color: widget.isDarkMode ? Colors.grey[800] : Colors.white,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Active Workflows: $totalWorkflows',
              style: TextStyle(
                fontSize: 20,
                color:
                    widget.isDarkMode ? Colors.amber : const Color(0xFF1C2942),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Last Updated: ${DateTime.now().toString().split('.')[0]}',
              style: TextStyle(
                fontSize: 14,
                color: widget.isDarkMode ? Colors.grey : Colors.grey[600],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWorkflowsList() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Your Active Workflows',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: widget.isDarkMode ? Colors.amber : const Color(0xFF1C2942),
          ),
        ),
        const SizedBox(height: 12),
        ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: activeAreas.length,
          itemBuilder: (context, index) {
            final area = activeAreas[index];
            return Card(
              margin: const EdgeInsets.symmetric(vertical: 8),
              color: widget.isDarkMode ? Colors.grey[800] : Colors.white,
              child: ListTile(
                title: Text(
                  'Workflow #${area['id']}',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: widget.isDarkMode
                        ? Colors.amber
                        : const Color(0xFF1C2942),
                  ),
                ),
                subtitle: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'When: ${getActionName(area['action_id'])}',
                      style: TextStyle(
                        color: widget.isDarkMode
                            ? Colors.grey[300]
                            : Colors.grey[700],
                      ),
                    ),
                    Text(
                      'Then: ${getReactionName(area['reaction_id'])}',
                      style: TextStyle(
                        color: widget.isDarkMode
                            ? Colors.grey[300]
                            : Colors.grey[700],
                      ),
                    ),
                  ],
                ),
                trailing: IconButton(
                  icon: Icon(
                    Icons.delete,
                    color: widget.isDarkMode ? Colors.red[300] : Colors.red,
                  ),
                  onPressed: () async {
                    final ctx = context;
                    final confirmed = await showDialog<bool>(
                      context: ctx,
                      builder: (context) => AlertDialog(
                        title: const Text('Delete Workflow'),
                        content: const Text(
                            'Are you sure you want to delete this workflow?'),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.of(context).pop(false),
                            child: const Text('Cancel'),
                          ),
                          TextButton(
                            onPressed: () => Navigator.of(context).pop(true),
                            style: TextButton.styleFrom(
                              foregroundColor: Colors.red,
                            ),
                            child: const Text('Delete'),
                          ),
                        ],
                      ),
                    );

                    if (confirmed == true && ctx.mounted) {
                      try {
                        final workflowService = WorkflowService();
                        final success =
                            await workflowService.deleteArea(area['id']);

                        if (success && ctx.mounted) {
                          setState(() {
                            activeAreas.removeAt(index);
                            totalWorkflows = activeAreas.length;
                          });

                          ScaffoldMessenger.of(ctx).showSnackBar(
                            const SnackBar(
                              content: Text('Workflow deleted successfully'),
                              backgroundColor: Colors.green,
                            ),
                          );
                        } else {
                          throw Exception('Failed to delete workflow');
                        }
                      } catch (e) {
                        if (ctx.mounted) {
                          ScaffoldMessenger.of(ctx).showSnackBar(
                            SnackBar(
                              content: Text('Error deleting workflow: $e'),
                              backgroundColor: Colors.red,
                            ),
                          );
                        }
                      }
                    }
                  },
                ),
              ),
            );
          },
        ),
      ],
    );
  }
}

class WorkflowService {
  Future<bool> deleteArea(int areaId) async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('auth_token');

    final response = await http.delete(
      Uri.parse('${dotenv.env['BASE_URL']}/api/areas/$areaId'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    return response.statusCode == 200;
  }
}
