import 'dart:convert';
import 'dart:io';

const _planRelativePath = 'docs/planning/ENGINEERING_PLAN.json';
const _mapRelativePath = 'docs/planning/PROJECT_MAP.md';
const _matrixRelativePath = 'docs/planning/TRACEABILITY_MATRIX.md';
const _allowedStatuses = <String>{
  'planned',
  'ready',
  'in_progress',
  'verification_pending',
  'done',
  'blocked',
  'deferred',
  'superseded',
};
const _activeStatuses = <String>{'in_progress', 'verification_pending'};
const _requiredRoles = <String>{
  'MD',
  'LEGAL',
  'SEC',
  'TECH',
  'QA',
  'ETHICS',
  'PO',
};

void main(List<String> arguments) {
  try {
    final parsed = _parseArguments(arguments);
    final root = _resolveProjectRoot(parsed.projectRoot);
    final plan = _readJsonObject(_resolveManagedPath(root, _planRelativePath));

    switch (parsed.command) {
      case 'validate':
        _exitOnErrors(_validatePlan(plan, root));
        stdout.writeln('YunMom engineering plan: VALID');
        return;
      case 'render':
        _exitOnErrors(_validatePlan(plan, root));
        _writeGeneratedViews(plan, root);
        stdout.writeln('YunMom engineering plan: RENDERED');
        return;
      case 'check':
        _exitOnErrors(_validatePlan(plan, root));
        _checkGeneratedViews(plan, root);
        stdout.writeln('YunMom engineering plan: CHECKED');
        return;
      case 'self-test':
        _runSelfTests(plan, root);
        stdout.writeln('YunMom engineering plan: SELF-TEST PASSED');
        return;
      default:
        _usageError('Unknown command: ${parsed.command}');
    }
  } on PlanError catch (error) {
    stderr.writeln(error.message);
    exitCode = 2;
  } on FileSystemException catch (error) {
    stderr.writeln('File-system error: ${error.message}');
    exitCode = 2;
  } on FormatException catch (error) {
    stderr.writeln('Format error: ${error.message}');
    exitCode = 2;
  }
}

final class _Arguments {
  const _Arguments({required this.command, this.projectRoot});

  final String command;
  final String? projectRoot;
}

_Arguments _parseArguments(List<String> arguments) {
  if (arguments.isEmpty ||
      arguments.contains('--help') ||
      arguments.contains('-h')) {
    stdout.writeln(
      'Usage: dart run tool/plan_ops.dart '
      '<validate|render|check|self-test> [--project-root <path>]',
    );
    exit(0);
  }

  String? root;
  final positional = <String>[];
  for (var index = 0; index < arguments.length; index += 1) {
    final argument = arguments[index];
    if (argument == '--project-root') {
      if (index + 1 >= arguments.length) {
        _usageError('--project-root requires a path.');
      }
      root = arguments[++index];
    } else if (argument.startsWith('-')) {
      _usageError('Unknown option: $argument');
    } else {
      positional.add(argument);
    }
  }
  if (positional.length != 1) {
    _usageError('Exactly one command is required.');
  }
  return _Arguments(command: positional.single, projectRoot: root);
}

Never _usageError(String message) => throw PlanError(message);

Directory _resolveProjectRoot(String? explicitRoot) {
  if (explicitRoot != null) {
    return _validateProjectRoot(Directory(explicitRoot).absolute);
  }

  var current = Directory.current.absolute;
  while (true) {
    if (_isProjectRoot(current)) {
      return current;
    }
    final parent = current.parent;
    if (parent.path == current.path) {
      break;
    }
    current = parent;
  }

  final scriptRoot = File.fromUri(Platform.script).parent.parent.absolute;
  return _validateProjectRoot(scriptRoot);
}

Directory _validateProjectRoot(Directory directory) {
  if (!_isProjectRoot(directory)) {
    throw PlanError('Not a YunMom project root: ${directory.path}');
  }
  return directory;
}

bool _isProjectRoot(Directory directory) =>
    File(_join(directory.path, 'pubspec.yaml')).existsSync() &&
    File(_join(directory.path, _planRelativePath)).existsSync();

String _join(String first, String second) {
  final normalized = second.replaceAll('/', Platform.pathSeparator);
  return '$first${Platform.pathSeparator}$normalized';
}

File _resolveManagedPath(Directory root, String relativePath) {
  if (relativePath.isEmpty ||
      relativePath.contains('\\') ||
      relativePath.startsWith('/') ||
      RegExp(r'^[A-Za-z]:').hasMatch(relativePath)) {
    throw PlanError(
      'Managed path must be non-empty project-relative POSIX text: $relativePath',
    );
  }
  final segments = relativePath.split('/');
  if (segments.any(
    (segment) => segment.isEmpty || segment == '.' || segment == '..',
  )) {
    throw PlanError('Managed path contains an invalid segment: $relativePath');
  }
  final candidate = File(_join(root.path, relativePath)).absolute;
  final rootPrefix = '${root.absolute.path}${Platform.pathSeparator}'
      .toLowerCase();
  if (!candidate.path.toLowerCase().startsWith(rootPrefix)) {
    throw PlanError('Managed path escaped the project root: $relativePath');
  }
  return candidate;
}

