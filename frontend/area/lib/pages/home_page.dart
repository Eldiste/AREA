import 'package:flutter/material.dart';
import 'dashboard_page.dart';
import 'create_workflow_page.dart';
import 'services_page.dart';
import 'package:go_router/go_router.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage>
    with SingleTickerProviderStateMixin {
  int _selectedIndex = 0;
  bool _isDarkMode = false;
  bool _isHoveringProfile = false;

  final List<String> _pageTitles = ['Dashboard', 'Create Workflow', 'Services'];
  late List<Widget> _pages;

  @override
  void initState() {
    super.initState();
    _pages = [
      DashboardPage(isDarkMode: _isDarkMode),
      CreateWorkflowPage(isDarkMode: _isDarkMode),
      ServicesPage(isDarkMode: _isDarkMode),
    ];
  }

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  void _toggleDarkMode() {
    setState(() {
      _isDarkMode = !_isDarkMode;
      _pages = [
        DashboardPage(isDarkMode: _isDarkMode),
        CreateWorkflowPage(isDarkMode: _isDarkMode),
        ServicesPage(isDarkMode: _isDarkMode),
      ];
    });
  }

  void _showProfile() {
    context.push('/home/profile', extra: _isDarkMode);
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
          _pageTitles[_selectedIndex],
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
            onChanged: (value) => _toggleDarkMode(),
            activeColor: Colors.white,
          ),
        ),
        actions: [
          MouseRegion(
            onEnter: (_) {
              setState(() {
                _isHoveringProfile = true;
              });
            },
            onExit: (_) {
              setState(() {
                _isHoveringProfile = false;
              });
            },
            cursor: SystemMouseCursors.click,
            child: GestureDetector(
              onTap: _showProfile,
              child: Padding(
                padding: const EdgeInsets.all(8.0),
                child: AnimatedScale(
                  scale: _isHoveringProfile ? 1.2 : 1.0,
                  duration: const Duration(milliseconds: 200),
                  child: CircleAvatar(
                    radius: 24,
                    backgroundColor: Colors.grey[300],
                    child: Icon(
                      Icons.account_circle,
                      size: 36,
                      color: Colors.grey[700],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
      body: _pages[_selectedIndex],
      bottomNavigationBar: Padding(
        padding: const EdgeInsets.all(16.0),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(16.0),
          child: BottomNavigationBar(
            currentIndex: _selectedIndex,
            onTap: _onItemTapped,
            backgroundColor:
                _isDarkMode ? Colors.grey[800] : const Color(0xFF1C2942),
            selectedItemColor:
                _isDarkMode ? Colors.amber : Colors.lightBlueAccent,
            unselectedItemColor: _isDarkMode ? Colors.grey : Colors.white70,
            items: const [
              BottomNavigationBarItem(
                icon: Icon(Icons.dashboard),
                label: 'Dashboard',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.create),
                label: 'Create Workflow',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.settings),
                label: 'Services',
              ),
            ],
          ),
        ),
      ),
    );
  }
}
