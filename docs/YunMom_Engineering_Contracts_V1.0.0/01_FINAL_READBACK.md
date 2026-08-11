# 云妈妈工程合同冻结访谈最终 Readback

> 决策状态：`PRODUCT_DECISIONS_FROZEN`  
> 发布状态：`RELEASE_NOT_APPROVED` / `NO-GO — PENDING EVIDENCE AND SIGNATURES`  
> 冻结日期：2026-08-11  
> 首发目标：中国大陆、18 岁及以上成年孕期用户、公开商店 V1  
> 决策总数：10 轮、91 项  
> 权威明细：[工程合同决策台账](./00_DECISION_LEDGER.md)  
> 产品输入：[YunMom Product Baseline V1.0.0](../YunMom_Product_Baseline_V1.0.0/)

## 1. 最终结论

“云妈妈工程合同冻结访谈”已完成 10/10 轮。R1–R10 最终交叉审计结论为：

- 产品决策之间在经确认修正 MAT-001 后不存在未解决的重大架构、范围、医疗、隐私或发布治理冲突。
- 产品决策现已冻结；任何超出本 Readback 和决策台账的能力都不因出现在原型、基线描述、演示或口头沟通中而自动进入 V1。
- 当前只有一台电脑和一台 Android 手机，不阻止现在开始架构、Android 首实现、自动化测试和首轮真机验证；它也不构成公开发布测试豁免。
- 多机与 iOS 真机验证可延至内测阶段，但必须在公开商店 V1 的最终 Go/No-Go 前完成。未完成时只能继续开发或受控内测，不能标记 Production Ready，不能公开发布。
- MD、LEGAL、SEC、TECH、QA、ETHICS、PO 必须对同一个 Release Candidate 及同一份版本清单共同签字。任一专业域 No-Go 即整体 No-Go。
- 截至本 Readback 生成时，正式实现、外部意见、独立渗透、双端真机证据、生产演练和七方签字尚未齐全，因此当前发布结论明确为 `NO-GO`。

## 2. 唯一已发现并已解决的冲突

Round 10 原始第 2 项提出“只用 Android 模拟器和一台开发机验收，iOS 真机在公开发布后补测”。这与以下已冻结合同冲突：

- BND-001 的公开商店生产门槛；
- BND-003 的双端统一合同；
- ACCD-001 的 Android/iOS Projection 与 Archive 等价性；
- ACCS-001 的双端永久删除真机取证；
- ACCU-001 的双端无障碍与 Widget 验收；
- ACCP-001 的双端性能和稳定性门槛；
- SIGN-001 的同一构建、完整证据共同签字。

用户已确认将其修正并冻结为 MAT-001：

> 现在使用现有电脑和 Android 手机推进；多机及 iOS 真机测试可以延至内测阶段，但必须在公开商店 Go/No-Go 前完成。Android 首实现不代表 iOS 验收被取消，当前资源不足不构成公开发布豁免。

修正后，Round 10 结论为 `NO_CONFLICT_AFTER_CONFIRMED_AMENDMENT`。

## 3. R1–R10 决策索引

完整规范性措辞以[决策台账](./00_DECISION_LEDGER.md)中的对应 ID 为准。本节是最终共同签字用的 Readback 索引，不替代原条款。

| 轮次 | 决策 ID | 冻结结果 |
|---|---|---|
| R1 边界 | BND-001–004 | 以中国大陆公开商店生产版为下一里程碑；双端统一合同、Android 首实现/首测；V1 一次覆盖 Phase 1–6 全闭环，不能静默缩减。 |
| R2 Episode/家庭 | EPI-001–004、USR-001、FAM-001–003 | 无限历史 Episode、默认单 Active；Episode 下 1..N BabySubject；有限生命周期；结局仅经用户/医疗记录确认；V1 仅成年人；DadEntry 同设备+主动摘要；家庭按类别最小授权并可即时撤销。 |
| R3 Medical Safety | MED-001–009 | 消费级孕期照料与临床规则 Safety Signposting；不诊断、不治疗、不处方、不改药；本地确定性 Rule Pack 为最终权威；R0–R3 固定动作；逐类验证输入；超范围保守转介；危机独立协议；版本化规则与 Clinical Golden。 |
| R4 数据/同意/AI | DATA-001、IDN-001、CONSENT-001、EGRESS-001、CTX-001、FILE-001、PROV-001/002、BYOK-001、TEL-001 | 五级数据分级；匿名 Local-first；账号仅商业权益且不可联表健康档案；按目的/Provider/数据类型 JIT 同意；最小 Context Capsule；文件逐次确认；中国大陆 Provider 白名单；无自动 Fallback；BYOK 设备直连；无内容遥测与禁止健康内容训练。 |
| R5 Event/Command | EVT-001–004、CMD-001、RCT-001、FLD-001/002、CFL-001、SCH-001 | Pregnancy Event Store 是唯一事实源；Projection 可重建；Event 正常生命周期不可变；Typed Command 原子写入；所有持久化动作有 Receipt；22 类字段；单位与 Provenance；Conflict Set 显式解决；版本化 Schema 与纯函数 Upcaster。 |
| R6 加密/删除/Archive | KEY-001/002、CRYPTO-001、DEL-001–003、BAK-001、ARC-001–003 | 安装 KEK、Episode Key、Attachment DEK 分层；成熟加密实现；Undo/隐藏/永久删除分离；crypto-shred+全路径 Purge+残留扫描；健康相关数据全面排除系统自动备份；Archive 强制加密、零密钥托管、离线预检、原子导入、支持当前及前两个主要版本。 |
| R7 Queue/Gateway/计量 | QUE-001–004、CONSENT-002、GWY-001、RETRY-001、RES-001、MTR-001、IDEMP-001 | 仅用户发起且非时效任务进入本地加密队列；Safety/危机永不排；文件不自动发送；Consent 实质变化即失效；Gateway 无状态且无正文；同 Provider 最多 2 次瞬时重试；Partial Stream 不写入；额度一次结算；Operation→Attempt→Command/Receipt 端到端幂等。 |
| R8 无障碍/Widget/Token | A11Y-001–003、WGT-001–004、TOK-001–003 | 双端 WCAG 2.2 AA 等效移动基线；P0 读屏、最大字号、非手势操作；Safety 不只靠颜色/动效；Widget 默认关闭、逐字段授权、只读、非 Safety 渠道、加密最小快照、最长 24 小时；语义 Token 仓库唯一事实源，Safety 优先级不可被装饰覆盖。 |
| R9 生产/事故 | TOP-001、SAFEOPS-001、SLO-001、LOG-001、OBS-001、IAM-001、SUP-001、REL-001、INC-001、OPS-001 | 中国大陆单主区域、至少双 AZ Active-Active；本地核心/Safety 不依赖云；量化 SLO/RTO/RPO；全链路无正文白名单；环境和生产访问隔离；签名供应链与 SBOM；Canary、回滚、分层 Kill Switch/LKG；医疗与隐私安全双事故通道；7×24 P0 响应和演练。 |
| R10 验收/签字 | SCP-001、MAT-001、EXIT-001、ACCD-001、ACCM-001、ACCS-001、ACCU-001、ACCP-001、CHG-001、SIGN-001 | 签名 Scope/Allowlist；现有设备先开发、公开发布前补齐双端真机；严格缺陷出口；数据/Archive、Medical/AI、隐私安全删除、无障碍视觉、性能稳定性量化验收；书面变更与限时豁免；七方对同一构建共同 Go/No-Go。 |

