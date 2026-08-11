import 'dart:convert';
import 'dart:io';

const _scopePath = 'docs/engineering/scope/V1_SCOPE_ALLOWLIST.json';
const _scopeSchemaPath =
    'docs/engineering/scope/V1_SCOPE_ALLOWLIST.schema.json';
const _scopeViewPath = 'docs/engineering/scope/SCOPE_FOUR_LISTS.md';

const _registerIds = <String>{
  'R1_PRODUCT_AND_SKILLS',
  'R2_CLINICAL_DATA_AND_EGRESS',
  'R3_SURFACES_PORTABILITY_AND_PLATFORMS',
  'R4_EXCLUSIONS_AND_CHANGE_TRIGGERS',
};
const _scopeStatuses = <String>{
  'required_enabled',
  'required_present_disabled',
  'future_explicitly_excluded',
};
const _deliveryStates = <String>{
  'planned',
  'scaffolded_disabled',
  'implemented',
  'verified',
  'excluded',
};
const _kinds = <String>{
  'feature',
  'skill',
  'rule_pack',
  'provider_model',
  'field_type',
  'widget',
  'export_archive',
  'platform',
  'exclusion',
};
const _phases = <String>{'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'CROSS', 'FUTURE'};
const _roles = <String>{'PO', 'TECH', 'QA', 'MD', 'LEGAL', 'SEC', 'ETHICS'};
const _skills = <String>{
  'PregnancyCore',
  'GestationalAge',
  'PregnancyProfile',
  'PrenatalSchedule',
  'PrenatalReportParser',
  'HospitalVisit',
  'SymptomRecord',
  'SymptomTriage',
  'MedicationRecord',
  'MedicationSafety',
  'MedicationReminder',
  'NutritionRecord',
  'NutritionAnalysis',
  'WeightTracking',
  'BloodPressure',
  'GlucoseTracking',
  'ActivityRecord',
  'FetalMovement',
  'MoodDiary',
  'PregnancyJournal',
  'PregnancyKnowledge',
  'PregnancyRAG',
  'ShoppingList',
  'HospitalBag',
  'MaternityLeave',
  'WeatherAmbient',
  'MemoryTimeline',
  'PregnancySummary',
  'Export',
  'DadEntry',
};
const _fieldTypes = <String>{
  'number_unit',
  'text',
  'boolean',
  'tristate',
  'enum',
  'multienum',
  'tag',
  'date',
  'datetime',
  'duration',
  'range',
  'count',
  'composite_measurement',
  'symptom_event',
  'medication',
  'food_event',
  'activity_event',
  'location',
  'attachment',
  'timeseries',
  'derived',
  'custom',
};

void main(List<String> arguments) {
  try {
    final parsed = _parseArguments(arguments);
    final root = _projectRoot(parsed.root);
    final scope = _readObject(_managedFile(root, _scopePath));
    _readObject(_managedFile(root, _scopeSchemaPath));
    final errors = _validate(scope, root);
    if (errors.isNotEmpty) {
      throw ScopeError('Scope allowlist is invalid:\n- ${errors.join('\n- ')}');
    }
    switch (parsed.command) {
      case 'validate':
        stdout.writeln('YunMom V1 scope: VALID');
        return;
      case 'render':
        _managedFile(
          root,
          _scopeViewPath,
        ).writeAsStringSync(_render(scope), flush: true);
        stdout.writeln('YunMom V1 scope: RENDERED');
        return;
      case 'check':
        final view = _managedFile(root, _scopeViewPath);
        if (!view.existsSync() ||
            view.readAsStringSync().replaceAll('\r\n', '\n') !=
                _render(scope)) {
          throw ScopeError(
            'Generated scope view drifted. Run: dart run tool/scope_ops.dart render',
          );
        }
        stdout.writeln('YunMom V1 scope: CHECKED');
        return;
      case 'self-test':
        _selfTest(scope, root);
        stdout.writeln('YunMom V1 scope: SELF-TEST PASSED');
        return;
      default:
        throw ScopeError('Unknown command: ${parsed.command}');
    }
  } on ScopeError catch (error) {
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
  const _Arguments(this.command, this.root);
  final String command;
  final String? root;
}

_Arguments _parseArguments(List<String> arguments) {
  if (arguments.isEmpty ||
      arguments.contains('--help') ||
      arguments.contains('-h')) {
    stdout.writeln(
      'Usage: dart run tool/scope_ops.dart '
      '<validate|render|check|self-test> [--project-root <path>]',
    );
    exit(0);
  }
  final positional = <String>[];
  String? root;
  for (var index = 0; index < arguments.length; index += 1) {
    final argument = arguments[index];
    if (argument == '--project-root') {
      if (index + 1 >= arguments.length) {
        throw ScopeError('--project-root requires a path');
      }
      root = arguments[++index];
    } else if (argument.startsWith('-')) {
      throw ScopeError('Unknown option: $argument');
    } else {
      positional.add(argument);
    }
  }
  if (positional.length != 1) {
    throw ScopeError('Exactly one command is required');
  }
  return _Arguments(positional.single, root);
}

Directory _projectRoot(String? explicit) {
  if (explicit != null) {
    final root = Directory(explicit).absolute;
    if (_isRoot(root)) return root;
    throw ScopeError('Not a YunMom project root: ${root.path}');
  }
  var current = Directory.current.absolute;
  while (true) {
    if (_isRoot(current)) return current;
    if (current.parent.path == current.path) break;
    current = current.parent;
  }
  final scriptRoot = File.fromUri(Platform.script).parent.parent.absolute;
  if (_isRoot(scriptRoot)) return scriptRoot;
  throw ScopeError('Cannot locate YunMom project root');
}

bool _isRoot(Directory directory) =>
    File('${directory.path}${Platform.pathSeparator}AGENTS.md').existsSync() &&
    File(
      '${directory.path}${Platform.pathSeparator}docs${Platform.pathSeparator}planning'
      '${Platform.pathSeparator}ENGINEERING_PLAN.json',
    ).existsSync();

File _managedFile(Directory root, String relativePath) {
  if (relativePath.contains('..') ||
      relativePath.contains(':') ||
      relativePath.startsWith('/')) {
    throw ScopeError('Unsafe managed path: $relativePath');
  }
  final file = File(
    '${root.path}${Platform.pathSeparator}${relativePath.replaceAll('/', Platform.pathSeparator)}',
  ).absolute;
  final rootPrefix = '${root.path}${Platform.pathSeparator}'.toLowerCase();
  if (!file.path.toLowerCase().startsWith(rootPrefix)) {
    throw ScopeError('Managed path escaped project root: ${file.path}');
  }
  return file;
}

Map<String, dynamic> _readObject(File file) {
  if (!file.existsSync()) throw ScopeError('Missing file: ${file.path}');
  final decoded = jsonDecode(file.readAsStringSync());
  if (decoded is! Map<String, dynamic>) {
    throw ScopeError('Expected JSON object: ${file.path}');
  }
  return decoded;
}

List<String> _validate(Map<String, dynamic> scope, Directory root) {
  final errors = <String>[];
  if (scope['schema_version'] != 1) errors.add('SCHEMA_VERSION');
  if (scope['scope_id'] != 'yunmom-cn-public-store-v1') errors.add('SCOPE_ID');
  if (scope['jurisdiction'] != 'CN_MAINLAND') errors.add('JURISDICTION');
  if (scope['audience'] != 'ADULT_18_PLUS_PREGNANCY') errors.add('AUDIENCE');
  if (scope['platform_contract'] !=
      'ANDROID_FIRST_IOS_ANDROID_SEMANTIC_PARITY') {
    errors.add('PLATFORM_CONTRACT');
  }
  if (scope['release_status'] != 'RELEASE_NOT_APPROVED' &&
      scope['release_status'] != 'RELEASE_APPROVED') {
    errors.add('RELEASE_STATUS');
  }
  _zonedTime(scope['updated_at'], 'UPDATED_AT', errors);

  final ledger = _managedFile(
    root,
    'docs/YunMom_Engineering_Contracts_V1.0.0/00_DECISION_LEDGER.md',
  ).readAsStringSync();
  final contractIds = RegExp(
    r'^### ([A-Z0-9]+-[0-9]{3})：',
    multiLine: true,
  ).allMatches(ledger).map((match) => match.group(1)!).toSet();

  final registers = _objects(scope['registers'], 'REGISTERS', errors);
  final seenRegisters = <String>{};
  final seenItems = <String>{};
  final items = <Map<String, dynamic>>[];
  for (final register in registers) {
    final id = register['id'];
    if (id is! String || !_registerIds.contains(id)) {
      errors.add('REGISTER_ID:$id');
    } else if (!seenRegisters.add(id)) {
      errors.add('REGISTER_DUPLICATE:$id');
    }
    final owners = _strings(
      register['default_owner_roles'],
      'REGISTER_OWNERS:$id',
      errors,
    );
    if (owners.isEmpty || owners.any((role) => !_roles.contains(role))) {
      errors.add('REGISTER_OWNER_ROLE:$id');
    }
    for (final item in _objects(
      register['items'],
      'REGISTER_ITEMS:$id',
      errors,
    )) {
      items.add(item);
      final itemId = item['id'];
      if (itemId is! String || !RegExp(r'^[A-Z][A-Z0-9-]+$').hasMatch(itemId)) {
        errors.add('ITEM_ID:$itemId');
      } else if (!seenItems.add(itemId)) {
        errors.add('ITEM_DUPLICATE:$itemId');
      }
      final kind = item['kind'];
      final phase = item['phase'];
      final scopeStatus = item['scope_status'];
      final delivery = item['delivery_state'];
      if (!_kinds.contains(kind)) errors.add('ITEM_KIND:$itemId:$kind');
      if (!_phases.contains(phase)) errors.add('ITEM_PHASE:$itemId:$phase');
      if (!_scopeStatuses.contains(scopeStatus)) {
        errors.add('ITEM_SCOPE_STATUS:$itemId:$scopeStatus');
      }
      if (!_deliveryStates.contains(delivery)) {
        errors.add('ITEM_DELIVERY_STATE:$itemId:$delivery');
      }
      if (item['name'] is! String || (item['name'] as String).trim().isEmpty) {
        errors.add('ITEM_NAME:$itemId');
      }
      final refs = _strings(
        item['contract_refs'],
        'ITEM_CONTRACTS:$itemId',
        errors,
      );
      if (refs.isEmpty) errors.add('ITEM_CONTRACTS_EMPTY:$itemId');
      for (final ref in refs) {
        if (!contractIds.contains(ref))
          errors.add('CONTRACT_UNKNOWN:$itemId:$ref');
      }
      final gates = item.containsKey('gates')
          ? _strings(item['gates'], 'ITEM_GATES:$itemId', errors)
          : const <String>[];
      if (scopeStatus == 'required_present_disabled' && gates.isEmpty) {
        errors.add('DISABLED_WITHOUT_GATE:$itemId');
      }
      if (kind == 'exclusion') {
        if (scopeStatus != 'future_explicitly_excluded' ||
            delivery != 'excluded' ||
            phase != 'FUTURE' ||
            !refs.contains('CHG-001')) {
          errors.add('EXCLUSION_CONTRACT:$itemId');
        }
      } else if (scopeStatus == 'future_explicitly_excluded' ||
          delivery == 'excluded') {
        errors.add('NON_EXCLUSION_MARKED_EXCLUDED:$itemId');
      }
    }
  }
  if (seenRegisters.length != _registerIds.length ||
      !seenRegisters.containsAll(_registerIds)) {
    errors.add('REGISTER_SET');
  }
  for (final phase in const ['P1', 'P2', 'P3', 'P4', 'P5', 'P6']) {
    if (!items.any(
      (item) => item['kind'] == 'feature' && item['phase'] == phase,
    )) {
      errors.add('PHASE_FEATURE_MISSING:$phase');
    }
  }
  _exactNamedSet(items, 'skill', _skills, 'SKILL_SET', errors);
  _exactNamedSet(items, 'field_type', _fieldTypes, 'FIELD_TYPE_SET', errors);
  if (items.where((item) => item['kind'] == 'provider_model').length < 3) {
    errors.add('PROVIDER_PATHS_INCOMPLETE');
  }
  if (items.where((item) => item['kind'] == 'rule_pack').length < 5) {
    errors.add('RULE_PACKS_INCOMPLETE');
  }
  if (items.where((item) => item['kind'] == 'widget').length != 2) {
    errors.add('WIDGET_SURFACES_INCOMPLETE');
  }
  final platformNames = items
      .where((item) => item['kind'] == 'platform')
      .map((item) => item['name'])
      .whereType<String>()
      .toSet();
  if (!platformNames.containsAll({'Android App', 'iOS App'})) {
    errors.add('DUAL_PLATFORM_APP_CONTRACT_MISSING');
  }

  final binding = scope['release_binding'];
  if (binding is! Map<String, dynamic>) {
    errors.add('RELEASE_BINDING');
  } else {
    final signatures = _strings(
      binding['required_signatures'],
      'RELEASE_SIGNATURES',
      errors,
    ).toSet();
    if (!signatures.containsAll(_roles)) errors.add('RELEASE_SIGNATURE_SET');
    if (scope['release_status'] == 'RELEASE_APPROVED') {
      if (items.any(
        (item) =>
            item['scope_status'] == 'required_present_disabled' ||
            (item['scope_status'] == 'required_enabled' &&
                item['delivery_state'] != 'verified'),
      )) {
        errors.add('RELEASE_WITH_INCOMPLETE_REQUIRED_ITEM');
      }
      for (final key in const [
        'source_tag',
        'build_hash',
        'feature_flag_manifest',
      ]) {
        if (binding[key] is! String || (binding[key] as String).isEmpty) {
          errors.add('RELEASE_BINDING_MISSING:$key');
        }
      }
    }
  }
  return errors;
}

void _exactNamedSet(
  List<Map<String, dynamic>> items,
  String kind,
  Set<String> expected,
  String marker,
  List<String> errors,
) {
  final actual = items
      .where((item) => item['kind'] == kind)
      .map((item) => item['name'])
      .whereType<String>()
      .toSet();
  if (actual.length != expected.length || !actual.containsAll(expected)) {
    final missing = expected.difference(actual).toList()..sort();
    final extra = actual.difference(expected).toList()..sort();
    errors.add('$marker:missing=${missing.join(',')}:extra=${extra.join(',')}');
  }
}

List<Map<String, dynamic>> _objects(
  Object? value,
  String label,
  List<String> errors,
) {
  if (value is! List) {
    errors.add('$label:expected_array');
    return const [];
  }
  final result = <Map<String, dynamic>>[];
  for (var index = 0; index < value.length; index += 1) {
    if (value[index] is Map<String, dynamic>) {
      result.add(value[index] as Map<String, dynamic>);
    } else {
      errors.add('$label[$index]:expected_object');
    }
  }
  return result;
}

List<String> _strings(Object? value, String label, List<String> errors) {
  if (value is! List) {
    errors.add('$label:expected_array');
    return const [];
  }
  final result = <String>[];
  for (var index = 0; index < value.length; index += 1) {
    final item = value[index];
    if (item is String && item.isNotEmpty) {
      result.add(item);
    } else {
      errors.add('$label[$index]:expected_non_empty_string');
    }
  }
  if (result.toSet().length != result.length) errors.add('$label:duplicates');
  return result;
}

void _zonedTime(Object? value, String label, List<String> errors) {
  if (value is! String ||
      !RegExp(r'(Z|[+-][0-9]{2}:[0-9]{2})$').hasMatch(value)) {
    errors.add('$label:timezone_required');
    return;
  }
  try {
    DateTime.parse(value);
  } on FormatException {
    errors.add('$label:invalid');
  }
}

String _render(Map<String, dynamic> scope) {
  final registers = (scope['registers'] as List).cast<Map<String, dynamic>>();
  final allItems = registers
      .expand(
        (register) => (register['items'] as List).cast<Map<String, dynamic>>(),
      )
      .toList();
  final buffer = StringBuffer()
    ..writeln('<!-- GENERATED by tool/scope_ops.dart. DO NOT EDIT. -->')
    ..writeln('# YunMom V1 signed-scope working view')
    ..writeln()
    ..writeln('- Scope: `${scope['scope_id']}` / `${scope['scope_version']}`')
    ..writeln('- Jurisdiction: `${scope['jurisdiction']}`')
    ..writeln('- Audience: `${scope['audience']}`')
    ..writeln('- Platform contract: `${scope['platform_contract']}`')
    ..writeln('- Release: `${scope['release_status']}`')
    ..writeln();
  for (final register in registers) {
    buffer
      ..writeln('## ${register['id']} · ${register['title']}')
      ..writeln()
      ..writeln(
        '| ID | Kind | Phase | Item | Scope status | Delivery | Gates | Contracts |',
      )
      ..writeln('|---|---|---|---|---|---|---|---|');
    for (final item
        in (register['items'] as List).cast<Map<String, dynamic>>()) {
      buffer.writeln(
        '| `${item['id']}` | `${item['kind']}` | `${item['phase']}` | ${_cell(item['name'])} | '
        '`${item['scope_status']}` | `${item['delivery_state']}` | ${_listCell(item['gates'])} | '
        '${_listCell(item['contract_refs'])} |',
      );
    }
    buffer.writeln();
  }
  final counts = <String, int>{for (final status in _scopeStatuses) status: 0};
  for (final item in allItems) {
    counts[item['scope_status'] as String] =
        (counts[item['scope_status']] ?? 0) + 1;
  }
  final blockers = allItems
      .where(
        (item) =>
            item['scope_status'] == 'required_present_disabled' ||
            (item['scope_status'] == 'required_enabled' &&
                item['delivery_state'] != 'verified'),
      )
      .length;
  buffer
    ..writeln('## Scope summary')
    ..writeln()
    ..writeln('- Total entries: `${allItems.length}`')
    ..writeln('- Required enabled target: `${counts['required_enabled']}`')
    ..writeln(
      '- Required present-disabled: `${counts['required_present_disabled']}`',
    )
    ..writeln(
      '- Future explicitly excluded: `${counts['future_explicitly_excluded']}`',
    )
    ..writeln('- Current release-blocking entries: `$blockers`')
    ..writeln(
      '- Frozen Skill entries: `${allItems.where((item) => item['kind'] == 'skill').length}`',
    )
    ..writeln(
      '- Formal Field Type entries: `${allItems.where((item) => item['kind'] == 'field_type').length}`',
    )
    ..writeln()
    ..writeln(
      '`required_present_disabled` is not delivered unless the same-build signed release package proves '
      'it is solely the approved safety Kill Switch state. This working allowlist is not a release signature.',
    );
  return buffer.toString();
}

String _cell(Object? value) =>
    value.toString().replaceAll('|', r'\|').replaceAll('\n', '<br>');

String _listCell(Object? value) {
  if (value is! List || value.isEmpty) return '—';
  return value.map(_cell).join('<br>');
}

void _selfTest(Map<String, dynamic> canonical, Directory root) {
  Map<String, dynamic> clone() =>
      jsonDecode(jsonEncode(canonical)) as Map<String, dynamic>;
  void expect(String name, Map<String, dynamic> candidate, String marker) {
    final errors = _validate(candidate, root);
    if (!errors.any((error) => error.contains(marker))) {
      throw ScopeError(
        'SELF_TEST_$name expected $marker, got ${errors.join(' | ')}',
      );
    }
  }

  List items(Map<String, dynamic> value, int register) =>
      ((value['registers'] as List)[register] as Map<String, dynamic>)['items']
          as List;

  final duplicate = clone();
  items(duplicate, 0).add(jsonDecode(jsonEncode(items(duplicate, 0).first)));
  expect('DUPLICATE', duplicate, 'ITEM_DUPLICATE');

  final unknownContract = clone();
  (items(unknownContract, 0).first['contract_refs'] as List).add('NOPE-999');
  expect('UNKNOWN_CONTRACT', unknownContract, 'CONTRACT_UNKNOWN');

  final missingSkill = clone();
  items(missingSkill, 0).removeWhere((item) => item['kind'] == 'skill');
  expect('SKILLS', missingSkill, 'SKILL_SET');

  final badExclusion = clone();
  items(badExclusion, 3).first['scope_status'] = 'required_enabled';
  expect('EXCLUSION', badExclusion, 'EXCLUSION_CONTRACT');

  final noGate = clone();
  items(noGate, 0).firstWhere(
    (item) => item['scope_status'] == 'required_present_disabled',
  )['gates'] = <String>[];
  expect('DISABLED_GATE', noGate, 'DISABLED_WITHOUT_GATE');

  final falseRelease = clone();
  falseRelease['release_status'] = 'RELEASE_APPROVED';
  expect(
    'FALSE_RELEASE',
    falseRelease,
    'RELEASE_WITH_INCOMPLETE_REQUIRED_ITEM',
  );

  final rendered = _render(canonical);
  if (!rendered.contains('R1_PRODUCT_AND_SKILLS') ||
      !rendered.contains('Frozen Skill entries: `30`') ||
      !rendered.contains('Formal Field Type entries: `22`')) {
    throw ScopeError('SELF_TEST_RENDER incomplete');
  }
}

final class ScopeError implements Exception {
  const ScopeError(this.message);
  final String message;
}
