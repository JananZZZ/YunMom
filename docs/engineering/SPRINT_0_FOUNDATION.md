# Sprint 0 — 工程地基

状态：`FOUNDATION_READY_FOR_FIRST_VERTICAL_SLICE`  
发布状态：`RELEASE_NOT_APPROVED`

## 本轮目标

建立可复现、可测试、Android 首行但不制造 Android 私有业务合同的工程基础。
本轮不实现临床规则、不启用 Provider、不处理真实健康数据、不宣称正式 UI 完成。

## 已建立

- Git `main` 仓库，项目内固定 LF、`fast-forward-only`、长路径支持与安全忽略规则。
- 用户级 Flutter、Dart、Android SDK/ADB、JDK 环境变量和 PATH。
- Android/iOS 同时存在的 Flutter App。
- `contracts`、`domain`、`design_system` 三个共享包与原生 Pub Workspace。
- provisional Token 的 fail-closed 代码门禁。
- 合成数据、私有 RAG、本地 Secret 和生成物的 Git 边界。
- 可复现工具链清单与本地 CI 入口。
- 严格格式化、分析、四组测试与 Android Debug APK 实际构建均已通过；详见
  `docs/engineering/SPRINT_0_VERIFICATION.md`。
- 项目级磁盘护栏已建立：依赖、Gradle、Android 用户数据、AVD 与临时文件默认收口到
  `.local/`，项目脚本监测 C 盘前后变化；详见 `docs/engineering/STORAGE_GUARDRAIL.md`。

## 身份与迁移说明

Android 暂沿用旧原型的 `cn.cloudmom.cloud_mom`，避免在尚未完成数据迁移设计前
主动切断安装/数据连续性。iOS 使用 Flutter 对应 Bundle Identifier。公开商店登记、
签名与最终 ID 必须在产生不可逆商店资产前由 PO/TECH/LEGAL 冻结；若改变，必须
明确旧原型迁移与并存策略。

## 手机连接节奏

手机无需长期连接。默认使用单元/Widget/集成测试与 `YunMom_Android_36` 模拟器。

只在以下里程碑短时连接现有 Android 手机：

1. **基础存储里程碑**：Keystore、安装哨兵、系统备份排除、升级/卸载/重装。
2. **关键体验里程碑**：TalkBack、平台最大字号、Reduce Motion、通知、Widget、弱网/飞行模式。
3. **内测候选里程碑**：Release 构建、性能、Archive 往返、永久删除残留检查。

每次连接应形成具名设备/OS/Build 记录；首轮证据不能冒充最终双端矩阵。

## 下一工程切片

首个纵向切片按冻结合同实现：

`CreateEpisode Command → Event 集 → Projection → Receipt → correct/revert → Purge dry-run`

仅使用合成 Fixture。Rule Pack 在 MD 来源与 Golden 未齐前只建立签名、版本、
适用范围和 fail-safe 框架，不写入未经批准的临床阈值。

## 尚未解除的阻塞

- Android Emulator Hypervisor Driver 需要一次管理员权限安装：
  `C:\dev\android-sdk\extras\google\Android_Emulator_Hypervisor_Driver\silent_install_safe.bat`。
- Android Studio 已由 Flutter Doctor 识别；首次图形界面启动仅需确认界面偏好，不阻塞构建。
- G1 YunMom Master、G3 HOME 与 G4 implementation-ready Tokens 尚未完成。
- 医疗、法律、隐私、安全、伦理、iOS 真机与公开发布证据仍全部保持 No-Go。