决策数量核对：R1 4 项、R2 8 项、R3 9 项、R4–R10 各 10 项，共 91 项。

## 4. 最终工程合同 Readback

### 4.1 产品范围与平台

- 当前目标不是概念验证或仅供演示的 MVP，而是以中国大陆生产、公开应用市场、完整合规门槛为目标的 V1。
- V1 首发人群限定为 18 岁及以上成年孕期用户；未成年人、新法域和其他人群不在当前批准范围。
- Phase 1–6 是 Required 全闭环。发布前必须形成逐项签名 Scope/Allowlist，至少覆盖功能、Skill、Rule Pack、Provider/Model、Field、Widget、Export/Archive 和平台状态。
- Allowlist 只有 `required_enabled`、`required_present_disabled`、`future_explicitly_excluded` 三类。Required 项未实现、未验收或未签字即阻断 V1；安全 Kill Switch 之外，`required_present_disabled` 不得冒充已交付。
- Android 是首个实现和当前测试基准；领域、Schema、Archive、Token、Safety、隐私和验收合同从第一天即为 iOS/Android 统一合同，平台差异只能进入 Adapter 或原生组件层。

### 4.2 Episode、Subject、结局与家庭

- 用户可以保留无限历史 Pregnancy Episode，但任一时刻默认只有一个 Active Episode。
- 每个 Episode 下有 1..N 个 BabySubject；母体数据属于 Episode，胎儿专属数据属于对应 Subject。多胎的数据表达能力不等于所有规则已对多胎获临床验证。
- 生命周期固定为 `active`、`delivery_completed`、`closure_confirmation_pending`、`quiet_archive`、`archived`；永久删除是独立管理命令，不是生命周期状态。
- 特殊结局使用经临床审核的有限 Outcome 枚举加 `other/unknown`。只有用户明确陈述或确认医疗记录后才能转换，AI/OCR 不得自动触发。
- DadEntry V1 采用同设备受控入口与用户主动生成的分享摘要，不建设健康数据实时跨设备同步。
- 家庭成员只有逐类最小权限；可创建自己的任务/备注建议，但不得修改母体健康记录、EDD、药物、风险或医生指令。Risk、Gentle Closure、日记、心情、报告、症状、药物和 AI 对话默认不共享。

### 4.3 Medical Safety 与 AI 边界

- 云妈妈是消费级孕期照料产品，提供经临床规则驱动的 Safety Signposting；不诊断、不治疗、不处方、不自动开始/停止/更换药物或改变剂量。
- 本地、签名、版本化的确定性 Rule Pack 是 Safety 最终权威。AI 只能提取输入和生成受控语言，不能独立降低、解除或覆盖风险。
- 风险枚举为 R0 无活动风险、R1 常规咨询、R2 尽快联系医疗人员、R3 立即行动；每级绑定由 MD 批准的时间窗和用户主动触发的行动。
- 症状、生命体征、胎动/宫缩、报告/OCR、药物信息只有逐类完成临床规则验证后才启用。超出适用孕周、人群、单胎/多胎或排除条件时可记录，但只作保守转介，不显示“未发现风险”。
- 报告页面必须区分报告事实、AI 解释和医生判断；低置信关键字段必须确认。MoodCare 不得覆盖 Safety；心理危机进入独立协议和大陆可用真人/紧急资源。
- Safety、药物紧急判断、心理危机永不进入 Pending AI Queue；Provider/Gateway/登录/权益/网络故障也不得阻止本地 Safety。

### 4.4 隐私、同意、Provider 与数据出站

