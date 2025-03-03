import 'dart:convert';
import 'package:flutter/material.dart';
import '../services/workflow_service.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class CreateWorkflowPage extends StatefulWidget {
  final bool isDarkMode;
  const CreateWorkflowPage({super.key, required this.isDarkMode});

  @override
  State<CreateWorkflowPage> createState() => _CreateWorkflowPageState();
}

class _CreateWorkflowPageState extends State<CreateWorkflowPage> {
  final WorkflowService _workflowService = WorkflowService();
  List<Map<String, dynamic>> actions = [];
  List<Map<String, dynamic>> reactions = [];
  Map<String, dynamic>? selectedAction;
  Map<String, dynamic>? selectedReaction;
  Map<String, dynamic>? actionConfigSchema;
  Map<String, dynamic>? reactionConfigSchema;
  Map<String, dynamic>? triggerConfigSchema;
  bool isLoading = true;
  final Map<String, TextEditingController> _actionControllers = {};
  final Map<String, TextEditingController> _reactionControllers = {};
  final Map<String, TextEditingController> _triggerControllers = {};
  final List<Map<String, String>> _filterConditions = [];
  final Map<String, List<TextEditingController>> _arrayControllers = {};

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  @override
  void dispose() {
    _actionControllers.forEach((key, controller) => controller.dispose());
    _reactionControllers.forEach((key, controller) => controller.dispose());
    _triggerControllers.forEach((key, controller) => controller.dispose());
    super.dispose();
  }

  Future<void> _loadData() async {
    try {
      final actionsData = await _workflowService.getActions();
      final reactionsData = await _workflowService.getReactions();

      setState(() {
        actions = actionsData;
        reactions = reactionsData;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading data: $e')),
        );
      }
    }
  }

  Future<void> _loadActionConfigSchema(String actionName) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token');