Map<String, dynamic> _readJsonObject(File file) {
  final decoded = jsonDecode(file.readAsStringSync());
  if (decoded is! Map<String, dynamic>) {
    throw PlanError('Expected a JSON object: ${file.path}');
  }
  return decoded;
}

List<String> _validatePlan(
  Map<String, dynamic> plan,
  Directory root, {
  bool verifyFileBindings = true,
}) {
  final errors = <String>[];
  final requiredTopLevel = <String>{
    'schema_version',
    'plan_id',
    'program_version',
    'updated_at',
    'release_status',
    'current_stage',
    'authority',
    'visual_input',
    'path_ownership',
    'stages',
    'evidence',
    'work_items',
  };
  final unknownTopLevel = plan.keys.toSet().difference(requiredTopLevel);
  final missingTopLevel = requiredTopLevel.difference(plan.keys.toSet());
  if (unknownTopLevel.isNotEmpty) {
    errors.add('SCHEMA_UNKNOWN_TOP_LEVEL: ${unknownTopLevel.join(', ')}');
  }
  if (missingTopLevel.isNotEmpty) {
    errors.add('SCHEMA_MISSING_TOP_LEVEL: ${missingTopLevel.join(', ')}');
    return errors;
  }
  if (plan['schema_version'] != 1) {
    errors.add('SCHEMA_VERSION: expected 1');
  }
  if (plan['plan_id'] != 'yunmom-engineering-program') {
    errors.add('PLAN_ID: unexpected plan_id');
  }
  if (plan['release_status'] != 'RELEASE_NOT_APPROVED' &&
      plan['release_status'] != 'RELEASE_APPROVED') {
    errors.add('RELEASE_STATUS: unsupported release status');
  }
  _validateZonedTimestamp(plan['updated_at'], 'updated_at', errors);

  final authority = _objectList(plan['authority'], 'authority', errors);
  final stages = _objectList(plan['stages'], 'stages', errors);
  final evidence = _objectList(plan['evidence'], 'evidence', errors);
  final workItems = _objectList(plan['work_items'], 'work_items', errors);

  final ledgerBinding = authority
      .where((item) => item['kind'] == 'decision_ledger')
      .toList();
  if (ledgerBinding.length != 1) {
    errors.add(
      'AUTHORITY_LEDGER: exactly one decision_ledger binding is required',
    );
    return errors;
  }
  final ledgerPath = ledgerBinding.single['path'];
  if (ledgerPath is! String) {
    errors.add('AUTHORITY_LEDGER_PATH: decision ledger path must be a string');
    return errors;
  }
  final ledgerFile = _safeResolve(
    root,
    ledgerPath,
    'AUTHORITY_LEDGER_PATH',
    errors,
  );
  final contractIds = <String>{};
  if (ledgerFile != null && ledgerFile.existsSync()) {
    contractIds.addAll(
      RegExp(r'^###\s+([A-Z0-9]+-[0-9]+)', multiLine: true)
          .allMatches(ledgerFile.readAsStringSync())
          .map((match) => match.group(1)!),
    );
    if (contractIds.length != 91) {
      errors.add(
        'CONTRACT_CATALOG_COUNT: expected 91, found ${contractIds.length}',
      );
    }
  } else {
    errors.add('AUTHORITY_LEDGER_MISSING: $ledgerPath');
  }

  if (verifyFileBindings) {
    for (final binding in authority) {
      _validateFileBinding(binding, root, 'AUTHORITY', errors);
    }
  }

  final stageById = <String, Map<String, dynamic>>{};
  for (final stage in stages) {
    final id = stage['id'];
    if (id is! String || !RegExp(r'^M([0-9]|1[01])$').hasMatch(id)) {
      errors.add('STAGE_ID: invalid stage id $id');
      continue;
    }
    if (stageById.containsKey(id)) {
      errors.add('STAGE_DUPLICATE: $id');
    } else {
      stageById[id] = stage;
    }
    _requireNonEmptyString(stage['title'], 'STAGE_TITLE:$id', errors);
    _requireNonEmptyStrings(stage['exit_criteria'], 'STAGE_EXIT:$id', errors);
  }
  if (stageById.length != 12) {
    errors.add('STAGE_COUNT: expected 12, found ${stageById.length}');
  }
  if (!stageById.containsKey(plan['current_stage'])) {
    errors.add('CURRENT_STAGE: ${plan['current_stage']} does not exist');
  }
  final stageEdges = <String, List<String>>{};
  for (final entry in stageById.entries) {
    final dependencies = _stringList(
      entry.value['depends_on'],
      'STAGE_DEPENDS:${entry.key}',
      errors,
    );
    for (final dependency in dependencies) {
      if (!stageById.containsKey(dependency)) {
        errors.add('STAGE_DEPENDENCY_UNKNOWN: ${entry.key} -> $dependency');
      }
    }
    stageEdges[entry.key] = dependencies;
  }
  _findCycles(stageEdges, 'STAGE_CYCLE', errors);

  final evidenceById = <String, Map<String, dynamic>>{};
  for (final record in evidence) {
    final id = record['id'];
    if (id is! String || !RegExp(r'^EV-[A-Z0-9-]+$').hasMatch(id)) {
      errors.add('EVIDENCE_ID: invalid evidence id $id');
      continue;
    }
    if (evidenceById.containsKey(id)) {
      errors.add('EVIDENCE_DUPLICATE: $id');
    } else {
      evidenceById[id] = record;
    }
    final sourceCommit = record['source_commit'];
    if (sourceCommit is! String ||
        !RegExp(r'^[a-f0-9]{40}$').hasMatch(sourceCommit)) {
      errors.add('EVIDENCE_SOURCE_COMMIT:$id');
    }
    if (!const {'pass', 'fail', 'blocked'}.contains(record['result'])) {
      errors.add('EVIDENCE_RESULT:$id');
    }
    if (!const {
      'no_health_content',
      'synthetic',
      'irreversibly_deidentified',
    }.contains(record['data_class'])) {
      errors.add('EVIDENCE_DATA_CLASS:$id');
    }
    _validateZonedTimestamp(record['captured_at'], 'EVIDENCE_TIME:$id', errors);
    _requireNonEmptyStrings(
      record['reviewer_roles'],
      'EVIDENCE_REVIEWERS:$id',
      errors,
    );
    if (verifyFileBindings) {
      _validateFileBinding(record, root, 'EVIDENCE:$id', errors);
    }
  }

  final itemById = <String, Map<String, dynamic>>{};
  final referencedContracts = <String>{};
  final workEdges = <String, List<String>>{};
  for (final item in workItems) {
    final id = item['id'];
    if (id is! String || !RegExp(r'^M([0-9]|1[01])-WP[0-9]{2}$').hasMatch(id)) {
      errors.add('WORK_ID: invalid work-item id $id');
      continue;
    }
    if (itemById.containsKey(id)) {
      errors.add('WORK_DUPLICATE: $id');
    } else {
      itemById[id] = item;
    }
    if (!stageById.containsKey(item['stage'])) {
      errors.add('WORK_STAGE_UNKNOWN:$id:${item['stage']}');
    }
    if (!_allowedStatuses.contains(item['status'])) {
      errors.add('WORK_STATUS:$id:${item['status']}');
    }
    final scopeClass = item['scope_class'];
    if (scopeClass != 'required' &&
        scopeClass != 'future_explicitly_excluded') {
      errors.add('WORK_SCOPE:$id:$scopeClass');
    }
    if (scopeClass == 'required' && item['status'] == 'deferred') {
      errors.add('REQUIRED_DEFERRED:$id');
    }
    if (item['status'] == 'blocked') {
      final blocker = item['blocker'];
      if (blocker is! Map<String, dynamic> ||
          blocker['type'] is! String ||
          blocker['owner'] is! String ||
          blocker['exit_condition'] is! String) {
        errors.add('BLOCKER_INCOMPLETE:$id');
      }
    }
    if (item['status'] == 'superseded' &&
        (item['successor'] is! String || item['change_ref'] is! String)) {
      errors.add('SUPERSEDED_INCOMPLETE:$id');
    }
    _requireNonEmptyString(item['title'], 'WORK_TITLE:$id', errors);
    _requireNonEmptyStrings(item['owner_roles'], 'WORK_OWNERS:$id', errors);
    _requireNonEmptyStrings(
      item['deliverables'],
      'WORK_DELIVERABLES:$id',
      errors,
    );
    _requireNonEmptyStrings(item['acceptance'], 'WORK_ACCEPTANCE:$id', errors);

    final refs = _stringList(
      item['contract_refs'],
      'WORK_CONTRACTS:$id',
      errors,
    );
    if (refs.isEmpty) {
      errors.add('WORK_CONTRACTS_EMPTY:$id');
    }
    for (final ref in refs) {
      referencedContracts.add(ref);
      if (!contractIds.contains(ref)) {
        errors.add('CONTRACT_UNKNOWN:$id:$ref');
      }
    }
    final engRefs = _stringList(
      item['eng_attachment_refs'],
      'WORK_ENG:$id',
      errors,
    );
    if (engRefs.isEmpty) {
      errors.add('WORK_ENG_EMPTY:$id');
    }
    for (final ref in engRefs) {
      if (!RegExp(r'^ENG-(0[0-9]|1[0-5])$').hasMatch(ref)) {
        errors.add('ENG_UNKNOWN:$id:$ref');
      }
    }
    final evidenceRefs = _stringList(
      item['evidence_refs'],
      'WORK_EVIDENCE:$id',
      errors,
    );
    for (final ref in evidenceRefs) {
      if (!evidenceById.containsKey(ref)) {
        errors.add('EVIDENCE_REF_UNKNOWN:$id:$ref');
      }
    }
    if (item['status'] == 'done') {
      if (evidenceRefs.isEmpty) {
        errors.add('DONE_WITHOUT_EVIDENCE:$id');
      }
      for (final ref in evidenceRefs) {
        if (evidenceById[ref]?['result'] != 'pass') {
          errors.add('DONE_WITHOUT_PASSING_EVIDENCE:$id:$ref');
        }
      }
    }
    workEdges[id] = _stringList(item['depends_on'], 'WORK_DEPENDS:$id', errors);
    _stringList(item['path_claims'], 'WORK_PATHS:$id', errors);
    _stringList(item['external_gates'], 'WORK_GATES:$id', errors);
  }

  for (final entry in workEdges.entries) {
    for (final dependency in entry.value) {
      if (!itemById.containsKey(dependency)) {
        errors.add('WORK_DEPENDENCY_UNKNOWN:${entry.key}:$dependency');
      }
    }
  }
  _findCycles(workEdges, 'WORK_CYCLE', errors);

  for (final item in workItems) {
    final id = item['id'];
    if (id is! String || !itemById.containsKey(id)) {
      continue;
    }
    if (const {
      'ready',
      'in_progress',
      'verification_pending',
      'done',
    }.contains(item['status'])) {
      for (final dependency in workEdges[id] ?? const <String>[]) {
        if (itemById[dependency]?['status'] != 'done') {
          errors.add('WORK_DEPENDENCY_NOT_DONE:$id:$dependency');
        }
      }
    }
  }

  final uncovered = contractIds.difference(referencedContracts);
  if (uncovered.isNotEmpty) {
    errors.add('CONTRACT_UNCOVERED:${uncovered.toList()..sort()}');
  }

  final activeItems = workItems
      .where((item) => _activeStatuses.contains(item['status']))
      .toList();
  for (var left = 0; left < activeItems.length; left += 1) {
    for (var right = left + 1; right < activeItems.length; right += 1) {
      final leftPaths = _stringList(
        activeItems[left]['path_claims'],
        'ACTIVE_PATHS',
        errors,
      );
      final rightPaths = _stringList(
        activeItems[right]['path_claims'],
        'ACTIVE_PATHS',
        errors,
      );
      for (final leftPath in leftPaths) {
        for (final rightPath in rightPaths) {
          if (_pathClaimsOverlap(leftPath, rightPath)) {
            errors.add(
              'ACTIVE_PATH_OVERLAP:${activeItems[left]['id']}:${activeItems[right]['id']}:$leftPath:$rightPath',
            );
          }
        }
      }
    }
  }

  final visual = plan['visual_input'];
  if (visual is! Map<String, dynamic>) {
    errors.add('VISUAL_INPUT: expected object');
  } else {
    final visualPath = visual['path'];
    if (visualPath is! String) {
      errors.add('VISUAL_PATH: expected string');
    } else {
      final visualFile = _safeResolve(root, visualPath, 'VISUAL_PATH', errors);
      if (visualFile == null || !visualFile.existsSync()) {
        errors.add('VISUAL_MISSING:$visualPath');
      } else if (verifyFileBindings) {
        final actualHash = _sha256File(visualFile);
        if (visual['sha256'] != actualHash) {
          errors.add('VISUAL_HASH_MISMATCH:$visualPath');
        }
        final actual = _readJsonObject(visualFile);
        if (visual['observed_revision'] != actual['revision']) {
          errors.add(
            'VISUAL_REVISION_DRIFT:${visual['observed_revision']}:${actual['revision']}',
          );
        }
        if (visual['observed_gate'] != actual['current_gate']) {
          errors.add(
            'VISUAL_GATE_DRIFT:${visual['observed_gate']}:${actual['current_gate']}',
          );
        }
        if (visual['observed_release_status'] != actual['release_status']) {
          errors.add('VISUAL_RELEASE_DRIFT');
        }
      }
    }
  }

  if (plan['release_status'] == 'RELEASE_APPROVED') {
    final finalItems = workItems
        .where((item) => item['stage'] == 'M11')
        .toList();
    final hasAllRoles = finalItems
        .expand(
          (item) => _stringList(item['owner_roles'], 'RELEASE_ROLES', errors),
        )
        .toSet()
        .containsAll(_requiredRoles);
    if (finalItems.isEmpty ||
        finalItems.any((item) => item['status'] != 'done') ||
        !hasAllRoles) {
      errors.add('RELEASE_APPROVAL_WITHOUT_SEVEN_PARTY_SIGNOFF');
    }
  }

  return errors;
}

