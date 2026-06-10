import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

class PcStatus {
  final bool online;
  final String platform;
  final double cpu;
  final double ram;

  PcStatus(
      {required this.online,
      required this.platform,
      required this.cpu,
      required this.ram});

  factory PcStatus.offline() =>
      PcStatus(online: false, platform: 'Unknown', cpu: 0, ram: 0);
}

class ChatMessage {
  final String role; // 'user' or 'jarvis'
  final String content;
  final DateTime timestamp;

  ChatMessage(
      {required this.role, required this.content, required this.timestamp});
}

class ApiService extends ChangeNotifier {
  String _serverIp = '';
  String _token = 'jarvis-secret-token-2024';
  int _port = 8765;

  PcStatus _pcStatus = PcStatus.offline();
  List<ChatMessage> _messages = [];
  WebSocketChannel? _ws;
  bool _wsConnected = false;

  String get serverIp => _serverIp;
  String get token => _token;
  int get port => _port;
  PcStatus get pcStatus => _pcStatus;
  List<ChatMessage> get messages => _messages;
  bool get wsConnected => _wsConnected;

  String get baseUrl => 'http://$_serverIp:$_port';
  Map<String, String> get _headers => {
        'Authorization': 'Bearer $_token',
        'Content-Type': 'application/json',
      };

  // --- Persistence ---
  Future<void> loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    _serverIp = prefs.getString('server_ip') ?? '';
    _token = prefs.getString('token') ?? 'jarvis-secret-token-2024';
    _port = prefs.getInt('port') ?? 8765;
    notifyListeners();
  }

  Future<void> saveSettings(
      {required String ip, required String token, required int port}) async {
    _serverIp = ip;
    _token = token;
    _port = port;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('server_ip', ip);
    await prefs.setString('token', token);
    await prefs.setInt('port', port);
    notifyListeners();
  }

  // --- Status ---
  Future<bool> checkStatus() async {
    try {
      final res = await http
          .get(Uri.parse('$baseUrl/status'), headers: _headers)
          .timeout(const Duration(seconds: 5));
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        _pcStatus = PcStatus(
          online: true,
          platform: data['platform'] ?? 'Windows',
          cpu: (data['cpu'] ?? 0).toDouble(),
          ram: (data['ram'] ?? 0).toDouble(),
        );
        notifyListeners();
        return true;
      }
    } catch (_) {}
    _pcStatus = PcStatus.offline();
    notifyListeners();
    return false;
  }

  // --- Commands ---
  Future<String> sendCommand(String command) async {
    _messages.add(ChatMessage(
        role: 'user', content: command, timestamp: DateTime.now()));
    notifyListeners();

    try {
      final res = await http.post(
        Uri.parse('$baseUrl/command'),
        headers: _headers,
        body: jsonEncode({'command': command}),
      );
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        final response = data['response'] as String;
        _messages.add(ChatMessage(
            role: 'jarvis', content: response, timestamp: DateTime.now()));
        notifyListeners();
        return response;
      }
    } catch (e) {
      final err = 'Connection error: $e';
      _messages.add(
          ChatMessage(role: 'jarvis', content: err, timestamp: DateTime.now()));
      notifyListeners();
      return err;
    }
    return 'No response.';
  }

  // --- History ---
  Future<void> fetchHistory() async {
    try {
      final res = await http
          .get(Uri.parse('$baseUrl/history'), headers: _headers)
          .timeout(const Duration(seconds: 5));
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        final history = data['history'] as List;
        _messages = history
            .map((m) => ChatMessage(
                role: m['role'] == 'user' ? 'user' : 'jarvis',
                content: m['content'],
                timestamp: DateTime.now()))
            .toList();
        notifyListeners();
      }
    } catch (_) {}
  }

  Future<void> clearHistory() async {
    try {
      await http.delete(Uri.parse('$baseUrl/history'), headers: _headers);
      _messages.clear();
      notifyListeners();
    } catch (_) {}
  }

  // --- WebSocket ---
  void connectWebSocket() {
    if (_serverIp.isEmpty) return;
    _ws = WebSocketChannel.connect(
        Uri.parse('ws://$_serverIp:$_port/ws'));
    _wsConnected = true;
    notifyListeners();

    _ws!.stream.listen(
      (data) {
        _messages.add(ChatMessage(
            role: 'jarvis', content: data.toString(), timestamp: DateTime.now()));
        notifyListeners();
      },
      onDone: () {
        _wsConnected = false;
        notifyListeners();
      },
      onError: (_) {
        _wsConnected = false;
        notifyListeners();
      },
    );
  }

  void sendViaWebSocket(String text) {
    _ws?.sink.add(text);
    _messages.add(
        ChatMessage(role: 'user', content: text, timestamp: DateTime.now()));
    notifyListeners();
  }

  @override
  void dispose() {
    _ws?.sink.close();
    super.dispose();
  }
}
