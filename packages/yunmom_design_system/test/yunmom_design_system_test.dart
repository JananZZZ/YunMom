import 'package:flutter_test/flutter_test.dart';
import 'package:yunmom_design_system/yunmom_design_system.dart';

void main() {
  test('bootstrap tokens fail closed for production consumption', () {
    const readiness = YunMomTokenReadiness.bootstrapProvisional();

    expect(readiness.implementationReady, isFalse);
    expect(readiness.requireProductionConsumption, throwsStateError);
  });
}
