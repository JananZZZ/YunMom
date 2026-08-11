# 云妈妈 / YunMom

Android-first、iOS/Android 双端统一合同的 Local-first 孕期照料应用。

当前状态：`SPRINT_0_FOUNDATION` / `RELEASE_NOT_APPROVED`。

## Workspace

- `apps/yunmom_app` — Flutter App；Android 首实现，iOS 合同从第一天存在。
- `packages/yunmom_contracts` — 版本化共享合同与 Schema 边界。
- `packages/yunmom_domain` — 不依赖 Flutter UI 的领域与 Policy 边界。
- `packages/yunmom_design_system` — 语义 Design Token 的代码侧门禁与未来生成输出。
- `docs/YunMom_Engineering_Contracts_V1.0.0` — 冻结工程合同。
- `visual` — YunMom 视觉治理、Token、证据和 Golden 状态。

## Bootstrap

在新终端中运行：

```powershell
flutter doctor -v
flutter pub get
.\tool\run_ci.ps1
```

当前启动页只是开发诊断面，不是正式 HOME 或生产视觉。正式 UI 必须等
G1/G3 Goldens 与 G4 Token Bundle 通过相应治理后再进入生产实现。

## Safety and data

- 仅使用合成数据或不可逆去标识化 Fixture。
- `RAG/` 中的本地资料不进入 Git，也不自动成为临床来源或生产 RAG。
- 本地确定性 Rule Pack、Provider、加密、删除和 Archive 能力必须按照冻结合同逐步实现与验收。