- 数据分为公开产品数据、身份/商业数据、设备与低敏运营数据、健康/亲密内容、密钥与安全凭证五级；每个字段映射存储、日志、备份、导出、删除和出站规则。
- 健康数据匿名 Local-first；可选账号只承载购买、权益和 AI 额度。身份/商业后端与本地健康库隔离，后台不得形成可联表 Episode 健康档案。
- 官方 AI 可能在用户明确授权时经 Gateway/Provider 瞬时处理最小健康上下文；因此“No Health Data Backend”不得宣传成“任何健康数据永不离机”。后台不得持久保存健康正文。
- 同意绑定目的、数据类别、Provider 法律实体/模型、地域、保留/训练条款和政策版本。撤回立即停止未来出站、取消 Pending/Retry 并擦除 Capsule；已经送达 Provider 的部分不得虚构为可由本机召回。
- 每个 Skill 使用冻结的字段白名单和 Minimal Context Capsule；禁止发送完整 Episode 或无关历史。报告、照片、音频、日记、危机等高敏内容每次发送前都明确确认。
- V1 Provider 必须进入中国大陆版本化白名单；不自动切换 Provider。BYOK Key 只进入 Keychain/Keystore并由设备直连 Provider，不经过官方 Gateway；任意 OpenAI-compatible 自定义端点后置。
- 遥测只允许第一方、版本化、无内容字段；禁止 Prompt、Response、报告、图片、OCR、健康字段、Session Replay 和可推断健康行为的事件名，健康内容永不用于产品训练。

### 4.5 唯一事实源、写入和 Schema

- Pregnancy Event Store 是唯一事实源。实体表、Snapshot、Timeline、RAG/Vector、WidgetState 等都是可重建 Projection。
- 领域对象有稳定 `aggregate_id`；Attachment 原件单独加密，并由 Event 引用。正常业务历史不可变，纠错/替代/撤销通过新 Event 表达。
- Typed Command 携带 `command_id`、`idempotency_key`、`expected_revision`、Actor/Source 和 Policy Version；一个 Command 可原子产生一组 Event，校验失败时零写入。
- 所有持久化动作都有 Receipt；A/B 可直接执行，B 突出撤销，C 必须确认，D 永不执行。Partial Stream、取消后的迟到响应和未通过 Schema/Policy/Consent/Revision 复核的结果不能形成 Command。
- 22 类 Universal Field 是正式枚举；健康值同时保存规范单位和原始值/单位/精度/片段，并强制携带 Provenance。
- 冲突进入 `conflict_set`，Reducer 不以最新或最高置信度暗选；用户确认后写 Resolution Event，原证据保留到明确永久删除。
- Event/Payload/Command/Field/Receipt/Archive 使用版本化 Schema Registry；旧 Event 不原地改写，使用纯函数 Upcaster 和版本化 Projection 重建。

### 4.6 加密、备份、永久删除与 Archive

- 设备绑定安装 KEK 只负责包裹；每个 Episode 有独立内容密钥，每个 Attachment 有独立 DEK。Secure Storage 必须不可同步、优先硬件保护，重装/恢复哨兵异常时 fail-closed。
- 使用经审核的 SQLite 加密和流式 AEAD 文件加密，不自研算法；格式、算法、Key Slot 分别版本化，轮换可恢复、可中断续跑和失败回滚。
- Undo、从视图隐藏、永久删除是三种不同语义。永久删除位于 Event Store 正常历史之外，先 crypto-shred，再由可恢复 Purge Job 清理所有存储位置并重建 Projection。
- 删除合同覆盖 DB/WAL/SHM、Event、Receipt、Attachment、Thumbnail、Cache、OCR/Temp、Index/Vector、RAG、Pending Queue、通知、Widget/App Group 和 Key。审计结果不得包含健康正文。
- “物理删除”指应用层全路径清除、密钥失效、残留扫描和取证验证，不承诺移动闪存逐比特覆盖。
- 健康 DB、密钥、附件、Queue、Widget、索引和临时数据全部排除系统自动备份。跨设备迁移只使用用户主动创建的加密 Archive。
- Archive 以 Canonical Event Log/Payload、必要 Provenance、Attachment、Field Registry 快照和校验信息为恢复依据；Snapshot/Index/Cache/Token/BYOK Key/设备标识不进入。Archive 解密密钥由用户口令和可选离线恢复码掌握，云妈妈零托管。
- 导入先离线认证和兼容预检，再原子导入/回滚；不静默合并或覆盖，支持当前及前两个主要 Archive 版本，旧 Consent/Egress 不继承。

### 4.7 Pending Queue、Gateway、计量和幂等

- 队列只位于设备本地、加密、用户可见且可取消。每个安装最多 20 个活动项，其中最多 3 个文件项；非文件默认 7 天，文件默认 72 小时；容量/期限只能经签名配置收紧。
- 发送时重建 Minimal Context Capsule。来源、Consent、Provider 或文件内容有实质变化时显示差异并重新确认；队列不保存 BYOK Key 或云端正文副本。
- 只有 offline/timeout/rate_limited/provider_unavailable 等瞬时错误可对原 Provider 自动重试，最多 2 次；文件、鉴权、余额、Schema、Policy、`outcome_unknown` 不后台重试，不跨 Provider。
- 官方 Gateway 只作有界内存无状态流式转发，禁止正文磁盘缓冲、持久队列、缓存、Core Dump 和正文 Trace；Proxy/WAF/APM 也不记录原始 Provider error body。
- 同一用户意图有稳定 `operation_id`，每次尝试有 `attempt_id`；Provider 重试复用幂等键，结果提交使用确定性 `command_id`。响应丢失时查询/返回原 Event 与 Receipt，不重复执行。
- 官方额度在派发前预占，只有完整响应通过 Schema/Policy 并成功交付后结算一次；失败、取消、Partial、重复回调释放或不重复扣费。BYOK 不进入官方计量。

### 4.8 无障碍、Widget 和 Design Token

