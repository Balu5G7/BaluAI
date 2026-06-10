import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import 'home_screen.dart';

class SetupScreen extends StatefulWidget {
  const SetupScreen({super.key});

  @override
  State<SetupScreen> createState() => _SetupScreenState();
}

class _SetupScreenState extends State<SetupScreen> with SingleTickerProviderStateMixin {
  final _ipController = TextEditingController();
  final _tokenController =
      TextEditingController(text: 'jarvis-secret-token-2024');
  final _portController = TextEditingController(text: '8765');
  bool _loading = false;
  String? _error;

  late AnimationController _anim;

  @override
  void initState() {
    super.initState();
    _anim = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 1200));
    _anim.forward();
  }

  @override
  void dispose() {
    _anim.dispose();
    _ipController.dispose();
    _tokenController.dispose();
    _portController.dispose();
    super.dispose();
  }

  Future<void> _connect() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    final api = context.read<ApiService>();
    await api.saveSettings(
      ip: _ipController.text.trim(),
      token: _tokenController.text.trim(),
      port: int.tryParse(_portController.text.trim()) ?? 8765,
    );

    final ok = await api.checkStatus();
    if (ok && mounted) {
      Navigator.pushReplacement(
          context, MaterialPageRoute(builder: (_) => const HomeScreen()));
    } else {
      setState(() {
        _loading = false;
        _error = 'Cannot reach JARVIS server. Check IP and ensure PC is running.';
      });
    }
  }

  Widget _animItem(Widget child, double start, double end) {
    final animation = CurvedAnimation(
      parent: _anim,
      curve: Interval(start, end, curve: Curves.easeOutCubic),
    );
    return FadeTransition(
      opacity: animation,
      child: SlideTransition(
        position: Tween<Offset>(begin: const Offset(0, 0.3), end: Offset.zero)
            .animate(animation),
        child: child,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF010B13), Color(0xFF0A1929)],
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                _animItem(
                  ShaderMask(
                    shaderCallback: (bounds) => const LinearGradient(
                      colors: [Color(0xFF00D4FF), Color(0xFF0066CC)],
                    ).createShader(bounds),
                    child: const Icon(Icons.link, size: 64, color: Colors.white),
                  ),
                  0.0, 0.5,
                ),
                const SizedBox(height: 24),
                _animItem(
                  const Text(
                    'CONNECT TO JARVIS',
                    style: TextStyle(
                      color: Color(0xFF00D4FF),
                      fontSize: 20,
                      letterSpacing: 4,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  0.1, 0.6,
                ),
                const SizedBox(height: 8),
                _animItem(
                  const Text(
                    'Enter your PC\'s local IP address',
                    style: TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                  0.2, 0.7,
                ),
                const SizedBox(height: 40),
                _animItem(
                  _buildField(_ipController, 'PC IP Address', '192.168.x.x',
                      Icons.computer),
                  0.3, 0.8,
                ),
                const SizedBox(height: 16),
                _animItem(
                  _buildField(
                      _portController, 'Port', '8765', Icons.settings_ethernet),
                  0.4, 0.9,
                ),
                const SizedBox(height: 16),
                _animItem(
                  _buildField(
                      _tokenController, 'Auth Token', '', Icons.lock_outline),
                  0.5, 1.0,
                ),
                if (_error != null) ...[
                  const SizedBox(height: 16),
                  _animItem(
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.red.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.redAccent.withOpacity(0.3)),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.error_outline,
                              color: Colors.redAccent, size: 18),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(_error!,
                                style: const TextStyle(
                                    color: Colors.redAccent, fontSize: 12)),
                          ),
                        ],
                      ),
                    ),
                    0.5, 1.0,
                  ),
                ],
                const SizedBox(height: 32),
                _animItem(
                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: ElevatedButton(
                      onPressed: _loading ? null : _connect,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF00D4FF),
                        foregroundColor: const Color(0xFF010B13),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12)),
                      ),
                      child: _loading
                          ? const SizedBox(
                              width: 24,
                              height: 24,
                              child: CircularProgressIndicator(
                                  strokeWidth: 2, color: Color(0xFF010B13)))
                          : const Text('ESTABLISH LINK',
                              style: TextStyle(
                                  fontSize: 16,
                                  letterSpacing: 3,
                                  fontWeight: FontWeight.bold)),
                    ),
                  ),
                  0.6, 1.0,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildField(TextEditingController ctrl, String label, String hint,
      IconData icon) {
    return TextField(
      controller: ctrl,
      style: const TextStyle(color: Colors.white, fontSize: 14),
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        hintStyle: TextStyle(color: Colors.grey.shade700),
        labelStyle: const TextStyle(color: Color(0xFF00D4FF), fontSize: 12),
        prefixIcon: Icon(icon, color: const Color(0xFF00D4FF), size: 20),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: const Color(0xFF00D4FF).withOpacity(0.3)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFF00D4FF)),
        ),
        filled: true,
        fillColor: const Color(0xFF0A1929),
      ),
    );
  }
}
