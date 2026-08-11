import 'package:test/test.dart';
import 'package:yunmom_contracts/yunmom_contracts.dart';

void main() {
  test('contract baseline stays explicit and release remains blocked', () {
    expect(
      YunMomContractBaseline.engineeringContractVersion,
      'YunMom_Engineering_Contracts_V1.0.0',
    );
    expect(YunMomContractBaseline.releaseStatus, 'RELEASE_NOT_APPROVED');
  });
}
