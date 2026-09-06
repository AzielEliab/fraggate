import 'package:flutter/material.dart';

import 'theme.dart';

void main() {
  runApp(const FragGateApp());
}

class FragGateApp extends StatelessWidget {
  const FragGateApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'FragGate',
      debugShowCheckedModeBanner: false,
      theme: buildAppTheme(),
      home: const DoorPage(),
    );
  }
}

class DoorPage extends StatelessWidget {
  const DoorPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('FragGate')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          Text(
            'One door — discover, route, refuse.',
            style: TextStyle(color: kGold, fontStyle: FontStyle.italic, fontSize: 16),
          ),
          SizedBox(height: 8),
          Text(
            'On-device reminder. Not a second kernel. '
            'Human Worker UI and MCP/OpenAPI share List / Describe / Call / Verify.',
          ),
          SizedBox(height: 16),
          _OpCard(
            title: 'List registry',
            body: 'GET /v1/fraggate/list  ·  MCP fraggate_list',
          ),
          _OpCard(
            title: 'Describe',
            body: 'GET /v1/fraggate/describe  ·  MCP fraggate_describe',
          ),
          _OpCard(
            title: 'Call op',
            body: 'POST /v1/fraggate/call  ·  MCP fraggate_call',
          ),
          _OpCard(
            title: 'Verify',
            body: 'POST /v1/fraggate/verify  ·  MCP fraggate_verify',
          ),
          SizedBox(height: 12),
          Text(
            'Canonical agent path:\n'
            'https://aziel-runtime.vibelock.workers.dev/mcp\n'
            'https://aziel-runtime.vibelock.workers.dev/v1/fraggate/*\n\n'
            'Human UI:\n'
            'https://fraggate-download-tracker.vibelock.workers.dev/',
            style: TextStyle(fontFamily: 'monospace', fontSize: 12, height: 1.4),
          ),
        ],
      ),
    );
  }
}

class _OpCard extends StatelessWidget {
  const _OpCard({required this.title, required this.body});
  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(color: kGold, fontWeight: FontWeight.w700)),
            const SizedBox(height: 4),
            Text(body, style: const TextStyle(fontFamily: 'monospace', fontSize: 12, height: 1.4)),
          ],
        ),
      ),
    );
  }
}
