import 'package:test/test.dart';
import 'package:yunmom_domain/yunmom_domain.dart';

void main() {
  test('accepts the frozen contract version', () {
    expect(
      () => YunMomDomainBoundary.requireContractVersion(
        YunMomDomainBoundary.engineeringContractVersion,
      ),
      returnsNormally,
    );
  });

  test('rejects a mismatched contract version', () {
    expect(
      () => YunMomDomainBoundary.requireContractVersion('unknown'),
      throwsStateError,
    );
  });
}