      final headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      };

      final response = await http.get(
        Uri.parse('${dotenv.env['BASE_URL']}/api/config/action/generic_action'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        setState(() {
          actionConfigSchema = json.decode(response.body)['config_schema'];
          _actionControllers.clear();
          _actionControllers['match'] = TextEditingController(text: 'all');
          _actionControllers['conditions'] = TextEditingController();
        });
      } else {
        throw Exception('Failed to load action config schema');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading action config schema: $e')),
        );
      }
    }
  }

  Future<void> _loadReactionConfigSchema(String reactionName) async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('auth_token');
    final headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };

    final response = await http.get(
      Uri.parse('${dotenv.env['BASE_URL']}/api/config/reaction/$reactionName'),
      headers: headers,
    );

    if (response.statusCode == 200) {
      setState(() {
        reactionConfigSchema = json.decode(response.body)['config_schema'];
        _reactionControllers.clear();
        final props =
            reactionConfigSchema!['properties'] as Map<String, dynamic>;
        props.forEach((key, value) {
          _reactionControllers[key] = TextEditingController();
        });
      });
    } else {
      throw Exception('Failed to load reaction config schema');
    }
  }

  Future<void> _loadTriggerConfigSchema(String actionName) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token');

      final headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      };

      final response = await http.get(
        Uri.parse('${dotenv.env['BASE_URL']}/api/config/trigger/$actionName'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        setState(() {
          triggerConfigSchema = json.decode(response.body)['config_schema'];
          _triggerControllers.clear();
          if (triggerConfigSchema != null &&
              triggerConfigSchema!['properties'] != null) {
            final properties =
                triggerConfigSchema!['properties'] as Map<String, dynamic>;
            properties.forEach((key, value) {
              _triggerControllers[key] = TextEditingController();
            });
          }
        });
      } else {
        throw Exception('Failed to load trigger config schema');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading trigger config schema: $e')),
        );
      }
    }
  }

  Widget _buildActionConfig() {
    if (selectedAction == null || actionConfigSchema == null) {
      return const SizedBox.shrink();
    }

    final textColor = widget.isDarkMode ? Colors.amber : Colors.black;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Action Configuration',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: textColor,
          ),
        ),
        const SizedBox(height: 16),
        Text(
          'Filter Match Logic',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: textColor,
          ),
        ),
        const SizedBox(height: 8),
        DropdownButton<String>(
          value: _actionControllers['match']?.text ?? 'all',
          dropdownColor: widget.isDarkMode ? Colors.grey[900] : Colors.white,
          items: ['all', 'any'].map((String value) {
            return DropdownMenuItem<String>(
              value: value,
              child: Text(
                value,
                style: TextStyle(color: textColor),
              ),
            );
          }).toList(),
          onChanged: (String? newValue) {
            setState(() {
              _actionControllers['match']?.text = newValue ?? 'all';
            });
          },
        ),
        const SizedBox(height: 16),
        Text(
          'Filter Conditions',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: textColor,
          ),
        ),
        const SizedBox(height: 8),
        ..._filterConditions.asMap().entries.map((entry) {
          final index = entry.key;
          final condition = entry.value;
          return Padding(
            padding: const EdgeInsets.only(bottom: 16.0),
            child: Card(
              color: widget.isDarkMode ? Colors.grey[900] : Colors.grey[100],
              child: Padding(
                padding: const EdgeInsets.all(8.0),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            onChanged: (value) {
                              _filterConditions[index]['field'] = value;
                            },
                            style: TextStyle(color: textColor),
                            decoration: InputDecoration(
                              labelText: 'Field',
                              labelStyle: TextStyle(color: textColor),
                              hintText: 'e.g., message content, channel_id',
                              hintStyle:
                                  TextStyle(color: textColor.withOpacity(0.5)),
                            ),
                            controller:
                                TextEditingController(text: condition['field']),
                          ),
                        ),
                        IconButton(
                          icon: Icon(Icons.delete, color: textColor),
                          onPressed: () {
                            setState(() {
                              _filterConditions.removeAt(index);
                            });
                          },
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      onChanged: (value) {
                        _filterConditions[index]['operator'] = value;
                      },
                      style: TextStyle(color: textColor),
                      decoration: InputDecoration(
                        labelText: 'Operator',
                        labelStyle: TextStyle(color: textColor),
                        hintText: 'e.g., contains, equals',
                        hintStyle: TextStyle(color: textColor.withOpacity(0.5)),
                      ),
                      controller:
                          TextEditingController(text: condition['operator']),
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      onChanged: (value) {
                        _filterConditions[index]['value'] = value;
                      },
                      style: TextStyle(color: textColor),
                      decoration: InputDecoration(
                        labelText: 'Value',
                        labelStyle: TextStyle(color: textColor),
                        hintText: 'e.g., urgent, 12345',
                        hintStyle: TextStyle(color: textColor.withOpacity(0.5)),
                      ),
                      controller:
                          TextEditingController(text: condition['value']),
                    ),
                  ],
                ),
              ),
            ),
          );
        }),
        const SizedBox(height: 8),
        ElevatedButton(
          onPressed: () {
            setState(() {
              _filterConditions.add({
                'field': '',
                'operator': '',
                'value': '',
              });
            });
          },
          style: ElevatedButton.styleFrom(
            backgroundColor:
                widget.isDarkMode ? Colors.amber : const Color(0xFF1C2942),
          ),
          child: Text(
            'Add Filter Condition',
            style: TextStyle(
              color: widget.isDarkMode ? Colors.black : Colors.white,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildReactionConfig() {
    if (reactionConfigSchema == null) return const SizedBox.shrink();
    final props = reactionConfigSchema!['properties'] as Map<String, dynamic>?;
    if (props == null) return const SizedBox.shrink();

    final textColor = widget.isDarkMode ? Colors.amber : Colors.black;

    final filteredProps = props.entries
        .where((entry) => entry.key != 'description' && entry.key != 'token');

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Reaction Configuration',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: textColor,
          ),
        ),
        const SizedBox(height: 16),
        ...filteredProps.map((entry) {
          final key = entry.key;
          final value = entry.value as Map<String, dynamic>;
          final title = value['title'] as String? ?? key;
          final description = value['description'] as String?;

          // Check if field is an array type
          final isArray = value['anyOf'] != null &&
              (value['anyOf'] as List).any((type) =>
                  type is Map<String, dynamic> &&
                  type['type'] == 'array' &&
                  type['items']?['type'] == 'string');

          if (isArray) {
            _arrayControllers.putIfAbsent(key, () => [TextEditingController()]);

            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: textColor,
                    )),
                if (description != null)
                  Text(description,
                      style: TextStyle(
                        fontSize: 12,
                        color: textColor.withOpacity(0.7),
                      )),
                const SizedBox(height: 8),
                ..._arrayControllers[key]!.asMap().entries.map((entry) {
                  final index = entry.key;
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 8.0),
                    child: Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: entry.value,
                            style: TextStyle(color: textColor),
                            decoration: InputDecoration(
                              hintText: 'Enter $title ${index + 1}',
                              hintStyle:
                                  TextStyle(color: textColor.withOpacity(0.5)),
                            ),
                          ),
                        ),
                        IconButton(
                          icon: Icon(Icons.remove_circle, color: textColor),
                          onPressed: () {
                            setState(() {
                              _arrayControllers[key]!.removeAt(index);
                            });
                          },
                        ),
                      ],
                    ),
                  );
                }),
                ElevatedButton(
                  onPressed: () {
                    setState(() {
                      _arrayControllers[key]!.add(TextEditingController());
                    });
                  },
                  child: Text('Add $title'),
                ),
                const SizedBox(height: 16),
              ],
            );
          }

          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: textColor,
                ),
              ),
              if (description != null)
                Padding(
                  padding: const EdgeInsets.only(top: 4.0, bottom: 8.0),
                  child: Text(
                    description,
                    style: TextStyle(
                      fontSize: 12,
                      color: textColor.withOpacity(0.7),
                    ),
                  ),
                ),
              const SizedBox(height: 8),
              TextField(
                controller: _reactionControllers[key],
                keyboardType: TextInputType.text,
                style: TextStyle(color: textColor),
                decoration: InputDecoration(
                  hintText: 'Enter $title',
                  hintStyle: TextStyle(color: textColor.withOpacity(0.5)),
                  enabledBorder: OutlineInputBorder(
                    borderSide: BorderSide(color: textColor.withOpacity(0.3)),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderSide: BorderSide(color: textColor),
                  ),
                ),
              ),
              const SizedBox(height: 16),
            ],
          );
        }),
      ],
    );
  }

  Widget _buildTriggerConfig() {
    if (selectedAction == null || triggerConfigSchema == null) {
      return const SizedBox.shrink();
    }
    final properties =
        triggerConfigSchema!['properties'] as Map<String, dynamic>?;
    if (properties == null) return const SizedBox.shrink();

    final textColor = widget.isDarkMode ? Colors.amber : Colors.black;
    final required = triggerConfigSchema!['required'] as List<dynamic>? ?? [];

    final filteredProperties = properties.entries.where((entry) {
      return required.contains(entry.key) || entry.key == 'interval';
    });

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Trigger Configuration',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: textColor,
          ),
        ),
        const SizedBox(height: 16),
        ...filteredProperties.map((entry) {
          final key = entry.key;
          final value = entry.value as Map<String, dynamic>;
          final title = value['title'] as String? ?? key;
          final type = value['type'] as String? ?? 'string';
          final description = value['description'] as String?;

          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: textColor,
                ),
              ),
              if (description != null)
                Padding(
                  padding: const EdgeInsets.only(top: 4.0, bottom: 8.0),
                  child: Text(
                    description,
                    style: TextStyle(
                      fontSize: 12,
                      color: textColor.withOpacity(0.7),
                    ),
                  ),
                ),
              const SizedBox(height: 8),
              TextField(
                controller: _triggerControllers[key],
                keyboardType: type == 'string'
                    ? TextInputType.text
                    : TextInputType.number,
                style: TextStyle(color: textColor),
                decoration: InputDecoration(
                  hintText: 'Enter $title',
                  hintStyle: TextStyle(color: textColor.withOpacity(0.5)),
                  enabledBorder: OutlineInputBorder(
                    borderSide: BorderSide(color: textColor.withOpacity(0.3)),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderSide: BorderSide(color: textColor),
                  ),
                ),
              ),
              const SizedBox(height: 16),
            ],
          );
        }),
      ],
    );
  }

  Future<void> _createWorkflow() async {
    if (selectedAction == null || selectedReaction == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
            content: Text('Please select both an action and a reaction')),
      );
      return;
    }

    Map<String, dynamic> actionConfig = {};
    if (_filterConditions.isNotEmpty) {
      actionConfig['filter'] = {
        'match': _actionControllers['match']?.text ?? 'all',
        'conditions': _filterConditions,
      };
    }

    Map<String, dynamic> reactionConfig = {};
    Map<String, String> triggerConfig = {};

    if (reactionConfigSchema != null) {
      final properties =
          reactionConfigSchema!['properties'] as Map<String, dynamic>;
      for (var key in properties.keys) {
        if (key != 'description' && key != 'token') {
          if (_arrayControllers.containsKey(key)) {
            // Handle array fields - keep as array instead of converting to string
            final values = _arrayControllers[key]!
                .map((controller) => controller.text)
                .where((text) => text.isNotEmpty)
                .toList();
            if (values.isNotEmpty) {
              reactionConfig[key] = values; // Keep as array
            }
          } else {
            final value = _reactionControllers[key]?.text ?? '';
            if (value.isNotEmpty) {
              reactionConfig[key] = value;
            }
          }
        }
      }
    }

    if (triggerConfigSchema != null) {
      final properties =
          triggerConfigSchema!['properties'] as Map<String, dynamic>;
      final required = triggerConfigSchema!['required'] as List<dynamic>? ?? [];

      for (var key in properties.keys) {
        if ((required.contains(key) || key == 'interval') && key != 'token') {
          final value = _triggerControllers[key]?.text ?? '';
          if (value.isNotEmpty) {
            triggerConfig[key] = value;
          }
        }
      }
    }

    try {
      if (selectedAction == null || selectedReaction == null) {
        throw Exception('Action and reaction must be selected');
      }

      await _workflowService.createWorkflow(
        actionId: selectedAction!['id'],
        reactionId: selectedReaction!['id'],
        actionConfig: actionConfig,
        reactionConfig:
            reactionConfig, // Send as is, without converting to string
        triggerConfig: triggerConfig,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Workflow created successfully')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error creating workflow: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final backgroundColor = widget.isDarkMode ? Colors.black : Colors.white;
    final textColor = widget.isDarkMode ? Colors.amber : Colors.black;
    final dropdownColor = widget.isDarkMode ? Colors.grey[900] : Colors.white;

    if (isLoading) {
      return Scaffold(
        backgroundColor: backgroundColor,
        body: Center(
          child: CircularProgressIndicator(
            color: widget.isDarkMode ? Colors.amber : Colors.blue,
          ),
        ),
      );
    }

    Map<String, List<Map<String, dynamic>>> groupedActions = {};

    for (var action in actions) {
      final id = action['service_id'] as int?;
      if (id == 4) {
        groupedActions.putIfAbsent('Discord', () => []).add(action);
      } else if (id == 8) {
        groupedActions.putIfAbsent('Google', () => []).add(action);
      } else if (id == 5) {
        groupedActions.putIfAbsent('GitHub', () => []).add(action);
      } else if (id == 6) {
        groupedActions.putIfAbsent('Spotify', () => []).add(action);
      } else if (id == 7) {
        groupedActions.putIfAbsent('Outlook', () => []).add(action);
      } else if (id == 1) {
        groupedActions.putIfAbsent('Time', () => []).add(action);
      } else if (id == 2) {
        groupedActions.putIfAbsent('Misc', () => []).add(action);
      } else {
        final serviceName = action['service'] ?? 'Unknown';
        groupedActions.putIfAbsent(serviceName, () => []).add(action);
      }
    }

    Map<String, List<Map<String, dynamic>>> groupedReactions = {};

    for (var reaction in reactions) {
      final id = reaction['service_id'] as int?;
      if (id == 4) {
        groupedReactions.putIfAbsent('Discord', () => []).add(reaction);
      } else if (id == 8) {
        groupedReactions.putIfAbsent('Google', () => []).add(reaction);
      } else if (id == 5) {
        groupedReactions.putIfAbsent('GitHub', () => []).add(reaction);
      } else if (id == 6) {
        groupedReactions.putIfAbsent('Spotify', () => []).add(reaction);
      } else if (id == 7) {
        groupedReactions.putIfAbsent('Outlook', () => []).add(reaction);
      } else if (id == 1) {
        groupedReactions.putIfAbsent('Time', () => []).add(reaction);
      } else if (id == 2) {
        groupedReactions.putIfAbsent('Misc', () => []).add(reaction);
      } else {
        final serviceName = reaction['service'] ?? 'Unknown';
        groupedReactions.putIfAbsent(serviceName, () => []).add(reaction);
      }
    }

    return Scaffold(
      backgroundColor: backgroundColor,
      appBar: AppBar(
        title: Text('Create Workflow', style: TextStyle(color: textColor)),
        backgroundColor: backgroundColor,
        iconTheme: IconThemeData(color: textColor),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Select an Action',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: textColor,
                ),
              ),
              const SizedBox(height: 10),
              DropdownButton<Map<String, dynamic>>(
                dropdownColor: dropdownColor,
                value: selectedAction,
                isExpanded: true,
                hint: Text('Choose an Action',
                    style: TextStyle(color: textColor)),
                items: groupedActions.entries.expand((entry) {
                  final serviceName = entry.key;
                  final actions = entry.value;
                  return [
                    DropdownMenuItem<Map<String, dynamic>>(
                      enabled: false,
                      child: Text(
                        serviceName,
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: textColor,
                        ),
                      ),
                    ),
                    ...actions.map((action) {
                      return DropdownMenuItem<Map<String, dynamic>>(
                        value: action,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              action['name'],
                              style: TextStyle(color: textColor),
                            ),
                            Text(
                              action['description'] ?? '',
                              style: TextStyle(
                                color: textColor.withOpacity(0.7),
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      );
                    }),
                  ];
                }).toList(),
                onChanged: (value) {
                  if (value != null) {
                    setState(() {
                      selectedAction = value;
                      _loadActionConfigSchema(value['name']);
                      _loadTriggerConfigSchema(value['name']);
                    });
                  }
                },
              ),
              const SizedBox(height: 20),
              _buildActionConfig(),
              const SizedBox(height: 20),
              _buildTriggerConfig(),
              const SizedBox(height: 20),
              Text(
                'Select a Reaction',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: textColor,
                ),
              ),
              const SizedBox(height: 10),
              DropdownButton<Map<String, dynamic>>(
                dropdownColor: dropdownColor,
                value: selectedReaction,
                isExpanded: true,
                hint: Text('Choose a Reaction',
                    style: TextStyle(color: textColor)),
                items: groupedReactions.entries.expand((entry) {
                  final serviceName = entry.key;
                  final reactions = entry.value;
                  return [
                    DropdownMenuItem<Map<String, dynamic>>(
                      enabled: false,
                      child: Text(
                        serviceName,
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: textColor,
                        ),
                      ),
                    ),
                    ...reactions.map((reaction) {
                      return DropdownMenuItem<Map<String, dynamic>>(
                        value: reaction,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              reaction['name'],
                              style: TextStyle(color: textColor),
                            ),
                            Text(
                              reaction['description'] ?? '',
                              style: TextStyle(
                                color: textColor.withOpacity(0.7),
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      );
                    }),
                  ];
                }).toList(),
                onChanged: (value) {
                  if (value != null) {
                    setState(() {
                      selectedReaction = value;
                      _loadReactionConfigSchema(value['name']);
                    });
                  }
                },
              ),
              const SizedBox(height: 40),
              _buildReactionConfig(),
              const SizedBox(height: 40),
              Center(
                child: ElevatedButton(
                  onPressed: _createWorkflow,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: widget.isDarkMode
                        ? Colors.amber
                        : const Color(0xFF1C2942),
                    padding: const EdgeInsets.symmetric(
                        horizontal: 20, vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                  child: Text(
                    'Create Workflow',
                    style: TextStyle(
                      color: widget.isDarkMode ? Colors.black : Colors.white,
                      fontSize: 16,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