- iOS/Android 使用统一 WCAG 2.2 AA 等效移动端合同并遵守原生规范；100% P0 流程支持 VoiceOver/TalkBack、平台最大字号且至少 200%、非手势替代和平台最小触控目标。
- Safety/危机同时使用明确文字、非装饰图标、对比、正确 role/label/state 和可操作下一步；颜色、声音、触觉和动画只能辅助。Reduce Motion 不得移除风险、错误、确认或状态语义。
- Widget V1 默认关闭且逐字段授权；孕周/预产期也按敏感信息处理。Risk、“当前安全/无风险”、报告、药物、心情、日记、AI 对话和 Gentle Closure 详情均禁止进入 Widget。
- Widget 只读取主 App 生成的最小 `WidgetProjection`，不能写库、关闭风险或从 Gateway 获取健康状态；交互只能深链到已解锁主 App。
- 共享容器应用层加密、平台保护、专用密钥、备份/搜索/遥测/日志排除；快照最长 24 小时。撤回、Episode 切换/归档/删除、Gentle Closure 或全部删除均立即清理投影、缓存、预览和扩展密钥。
- 版本化、机器可读的语义 Design Token 仓库是唯一事实源。系统无障碍约束始终生效，内容优先级固定为 Medical Safety/Crisis > Error/Permission/Destructive Confirmation > Temporary Interaction > Mood/Ambient > Task > Decorative。

### 4.9 生产、供应链、SLO 和事故

- 中国大陆单主云区域、至少两个 AZ Active-Active；Gateway 无状态跨 AZ，身份/权益/计量元数据高可用。健康正文、Prompt、文件和 Episode 不进入后台数据库，AZ 故障不影响本地 App。
- 本地 Rule Pack 执行成功率目标 ≥99.99%、p99 ≤1 秒，关键 Golden 发布时 100% 通过；签名失败、损坏或超范围时只能保守转介，不能输出“安全”。
- Gateway 月可用性 ≥99.9%，自身附加延迟 p95 ≤300 ms；云端 RTO ≤30 分钟，身份/权益/计量元数据 RPO ≤15 分钟。服务端健康正文 RPO 不适用，因为不得存在该数据库。
- Dev/Staging/Prod 独立账号、网络、数据库、KMS/HSM Key、Provider 凭据和域名；生产权限采用审批 JIT 或双人 Break-glass，全程审计。
- App、Gateway、Rule Pack、Provider Allowlist、远程配置和 Token Bundle 都签名；生成 SBOM 和构建 Provenance。Critical 漏洞、签名失败、未批准 SDK 阻断发布。
- Kill Switch 分 Provider/Model、区域 Egress、Skill/Version、文件上传和 Rule Pack。它可以停用远端能力，但不能整体关闭本地 Safety；只能回滚到最后一个 MD 批准的 Last-Known-Good Rule Pack。
- 医疗安全事故和隐私/安全事故是两个可同时开启的通道。公开生产必须具有 7×24 P0 值守；P0 15 分钟确认、30 分钟指定 Incident Commander、60 分钟完成首轮隔离、2 小时完成 MD+LEGAL+SEC 初评、4 小时决定并准备用户通知。
- 7×24 事故响应不是 7×24 医疗监护，营销和条款不得将其表述成持续临床监测。

### 4.10 量化验收、变更和共同签字

- 开放 P0/P1 为 0；医疗安全、隐私/未授权出站、数据丢失/错 Episode、迁移/Archive、删除、密钥/鉴权/签名/Kill Switch、关键无障碍 P2 为 0。
- 其他普通 P2 最多 5 个，逐项由域 Owner 书面接受，含补偿措施、回归计划和 ≤30 天到期日，不跨 Major 继承。PO 不能单独豁免专业域 No-Go。
- 所有受支持 Event/Payload/Command/Field/Receipt/Archive Fixture/Golden 100% 通过；Android/iOS 对同一 Event 流产生语义等价 Projection；跨 Episode/Subject 污染为 0；Archive 当前及前两个主要版本往返和原子失败回滚 100%。
- Clinical Golden 的安全红线和关键集 100% 通过；未经确认的医学关键字段自动写入为 0。非关键报告字段精确匹配率 ≥95%，医学关键字段由 MD 逐字段设定，不得用整体平均掩盖关键失败。
- 全链路正文/Key 泄漏、无同意或撤回后出站、BYOK 经 Gateway、Safety/危机排队、静默文件上传/Fallback、未签名 Rule 接受、鉴权绕过、Kill Switch 后新请求均为 0。
- P0 无障碍流程 100% 可完成；视觉相似度 ≥0.99 不能代替可读性、读屏、焦点或隐私验收，关键区域不得 Mask。
- 性能门槛绑定具名 Release Build 和设备矩阵；不得在验收失败后单方降低。
- 法域、人群、平台、医疗阈值、Rule/Model/Skill/Prompt/译文、Provider 法律路径、数据类别、SDK/遥测、备份/删除/导出、Breaking Schema/Token、危机/Gentle Closure/事故文案或安全/无障碍门槛变化，必须走书面变更和对应重新签字。

## 5. R1–R10 一致性审计

