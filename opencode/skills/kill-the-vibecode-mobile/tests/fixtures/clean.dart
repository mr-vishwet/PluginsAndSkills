// Fixture: a screen written to this plugin's own mobile rules. The tell scanner
// must report zero hits on it.
import 'package:flutter/material.dart';

class TaskSplitScreen extends StatefulWidget {
  const TaskSplitScreen({super.key, required this.controller});

  final SplitController controller;

  @override
  State<TaskSplitScreen> createState() => _TaskSplitScreenState();
}

class _TaskSplitScreenState extends State<TaskSplitScreen> {
  @override
  void initState() {
    super.initState();
    widget.controller.addListener(_onTasksChanged);
  }

  @override
  void dispose() {
    widget.controller.removeListener(_onTasksChanged);
    super.dispose();
  }

  void _onTasksChanged() => setState(() {});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final tasks = widget.controller.value;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Standup, Tuesday'),
        backgroundColor: theme.colorScheme.surface,
        foregroundColor: theme.colorScheme.onSurface,
        elevation: 0,
      ),
      body: SafeArea(
        child: switch (tasks) {
          AsyncData(:final value) when value.isEmpty => _EmptyState(
              onPaste: () => _openTranscript(context),
            ),
          AsyncData(:final value) => _TaskList(rows: value),
          AsyncLoading() => _LoadingList(),
          AsyncFailure(:final error) => _FailureState(
              message: 'Could not reach the server. $error',
              onRetry: widget.controller.refresh,
            ),
          _ => const SizedBox.shrink(),
        },
      ),
    );
  }

  void _openTranscript(BuildContext context) {
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      isScrollControlled: true,
      useSafeArea: true,
      builder: (_) => const TranscriptSheet(),
    );
  }
}

class _TaskList extends StatelessWidget {
  const _TaskList({required this.rows});

  final List<TaskRow> rows;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return ListView.separated(
      itemCount: rows.length,
      separatorBuilder: (_, __) => const SizedBox(height: 8),
      itemBuilder: (context, index) {
        final row = rows[index];
        return ListTile(
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
          minLeadingWidth: 44,
          title: Text(row.title, style: theme.textTheme.bodyLarge),
          subtitle: Text(
            '${row.owner} due ${row.dueDate}',
            style: theme.textTheme.bodyMedium
                ?.copyWith(color: theme.colorScheme.onSurfaceVariant),
          ),
          trailing: Semantics(
            button: true,
            label: 'Reassign ${row.title}',
            child: const Icon(Icons.person_outline, size: 20),
          ),
          onTap: () => _assign(context, row),
        );
      },
    );
  }

  void _assign(BuildContext context, TaskRow row) {/* opens the owner picker */}
}

class _EmptyState extends StatelessWidget {
  const _EmptyState({required this.onPaste});
  final VoidCallback onPaste;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 28),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('No tasks yet',
                style: theme.textTheme.titleMedium,
                textAlign: TextAlign.center),
            const SizedBox(height: 8),
            Text(
              'Paste a transcript and the owners named in the room become tasks.',
              style: theme.textTheme.bodyMedium
                  ?.copyWith(color: theme.colorScheme.onSurfaceVariant),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 20),
            FilledButton(onPressed: onPaste, child: const Text('Paste transcript')),
          ],
        ),
      ),
    );
  }
}

class _FailureState extends StatelessWidget {
  const _FailureState({required this.message, required this.onRetry});
  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) => Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: 16),
            OutlinedButton(onPressed: onRetry, child: const Text('Try again')),
          ],
        ),
      );

class _LoadingList extends StatelessWidget {
  @override
  Widget build(BuildContext context) => ListView.builder(
        itemCount: 6,
        itemBuilder: (_, __) => const Padding(
          padding: EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          child: LinearProgressIndicator(minHeight: 48),
        ),
      );
}

class TranscriptSheet extends StatelessWidget {
  const TranscriptSheet({super.key});
  @override
  Widget build(BuildContext context) => const SizedBox(height: 88);
}
