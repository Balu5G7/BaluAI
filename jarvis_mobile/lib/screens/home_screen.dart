import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:flutter_tts/flutter_tts.dart';
import '../services/api_service.dart';
import 'setup_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with TickerProviderStateMixin {
  final stt.SpeechToText _speech = stt.SpeechToText();
  final FlutterTts _tts = FlutterTts();
  final ScrollController _scrollController = ScrollController();
  final TextEditingController _textController = TextEditingController();

  bool _isListening = false;
  bool _speechAvailable = false;
  String _liveText = '';
  Timer? _statusTimer;

  // Animations
  late AnimationController _pulseController;
  late AnimationController _arcController;
  late Animation<double> _pulseAnim;

  @override
  void initState() {
    super.initState();
    _initSpeech();
    _initTts();

    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    );
    _pulseAnim =
        Tween<double>(begin: 1.0, end: 1.3).animate(CurvedAnimation(
      parent: _pulseController,
      curve: Curves.easeInOut,
    ));

    _arcController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 8),
    )..repeat();

    // Fetch initial data
    final api = context.read<ApiService>();
    api.loadSettings().then((_) {
      api.checkStatus();
      api.fetchHistory();
      api.connectWebSocket();
    });

    // Poll status every 10s
    _statusTimer = Timer.periodic(const Duration(seconds: 10), (_) {
      context.read<ApiService>().checkStatus();
    });
  }

  Future<void> _initSpeech() async {
    _speechAvailable = await _speech.initialize();
  }

  void _initTts() {
    _tts.setLanguage('en-US');
    _tts.setSpeechRate(0.45);
    _tts.setPitch(1.0);
  }

  void _startListening() {
    if (!_speechAvailable) return;
    _pulseController.repeat(reverse: true);
    setState(() {
      _isListening = true;
      _liveText = '';
    });
    _speech.listen(
      onResult: (result) {
        setState(() => _liveText = result.recognizedWords);
        if (result.finalResult && _liveText.isNotEmpty) {
          _stopListening();
          _sendCommand(_liveText);
        }
      },
      listenFor: const Duration(seconds: 30),
      pauseFor: const Duration(seconds: 3),
    );
  }

  void _stopListening() {
    _speech.stop();
    _pulseController.stop();
    _pulseController.reset();
    setState(() => _isListening = false);
  }

  Future<void> _sendCommand(String text) async {
    if (text.trim().isEmpty) return;
    _textController.clear();
    final api = context.read<ApiService>();
    final response = await api.sendCommand(text);
    await _tts.speak(response);
    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _arcController.dispose();
    _statusTimer?.cancel();
    _scrollController.dispose();
    _textController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ApiService>(
      builder: (context, api, _) {
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
              child: Column(
                children: [
                  _buildTopBar(api),
                  _buildStatusBar(api),
                  Expanded(child: _buildChatList(api)),
                  if (_isListening) _buildLiveIndicator(),
                  _buildMicArea(),
                  _buildTextInput(),
                  const SizedBox(height: 8),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  // ─── TOP BAR ───
  Widget _buildTopBar(ApiService api) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: [
          ShaderMask(
            shaderCallback: (b) => const LinearGradient(
              colors: [Color(0xFF00D4FF), Color(0xFF0066CC)],
            ).createShader(b),
            child: const Text('JARVIS',
                style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                    letterSpacing: 6)),
          ),
          const Spacer(),
          _statusDot(api.pcStatus.online),
          const SizedBox(width: 6),
          Text(
            api.pcStatus.online ? 'LINKED' : 'OFFLINE',
            style: TextStyle(
              color: api.pcStatus.online ? const Color(0xFF00FF88) : Colors.redAccent,
              fontSize: 11,
              letterSpacing: 2,
            ),
          ),
          const SizedBox(width: 12),
          IconButton(
            onPressed: () => Navigator.pushReplacement(
                context, MaterialPageRoute(builder: (_) => const SetupScreen())),
            icon:
                const Icon(Icons.settings, color: Color(0xFF00D4FF), size: 20),
          ),
        ],
      ),
    );
  }

  Widget _statusDot(bool online) {
    return Container(
      width: 8,
      height: 8,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: online ? const Color(0xFF00FF88) : Colors.redAccent,
        boxShadow: [
          BoxShadow(
            color: (online ? const Color(0xFF00FF88) : Colors.redAccent)
                .withOpacity(0.5),
            blurRadius: 6,
          ),
        ],
      ),
    );
  }

  // ─── STATUS BAR ───
  Widget _buildStatusBar(ApiService api) {
    if (!api.pcStatus.online) return const SizedBox.shrink();
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: const Color(0xFF00D4FF).withOpacity(0.07),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF00D4FF).withOpacity(0.15)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _statItem('CPU', '${api.pcStatus.cpu.toStringAsFixed(0)}%',
              Icons.memory),
          _statItem('RAM', '${api.pcStatus.ram.toStringAsFixed(0)}%',
              Icons.storage),
          _statItem('OS', api.pcStatus.platform, Icons.computer),
          _statItem(
              'WS',
              api.wsConnected ? 'LIVE' : 'OFF',
              api.wsConnected ? Icons.wifi : Icons.wifi_off),
        ],
      ),
    );
  }

  Widget _statItem(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, color: const Color(0xFF00D4FF), size: 16),
        const SizedBox(height: 4),
        Text(value,
            style: const TextStyle(
                color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
        Text(label,
            style: TextStyle(color: Colors.grey.shade600, fontSize: 9)),
      ],
    );
  }

  // ─── CHAT LIST ───
  Widget _buildChatList(ApiService api) {
    if (api.messages.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.mic_none, size: 48,
                color: const Color(0xFF00D4FF).withOpacity(0.3)),
            const SizedBox(height: 16),
            Text('Tap the microphone to start',
                style: TextStyle(
                    color: Colors.grey.shade600,
                    fontSize: 14,
                    letterSpacing: 1)),
          ],
        ),
      );
    }
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      itemCount: api.messages.length,
      itemBuilder: (ctx, i) {
        final msg = api.messages[i];
        final isUser = msg.role == 'user';
        return TweenAnimationBuilder<double>(
          key: ValueKey('msg_${i}_${msg.content.hashCode}'),
          tween: Tween<double>(begin: 0.0, end: 1.0),
          duration: const Duration(milliseconds: 500),
          curve: Curves.easeOutCubic,
          builder: (context, val, child) {
            return Transform.translate(
              offset: Offset(isUser ? 30 * (1 - val) : -30 * (1 - val), 0),
              child: Opacity(
                opacity: val.clamp(0.0, 1.0),
                child: child,
              ),
            );
          },
          child: Align(
            alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
            child: Container(
              margin: const EdgeInsets.symmetric(vertical: 4),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              constraints:
                  BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.78),
              decoration: BoxDecoration(
                color: isUser
                    ? const Color(0xFF00D4FF).withOpacity(0.12)
                    : const Color(0xFF0A1929),
                borderRadius: BorderRadius.circular(16).copyWith(
                  bottomRight: isUser ? const Radius.circular(4) : null,
                  bottomLeft: !isUser ? const Radius.circular(4) : null,
                ),
                border: Border.all(
                  color: isUser
                      ? const Color(0xFF00D4FF).withOpacity(0.25)
                      : const Color(0xFF00D4FF).withOpacity(0.08),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    isUser ? 'YOU' : 'JARVIS',
                    style: TextStyle(
                      color: isUser
                          ? const Color(0xFF00D4FF)
                          : const Color(0xFF00FF88),
                      fontSize: 9,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 2,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(msg.content,
                      style: const TextStyle(color: Colors.white, fontSize: 14)),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  // ─── LIVE LISTENING INDICATOR ───
  Widget _buildLiveIndicator() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF00D4FF).withOpacity(0.07),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF00D4FF).withOpacity(0.2)),
      ),
      child: Row(
        children: [
          const SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(
                  strokeWidth: 2, color: Color(0xFF00D4FF))),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              _liveText.isEmpty ? 'Listening...' : _liveText,
              style: TextStyle(
                color: _liveText.isEmpty ? Colors.grey : Colors.white,
                fontSize: 13,
                fontStyle:
                    _liveText.isEmpty ? FontStyle.italic : FontStyle.normal,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ─── ANIMATED MIC BUTTON ───
  Widget _buildMicArea() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Rotating arc
          AnimatedBuilder(
            animation: _arcController,
            builder: (_, __) {
              return CustomPaint(
                size: const Size(100, 100),
                painter: _ArcPainter(
                    _arcController.value, _isListening ? 1.0 : 0.3),
              );
            },
          ),
          // Pulse
          ScaleTransition(
            scale: _isListening ? _pulseAnim : const AlwaysStoppedAnimation(1.0),
            child: GestureDetector(
              onTap: _isListening ? _stopListening : _startListening,
              child: Container(
                width: 72,
                height: 72,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: LinearGradient(
                    colors: _isListening
                        ? [const Color(0xFFFF3D00), const Color(0xFFFF6D00)]
                        : [const Color(0xFF00D4FF), const Color(0xFF0066CC)],
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: (_isListening
                              ? const Color(0xFFFF3D00)
                              : const Color(0xFF00D4FF))
                          .withOpacity(0.4),
                      blurRadius: 20,
                      spreadRadius: 2,
                    ),
                  ],
                ),
                child: Icon(
                  _isListening ? Icons.stop : Icons.mic,
                  color: Colors.white,
                  size: 32,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ─── TEXT INPUT FALLBACK ───
  Widget _buildTextInput() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _textController,
              style: const TextStyle(color: Colors.white, fontSize: 14),
              decoration: InputDecoration(
                hintText: 'Type a command...',
                hintStyle: TextStyle(color: Colors.grey.shade700, fontSize: 13),
                filled: true,
                fillColor: const Color(0xFF0A1929),
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide:
                      BorderSide(color: const Color(0xFF00D4FF).withOpacity(0.2)),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide:
                      BorderSide(color: const Color(0xFF00D4FF).withOpacity(0.2)),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide: const BorderSide(color: Color(0xFF00D4FF)),
                ),
              ),
              onSubmitted: (v) => _sendCommand(v),
            ),
          ),
          const SizedBox(width: 8),
          Container(
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: const Color(0xFF00D4FF).withOpacity(0.15),
            ),
            child: IconButton(
              onPressed: () => _sendCommand(_textController.text),
              icon:
                  const Icon(Icons.send, color: Color(0xFF00D4FF), size: 20),
            ),
          ),
        ],
      ),
    );
  }
}

// ─── CUSTOM PAINTERS ───

class _ArcPainter extends CustomPainter {
  final double progress;
  final double opacity;
  _ArcPainter(this.progress, this.opacity);

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final paint = Paint()
      ..color = const Color(0xFF00D4FF).withOpacity(opacity)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.5
      ..strokeCap = StrokeCap.round;

    final startAngle = progress * 2 * pi;
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: 46),
      startAngle,
      pi * 0.7,
      false,
      paint,
    );
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: 46),
      startAngle + pi,
      pi * 0.5,
      false,
      paint..color = const Color(0xFF0066CC).withOpacity(opacity),
    );
  }

  @override
  bool shouldRepaint(covariant _ArcPainter old) => true;
}