| 审计链 | 结论 | 关键解释 |
|---|---|---|
| 范围链 | 一致 | Phase 1–6 全闭环由 SCP-001 四列表和 SIGN-001 绑定，任何 Required 缺项都不能静默从 V1 删除。 |
| 事实与写入链 | 一致 | Local Event Store → Projection → Typed Command/Policy → Event/Receipt/Provenance → Replay/Migration，只有一个事实源。 |
| 医疗链 | 一致 | Rule Pack 是 Safety 权威；AI、OCR、Mood、Queue、Widget、Provider 和 Incident 均不能越权解除风险或改药。 |
| 隐私链 | 一致 | 默认本地；出站最小化和逐目的同意；Gateway 瞬时处理但不持久化；日志、计量、遥测和取证无正文。 |
| 删除链 | 一致 | 正常历史 Append-only；用户明确永久删除时删除权优先，通过 crypto-shred、Purge、重建和残留验证清除。 |
| 恢复链 | 一致 | 系统健康备份被排除；唯一迁移通道是用户持钥的加密 Archive；导入后从 Canonical Event 重建。 |
| 双端链 | 一致 | Domain/Schema/Archive/Token/验收统一，Android 先行；iOS 与多机在公开发布前仍是硬门槛。 |
| 生产链 | 一致 | 云端高可用、SLO、Kill Switch 和事故响应服务于远端能力，不反向成为本地核心/Safety 的依赖。 |
| 治理链 | 一致 | 量化门槛、专业域否决、同一 Build 签字和重新签字触发器阻止口头降级或证据漂移。 |

最终交叉审计结论：`PRODUCT_DECISIONS_COHERENT`。该结论只说明合同选择相互兼容，不表示实现、法规、临床、安全或发布证据已经通过。

## 6. 必须进入术语表和状态/数据合同的 12 项显式消歧

以下消歧不是新增产品范围，而是防止相同术语在实现、法律文本、营销和签字中被误读：

1. “风险 Event 必须保留”只指本地 Event Store，不得解释为云端健康事件库。
2. “No Health Data Backend”不等于“健康数据从不被远端处理”；官方 AI 经同意后仍可能由 Gateway/Provider 瞬时处理最小上下文，必须准确披露。
3. Event/Risk 默认保留用于本地追溯，但用户明确永久删除 Episode/全部数据时，删除权优先；不得保留含健康正文的 Tombstone。
4. “物理删除”定义为应用层全路径清除、密钥销毁和残留验证，不承诺移动闪存逐比特不可恢复；系统备份必须排除或准确披露现实边界。
5. Rule Pack Kill Switch 不能整体关闭本地 Safety；只能回滚到 MD 批准的 Last-Known-Good。无可用包时显示通用保守指引，不输出“安全”。
6. Safety/危机永不进入 Pending Queue；文件只保存本地引用并逐次重确认；撤回同意立即取消相关队列和重试。
7. Widget 不显示 Risk，也不得用“无风险”替代；孕周是敏感信息并逐字段 opt-in；Gentle Closure 立即清除快照。
8. 7×24 事故响应是生产运维义务，不是 7×24 医疗监护或持续风险监测。
9. 无正文取证是默认且持续的硬边界；确需内容时，只能由用户主动同意并发送最小脱敏证据包，事故本身不能自动开启正文日志。
10. BYOK 设备直连不等于 YunMom 为第三方 Provider 的隐私合规担保；本地 Schema/Policy/Safety 仍强制，Provider 条款必须透明披露。
11. Provider 法律实体、地域、用途、数据类别、保留/训练条款实质变化必须重新同意；仅模型 ID 变化且法律数据条件不变时，至少触发 MD/QA 全量回归与适当通知，不制造无意义的重复同意。
12. “Golden 关键集 100%”只表示获批测试集零失败，不得营销为真实世界零误诊、零漏报或医疗保证。

若这 12 项尚未进入同一术语表、Schema、状态机、用户文案和测试合同，最终签字仍应为 No-Go。

## 7. 不可豁免红线

以下类别不能由 PO 单签、免责声明、灰度、内测表现、已知问题或“上线后补证据”豁免：

1. 本地 Medical Safety 被网络、登录、权益、Gateway、Provider 或远程 Kill Switch 阻断；未签名/过期/损坏 Rule 仍给出“安全”。
2. LLM/OCR 独立诊断、治疗、处方、改药、解除/降低 R2/R3，或未经用户确认写入医学关键字段。
3. Safety/危机被延迟排队，Mood/Persona 安慰覆盖风险，或危机资源/行动路径错误。
4. 未授权、撤回后、数据路径实质变化未再确认的出站；静默文件上传、静默 Fallback、未经批准跨境或 BYOK 经 Gateway。
5. Prompt/Response/OCR/报告/图片/健康字段/Key 进入日志、APM、WAF、Crash、遥测、计量、备份、诊断包或事故证据。
6. 健康云档案、后台可联表 Episode、员工可浏览健康正文，或账号/商业身份和健康库未隔离。
7. Event 双事实源、覆盖历史、服务器成功作为本地生效前提、无 Receipt、无 Schema 版本、重复 Command/Event/Receipt/扣费或跨 Episode/Subject 污染。
8. 永久删除只留 Tombstone、未覆盖派生/Queue/Widget/Key/备份，或用“闪存覆盖”替代密钥销毁与全路径清理。
9. 服务器托管 Archive 恢复密钥、静默合并/覆盖 Archive、未验证的破坏性迁移或无法回滚/回环。
10. Safety 只靠颜色、动画、声音或触觉；关键流程无障碍阻断；Widget 默认暴露健康详情、直接写库、从 Gateway 取健康状态或删除后残留。
11. 共享生产密钥、长期管理员、未签名制品/Rule/配置、开放 Critical/High 漏洞、Kill Switch 后仍发新请求或无 Last-Known-Good。
12. 医疗和隐私安全事故被普通 Bug/客服流程替代；公开生产没有 7×24 P0 响应；可能受既往错误建议影响的用户没有及时安全更正机制。
13. 开放 P0/P1 或专业高风险 P2；缺少目标法域医疗/隐私法律意见；任一 MD/LEGAL/SEC/TECH/QA/ETHICS No-Go 被 PO 覆盖。
14. 公开发布前未完成 iOS/Android 具名真机矩阵、独立渗透复测、删除取证、无障碍、迁移/Archive 和同一 Build 的共同签字。