List<Map<String, dynamic>> _objectList(
  Object? value,
  String label,
  List<String> errors,
) {
  if (value is! List) {
    errors.add('$label: expected array');
    return <Map<String, dynamic>>[];
  }
  final result = <Map<String, dynamic>>[];
  for (var index = 0; index < value.length; index += 1) {
    final item = value[index];
    if (item is! Map<String, dynamic>) {
      errors.add('$label[$index]: expected object');
    } else {
      result.add(item);
    }
  }
  return result;
}

List<String> _stringList(Object? value, String label, List<String> errors) {
  if (value is! List) {
    errors.add('$label: expected array');
    return const <String>[];
  }
  final result = <String>[];
  for (var index = 0; index < value.length; index += 1) {
    final item = value[index];
    if (item is! String || item.isEmpty) {
      errors.add('$label[$index]: expected non-empty string');
    } else {
      result.add(item);
    }
  }
  return result;
}

void _requireNonEmptyString(Object? value, String label, List<String> errors) {
  if (value is! String || value.trim().isEmpty) {
    errors.add('$label: expected non-empty string');
  }
}

void _requireNonEmptyStrings(Object? value, String label, List<String> errors) {
  if (_stringList(value, label, errors).isEmpty) {
    errors.add('$label: at least one value is required');
  }
}

