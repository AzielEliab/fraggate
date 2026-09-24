import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

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
      theme: buildLightTheme(),
      darkTheme: buildDarkTheme(),
      themeMode: ThemeMode.system,
      home: const DoorPage(),
    );
  }
}

class DoorPage extends StatelessWidget {
  const DoorPage({super.key});

  static const _next = 'fraggate ping';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('FragGate')),
      body: Align(
        alignment: Alignment.topCenter,
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 560),
          child: ListView(
            padding: const EdgeInsets.fromLTRB(20, 24, 20, 32),
            children: [
              Text(
                'Check this kernel',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 8),
              const Text(
                'FragGate runs a registered tool and writes each call to a local ledger.',
              ),
              const SizedBox(height: 20),
              const SelectableText(
                _next,
                style: TextStyle(fontFamily: 'monospace', fontSize: 16),
              ),
              const SizedBox(height: 16),
              FilledButton(
                onPressed: () async {
                  await Clipboard.setData(const ClipboardData(text: _next));
                  if (!context.mounted) return;
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Copied fraggate ping')),
                  );
                },
                child: const Text('Copy command'),
              ),
              const SizedBox(height: 8),
              TextButton(
                onPressed: () {
                  Navigator.of(context).push(
                    MaterialPageRoute<void>(builder: (_) => const AboutPage()),
                  );
                },
                child: const Text('About'),
              ),
              const SizedBox(height: 12),
              const ExpansionTile(
                title: Text('Advanced'),
                initiallyExpanded: false,
                childrenPadding: EdgeInsets.only(bottom: 12),
                children: [
                  _CommandLine('fraggate list'),
                  _CommandLine('fraggate verify runtime.ping'),
                  _CommandLine('fraggate receipt "kernel is local"'),
                  _CommandLine('fraggate call runtime.ping'),
                  _CommandLine('fraggate ui'),
                  Padding(
                    padding: EdgeInsets.only(top: 8),
                    child: Text('Add --json for the ResultEnvelope.'),
                  ),
                  Padding(
                    padding: EdgeInsets.only(top: 8),
                    child: Text(
                      'Public door tools: fraggate_list, fraggate_describe, fraggate_verify, fraggate_call.',
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              Text(
                'Aziel Eliab · 0.1.0',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class AboutPage extends StatelessWidget {
  const AboutPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('About')),
      body: const Align(
        alignment: Alignment.topCenter,
        child: ConstrainedBox(
          constraints: BoxConstraints(maxWidth: 560),
          child: ListView(
            padding: EdgeInsets.fromLTRB(20, 24, 20, 32),
            children: [
              Text(
                'This screen reminds you of the FragGate kernel on your computer. '
                'Copy the command, then run it in a terminal.',
              ),
              SizedBox(height: 16),
              Text('Author: Aziel Eliab'),
              Text('Version: 0.1.0'),
              SizedBox(height: 12),
              Text(
                'Calls append to ./.fraggate/ledger.jsonl on that computer. '
                'Aziel Runtime hosts the public mesh.',
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _CommandLine extends StatelessWidget {
  const _CommandLine(this.command);
  final String command;

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 4),
        child: SelectableText(
          command,
          style: const TextStyle(fontFamily: 'monospace'),
        ),
      ),
    );
  }
}