## 8. 最终 Go/No-Go 阻塞矩阵

当前所有角色均为 `PENDING / NO-GO`。这里的 No-Go 表示证据和外部签字尚未齐全，不表示产品方向被否决。

| 角色 | 必签范围 | 最低证据包 | 当前阻塞/No-Go 条件 |
|---|---|---|---|
| MD | 产品适用/排除人群；R0–R3、时间窗、症状/生命体征/报告/药物/胎动；本地 Safety、危机、Gentle Closure、Widget 非 Safety、LKG/事故更正 | 目标法域执业妇产科专业意见；版本化 Rule Pack；Clinical Golden 关键集 100%；低置信/OCR/药物/断网/危机/失去/无障碍和事故演练报告 | 关键 Golden 任一漏项或行动降级；远端故障影响 Safety；LLM 可解除风险/改药；Safety/危机排队；未签名或过期规则判断；范围超证据；开放临床 P0/P1 |
| LEGAL | 中国大陆产品分类、PIPL/敏感信息、Consent/撤回、AI/BYOK、Provider/地域/跨境、Queue/文件、日志、Widget、备份/删除、商店、事故时钟 | 外部律师书面意见；数据清单/流图/DPIA；Provider 合同与分包商；Consent 负向测试；无正文抓包；删除/备份真机取证；政策/商店材料/通知矩阵 | 无书面分类；未批准 Provider/跨境；同意不可撤回；撤回后出站；正文日志；静默 Fallback；删除/备份边界未披露；对外误称“绝不离机” |
| SEC | Threat Model、密钥/加密、日志、Queue、Gateway、Provider/BYOK、Widget、删除、供应链、IAM、Kill Switch、Incident | Threat Model；Crypto Profile；全链路无正文与 BYOK 零 Gateway；删除取证；SBOM/Provenance/签名；Kill Switch/LKG 演练；独立渗透及复测 | Critical/High 未关闭；Key/凭据泄漏；鉴权绕过；未签名 Rule/构建；Kill Switch 后新请求；正文泄漏；删除残留；生产访问/环境隔离不合格 |
| TECH | 跨端架构、Schema Registry、Event/Command/Receipt、Projection/Upcaster、加密/删除/Archive、Queue/幂等、Widget/Token、生产/IaC/SLO | 参考实现与 Conformance Fixture；跨端 Replay/Archive；迁移/回滚；删除状态机；Release Build、IaC、SBOM、容量、回滚和证据 Manifest | 双事实源/部分写入/重复提交；跨端语义不等价；破坏性迁移；Archive 不兼容；性能未达标；生产/回滚/Kill Switch 不可用；证据与 Build 不一致 |
| QA | 需求追踪与所有功能、平台、异常、Golden、迁移/Archive、删除、安全、无障碍、Widget、性能、生产故障和事故演练验收 | RTM；具名 OS/真机矩阵；全部 Golden/Fixture；抓包/取证；性能和 Crash-free；故障注入、恢复、Kill Switch、事故演练；开放缺陷/豁免清单 | P0/P1 或高风险 P2 未清零；iOS/Android 真机缺失；P0 流程不可完成；迁移/Archive/删除/幂等未 100%；性能/稳定性门槛未通过；证据漂移 |
| ETHICS | 心理危机、妊娠失去、Risk/Gentle Closure、事故通知、拟人化依赖/操控、低敏锁屏与不羞辱文案 | 危机/失去/医疗与隐私事故预审文案；伤害场景与对抗对话评审；围产心理/丧亲照护相关专业意见；大字/读屏/低认知负担审查 | 错误安慰弱化 Safety；危机陪伴替代真人求助；失去后残留/自动天使化/推备孕；暴露孕周/失去/心情；恐惧或内疚式转化；开放伦理 P0/P1 |
| PO | V1 Scope/Allowlist、法域/年龄/边界、资源、非目标能力、商业权益、7×24 资源、发布/回滚责任 | 91 项决策登记；Scope 四列表；RTM；发布清单；开放缺陷；回滚和值班；同一 Build 的六个专业域 Go | 任一专业签字缺失或 No-Go；公开范围超签字范围；无 7×24 P0 能力；证据与 Build 不同；试图以 PO 单签覆盖专业否决 |

最终共同封面必须绑定：源码 Tag、Build Hash、法域、语言、年龄/人群、功能开关/地区矩阵、Rule/Skill/Policy/Consent/Provider/Token/Schema/数据流版本、签署日期、有效期、全部证据哈希、开放缺陷和有效风险接受。

## 9. 尚待产出的工程附件登记册

以下附件全部属于发布合同，不是可选文档。可按实现阶段逐步产出，但公开发布前必须完成、版本化并进入最终证据 Manifest。