void _validateZonedTimestamp(Object? value, String label, List<String> errors) {
  if (value is! String ||
      !RegExp(r'(Z|[+-][0-9]{2}:[0-9]{2})$').hasMatch(value)) {
    errors.add('$label: timestamp must include a timezone');
    return;
  }
  try {
    DateTime.parse(value);
  } on FormatException {
    errors.add('$label: invalid timestamp');
  }
}

void _validateFileBinding(
  Map<String, dynamic> binding,
  Directory root,
  String label,
  List<String> errors,
) {
  final path = binding['path'];
  final expectedHash = binding['sha256'];
  if (path is! String) {
    errors.add('$label: path must be a string');
    return;
  }
  if (expectedHash is! String ||
      !RegExp(r'^[a-f0-9]{64}$').hasMatch(expectedHash)) {
    errors.add('$label: sha256 must be lowercase hexadecimal');
    return;
  }
  final file = _safeResolve(root, path, label, errors);
  if (file == null || !file.existsSync()) {
    errors.add('$label: missing file $path');
    return;
  }
  final actualHash = _sha256File(file);
  if (actualHash != expectedHash) {
    errors.add('$label: hash mismatch for $path');
  }
}

File? _safeResolve(
  Directory root,
  String path,
  String label,
  List<String> errors,
) {
  try {
    return _resolveManagedPath(root, path);
  } on PlanError catch (error) {
    errors.add('$label: ${error.message}');
    return null;
  }
}

