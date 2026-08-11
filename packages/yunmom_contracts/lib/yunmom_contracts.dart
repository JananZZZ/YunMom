/// Immutable metadata shared by every YunMom platform implementation.
abstract final class YunMomContractBaseline {
  /// Frozen engineering-contract version used by this source tree.
  static const String engineeringContractVersion =
      'YunMom_Engineering_Contracts_V1.0.0';

  /// Android leads implementation, while semantics remain cross-platform.
  static const String platformPolicy = 'android_first_dual_platform_contract';

  /// Product decisions are frozen; release evidence and signatures are not.
  static const String releaseStatus = 'RELEASE_NOT_APPROVED';
}