| 编号 | 附件 | 最低内容 | 主责/签字 |
|---|---|---|---|
| ENG-00 | 最终决策与 Readback 包 | R1–R10、91 项 ID、12 项消歧、共同封面、证据哈希、签字页 | PO/TECH/QA/MD/LEGAL/SEC/ETHICS |
| ENG-01 | V1 Scope 与变更合同 | Phase 1–6 四列表、30 个 Skill、Rule/Provider/Field/Widget/Export/Archive/平台映射、Feature Flag、变更单、豁免登记 | PO/TECH/QA；按域加签 |
| ENG-02 | OS/设备/环境矩阵 | Android/iOS 版本、API、具名真机、内存/存储/刷新率、厂商/商店、安装/升级/离线/通知/Widget/备份/无障碍场景 | TECH/QA/SEC |
| ENG-03 | 架构、数据流与信任边界 | Local-first、No Health Data Backend、身份/健康隔离、Gateway 瞬时路径、Provider/BYOK、五级数据、威胁模型 | TECH/SEC/LEGAL |
| ENG-04 | Event/Command/Receipt Schema 包 | Event/Payload/Command/Field/Receipt/Conflict Schema Registry、代码生成、Reducer/Upcaster、Conformance Fixture | TECH/QA/SEC |
| ENG-05 | 迁移与加密 Archive 规范 | 版本窗口、Manifest、KDF/AEAD、Unicode/JSON/时间向量、恶意包限制、原子导入/回滚、跨端往返 | TECH/QA/SEC/LEGAL |
| ENG-06 | Crypto/Key/Delete/Backup 合同 | Crypto Profile、Key 状态机、Keychain/Keystore、Purge 状态机、逐存储删除矩阵、残留扫描、备份排除真机证据 | SEC/TECH/QA/LEGAL |
| ENG-07 | Provider/Gateway/Context 合同 | Provider 白名单/合同表、精确模型、数据地域/保留/训练/分包商、Context Manifest、Egress Policy、文件生命周期、错误注册表 | LEGAL/SEC/TECH/MD |
| ENG-08 | Queue/计量/幂等合同 | Queue Schema/状态机、TTL/容量、Consent 失效、Operation/Attempt/Command/Receipt、Reservation/Settlement、对账 | TECH/SEC/QA/LEGAL |
| ENG-09 | 双端无障碍验收包 | P0 Journey、语义/焦点/读屏脚本、最大字号、触控、对比、色觉、Reduce Motion、临床可用性 | QA/TECH/MD/ETHICS |
| ENG-10 | Widget 隐私与安全包 | Field Allowlist、逐字段授权、Projection Schema、加密/专用密钥、TTL、占位、深链、生命周期删除矩阵 | TECH/SEC/QA/LEGAL/ETHICS |
| ENG-11 | Design Token 与状态系统 | Token Schema/生成器、Flutter/Rive/iOS/Android Widget 映射、优先级、SemVer、Golden、回滚 | Design/TECH/QA/MD |
| ENG-12 | 生产拓扑、SLO 与可观测性 | 云厂商/区域/AZ/IaC、容量/成本、SLI/Error Budget、Dashboard、Retention、Telemetry Allowlist、RTO/RPO | TECH/SEC/QA/LEGAL |
| ENG-13 | 发布、供应链与事故包 | SBOM/Provenance/签名、第三方 SDK、漏洞门禁、Canary/回滚/Kill Switch/LKG、双事故 Runbook、值班/通知/RCA/CAPA | TECH/SEC/QA/MD/LEGAL/ETHICS |
| ENG-14 | Medical/AI Golden 包 | Rule Pack 来源/法域/人群/孕周/复审日、R0–R3、报告/OCR/药物/危机、多胎、Golden Corpus、回归结果 | MD/QA/TECH/LEGAL/SEC |
| ENG-15 | 测试、缺陷与证据索引 | RTM、全部 Golden/Fixture、抓包/取证、性能/稳定性、演练、开放缺陷/豁免、证据→Build 映射 | QA/TECH/PO；按域加签 |

## 10. 基于当前资源的分阶段执行计划

### 10.1 现在即可完成：一台电脑 + 一台 Android 手机

- 冻结 ENG-00/01/03/04 的文档结构、术语表、Schema、状态机和追踪 ID。
- 建立共享 Domain/Schema/Token/Archive 合同和跨端可生成接口，避免 Android 私有格式成为事实标准。
- 实现 Android Local Event Store、Command/Receipt、Projection、Rule Pack、Queue、Archive、Key/删除/备份排除、Widget 最小投影和首轮无障碍。
- 建立单元、属性、Fixture/Golden、崩溃恢复、离线、重复/乱序、迁移、Archive、Consent、删除和无正文静态/动态测试。
- 构建 Gateway/Provider Adapter 的无正文合同、错误注册表、BYOK 直连边界、计量/幂等模型及合成环境。
- 建立 CI、Schema/Token 代码生成、SBOM、Secret/SAST/依赖扫描、签名、证据 Manifest 模板和 Release Checklist。
- 在现有 Android 真机完成首轮 KeyStore、备份排除、删除、弱网/飞行模式、TalkBack、最大字号、Reduce Motion、Widget 和性能基线；结果标记为开发证据，不冒充最终矩阵。

### 10.2 Android 内测前必须补齐

- 冻结具体 Android 最低 API、目标 API、厂商/应用市场和具名设备矩阵；至少补一台最低支持档和一台上档 Android 真机或等效受控设备资源。
- 完成 Android 加密/删除/备份取证、P0 无障碍、Widget/Token 状态矩阵、性能/稳定性、升级/重装和 Archive 往返。
- 建立隔离 Staging、无正文 Gateway、Provider 白名单、BYOK 零 Gateway、Queue/计量/幂等、签名构建、SBOM、回滚/Kill Switch。
- 满足内测定义的缺陷出口、隐私同意、测试账户、日志白名单、用户反馈和事故升级流程；未获相应批准的 AI/医疗/文件能力保持关闭。

### 10.3 公开商店 V1 Go/No-Go 前必须补齐