void _findCycles(
  Map<String, List<String>> graph,
  String label,
  List<String> errors,
) {
  final visiting = <String>{};
  final visited = <String>{};

  bool visit(String node, List<String> stack) {
    if (visiting.contains(node)) {
      final start = stack.indexOf(node);
      final cycle = <String>[...stack.sublist(start), node];
      errors.add('$label:${cycle.join('->')}');
      return true;
    }
    if (visited.contains(node)) {
      return false;
    }
    visiting.add(node);
    stack.add(node);
    for (final dependency in graph[node] ?? const <String>[]) {
      if (graph.containsKey(dependency)) {
        visit(dependency, stack);
      }
    }
    stack.removeLast();
    visiting.remove(node);
    visited.add(node);
    return false;
  }

  for (final node in graph.keys) {
    visit(node, <String>[]);
  }
}

bool _pathClaimsOverlap(String left, String right) {
  String prefix(String value) =>
      value.endsWith('/**') ? value.substring(0, value.length - 3) : value;
  final leftPrefix = prefix(left);
  final rightPrefix = prefix(right);
  return leftPrefix == rightPrefix ||
      leftPrefix.startsWith('$rightPrefix/') ||
      rightPrefix.startsWith('$leftPrefix/');
}

void _exitOnErrors(List<String> errors) {
  if (errors.isEmpty) {
    return;
  }
  throw PlanError('Engineering plan is invalid:\n- ${errors.join('\n- ')}');
}

void _writeGeneratedViews(Map<String, dynamic> plan, Directory root) {
  final mapFile = _resolveManagedPath(root, _mapRelativePath);
  final matrixFile = _resolveManagedPath(root, _matrixRelativePath);
  mapFile.writeAsStringSync(_renderProjectMap(plan), flush: true);
  matrixFile.writeAsStringSync(_renderTraceabilityMatrix(plan), flush: true);
}

