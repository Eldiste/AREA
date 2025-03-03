import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart'
    show SharedPreferences;
import 'package:flutter_dotenv/flutter_dotenv.dart';

class WorkflowService {
  static final String baseUrl = '${dotenv.env['BASE_URL']}/api';

  Future<String?> _getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('auth_token');
  }

  Map<String, String> _getHeaders(String? token) {
    return {
      'Content-Type': 'application/json',
      'accept': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  Future<List<Map<String, dynamic>>> getActions() async {
    try {
      final token = await _getToken();
      final response = await http.get(
        Uri.parse('$baseUrl/actions'),
        headers: _getHeaders(token),
      );

      if (response.statusCode == 200) {
        final List<dynamic> jsonResponse = json.decode(response.body);
        return jsonResponse.cast<Map<String, dynamic>>();
      } else {
        throw Exception('Failed to load actions: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to load actions: $e');
    }
  }

  Future<List<Map<String, dynamic>>> getReactions() async {
    try {
      final token = await _getToken();
      final response = await http.get(
        Uri.parse('$baseUrl/reactions'),
        headers: _getHeaders(token),
      );

      if (response.statusCode == 200) {
        final List<dynamic> jsonResponse = json.decode(response.body);
        return jsonResponse.cast<Map<String, dynamic>>();
      } else {
        throw Exception('Failed to load reactions: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to load reactions: $e');
    }
  }

  Future<List<String>> getConnectedServices() async {
    try {
      final token = await _getToken();
      final response = await http.get(
        Uri.parse('$baseUrl/user_services/connected'),
        headers: _getHeaders(token),
      );

      if (response.statusCode == 200) {
        final List<dynamic> services = json.decode(response.body);
        return services.cast<String>();
      } else {
        throw Exception(
            'Failed to load connected services: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to load connected services: $e');
    }
  }

  Future<void> _createTrigger({
    required int areaId,
    required String actionName,
    required Map<String, String> triggerConfig,
  }) async {
    final token = await _getToken();
    if (token == null) {
      throw Exception('No authentication token found');
    }

    final triggerData = {
      'area_id': areaId,
      'name': actionName,
      'config': triggerConfig.isEmpty ? {'interval': 15} : triggerConfig,
    };

    final response = await http.post(
      Uri.parse('$baseUrl/triggers'),
      headers: _getHeaders(token),
      body: json.encode(triggerData),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to create trigger: ${response.statusCode}');
    }
  }

  Future<int> createWorkflow({
    required int actionId,
    required int reactionId,
    required Map<String, dynamic> actionConfig,
    required Map<String, dynamic>
        reactionConfig, // Changed from Map<String, String>
    required Map<String, String> triggerConfig,
  }) async {
    final token = await _getToken();
    if (token == null) {
      throw Exception('No authentication token found');
    }

    final workflowData = {
      'action_id': actionId,
      'reaction_id': reactionId,
      'action_config': actionConfig,
      'reaction_config':
          reactionConfig, // Send as is, without converting values to string
    };

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/areas'),
        headers: _getHeaders(token),
        body: json.encode(workflowData),
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to create workflow: ${response.statusCode}');
      }

      Map<String, dynamic> responseData = {};
      try {
        responseData = json.decode(response.body);
      } catch (e) {
        // Silently handle parse error since we have a fallback mechanism
      }

      int areaId;
      if (responseData.containsKey('id')) {
        areaId = responseData['id'];
      } else {
        final areas = await getAreas();
        if (areas.isEmpty) {
          throw Exception('Could not determine area ID');
        }
        areaId = areas.last['id'];
      }

      final actions = await getActions();
      final action = actions.firstWhere((a) => a['id'] == actionId);
      final actionName = action['name'] as String;

      await _createTrigger(
        areaId: areaId,
        actionName: actionName,
        triggerConfig: triggerConfig,
      );

      return areaId;
    } catch (e) {
      throw Exception('Failed to create workflow: $e');
    }
  }

  Future<List<Map<String, dynamic>>> getAreas() async {
    final token = await _getToken();
    if (token == null) {
      throw Exception('No authentication token found');
    }

    final response = await http.get(
      Uri.parse('$baseUrl/areas'),
      headers: _getHeaders(token),
    );

    if (response.statusCode == 200) {
      List<dynamic> areas = json.decode(response.body);
      return areas.cast<Map<String, dynamic>>();
    }
    throw Exception('Failed to fetch areas');
  }
}