- 获得 macOS/Xcode、受支持 iPhone/iPad（如纳入范围）和 iOS 真机构建/调试资源；完成 iOS App、WidgetKit、Keychain、VoiceOver、通知、备份排除、删除取证、性能和 Archive 往返。
- 完成 MAT-001 双端具名真机矩阵，证明 Android/iOS 的 Projection、Schema、Archive、Safety、Consent、删除、Widget、无障碍和性能合同等价。
- 完成双 AZ 生产环境、KMS/HSM、JIT/Break-glass、字段白名单 APM/WAF、容量、SLO、RTO/RPO、恢复和 Kill Switch 演练。
- 完成 Provider/Model、支付/权益、应用市场、隐私/法律、临床和伦理外部意见；目标法域专业律师与临床专家必须审阅最终能力和文案。
- 完成独立专业渗透与复测，Critical/High 为 0；完成双端删除取证、无正文全链路抓包、三次事故/恢复演练及 7×24 值班验证。
- 由七个角色对同一 Release Candidate Manifest 共同签字。签字后任何对象发生变化必须按 CHG-001 判断回归和重新签字。

## 11. 量化发布出口总表

| 类别 | 必须达到的出口 |
|---|---|
| 缺陷 | P0=0、P1=0、专业高风险 P2=0；普通 P2≤5 且每项书面、具名、补偿、回归、≤30 天 |
| Clinical Golden | MD 批准关键集 100% 通过；未经确认医学关键字段自动写入=0；不宣称真实世界零误诊 |
| 报告解析 | 非关键字段精确匹配率≥95%；关键字段逐字段阈值和低置信确认由 MD 冻结 |
| 数据/迁移 | 全部受支持 Schema/Fixture/Golden 100%；跨端 Projection 语义等价；跨 Episode/Subject 污染=0 |
| 幂等 | 每个用户意图最多一次有效 Command/Event 集、主 Receipt 和额度结算 |
| Archive | 当前及前两个主要版本认证、导入、往返、兼容和原子回滚 100% |
| 隐私 | 正文/Key 泄漏=0；无授权/撤回后出站=0；静默文件/Fallback=0；BYOK 经 Gateway=0 |
| 安全 | 未签名 Rule 接受=0；鉴权绕过=0；Kill Switch 后新请求=0；Critical=0、High=0 |
| 删除 | 自动化删除路径 100%；Android/iOS 真机覆盖所有存储位置、Key 失效和残留扫描 |
| 无障碍 | iOS/Android/Widget 的 100% P0 Journey 通过读屏、最大字号、对比、焦点、非手势和 Reduce Motion |
| 视觉 | 关键区缺字/遮挡/错层=0；Golden 感知相似度≥0.99；关键语义/隐私区不得 Mask |
| 上档性能 | 60 Hz 设备帧时长 p95≤16.7 ms，>33.3 ms 严重卡顿帧≤1% |
| 最低档性能 | 帧时长 p95≤33.3 ms，>33.3 ms 帧≤5%；双端冷启动 p95≤3 秒 |
| 稳定性 | Android/iOS 分别 Crash-free Sessions≥99.5%；飞行模式 P0 本地清单 100% |
| 本地 Safety | Rule 执行成功率目标≥99.99%、p99≤1 秒；关键 Golden 发布时 100% |
| Gateway/SRE | 月可用性≥99.9%、自身附加延迟 p95≤300 ms、RTO≤30 分钟、元数据 RPO≤15 分钟 |
| 事故 | 7×24 P0；15 分钟确认、30 分钟 IC、60 分钟隔离、2 小时联合初评、4 小时通知决定；季度桌面/半年实操 |

## 12. 重新取得意见或签字的触发器

- MD：风险阈值、行动时间窗、孕周/人群/多胎高危、药物/报告解释、医疗主张、Rule/Skill/Model/Prompt/译文、新证据或医疗事故变化；Rule Pack 至少每 6 个月主动复审。
- LEGAL：法域/语言/未成年人、账号健康同步、Provider 实体/地域/保留训练/分包商、新数据类别/Context、SDK/分析/广告、备份/删除/导出、隐私/Consent/营销、法规/商店规则或事故变化；至少每年主动复审。
- SEC：架构、权限、密钥、加密、Gateway/日志、SDK、更新/签名、生产访问或 Kill Switch 变化；重大版本及至少每年独立渗透。
- TECH/QA：Schema/Archive/Token Breaking Change、支持 OS/设备、性能门槛、存储引擎、迁移/回滚、Provider Adapter、生产拓扑或证据对象变化。
- ETHICS：Persona、危机、妊娠失去、Risk、Gentle Closure、事故通知、商业化/广告、语言文化或用户研究发现新伤害时；至少年度复审。
- PO：范围、法域、人群、主张、商业模式、能力开关或 Release Candidate Manifest 改变时，必须重新确认相关专业域是否需要回归/重签。

## 13. 发布状态与下一步

本次访谈的工作成果可以正式标记为：

> `10/10 轮完成 — 产品决策已冻结 — 发布未批准`

立即可执行的下一步不是继续增加选择题，而是把 ENG-00–ENG-15 转化为可追踪的工程合同和实现任务，优先建立 Scope 四列表、Schema Registry、Android Local-first 垂直切片、Medical/Privacy Golden 框架和证据 Manifest。

只有当以下条件同时成立，发布状态才可以从 No-Go 转为 Go：

1. Phase 1–6 Required Scope 全部实现且无静默删减；
2. Android/iOS 具名真机和全部量化出口通过；
3. 中国大陆法律/隐私、临床、安全、伦理意见及独立渗透证据齐全；
4. 生产拓扑、值班、回滚、Kill Switch、恢复和双事故演练通过；
5. MD、LEGAL、SEC、TECH、QA、ETHICS、PO 对同一 Build 和同一版本清单全部签署 Go。

在此之前，任何构建都只能是开发版或受控内测候选，不能宣称完成公开商店 V1 的发布批准。