void _checkGeneratedViews(Map<String, dynamic> plan, Directory root) {
  final expected = <String, String>{
    _mapRelativePath: _renderProjectMap(plan),
    _matrixRelativePath: _renderTraceabilityMatrix(plan),
  };
  final drift = <String>[];
  for (final entry in expected.entries) {
    final file = _resolveManagedPath(root, entry.key);
    if (!file.existsSync()) {
      drift.add('${entry.key} is missing');
      continue;
    }
    final actual = file.readAsStringSync().replaceAll('\r\n', '\n');
    if (actual != entry.value) {
      drift.add('${entry.key} is stale');
    }
  }
  if (drift.isNotEmpty) {
    throw PlanError(
      'Generated planning views drifted:\n- ${drift.join('\n- ')}\n'
      'Run: dart run tool/plan_ops.dart render',
    );
  }
}

String _renderProjectMap(Map<String, dynamic> plan) {
  final stages = (plan['stages'] as List).cast<Map<String, dynamic>>();
  final workItems = (plan['work_items'] as List).cast<Map<String, dynamic>>();
  final visual = plan['visual_input'] as Map<String, dynamic>;
  final buffer = StringBuffer()
    ..writeln('<!-- GENERATED by tool/plan_ops.dart. DO NOT EDIT. -->')
    ..writeln('# YunMom engineering project map')
    ..writeln()
    ..writeln('- Program version: `${plan['program_version']}`')
    ..writeln('- Current stage: `${plan['current_stage']}`')
    ..writeln('- Release: `${plan['release_status']}`')
    ..writeln(
      '- Visual input: revision `${visual['observed_revision']}`, gate `${visual['observed_gate']}`, status `${visual['observed_release_status']}`',
    )
    ..writeln()
    ..writeln('## Stage dependency graph')
    ..writeln()
    ..writeln('```mermaid')
    ..writeln('flowchart LR');
  for (final stage in stages) {
    final id = stage['id'];
    final title = _mermaidText(stage['title'].toString());
    buffer.writeln('  $id["$id · $title"]');
  }
  for (final stage in stages) {
    for (final dependency in (stage['depends_on'] as List).cast<String>()) {
      buffer.writeln('  $dependency --> ${stage['id']}');
    }
  }
  buffer
    ..writeln('```')
    ..writeln()
    ..writeln('## Execution frontier')
    ..writeln()
    ..writeln(
      '| Work item | Stage | Status | Title | Dependencies | External gates |',
    )
    ..writeln('|---|---|---|---|---|---|');
  for (final item in workItems) {
    buffer.writeln(
      '| `${item['id']}` | `${item['stage']}` | `${item['status']}` | '
      '${_cell(item['title'])} | ${_cellList(item['depends_on'])} | ${_cellList(item['external_gates'])} |',
    );
  }
  buffer
    ..writeln()
    ..writeln('## Trust and workstream boundaries')
    ..writeln()
    ..writeln('```mermaid')
    ..writeln('flowchart LR')
    ..writeln(
      '  LOCAL["Local Event Store · health source of truth"] --> APP["Flutter/native adapters"]',
    )
    ..writeln('  APP -->|"minimal consented capsule"| GW["Stateless Gateway"]')
    ..writeln('  APP -->|"BYOK direct"| PROVIDER["Approved Provider"]')
    ..writeln('  GW --> PROVIDER')
    ..writeln('  ACCOUNT["Identity · entitlement · metering metadata"] --> GW')
    ..writeln('  LOCAL -. "health content never persists" .-> ACCOUNT')
    ..writeln('```')
    ..writeln()
    ..writeln('## Path ownership')
    ..writeln()
    ..writeln('| Stream | Paths |')
    ..writeln('|---|---|');
  for (final ownership
      in (plan['path_ownership'] as List).cast<Map<String, dynamic>>()) {
    buffer.writeln(
      '| `${ownership['stream']}` | ${_cellList(ownership['paths'])} |',
    );
  }
  return buffer.toString();
}

