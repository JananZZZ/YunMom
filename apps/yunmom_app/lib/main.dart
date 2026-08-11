import 'package:flutter/material.dart';
import 'package:yunmom_contracts/yunmom_contracts.dart';
import 'package:yunmom_design_system/yunmom_design_system.dart';
import 'package:yunmom_domain/yunmom_domain.dart';

void main() {
  YunMomDomainBoundary.requireContractVersion(
    YunMomContractBaseline.engineeringContractVersion,
  );
  runApp(const YunMomBootstrapApp());
}

/// Development-only boot surface used until the governed G3/G4 UI is ready.
class YunMomBootstrapApp extends StatelessWidget {
  const YunMomBootstrapApp({super.key});

  static const YunMomTokenReadiness _tokenReadiness =
      YunMomTokenReadiness.bootstrapProvisional();

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '云妈妈',
      debugShowCheckedModeBanner: true,
      theme: ThemeData(useMaterial3: true),
      home: Scaffold(
        body: SafeArea(
          child: Center(
            child: Semantics(
              container: true,
              label: '云妈妈开发环境状态',
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: <Widget>[
                  const Text('云妈妈'),
                  const Text('Sprint 0 工程地基已启动'),
                  Text('视觉 Token：${_tokenReadiness.status}'),
                  const Text('发布状态：RELEASE NOT APPROVED'),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
