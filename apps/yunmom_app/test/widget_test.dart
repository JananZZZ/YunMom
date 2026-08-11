import 'package:cloud_mom/main.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('Sprint 0 boot surface is honest about readiness', (
    tester,
  ) async {
    await tester.pumpWidget(const YunMomBootstrapApp());

    expect(find.text('云妈妈'), findsOneWidget);
    expect(find.text('Sprint 0 工程地基已启动'), findsOneWidget);
    expect(find.text('视觉 Token：bootstrap_provisional'), findsOneWidget);
    expect(find.text('发布状态：RELEASE NOT APPROVED'), findsOneWidget);
  });
}