String _renderTraceabilityMatrix(Map<String, dynamic> plan) {
  final workItems = (plan['work_items'] as List).cast<Map<String, dynamic>>();
  final coveredContracts = <String>{};
  final buffer = StringBuffer()
    ..writeln('<!-- GENERATED by tool/plan_ops.dart. DO NOT EDIT. -->')
    ..writeln('# YunMom engineering traceability matrix')
    ..writeln()
    ..writeln(
      '| Work item | Status | Contract IDs | ENG attachments | Deliverables | Acceptance | Evidence | Owners |',
    )
    ..writeln('|---|---|---|---|---|---|---|---|');
  for (final item in workItems) {
    coveredContracts.addAll((item['contract_refs'] as List).cast<String>());
    buffer.writeln(
      '| `${item['id']}` | `${item['status']}` | ${_cellList(item['contract_refs'])} | '
      '${_cellList(item['eng_attachment_refs'])} | ${_cellList(item['deliverables'])} | '
      '${_cellList(item['acceptance'])} | ${_cellList(item['evidence_refs'])} | '
      '${_cellList(item['owner_roles'])} |',
    );
  }
  final sortedContracts = coveredContracts.toList()..sort();
  buffer
    ..writeln()
    ..writeln('## Contract coverage')
    ..writeln()
    ..writeln('- Covered decision IDs: `${sortedContracts.length}`')
    ..writeln('- IDs: ${sortedContracts.map((id) => '`$id`').join(', ')}')
    ..writeln()
    ..writeln(
      'Engineering completion does not change `${plan['release_status']}`; release requires `SIGN-001` on one build.',
    );
  return buffer.toString();
}

String _cell(Object? value) =>
    value.toString().replaceAll('|', r'\|').replaceAll('\n', '<br>');

String _cellList(Object? value) {
  if (value is! List || value.isEmpty) {
    return '—';
  }
  return value.map(_cell).join('<br>');
}

String _mermaidText(String value) =>
    value.replaceAll('"', "'").replaceAll('\n', ' ');

void _runSelfTests(Map<String, dynamic> plan, Directory root) {
  final actualErrors = _validatePlan(plan, root);
  if (actualErrors.isNotEmpty) {
    throw PlanError(
      'Cannot self-test an invalid canonical plan:\n${actualErrors.join('\n')}',
    );
  }
  if (_sha256Bytes(utf8.encode('abc')) !=
      'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad') {
    throw PlanError('SELF_TEST_SHA256: known vector failed');
  }

  void expectError(String name, Map<String, dynamic> candidate, String marker) {
    final errors = _validatePlan(candidate, root);
    if (!errors.any((error) => error.contains(marker))) {
      throw PlanError(
        'SELF_TEST_$name: expected $marker, got ${errors.join(' | ')}',
      );
    }
  }

  Map<String, dynamic> clone() =>
      jsonDecode(jsonEncode(plan)) as Map<String, dynamic>;

  final duplicate = clone();
  (duplicate['work_items'] as List).add(
    (duplicate['work_items'] as List).first,
  );
  expectError('DUPLICATE', duplicate, 'WORK_DUPLICATE');

  final unknownContract = clone();
  ((unknownContract['work_items'] as List)[0]['contract_refs'] as List).add(
    'NOPE-999',
  );
  expectError('UNKNOWN_CONTRACT', unknownContract, 'CONTRACT_UNKNOWN');

  final cycle = clone();
  ((cycle['work_items'] as List)[0]['depends_on'] as List).add('M0-WP02');
  expectError('CYCLE', cycle, 'WORK_CYCLE');

  final deferred = clone();
  (deferred['work_items'] as List)[0]['status'] = 'deferred';
  expectError('REQUIRED_DEFERRED', deferred, 'REQUIRED_DEFERRED');

  final doneWithoutEvidence = clone();
  (doneWithoutEvidence['work_items'] as List)[0]['evidence_refs'] = <String>[];
  expectError('DONE_EVIDENCE', doneWithoutEvidence, 'DONE_WITHOUT_EVIDENCE');

  final badAuthority = clone();
  (badAuthority['authority'] as List)[0]['sha256'] = List<String>.filled(
    64,
    '0',
  ).join();
  expectError('AUTHORITY_HASH', badAuthority, 'hash mismatch');

  final visualDrift = clone();
  (visualDrift['visual_input'] as Map<String, dynamic>)['observed_revision'] =
      999;
  expectError('VISUAL_DRIFT', visualDrift, 'VISUAL_REVISION_DRIFT');

  final overlap = clone();
  final items = overlap['work_items'] as List;
  items[0]['status'] = 'verification_pending';
  items[0]['path_claims'] = <String>['docs/planning/**'];
  items[1]['status'] = 'in_progress';
  items[1]['path_claims'] = <String>['docs/planning/**'];
  expectError('PATH_OVERLAP', overlap, 'ACTIVE_PATH_OVERLAP');

  final expectedMap = _renderProjectMap(plan);
  if (!expectedMap.contains('flowchart LR') || !expectedMap.contains('M11')) {
    throw PlanError('SELF_TEST_RENDER: project map is incomplete');
  }
}

String _sha256File(File file) => _sha256Bytes(file.readAsBytesSync());

