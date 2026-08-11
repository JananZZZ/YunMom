import 'package:yunmom_contracts/yunmom_contracts.dart';

/// Fail-fast guard against loading code built for a different frozen contract.
abstract final class YunMomDomainBoundary {
  static String get engineeringContractVersion =>
      YunMomContractBaseline.engineeringContractVersion;

  static void requireContractVersion(String version) {
    if (version != engineeringContractVersion) {
      throw StateError(
        'Contract mismatch: expected $engineeringContractVersion, got $version',
      );
    }
  }
}
