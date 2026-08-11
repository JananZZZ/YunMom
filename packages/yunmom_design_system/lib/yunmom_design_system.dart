/// The code-side gate for the governed semantic Token Bundle.
///
/// Sprint 0 deliberately starts in [bootstrapProvisional]. Production screens
/// must not consume brand values until G1/G3 Goldens, generation, regression,
/// and required approvals make the canonical Token Bundle implementation-ready.
final class YunMomTokenReadiness {
  const YunMomTokenReadiness._({
    required this.status,
    required this.implementationReady,
  });

  const YunMomTokenReadiness.bootstrapProvisional()
    : this._(status: 'bootstrap_provisional', implementationReady: false);

  final String status;
  final bool implementationReady;

  void requireProductionConsumption() {
    if (!implementationReady) {
      throw StateError(
        'YunMom Design Tokens are provisional and cannot be consumed as '
        'production constants.',
      );
    }
  }
}