String _sha256Bytes(List<int> input) {
  final bytes = <int>[...input];
  final bitLength = input.length * 8;
  bytes.add(0x80);
  while ((bytes.length % 64) != 56) {
    bytes.add(0);
  }
  for (var shift = 56; shift >= 0; shift -= 8) {
    bytes.add((bitLength >>> shift) & 0xff);
  }

  final hash = <int>[
    0x6a09e667,
    0xbb67ae85,
    0x3c6ef372,
    0xa54ff53a,
    0x510e527f,
    0x9b05688c,
    0x1f83d9ab,
    0x5be0cd19,
  ];
  const constants = <int>[
    0x428a2f98,
    0x71374491,
    0xb5c0fbcf,
    0xe9b5dba5,
    0x3956c25b,
    0x59f111f1,
    0x923f82a4,
    0xab1c5ed5,
    0xd807aa98,
    0x12835b01,
    0x243185be,
    0x550c7dc3,
    0x72be5d74,
    0x80deb1fe,
    0x9bdc06a7,
    0xc19bf174,
    0xe49b69c1,
    0xefbe4786,
    0x0fc19dc6,
    0x240ca1cc,
    0x2de92c6f,
    0x4a7484aa,
    0x5cb0a9dc,
    0x76f988da,
    0x983e5152,
    0xa831c66d,
    0xb00327c8,
    0xbf597fc7,
    0xc6e00bf3,
    0xd5a79147,
    0x06ca6351,
    0x14292967,
    0x27b70a85,
    0x2e1b2138,
    0x4d2c6dfc,
    0x53380d13,
    0x650a7354,
    0x766a0abb,
    0x81c2c92e,
    0x92722c85,
    0xa2bfe8a1,
    0xa81a664b,
    0xc24b8b70,
    0xc76c51a3,
    0xd192e819,
    0xd6990624,
    0xf40e3585,
    0x106aa070,
    0x19a4c116,
    0x1e376c08,
    0x2748774c,
    0x34b0bcb5,
    0x391c0cb3,
    0x4ed8aa4a,
    0x5b9cca4f,
    0x682e6ff3,
    0x748f82ee,
    0x78a5636f,
    0x84c87814,
    0x8cc70208,
    0x90befffa,
    0xa4506ceb,
    0xbef9a3f7,
    0xc67178f2,
  ];

  for (var offset = 0; offset < bytes.length; offset += 64) {
    final schedule = List<int>.filled(64, 0);
    for (var index = 0; index < 16; index += 1) {
      final base = offset + index * 4;
      schedule[index] =
          (bytes[base] << 24) |
          (bytes[base + 1] << 16) |
          (bytes[base + 2] << 8) |
          bytes[base + 3];
    }
    for (var index = 16; index < 64; index += 1) {
      final s0 =
          _rotateRight(schedule[index - 15], 7) ^
          _rotateRight(schedule[index - 15], 18) ^
          (schedule[index - 15] >>> 3);
      final s1 =
          _rotateRight(schedule[index - 2], 17) ^
          _rotateRight(schedule[index - 2], 19) ^
          (schedule[index - 2] >>> 10);
      schedule[index] =
          (schedule[index - 16] + s0 + schedule[index - 7] + s1) & 0xffffffff;
    }

    var a = hash[0];
    var b = hash[1];
    var c = hash[2];
    var d = hash[3];
    var e = hash[4];
    var f = hash[5];
    var g = hash[6];
    var h = hash[7];
    for (var index = 0; index < 64; index += 1) {
      final sigma1 =
          _rotateRight(e, 6) ^ _rotateRight(e, 11) ^ _rotateRight(e, 25);
      final choose = (e & f) ^ ((~e) & g);
      final temp1 =
          (h + sigma1 + choose + constants[index] + schedule[index]) &
          0xffffffff;
      final sigma0 =
          _rotateRight(a, 2) ^ _rotateRight(a, 13) ^ _rotateRight(a, 22);
      final majority = (a & b) ^ (a & c) ^ (b & c);
      final temp2 = (sigma0 + majority) & 0xffffffff;
      h = g;
      g = f;
      f = e;
      e = (d + temp1) & 0xffffffff;
      d = c;
      c = b;
      b = a;
      a = (temp1 + temp2) & 0xffffffff;
    }
    hash[0] = (hash[0] + a) & 0xffffffff;
    hash[1] = (hash[1] + b) & 0xffffffff;
    hash[2] = (hash[2] + c) & 0xffffffff;
    hash[3] = (hash[3] + d) & 0xffffffff;
    hash[4] = (hash[4] + e) & 0xffffffff;
    hash[5] = (hash[5] + f) & 0xffffffff;
    hash[6] = (hash[6] + g) & 0xffffffff;
    hash[7] = (hash[7] + h) & 0xffffffff;
  }
  return hash.map((value) => value.toRadixString(16).padLeft(8, '0')).join();
}

int _rotateRight(int value, int count) =>
    ((value >>> count) | (value << (32 - count))) & 0xffffffff;

final class PlanError implements Exception {
  const PlanError(this.message);

  final String message;
}
