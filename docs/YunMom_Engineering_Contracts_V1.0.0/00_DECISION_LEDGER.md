# YunMom 工程合同决策台账

> 状态：`PRODUCT_DECISIONS_FROZEN` / `RELEASE_NOT_APPROVED`  
> 合同目标版本：V1.0.0  
> 来源基线：`../YunMom_Product_Baseline_V1.0.0/`  
> 创建日期：2026-08-10（Asia/Shanghai）  
> 产品冻结日期：2026-08-11（Asia/Shanghai）  
> 最终 Readback：`01_FINAL_READBACK.md`

## 1. 台账规则

1. 原始产品基线保持只读；本目录承载访谈决定、工程合同与后续签字附件。
2. 用户选择冻结产品意图与工程方向，不替代医学、法律、隐私或安全负责人的专业签字。
3. `FROZEN` 表示产品负责人已作出选择；带外部签字要求的条目在相应负责人签字前仍是发布阻塞项。
4. 后续决定若与已冻结条目冲突，必须记录变更原因、影响范围、替代方案和重新签字要求，不得静默覆盖。
5. 产品基线中的 Local-first、No Health Data Backend、AI 不直接写数据库、Typed Command、Receipt/Undo、正文不进日志、BYOK Key 不出设备、Medical Safety 与 MoodCare 分离等红线，不作为普通偏好反复表决；推翻时按重大版本变更处理。

签字标签：`PO` 产品负责人；`TECH` 技术负责人；`QA` 质量负责人；`MD` 临床安全负责人；`LEGAL` 中国大陆法律/隐私/监管顾问；`SEC` 安全负责人；`ETHICS` 科技伦理与敏感内容评审。

## 2. 访谈进度

| 轮次 | 主题 | 状态 |
|---|---|---|
| 1 | 项目边界、首发法域、平台与 V1 功能范围 | 已冻结 |
| 2 | Pregnancy Episode、用户与家庭权限 | 已冻结 |
| 3 | 医疗产品边界与 Medical Safety 治理 | 已冻结 |
| 4 | 数据分级、同意、AI 出站与 Provider 准入 | 已冻结 |
| 5 | Event、Command、Field、Receipt 与冲突 Schema | 已冻结 |
| 6 | 加密、密钥、Archive、备份与彻底删除 | 已冻结 |
| 7 | Pending Queue、Provider、Gateway 与计费幂等 | 已冻结 |
| 8 | 无障碍、Widget、Design Token 与状态组合 | 已冻结 |
| 9 | 生产拓扑、SLO、可观测性与事故响应 | 已冻结 |
| 10 | 量化验收、变更治理与最终签字包 | 已冻结 |

## 3. 已冻结决定

### BND-001：当前下一里程碑

- 状态：`FROZEN`
- 选择：公开商店 V1。
- 合同解释：按生产、应用市场、真实用户、完整隐私与安全治理、事故响应和发布审查门槛建设；内部演示或自用可作为中间构建，但不能替代公开发布验收。
- 直接影响：所有 P0 安全与合规缺口、目标法域发布包及上线签字必须在公开发布前关闭。
- 外部签字：LEGAL、MD、SEC，待取得。

### BND-002：首发法域

- 状态：`FROZEN`
- 选择：中国大陆单一区域。
- 合同解释：首个公开版本只承诺中国大陆；隐私、敏感个人信息、AI 数据路径、Provider 地域、应用市场材料、紧急资源与医学内容均建立中国大陆专项包。
- 排除：本合同不自动覆盖港澳台或其他国家/地区；新增法域必须触发书面变更单和独立地区矩阵。
- 外部签字：LEGAL、MD、SEC，待取得。

### BND-003：客户端合同与实现顺序

- 状态：`FROZEN`
- 选择：iOS/Android 双端统一合同，Android 作为首个实现、测试和验收基准。
- 合同解释：
  - Flutter Domain、Event/Command/Field Schema、Skill/Policy、数据迁移、导出格式和业务验收用例必须双端共用；
  - Android 原生适配器先实现并在用户现有 Android 真机上持续测试；
  - iOS 实现后置，但不得形成第二套数据库、事件语义、业务规则或迁移格式；
  - Android 验收通过不等于 iOS 平台验收通过。iOS 发布前仍须完成 Keychain、WidgetKit、通知、文件、系统备份、性能和无障碍专项验证。
- 直接影响：所有跨平台接口先合同化；平台差异收敛在 Adapter 层。
- 外部签字：TECH、QA；平台隐私差异另需 LEGAL/SEC。

### BND-004：V1 功能边界

- 状态：`FROZEN`
- 选择：Phase 1–6 全闭环进入公开商店 V1。
- 合同解释：V1 覆盖 Living World、AI 地基、专业管理、日常照料、生活准备、Widget、孕期总结、数据导出/迁移及 Gentle Closure 完整测试。
- 范围控制：该选择纳入六个既定 Phase，但不自动纳入规范中标注为“未来、可选、平台允许时、自定义 Provider、远程家庭实时共享或健康云同步”的能力；30 个 Skill 的启用白名单、Widget 隐私级别和 DadEntry 形态仍须单独冻结。
- 直接影响：发布周期和验证面采用最大范围估算；不得以删减 P0 安全、隐私、无障碍或异常状态换取功能齐全。
- 外部签字：PO、TECH、QA；医疗能力另需 MD/LEGAL。

## 4. 第 2 轮已冻结决定

### EPI-001：Episode 数量与活动约束

- 状态：`FROZEN`
- 选择：允许无限历史 Pregnancy Episode，但任一时刻默认只有一个 Active Episode。
- 合同解释：历史 Episode 可查看、导入、封存或删除；Planner、通知、Widget、Living World 和 AI Context 默认只绑定当前 Active Episode。
- Schema 义务：所有 Episode 作用域数据必须携带 `episode_id`；本地数据层必须强制单用户最多一个 Active Episode，状态切换采用事务与 Typed Command。

### EPI-002：多胎领域模型

- 状态：`FROZEN`
- 选择：一个 Episode 下建立 `1..N` 个 `BabySubject`。
- 合同解释：母体、共同孕周、医院、药物和 Episode 级任务归属 Episode；胎儿专属的超声测量、标识、结局与视觉资产归属 BabySubject；无法区分具体胎儿的记录保留在 Episode 层并标记不确定性，不得猜测分配。
- Schema 义务：胎儿专属 Event/Observation 使用 `subject_id`；母体或共享记录的 `subject_id` 为空；导出、报告解析、RAG、Timeline 与删除必须保持该归属。
- 外部签字：MD，胎儿专属字段和 Outcome 映射待临床审核。

### EPI-003：Episode 生命周期

- 状态：`FROZEN`
- 选择：有限状态机 `active → delivery_completed | closure_confirmation_pending → quiet_archive → archived`；永久删除是命令，不是状态。
- 合同解释：生命周期描述产品行为和可见状态，`outcome_code` 单独描述经确认的临床/事件结局；二者不得混为一个自由文本字段。所有转换必须由 Typed Command 产生 Event，并清理或重排相应 Planner、通知、Widget 与 Living World 投影。
- 删除边界：永久删除绕过生命周期终态，执行单独的不可恢复级联删除合同；具体密钥销毁与残留验证在第 6 轮冻结。

### EPI-004：特殊结局分类与触发

- 状态：`FROZEN`
- 选择：采用经临床审核的有限 `outcome_code` 枚举，并保留 `other` / `unknown`；只有用户明确陈述或确认医疗记录后才可转换。
- 安全边界：AI/OCR 可以提取或建议一次克制的确认，但不得自动改变 Episode 状态、停止提醒或进入 Gentle Closure。
- 待补合同：具体 Outcome 枚举、每项所需证据、确认文案、通知清理矩阵、多胎个体状态和撤回路径。
- 外部签字：MD、ETHICS；涉及监管表达时另需 LEGAL。

### USR-001：V1 年龄范围

- 状态：`FROZEN`
- 选择：V1 仅服务 18 岁及以上成年人。
- 合同解释：注册/Onboarding、服务条款、AI 使用和支持流程都以成年人为首发范围；不得在营销或商店材料中声称覆盖未成年孕期用户。
- 变更触发：未来支持未成年人必须另立监护人授权、家庭安全、危机处置、隐私隔离、内容适龄和法域合规附件。
- 外部签字：LEGAL。

### FAM-001：DadEntry 形态

- 状态：`FROZEN`
- 选择：同设备受控入口 + 用户主动生成分享摘要；V1 不做健康数据实时跨设备同步。
- 合同解释：不建立伴侣健康云账号、密文中继或后台共享档案；分享动作由孕妈妈在本地明确触发，导出内容使用最小字段集。
- 范围一致性：该实现满足 BND-004 中 Phase 5 的“爸爸入口”，不触发新的健康云架构。

### FAM-002：家庭权限

- 状态：`FROZEN`
- 选择：按类别最小授权。默认可选择任务、产检日程和用户选中的 Memory；家庭成员可创建带独立 Actor/Provenance 的任务、备注或建议，但不能修改母体健康 Observation、EDD、药物、风险状态或医生指令。
- Policy 义务：家庭成员内容只能作为提议或家庭侧 Event；进入主用户健康事实前必须由孕妈妈接受，并生成 Receipt。
- 禁止：Episode 全量默认共享、家庭成员同权修改、通过家庭入口绕过 Sensitive Access Policy。

### FAM-003：敏感内容授权与撤销

- 状态：`FROZEN`
- 选择：Risk、Gentle Closure、日记、心情、报告、症状、药物和 AI 对话默认不共享；逐类别单独授权，可设置期限并立即撤销。
- 合同解释：授权必须记录类别、范围、目的、有效期、Actor、创建时间和撤销时间；审计记录不得复制敏感正文。
- 现实边界：撤销立即停止 App 内未来访问和后续分享生成，但已由用户导出、截图或发送到外部的副本无法由 YunMom 远程收回，必须在分享前明确提示。
- 外部签字：LEGAL、SEC。

## 5. 第 3 轮已冻结决定

### MED-001：医疗产品边界

- 状态：`FROZEN`
- 选择：消费级孕期照料 + 经临床规则驱动的 Safety Signposting。
- 允许：记录、整理、提醒、报告信息提取、人话解释、经验证规则产生的分级安全行动指引。
- 禁止：诊断、治疗、处方、个体化剂量、开始/停止/更换药物，以及把 YunMom 描述成医生、急救服务或持续监护服务。
- 外部签字：MD、LEGAL；需形成基于最终功能、文案和数据流的中国大陆产品分类书面意见。

### MED-002：Safety 最终权威

- 状态：`FROZEN`
- 选择：本地、版本化、确定性的临床 Rule Pack 是最终判定权威；AI 只负责输入提取和受控语言生成。
- 执行约束：LLM/Provider 不得直接设置、降低或解除 `risk_state`；所有 Safety 结果必须记录命中的规则 ID/版本、适用范围、输入证据和时间。
- 失效策略：Rule Pack 不可用、版本不兼容或输入超出适用范围时，不得返回“未发现风险”，只允许保守转介与通用紧急入口。
- 外部签字：MD、SEC。

### MED-003：风险等级与用户动作

- 状态：`FROZEN`
- 选择：固定四级枚举：`R0 no_active_risk`、`R1 routine_consult`、`R2 contact_soon`、`R3 immediate_action`。
- 语义约束：R0 仅表示“基于当前已输入数据和当前适用规则，没有活动风险状态”，不构成健康保证或完整筛查结论。
- 行动合同：每一级由临床规则绑定受控行动时间窗、UI、通知和说明；呼叫、打开路线、复制/分享就医摘要均由用户明确触发，App 不自动拨号、不自动联系他人、不自动外发健康数据。
- 状态红线：关闭或隐藏提示不等于风险解除；解除必须由新的有效信息、用户/医生反馈或规则重评产生 Event。
- 外部签字：MD、LEGAL。

### MED-004：Safety 输入范围

- 状态：`FROZEN`
- 选择：症状、血压/血糖等生命体征、胎动/宫缩、报告/OCR 与药物信息组成核心医疗输入包。
- 启用方式：每一类别、字段与规则必须独立通过临床验证后由 Feature Flag 开启；未验证类别仍可本地记录，但不得进入安全结论或产生“无风险”暗示。
- 数据边界：Mood、日记和普通对话不进入该核心 Rule Pack；明确心理危机语言走 MED-008 的独立协议。
- 外部签字：MD。

### MED-005：临床适用范围

- 状态：`FROZEN`
- 选择：服务已冻结的成年孕期用户；每条规则声明适用法域、孕周、人群、单胎/多胎、输入前提和排除条件。
- 超范围行为：仍允许记录和查看本地数据，但只做保守转介，不显示“未发现风险”，并提醒遵循医生的个体化计划。
- 与 EPI-002 的关系：数据模型支持 `1..N BabySubject`，但任何多胎 Safety 能力必须逐规则取得多胎适用证据；数据可表达不等于医疗规则已验证。
- 外部签字：MD、LEGAL。

### MED-006：报告与 OCR 边界

- 状态：`FROZEN`
- 选择：提取 + 人话解释；明确区分报告事实、AI 解释和医生判断；Safety 仅经过已验证 Rule Pack，不诊断。
- 证据合同：每个字段保留原始片段/附件引用、来源、置信度、模型版本、提取时间、用户确认状态和修订历史；低置信医学关键字段必须确认后才能成为可信 Observation。
- 原件规则：原始报告不可被 AI 改写；新解析不得覆盖旧解析；失败不得丢失原件或假装已完成。
- 外部签字：MD、LEGAL。

### MED-007：药物能力边界

- 状态：`FROZEN`
- 选择：记录与提醒 + 药名/说明提取 + 保守安全提示。
- 禁止：AI 自动开始、停止、更换药物或改变剂量；不得生成个体化处方或治疗建议。
- 执行合同：涉及治疗变化的输入只可记录用户/医生明确陈述或建议联系医生；相应 Command 至少属于需确认或禁止自主执行等级，并保留完整 Provenance 与 Receipt。
- 外部签字：MD、LEGAL。

### MED-008：心理危机协议

- 状态：`FROZEN`
- 选择：建立与 MoodCare 分离的明确危机语言安全协议，提供中国大陆可用的真人与紧急资源，不进行精神科诊断。
- 安全行为：明确危机信号优先于安慰性人格输出；使用受控、克制、不羞辱的语言，鼓励联系真人支持或紧急资源；不得承诺保密、真人值守或替代专业服务。
- 资源合同：地区资源须版本化、可离线使用、设复审日期，并有资源失效时的通用回退。
- 外部签字：MD、LEGAL、ETHICS。

### MED-009：临床规则治理与验收

- 状态：`FROZEN`
- 选择：版本化 Rule Pack + 临床批准 Golden Set。
- Rule Pack 必填：来源、法域、适用人群/孕周、单胎/多胎范围、排除条件、风险等级、行动时间窗、受控语言、临床 Owner、发布日期、复审日、变更记录、回滚与 Kill Switch。
- 验收合同：规则、模型、Prompt、Provider、提取 Schema、翻译或 Safety 文案发生变化时，必须运行相应 Golden Set 全量回归；误报/漏报及升级/降级阈值由临床负责人签定，不能由 PO 或模型团队自行设定。
- 事故合同：建立独立医疗安全事件通道，可紧急停用规则/模型/Skill；排障不得自动上传完整健康正文。
- 外部签字：MD、LEGAL、SEC。

## 6. 第 4 轮已冻结决定

### DATA-001：五级统一数据分级

- 状态：`FROZEN`
- 选择：全产品统一分为公开产品数据、身份/商业数据、设备与低敏运营数据、健康/亲密内容、密钥与安全凭证五级。
- 合同义务：每个字段、附件、Event Payload、Projection、日志字段和导出项必须在 Data Registry 中声明等级，并映射本地/后台存储、日志、备份、导出、删除、出站目的、允许的 Provider 与同意要求。
- 边界：孕周、医院/医生、报告、附件、症状、生命体征、药物、胎动、心情、日记、AI 对话、风险、妊娠结局以及与其关联的位置/语音均进入健康/亲密内容级；API Key、加密密钥和恢复材料进入密钥与安全凭证级。
- 外部签字：LEGAL、SEC。

### IDN-001：匿名 Local-first 与身份隔离

- 状态：`FROZEN`
- 选择：账号可选，只承载购买、权益和 AI 额度；完整健康档案保持本地，身份/商业后端不存在可联表健康档案。
- 可用性义务：不登录、退出账号或 AI 额度到期时，本地记录、Pregnancy Time、Planner、通知、Timeline、查看与导出仍可使用。
- 后端边界：账号/匿名 ID、权益、计量与计费数据不得包含健康正文、字段值、附件、风险、Skill 输入输出或可重建健康档案的标签。
- 外部签字：LEGAL、SEC。

### CONSENT-001：分层、按目的的 JIT 同意

- 状态：`FROZEN`
- 选择：分层隐私说明 + 按目的、Provider、数据类型的 Just-in-time 同意；敏感内容按适用要求取得单独同意；用户可随时撤回。
- 同意记录：必须记录政策/文案版本、目的、数据类别、Provider、地域、处理动作、Actor、时间和撤回状态；不得把健康正文复制进同意日志。
- 撤回效果：停止未来出站、清除待发送任务并关闭自动重试；本地健康内容继续保留，除非用户另行删除；已经由第三方处理的数据按其合同与现实边界向用户说明。
- 外部签字：LEGAL。

### EGRESS-001：官方 AI 出站授权

- 状态：`FROZEN`
- 选择：首次使用每类 Skill/Provider 时说明目的和数据类型；设置中持续可见、可撤回；报告、照片、日记、危机内容及其他高敏内容每次发送前明确确认。
- 体验边界：普通低敏文本在授权范围未变化时不重复完整法律条款；Provider、目的、地域、数据类别或保留/训练政策实质变化时，必须重新披露并按适用规则重新取得同意。
- 完成语义：用户同意出站不等于同意持久化写入；任何结果写入本地仍须经过 Skill、Schema、Policy、Typed Command 与 Receipt。
- 外部签字：LEGAL、SEC。

### CTX-001：Minimal Context Capsule

- 状态：`FROZEN`
- 选择：每个 Skill 冻结 `allowed_context_fields`、`prohibited_context_fields`、目的、Provider、保留披露、脱敏规则和是否逐次确认。
- 最小化规则：只发送当前输入和完成当前任务确有必要的少量字段；禁止完整 Episode、无关历史、全量日记、全量对话、全量报告或全量照片；模型不得自主扩张读取范围。
- 用户可见性：发送前展示可理解的 Context 摘要；每个出站字段保留本地 Provenance，服务端不得为了排障记录 Capsule 正文。
- 外部签字：LEGAL、SEC；医学必要字段由 MD 复核。

### FILE-001：报告、照片与文件出站

- 状态：`FROZEN`
- 选择：原件先在本地加密保存；仅上传处理副本，移除不必要 EXIF；明确展示文件、目的与 Provider，由用户点击发送。
- 重试边界：文件任务不允许后台静默重试或自动切换 Provider；失败后保留本地原件，由用户重新确认发送路径。
- 清理义务：上传副本、Crop/Deskew/Compress/OCR 临时文件、网络缓冲、失败残留和缩略图必须进入生命周期与删除矩阵。
- 外部签字：LEGAL、SEC。

### PROV-001：中国大陆版本化 Provider 白名单

- 状态：`FROZEN`
- 选择：官方 Provider/Model 逐项审核合同、备案/登记与公示、精确模型版本、数据地域、保留/训练政策、分包商、安全、删除能力、模态和能力限制。
- 准入规则：只有进入目标任务白名单的 Provider/Model 才能接收对应数据等级；不合格路径关闭 Provider 或敏感任务，必要时关闭官方 AI，而不是用用户勾选代替准入。
- 变更规则：Provider、模型修订、地域、分包商或数据政策实质变化触发重新评测、灰度、回滚准备、披露和按适用要求重新同意。
- 外部签字：LEGAL、SEC。

### PROV-002：V1 禁止自动 Fallback

- 状态：`FROZEN`
- 选择：Provider 故障时不自动切换；保留本地原始输入，由用户选择重试或更换 Provider，并重新确认数据路径。
- 计费/写入边界：失败不得假装完成；用户更换 Provider 后复用业务任务标识但生成新的 Provider Attempt，防止重复计费和重复本地写入。
- 外部签字：LEGAL、SEC。

### BYOK-001：审计 Provider Adapter，自定义端点后置

- 状态：`FROZEN`
- 选择：V1 只开放经审计的 Provider Adapter；Key 仅保存在 iOS Keychain/Android Keystore 或等效安全区，由设备直连 Provider；任意 OpenAI-compatible 自定义端点后置。
- 安全边界：BYOK 不经过 YunMom Gateway，Key 不写普通数据库、不进日志、不上传 YunMom；Provider 自身条款需透明说明。
- 一致性义务：BYOK 仍必须执行 YunMom 的 Skill Schema、Context 最小化、Policy、Safety、Typed Command 和 Receipt，不允许“自带 Key”绕过产品安全。
- 外部签字：LEGAL、SEC。

### TEL-001：第一方无内容遥测与禁止健康内容训练

- 状态：`FROZEN`
- 选择：只采集第一方字段白名单中的无内容技术/运营指标；不采集健康行为路径、不做 Session Replay；Prompt、Response、图片、报告和健康内容永不用于产品训练。
- 遥测边界：允许 App 版本、设备/OS 档、渲染/崩溃/内存、Provider 无正文错误码、延迟与 Token/成本等必要指标；不得包含健康字段、对话、文件名、API Key、路径或可推断具体孕期事件的标签。
- 未来研究：必须另立明确目的、最小数据集、独立同意、退出/删除、伦理审查与法律评估，不得把当前产品同意扩张解释为研究授权。
- 外部签字：LEGAL、SEC、ETHICS。

## 7. 第 5 轮已冻结决定

### EVT-001：唯一事实源与 Projection

- 状态：`FROZEN`
- 选择：Pregnancy Event Store 是健康领域唯一事实源；当前实体表、Snapshot、Timeline、RAG 索引和 WidgetState 均为可从 Event 与附件重建的 Projection。
- 合同解释：任何 Projection、缓存或索引不得接受绕过 Typed Command/Event Store 的权威写入，也不得反向覆盖 Event；Projection 丢失、损坏或版本变化时必须能够确定性重建。
- Local-first 约束：Event 的创建、排序和生效不依赖 YunMom 服务器；本地离线写入在事务提交后即为已生效事实。

### EVT-002：领域对象、Aggregate 与 Attachment

- 状态：`FROZEN`
- 选择：领域对象拥有稳定 `aggregate_id`，每次变化由版本化 Event 驱动；实体表只承载 Projection；Attachment 原件单独加密保存并由 Event 引用。
- Schema 义务：Event 必须明确所属 Episode、可选 Subject 与 Aggregate；附件引用必须包含稳定 ID、内容完整性校验、加密版本、MIME/大小等非正文元数据及 Provenance，不能以易变文件路径作为身份。
- 删除边界：Event 对附件的引用不构成永久保留权；用户永久删除时二者按第 6 轮删除矩阵共同清除。

### EVT-003：不可变历史、纠错与撤销

- 状态：`FROZEN`
- 选择：正常生命周期内 Event 不可变；修改产生 `correct` / `supersede` Event，撤销产生 `revert` Event，`is_reverted` 等状态只由 Projection 推导。
- 禁止：原地覆盖 Event Payload、直接更新权威 `is_reverted` 标志，或用“最后写入覆盖”隐藏原证据。
- 永久删除例外：不可变性约束业务历史，不阻止用户明确发起的独立不可恢复删除命令；永久删除不得伪装成仅追加 Tombstone，也不得为了审计而保留可恢复的健康正文。

### EVT-004：Event Envelope

- 状态：`FROZEN`
- 选择：采用完整、版本化 Event Envelope：UUIDv7、`episode_id`、可选 `subject_id`、`aggregate_id`、`event_type`、Payload/Schema 版本、occurred/effective/recorded time、时区与时间精度、Actor、Device、设备内 Sequence、Command、Correlation、Causation 与 Provenance。
- 时间语义：三个时间字段不可互相替代；未知精度必须显式记录，不得伪造到秒。UUIDv7 和设备 Sequence 用于稳定本地排序与排障，不被解释为跨设备绝对因果顺序。
- 双端义务：Dart、Android、iOS 与 Archive 使用同一规范 Envelope；平台适配层不得增设另一套事件语义。

### CMD-001：Typed Command 原子事务

- 状态：`FROZEN`
- 选择：Command 必含 `command_id`、`idempotency_key`、`expected_revision`、Actor/Source 与 `policy_version`；一个 Command 可原子产生一组有关联的 Event。
- 执行合同：Schema、权限、临床/产品 Policy、Revision 与业务不变量全部通过后方可提交；任一校验失败或事务中断均为零 Event 写入。相同幂等键的安全重试不得重复生成 Event、Receipt 或扣费。
- 冲突语义：`expected_revision` 不匹配时返回结构化冲突，不得自动以服务器状态或最新写入覆盖本地事实。

### RCT-001：执行等级与 Receipt

- 状态：`FROZEN`
- 选择：A/B 可直接执行，C 在确认后执行，D 永不执行；所有持久化动作无论等级均生成 Receipt。A 使用紧凑反馈，B 使用突出撤销反馈。
- Receipt 合同：绑定 Command 与所产 Event、前后摘要、Actor、Skill、Model、Source、Policy 版本及 Undo 能力；摘要应足够解释变化，但不得制造额外的健康正文副本。
- Undo 义务：Receipt 必须明确可撤销范围、期限与不可撤销原因；撤销通过新 Command/Event 表达，不原地擦改既有 Event。永久删除的确认与回执在第 6 轮单独冻结。

### FLD-001：Universal Field 类型表

- 状态：`FROZEN`
- 选择：技术规范中的 22 类 Field Type 是正式枚举，`boolean` / `tristate` 与 `multienum` / `tag` 分别保留；产品规范的 20 类写法只作为展示别名，不另建类型。
- 演进约束：类型标识进入 Schema Registry；模块不得以自由字符串私建字段类型。展示别名的变化不改变存储语义，新增或破坏性修改必须走 Schema 版本与兼容性审查。

### FLD-002：单位、原始证据与 Provenance

- 状态：`FROZEN`
- 选择：内部同时保存规范单位码与归一化值，以及原始值、原单位、精度和原始文本片段；所有健康值强制携带统一 Provenance。
- Provenance 最小字段：Source、可选 Attachment 引用、Confidence、可选 Model/版本、`user_verified`、`extracted_at` 及适用的 Actor/设备/解析器信息。对人工或设备直接录入不适用的 Model 字段使用显式空值或来源类型约束，不得伪造模型身份。
- 安全约束：单位换算、舍入与解析结果必须可追溯；低置信关键字段仍受 MED-006 的确认门槛约束。

### CFL-001：冲突集合与显式解决

- 状态：`FROZEN`
- 选择：相互不一致且无法安全自动合并的事实进入 `conflict_set`；Reducer 不按“最新”或“最高置信度”暗选。
- UI 与处理：界面展示来源、时间、单位、置信度与差异；用户确认后产生 Resolution Command/Event，并记录采用、并存或暂不决定的结果。
- 证据边界：原始证据在正常生命周期内继续保留并可追溯；用户永久删除时仍按删除合同清除，不以“冲突审计”为由形成不可删除副本。

### SCH-001：Schema Registry、Upcaster 与可回滚演进

- 状态：`FROZEN`
- 选择：Event、Payload、Command、Field 与 Receipt 使用统一版本化 Schema Registry；旧 Event 永不原地改写，由纯函数 Upcaster 和版本化 Projection 读取、重建。
- 迁移合同：迁移必须可恢复、可回滚、可重复运行，并具备固定 Fixture/Golden 测试；Upcaster 不允许网络、当前时间、随机数、设备状态或模型调用等非确定性依赖。
- 双端义务：Schema、兼容窗口、生成代码与 Conformance Fixture 是双端统一合同；Android 先行实现不得产生无法由未来 iOS 读取或重放的私有格式。

## 8. 第 6 轮已冻结决定

### KEY-001：设备 KEK、Episode Key 与 Attachment DEK

- 状态：`FROZEN`
- 选择：设备绑定的安装级 KEK 只负责包裹；每个 Episode 使用独立内容密钥，每个 Attachment 使用独立 DEK。
- 合同解释：安装 KEK 不直接加密健康正文；Episode Key 与 Attachment DEK 必须可独立轮换和失效。整 Episode 可先通过销毁 Episode Key 实现快速不可读，单条结构化记录没有独立 DEK 时仍须执行行、页、WAL/SHM、临时文件与派生数据清理，不得把整 Episode crypto-shred 的能力误述为单条记录已完成密钥擦除。
- 架构一致性：物理密钥分区不得产生多个权威事实源；所有 Episode 分区仍组成一个逻辑 Pregnancy Event Store，并遵守 EVT-001。
- 外部签字：SEC、TECH。

### KEY-002：Secure Storage、透明解锁与重装哨兵

- 状态：`FROZEN`
- 选择：安装 KEK 使用设备绑定、不可同步、优先硬件保护的 iOS Keychain / Android Keystore 或等效安全区；系统解锁后可透明使用，并提供可选生物识别 App Lock。
- Fail-closed：数据库、安装哨兵和密钥状态不一致时不得尝试弱化解密或创建同名新密钥覆盖旧状态；系统恢复缺钥、卸载重装及 iOS Keychain 可能残留等情况必须进入不可读数据/孤儿密钥识别、用户提示与安全清理流程。
- 双端边界：平台 API 差异只存在于 Adapter；设备绑定、不可同步、错误状态和验收语义保持一致。Android 首验不替代 iOS Keychain、卸载残留与恢复专项验收。
- 外部签字：SEC、TECH、QA。

### CRYPTO-001：成熟加密实现、格式版本与可恢复轮换

- 状态：`FROZEN`
- 选择：使用经安全审核的 SQLite 加密、流式 AEAD 文件加密和标准口令 KDF；禁止自研密码算法或自定义非标准协议。
- 版本合同：密文携带彼此独立的算法、加密格式和 Key Slot 版本头；轮换支持断点恢复、崩溃重入、失败回滚与固定跨端测试向量，不改写 Event 的业务语义或历史版本。
- “采用常规方案”的解释：产品负责人授权 SEC/TECH 从目标系统实际支持的成熟标准与维护良好的实现中冻结精确算法、KDF、参数、库版本和迁移窗口；这些参数必须进入版本化 Crypto Profile 和发布签字，不得留给开发者临场选择。
- 外部签字：SEC、TECH、QA。

### DEL-001：Undo、隐藏与永久删除三语义

- 状态：`FROZEN`
- 选择：Undo、从视图隐藏与永久删除是三种独立语义。普通 Undo 通过补偿 Command/Event 表达；隐藏只改变 Projection 可见性；永久删除是 Event Store 业务历史之外的管理性 Purge。
- 永久删除合同：必须由用户明确选择并确认，执行后不可撤回；不得保留包含原健康信息或可恢复标识的 Tombstone。Purge 完成后从剩余 Canonical Event 重建全部受影响 Projection。
- 审计边界：允许保留不含健康正文、附件、原值、Episode 标识或可逆内容指纹的本地执行结果，例如删除命令版本、范围类别/数量、开始/完成时间与成功/失败状态。
- 外部签字：LEGAL、SEC、TECH。

### DEL-002：Crypto-shred、可恢复 Purge Job 与残留验证

- 状态：`FROZEN`
- 选择：永久删除 Episode 时，确认后立即销毁目标 Episode 内容密钥使其不可读，再由可恢复、幂等的 Purge Job 清理 Event Store、DB/WAL/SHM、Attachment、Cache、RAG/Vector、Pending Queue、通知、Widget 与临时文件。
- 完成语义：只有清理 Job 处理完全部适用位置、运行残留扫描并成功重建 Projection 后才可显示“已完成彻底删除”；中断时保持内容不可读并继续安全清理，不把部分成功报告为完成。
- 现实边界：不承诺移动闪存可逐字节覆盖；已由用户发送给外部接收者或已被合格 Provider 接收的数据，按披露、Provider 合同和适用权利请求处理，不虚构本机 Purge 能远程召回。
- 外部签字：LEGAL、SEC、TECH、QA。

### DEL-003：单条记录与派生数据级联

- 状态：`FROZEN`
- 选择：删除前展示影响预览；默认清除来源 Event、相关 Receipt、Projection、RAG/Vector、Attachment/Thumbnail、OCR/网络临时文件、Pending Task、通知和 Widget 状态。
- 单条记录：必须执行权威 Event/Payload 与适用的行、WAL/SHM、空闲页/临时页清理和残留验证；删除完成后只从剩余 Event 重建 Projection。
- 独立下游事实：只有已经由用户独立确认、且不再依赖被删来源才能解释的下游记录，才可在影响预览中供用户明确选择保留；默认不得暗中保留原始片段、Provenance 或可逆副本。
- 外部签字：LEGAL、SEC、TECH、QA。

### BAK-001：系统自动备份全面排除

- 状态：`FROZEN`
- 选择：健康 DB/WAL/SHM、Attachment、Thumbnail、RAG/Vector、OCR/网络临时文件、密钥、Pending Queue、Widget 共享状态和诊断缓存全部排除 iCloud/Android 系统自动备份；跨设备迁移只使用用户主动创建的加密 Archive。
- 平台义务：Android Backup Rules、iOS 文件保护/备份属性、共享容器与 Keychain 行为必须形成逐路径矩阵并在真机验证；系统恢复缺钥、卸载重装、升级和孤儿数据均采用 KEY-002 的 fail-closed 行为。
- 用户边界：YunMom 不提供自营健康云备份；用户把 Archive 保存到自选云盘或介质属于明确导出后的外部路径，导出前必须提示保管、丢失和第三方访问风险。
- 外部签字：LEGAL、SEC、TECH、QA。

### ARC-001：Canonical Archive 内容与身份切断

- 状态：`FROZEN`
- 选择：Archive 以 Canonical Event Log/Payload、必要 Provenance、Attachment、Field Registry 快照和完整性校验为恢复依据；报告历次解析、Task 等可携带为可验证的互操作派生视图，但导入后必须从 Event 重建并验证。
- 排除：Snapshot、RAG/Vector、Cache、账号/商业或权益 ID、Auth Token、BYOK Key、设备标识、安装 KEK/Key Slot，以及其他仅属于当前安装的秘密或运行状态。
- 隐私边界：Actor 映射为 Archive 内部角色或本地伪名；Conversation 默认不包含，只有用户明确勾选才进入。旧 Consent/Egress 记录即使作为历史证据存在，也不得在新安装上恢复为有效出站授权。
- 外部签字：LEGAL、SEC、TECH。

### ARC-002：强制加密、用户口令与离线恢复码

- 状态：`FROZEN`
- 选择：Archive 始终加密；随机 Archive DEK 由用户口令派生密钥包裹，并可选生成高熵离线恢复码。YunMom 不托管、不上传且无法找回解密密钥；口令和恢复码同时丢失即不可恢复。
- 版本合同：Archive Container、Crypto Profile、Event/Payload Schema 与 Projection 版本分别管理；双端冻结口令编码与 Unicode 规范化、KDF/AEAD 参数、JSON/JSONL 规范化、时间表示、Manifest、校验和错误处理测试向量。
- 常规实现原则：恢复码使用成熟的随机生成、校验与离线展示/保存方式，不自定义“安全问题”、账号后门或服务端托管路径。
- 外部签字：LEGAL、SEC、TECH、QA。

### ARC-003：离线预检、原子导入与兼容窗口

- 状态：`FROZEN`
- 选择：导入先离线验证认证完整性、格式、Schema 和版本兼容，再生成新的本机密钥并原子提交或完整回滚；按 `archive_id` / `episode_id` 去重，不静默合并或覆盖。
- 兼容合同：V1 支持当前及前两个主要 Archive 版本；旧 Event 通过 SCH-001 的确定性 Upcaster 读取，派生视图不成为事实源。导入 Active Episode 冲突时先展示选择，不自动替换当前活动妊娠。
- 安全合同：导入器必须限制大小、条目数量、压缩比例、路径、文件类型与资源消耗，并防范篡改、路径穿越、压缩炸弹和重复包；任何失败不得留下半导入 Event、Attachment 或 Key。
- 同意重置：旧 Consent/Egress 授权不继承；新安装首次出站时重新执行 JIT 同意。
- 外部签字：LEGAL、SEC、TECH、QA。

## 9. 第 7 轮已冻结决定

### QUE-001：可排队任务边界与本地权威

- 状态：`FROZEN`
- 选择：只有用户明确发起、尚未完成且非时效性的 AI 任务可进入设备本地加密 Pending Queue，并在 UI 中持续可见。
- 医疗红线：Medical Safety、药物紧急性判断、心理危机及其他需即时处理的任务永不等待云 AI。离线时先运行本地确定性 Safety Gate、展示中国大陆适用的即时行动/紧急资源并明确“云 AI 分析尚未进行”；联网后不得对陈旧症状静默补跑，若用户仍需分析必须确认当前状态。
- 后端边界：Gateway 不承载持久任务队列，不成为健康任务或 Queue 状态的事实源；Gateway 不可用不得影响本地记录、Rule Pack、Planner、查看与删除。
- 外部签字：MD、LEGAL、SEC、TECH。

### QUE-002：本地任务描述、最小引用与 Context 重建

- 状态：`FROZEN`
- 选择：Queue 在本地加密保存 Task/Operation、Skill/Schema/Policy 版本、目的、Provider/地域、Consent 版本、来源 Event Revision 与完成任务所需的最小字段引用；文件只保存本地引用与本地内容哈希。
- 发送合同：实际发送前按当前版本重建 Minimal Context Capsule，并比较来源 Revision、内容哈希、允许字段和目的；发生实质变化时展示差异并重新确认，不静默发送旧 Capsule，也不静默读取最新完整 Episode。
- 禁止：Queue 不保存 BYOK Key，不在 Gateway 或计量后台保存 Prompt、Response、文件副本、Capsule 正文或健康内容指纹；本地文件哈希不得作为服务端幂等键或遥测字段。
- 外部签字：LEGAL、SEC、TECH。

### QUE-003：网络恢复、文件例外与原 Provider 绑定

- 状态：`FROZEN`
- 选择：非文件、非 Safety 任务只有在用户预先明确开启“联网后处理”，且 Context、Consent、Provider/Model、地域和条款均未变化时，才可对原 Provider 进行有限自动重试。
- 文件红线：报告、照片、音频及其他文件每次发送均须前台重新确认文件、目的、Provider 与数据路径；不得后台静默上传、自动重试或自动切换 Provider。
- Provider 变更：用户可主动选择其他已准入 Provider，但必须创建新 Attempt、重新展示数据路径并按 CONSENT-002 重新确认；不得把 Provider 更换伪装成原 Attempt 的内部路由。
- 外部签字：LEGAL、SEC、TECH、QA。

### QUE-004：容量、TTL、取消与只可收紧的配置

- 状态：`FROZEN`
- 选择：每个安装最多 20 个活动 Pending 项，其中最多 3 个文件项；非文件默认 7 天、文件默认 72 小时到期。用户可随时取消；取消或到期立即停止自动重试，并清除 Queue Capsule、临时产物和派生状态，但不删除用户已明确保存的本地原始记录/原件。
- 配置治理：远程或版本化运营配置只能把活动数、文件数、TTL、重试次数和并发上限调得更保守，或关闭能力/Kill Switch；不得远程放宽 Context、延长保留、开启 Safety 排队、文件后台发送、自动 Fallback、BYOK Gateway 路径或降低确认等级。任何放宽必须形成新版本决定并重新签字/同意。
- 状态义务：`pending`、`awaiting_user`、`retry_scheduled`、`in_flight`、`cancelled`、`expired`、`failed`、`outcome_unknown`、`completed` 等状态须在正式状态机中版本化；未知结果不得显示为成功。
- 外部签字：LEGAL、SEC、TECH、QA。

### CONSENT-002：Queue Consent 的绑定、失效与撤回

- 状态：`FROZEN`
- 选择：Consent 绑定目的、数据类别、Provider 法律实体/精确模型、地域、保留/训练条款及政策/同意版本；文件每次发送确认。
- 失效条件：Provider、Model、地域、用途、数据类别、保留/训练条款或内容发生实质变化，Consent 到期或用户撤回时，相关授权立即失效；系统取消 Pending/Retry、擦除 Capsule 并禁止迟到结果提交。
- 现实边界：若请求已送达 Provider，应诚实披露本机无法召回已送达部分，并按 Provider 合同和适用权利流程处理；不得虚构“取消即代表第三方从未接收或已删除”。
- 外部签字：LEGAL、SEC。

### GWY-001：无状态流式 Gateway 与无正文错误合同

- 状态：`FROZEN`
- 选择：官方 Gateway 只使用有界内存进行无状态流式转发，禁用正文磁盘缓冲、持久消息队列、正文缓存、Core Dump、正文 Trace 和原始错误体日志；只返回版本化、无正文的稳定错误码。
- 全链路义务：Gateway、Reverse Proxy、WAF、APM、Crash、审计与支持工具执行同一字段白名单；Provider 原始 `error body` 在可能回显 Prompt、Response、文件名或健康字段时必须在内存映射后丢弃。
- BYOK 边界：BYOK 继续由设备直连 Provider；Adapter 只在设备内把 Provider 错误映射到同一错误分类，不经过 Gateway、不进入官方计量，也不上传 Key 或正文。
- 外部签字：LEGAL、SEC、TECH、QA。

### RETRY-001：同 Provider 瞬时错误的有限重试

- 状态：`FROZEN`
- 选择：只有 `offline`、`timeout`、`rate_limited`、`provider_unavailable` 等已分类瞬时错误可对同一 Provider 自动重试最多 2 次，复用 `operation_id` 并使用带抖动的退避。
- 禁止自动重试：文件、鉴权、余额、Schema、Policy、Consent、内容变化和 `outcome_unknown` 均转为用户可见状态；不得无限重试或跨 Provider 重试。
- 不确定结果：Provider 不支持幂等或状态查询、且已无法判断是否接收/完成时，进入 `outcome_unknown` 而不是盲目重发。每个 Adapter 必须声明幂等、取消和结果查询能力。
- 外部签字：SEC、TECH、QA。

### RES-001：Partial Stream、取消与结果接纳

- 状态：`FROZEN`
- 选择：Partial Stream 可在当前界面临时展示，但必须标记“未完成/未验证”，不得形成持久化 Command、Event、健康事实或业务成功 Receipt，也不得进入日志/遥测正文。
- 完整结果门槛：只有完整结果通过 Result Normalizer、Schema、Policy、Consent 与 `expected_revision` 复核后，才可提交 Typed Command；Provider 成功不等于本地持久化成功。
- 取消与迟到：用户取消后的迟到结果一律不得提交 Command；`outcome_unknown` 不得假装成功。临时展示在离开流程或过期后清除，除非用户另行明确保存其原始输入。
- 外部签字：MD、SEC、TECH、QA。

### MTR-001：官方额度的预占、一次结算与释放

- 状态：`FROZEN`
- 选择：官方 AI 请求派发前按 `operation_id` 预占额度；只有完整响应通过 Schema/Policy 并成功交付后才结算一次。Provider 接收前失败、Partial Stream、重复回调、取消及未完成结果释放预占，不重复扣用户额度。
- 账本边界：Provider 内部成本与用户额度分账核算；计量后台只保存不可反推健康内容的 Operation/Attempt、Provider/Model、权益、Token/费用、状态、时间和幂等元数据，不保存 Episode/Subject ID、正文 Hash、Skill 健康标签或 Context。BYOK 官方计量恒为零。
- 用户可见性：发送前展示可理解的额度预估，完成后展示最终用量、结算或释放状态；失败和争议处理规则进入中国大陆购买/权益条款。
- 外部签字：LEGAL、SEC、TECH、QA。

### IDEMP-001：Operation、Attempt、Command 与 Receipt 的端到端幂等

- 状态：`FROZEN`
- 选择：一次用户意图生成稳定 `operation_id`；每次 Provider 网络尝试生成 `attempt_id`；重试复用 `operation_id` 和 Provider 支持的幂等键；持久化结果使用确定性 `command_id` 并受本地唯一约束。
- 严格一次业务效果：同一 Operation 可有多个 Attempt，但最多产生一次有效 Command 提交、一次关联 Event 集、一个主 Receipt 和一次用户额度结算。Queue/Attempt 状态或 Provider 成功不得伪装成 Action Receipt。
- 响应丢失：若本地 Command 已提交但响应丢失，按 `command_id` 查询并返回原 Event/Receipt；未提交时重新执行全部 Schema/Policy/Revision 校验；未知状态不得假装成功或盲目创建第二个 Command。
- 服务端最小化：Gateway/计量不得使用正文、Episode ID、文件哈希或健康标签生成幂等键；仅使用随机、不透明标识和必要的有期限去重元数据。
- 外部签字：SEC、TECH、QA。

## 10. 第 8 轮已冻结决定

### A11Y-001：双端统一无障碍基线

- 状态：`FROZEN`
- 选择：iOS/Android 使用同一 WCAG 2.2 AA 等效移动端基线，同时遵循各平台原生无障碍规范，并完成中国大陆公开发布专项核对。
- 双端合同：相同用户旅程、信息语义、风险等级和验收门槛必须一致；VoiceOver/TalkBack、Dynamic Type/字体缩放、原生语义与焦点实现差异收敛在 Flutter/平台 Adapter 和原生组件层，不形成第二套功能范围。
- 发布门槛：无障碍不是可选设置或上线后优化；适用于 BND-004 纳入 V1 的全部 P0 用户旅程。
- 外部签字：LEGAL、TECH、QA。

### A11Y-002：P0 读屏、最大字号与操作覆盖

- 状态：`FROZEN`
- 选择：100% P0 流程支持 VoiceOver/TalkBack、平台最大无障碍字号且至少 200% 字体缩放、非手势操作替代和平台最小触控目标。
- 布局合同：允许内容重排、换行和滚动；Risk 标题、发生了什么、下一步、确认、撤销、删除、就医与紧急操作不得截断、互相覆盖、离屏不可达或功能丢失。相机拖拽、星星、角色、图表等手势/视觉入口必须有等价语义操作。
- P0 清单至少覆盖：Onboarding、创建/切换 Episode、健康记录、报告、Planner、Risk、Receipt/Undo、AI 同意/失败、Archive、永久删除、权限拒绝和 Widget 设置。
- 外部签字：MD、TECH、QA。

### A11Y-003：Safety 非颜色表达与 Reduce Motion

- 状态：`FROZEN`
- 选择：Safety/危机同时使用明确文字、非装饰图标、合格对比度、正确的 accessibility Role/Label/State 和可操作下一步；颜色、声音与触觉只作辅助，不能单独承载等级或行动语义。
- 读屏合同：按“严重性 → 发生了什么 → 现在做什么 → 可用操作”的稳定顺序朗读，不循环播报或用恐慌化语气；R0 不朗读为健康保证。
- 动效合同：Reduce Motion 移除漂浮、呼吸、视差、闪烁、粒子和非必要缩放/Shared Element；不得移除 Risk、错误、确认、进度或状态语义。Baby/YunMom 人格和装饰天气不得承担负面风险表达。
- 外部签字：MD、QA、ETHICS；对比度与平台实现另需 TECH。

### WGT-001：默认关闭、逐字段授权与禁止字段

- 状态：`FROZEN`
- 选择：V1 Widget 默认不添加、不启用；用户主动开启并逐字段选择后才显示。Widget 授权与通知授权互相独立，关闭任一项不影响主 App 本地功能。
- 敏感性：孕周/预产期也按生殖健康敏感个人信息处理，不默认展示。仅允许版本化白名单内、由用户明确选择的低风险字段或通用内容。
- 永久禁止：Risk/“无风险”结论、报告、药物、心情、日记、AI 对话、医院/医生和 Gentle Closure 详情不得进入 Widget，即使用户希望开启也不突破 V1 白名单。
- 外部签字：LEGAL、MD、SEC。

### WGT-002：只读 WidgetProjection 与非 Safety 渠道

- 状态：`FROZEN`
- 选择：主 App 从 Pregnancy Event Store 生成最小、只读的 `WidgetProjection`；Widget 不是事实源，也不能直接读取/修改业务实体表。
- 交互边界：Widget 交互只允许深链回已解锁的主 App；不得在 Widget 内完成任务、修改健康记录、关闭风险、执行 Typed Command 或生成 Receipt。深链到达后仍执行完整认证、Policy、Revision 与确认。
- 医疗边界：Widget 不是 Safety、紧急通知或持续监护渠道，不显示“当前安全/无风险”，不从 Gateway 获取健康状态；活动风险只在主 App 的受控界面和用户授权的低敏通知中处理。
- 外部签字：MD、SEC、TECH、QA。

### WGT-003：最小加密共享容器与扩展专用密钥

- 状态：`FROZEN`
- 选择：`WidgetProjection` 仅包含实际展示所需最小字段，存入受平台保护且应用层加密的共享容器，并使用扩展专用密钥；不得复用安装 KEK 作为内容密钥。
- 排除：共享容器不保存 Event、报告、对话、附件、完整 Task、安装 KEK 或其他健康正文；明确排除系统备份、搜索索引、遥测、日志、Crash 和诊断包。深链参数只使用不透明、短期标识，不携带健康正文。
- 平台义务：App Group/Extension、Android Widget Storage、文件保护、密钥可用性和备份规则由平台 Adapter 实现，但遵守同一字段白名单、失败关闭和删除合同。
- 外部签字：SEC、TECH、QA。

### WGT-004：硬过期、授权撤回与删除级联

- 状态：`FROZEN`
- 选择：`WidgetProjection` 携带 Schema、Policy、Episode、Authorization 版本与 `expires_at`；硬过期最长 24 小时，配置只能缩短。过期或版本不匹配时显示通用占位，不显示最后已知健康状态。
- 立即清理触发：关闭 Widget、撤回字段、切换/Archive/Delete Episode、Gentle Closure 或删除全部数据时，主 App 必须清除 Projection、共享容器、可控缓存/预览和扩展密钥，并主动触发平台刷新；永久删除把 Widget 位置纳入 DEL-002/003 残留扫描。
- 平台现实边界：对操作系统已截图、系统级备份历史或第三方截屏中无法由 App 技术保证远程抹除的副本，应通过默认关闭、低风险白名单、最短暴露和用户披露降低风险；不得把“已请求刷新”虚构成所有外部截图均已删除。
- 敏感结局：Gentle Closure 后不得继续显示孕周倒计时、成长文案、Baby 进度或旧健康内容。
- 外部签字：LEGAL、SEC、TECH、QA、ETHICS。

### TOK-001：机器可读语义 Token 唯一事实源

- 状态：`FROZEN`
- 选择：版本化、机器可读的语义 Design Token 仓库是唯一事实源，由生成器输出 Flutter Theme、Rive 参数、iOS Widget 与 Android Widget 映射。
- 禁止：生产代码不得散落未经审批的原始颜色、字号、间距、圆角、层级或动效时长；设计稿、Flutter 常量、原生 Widget 和 Rive 文件不得各自成为独立 Token 权威。
- 平台差异：平台原生可访问性、触控和控件差异必须通过显式语义映射表达，不复制或改写 Token 业务含义。
- 外部签字：TECH、QA。

### TOK-002：完整 Token 范围与状态优先级

- 状态：`FROZEN`
- 选择：Token 覆盖颜色、字体、间距、圆角、阴影、透明度、图标、触控、层级、Motion、Ambient、Safety/Crisis、Focus、Disabled 和高对比。
- 固定优先级：系统无障碍与可读性约束始终生效；内容状态按 `Medical Safety/Crisis > 错误/权限/破坏性确认 > 临时交互 > Silent Day/Mood > Task > 时间/天气 Ambient` 分层组合。低层装饰不得覆盖高层文字、焦点、对比、操作或确认。
- 医疗边界：Token 只表达 Rule Pack 已确定的风险语义，不决定、推断、升级或解除医学严重性；主题、品牌色、人格、天气和暗色模式不得弱化 Safety。
- 外部签字：MD、TECH、QA。

### TOK-003：SemVer、联合审批与状态矩阵回归

- 状态：`FROZEN`
- 选择：Design Token、状态优先级和生成器使用 Semantic Version；设计、双端工程和 QA 联合审批，Safety/无障碍相关变化另需 MD。
- 版本规则：Patch 只修正不改变语义的缺陷，Minor 只增加向后兼容 Token，Major 才能改变既有语义、生成接口或状态优先级；Breaking Change 必须走书面变更单并重新生成/验收双端与 Widget。
- 回归合同：每个受支持状态组合运行固定 Golden、对比度、读屏、焦点顺序、最大字号和 Reduce Motion 回归；Golden 的动态装饰区可使用受审 Mask，但 Risk、文字、焦点、Receipt、导航和确认区不得被 Mask 隐藏。
- 外部签字：MD、TECH、QA。

## 11. 第 9 轮已冻结决定

### TOP-001：中国大陆单主区域、双 AZ Active-Active

- 状态：`FROZEN`
- 选择：中国大陆一个主云区域、至少两个可用区 Active-Active；Gateway 无状态跨 AZ，身份/权益/计量元数据库跨 AZ 高可用并执行加密备份。
- 数据边界：健康正文、Prompt、Response、文件、Episode、Context Capsule 和完整健康任务不进入后台数据库、备份或消息系统；AZ 故障不得影响 App 的本地 Event Store、查看、Planner、Archive 或 Safety。
- 架构义务：生产拓扑、网络区、WAF/入口、数据库/KMS、故障域、容量与依赖必须由 IaC 表达并接受双 AZ 故障演练；扩展到第二云区域属于书面变更，不由“高可用”自动推导。
- 外部签字：SEC、TECH、QA；中国大陆地域和分包商另需 LEGAL。

### SAFEOPS-001：本地核心与 Safety 的独立降级

- 状态：`FROZEN`
- 选择：本地记录、Event Store、查看、Planner、Archive 与本地确定性 Safety 不依赖网络、登录、权益、Gateway 或 Provider。官方 AI 故障明确进入 Failed/Pending；BYOK 仍设备直连；Provider 故障不得自动切换。
- 工程 SLO：在已支持输入和参考设备上，签名有效 Rule Pack 的执行成功率目标 `≥99.99%`、p99 `≤1 秒`；MD 标记的关键 Golden Set 每次发布 100% 通过。该成功率只衡量规则引擎可执行性，不替代由 MD 签字的临床敏感度、特异度或适用范围。
- Fail-safe：规则签名失败、损坏、过期、版本不兼容或输入超范围时不得输出“安全/未发现风险”，只能回退到最后一个 MD 批准且仍有效的 Last-Known-Good Rule Pack，或显示保守转介与地区紧急资源。
- 外部签字：MD、SEC、TECH、QA。

### SLO-001：Gateway、客户端、RTO 与 RPO

- 状态：`FROZEN`
- 选择：Gateway 月可用性 `≥99.9%`，Gateway 自身附加延迟 p95 `≤300 ms`；Android/iOS 分别达到 Crash-free Sessions `≥99.5%`；云端 RTO `≤30 分钟`；身份/权益/计量元数据 RPO `≤15 分钟`。
- 边界：Provider 可用性、首 Token/完整响应延迟和失败率单独披露，不冒充 Gateway SLO；服务端健康正文 RPO 为“不适用”，因为 YunMom 不保存健康正文数据库。客户端和本地 Safety 使用各自指标，不被云 SLO 吞并。
- 测量义务：正式 SLI 必须定义有效请求、客户端取消、Provider 下游错误、维护窗口、时区、采样和误差预算；不能用平均值替代已冻结的 percentile/可用性指标。
- 外部签字：TECH、QA；用户承诺与赔付/权益文案另需 LEGAL。

### LOG-001：无正文日志、访问审计与计量留存

- 状态：`FROZEN`
- 选择：无正文技术/运行日志默认保留 30 天；生产访问与安全审计默认保留 180 天；计量/财务账本按中国大陆适用法定及争议周期单独保存并假名化。三类数据分表、分权、分别设定删除与 Legal Hold。
- 绝对禁止：任何期限均不得保存 Prompt、Response、图片、OCR、健康字段、Key、敏感 Header/Query、原始 Provider Error Body 或可反推 Episode 的标签。
- 治理：最终期限、法定义务、争议期与例外由 LEGAL/SEC 形成 Retention Schedule；延长必须有书面目的、最小字段和到期日，不得把安全调查当作无限期保留理由。
- 外部签字：LEGAL、SEC。

### OBS-001：全链路字段白名单与用户主动诊断包

- 状态：`FROZEN`
- 选择：客户端、Gateway、Proxy、WAF、APM 和 Crash 共用版本化 Telemetry Schema/字段白名单；未知字段默认丢弃。
- 禁止：Body、敏感 Header、Query、文件名、OCR、健康字段、Stack Locals、截图/录屏、Session Replay 和可推断健康行为的事件名不得采集；不得“先全量采集、后台再脱敏”。
- 诊断：客户端诊断包由用户主动生成并查看/确认后发送，只含完成支持所需的最小脱敏证据；自动测试、网络代理和 Schema Gate 阻止越界字段进入任何环境。
- 外部签字：LEGAL、SEC、TECH、QA。

### IAM-001：环境、KMS/HSM 与 JIT 生产访问

- 状态：`FROZEN`
- 选择：Dev/Staging/Prod 使用独立云账号/项目、网络、数据库、KMS/HSM Key、Provider 凭据和域名；生产密钥不可导出。非生产环境禁止复制真实生产正文，测试使用合成或批准的不可逆脱敏 Fixture。
- 人员访问：默认无生产权限；只有经审批的 JIT、限时、最小权限会话或双人 Break-glass 才能访问生产，并记录 Actor、目的、Ticket、命令/资源、开始/结束与复核。不得保存长期管理员凭据或本地 `.env` 生产密钥。
- 分权：发布、密钥、数据库、财务、日志和 Provider 配置采用职责分离；紧急止血可先执行，但须在规定时限内补齐复核，不得借 Break-glass 绕过审计。
- 外部签字：SEC、TECH、QA。

### SUP-001：签名供应链、SBOM 与构建 Provenance

- 状态：`FROZEN`
- 选择：移动制品、Gateway 容器、Rule Pack、Provider Allowlist、远程配置和 Token Bundle 均签名并在使用前验证来源；每个发布生成 SBOM、锁定依赖、记录可重现构建 Provenance，并扫描源码、依赖、镜像和泄露密钥。
- 发布门禁：Critical 漏洞、签名失败、来源不明制品、未批准第三方 SDK 或无法追溯的构建阻断发布；High 风险是否允许例外受最终第 10 轮缺陷/豁免合同约束。
- 可追溯性：每个线上版本必须关联源码提交、依赖锁、构建环境、签名身份、测试结果、审批和回滚目标；商店/仓库默认签名不替代 YunMom 自身供应链证据。
- 外部签字：SEC、TECH、QA；第三方 SDK/Provider 变化另需 LEGAL。

### REL-001：Canary、分阶段发布、熔断与分层 Kill Switch

- 状态：`FROZEN`
- 选择：Gateway 使用 Canary，Android/iOS 使用商店分阶段发布并支持快速回滚。签名 Kill Switch 至少分 Provider/Model、区域 Egress、Skill/Version、文件上传和 Rule Pack。
- 熔断门槛：5 分钟窗口内已分类错误/超时 `≥20%` 且样本 `≥20` 时自动熔断；确认存在系统性危险输出时可立即人工熔断，无需等待比例。Gateway 新请求目标 `≤1 分钟` 阻断，已联网客户端 p95 `≤5 分钟` 生效。
- Safety 红线：Provider/Skill 可关闭且不得自动 Fallback；本地 Safety 不得整体关闭，只能回滚至最后一个 MD 批准的 Last-Known-Good Rule Pack。未签名、损坏或过期 Rule Pack 必须 Fail-safe。
- 权限：值班人员可先止血；重新启用需要双人控制，并完成 MD/SEC/QA 对相应范围的复核。远程配置不能扩大已冻结的 Context、Provider、文件重试或授权边界。
- 外部签字：MD、SEC、TECH、QA。

### INC-001：隐私/安全与医疗安全双事故通道

- 状态：`FROZEN`
- 选择：建立可同时开启的隐私/安全事故与医疗安全事故双通道，共享 Incident Commander，但分别执行证据保全、严重度评估、法律/临床升级、Kill Switch 和通知决定。
- 无正文证据：默认只含构建/OS、Rule/Skill/Provider/Policy/Consent 版本、签名校验、Feature Flag、Request/Idempotency ID、时间、状态转换、规范错误码和影响数量；事故本身不授权自动上传 Prompt、Response、报告或健康字段。
- 用户通知：外层使用低敏提示，解锁后说明已知/未知、受影响版本/时间/能力或数据类别、已采取措施、用户现在该做什么和后续更新。可能影响既往建议的医疗 P0，目标在 4 小时内向可识别的受影响客户端提供安全更正，不等待完整 RCA；法定时限以 LEGAL 签字为准。
- 隐私保护：命中受影响设备应优先依赖 App/Rule/Skill/配置版本，不得为了定向通知反向建立服务器健康画像。危机与 Gentle Closure 使用预审模板。
- 外部签字：MD、LEGAL、SEC、TECH、QA、ETHICS。

### OPS-001：7×24 值班、量化响应与演练

- 状态：`FROZEN`
- 选择：P0/P1 技术与安全 7×24 值班，医疗安全有明确升级联系人。P0：15 分钟确认、30 分钟指定 Incident Commander、60 分钟完成首轮隔离/熔断、2 小时完成 MD+LEGAL+SEC 初评、4 小时决定并准备用户通知；P1：1 小时确认、4 小时缓解。
- 演练与改进：季度桌面演练，半年执行多 AZ、恢复和 Kill Switch 实操；P0 RCA 在 5 个工作日、CAPA 在 10 个工作日完成。演练仅使用合成数据，不得使用真实健康正文。
- 发布条件：无法提供 7×24 P0 响应时，只能保持封闭测试，不得进行 BND-001 的公开商店发布。内部目标不得延迟法定报告、用户通知或临床止血。
- 外部签字：MD、LEGAL、SEC、TECH、QA；敏感通知模板另需 ETHICS。

## 12. 第 10 轮已冻结决定

### SCP-001：Phase 1–6 签名 Scope/Allowlist

- 状态：`FROZEN`
- 选择：把 BND-004 的 Phase 1–6 全闭环逐项展开为版本化、签名的 Scope/Allowlist，至少列功能、Skill、Rule Pack、Provider/Model、Field、Widget、导出/Archive 与平台状态，并绑定发布证据。
- 状态枚举：`required_enabled`、`required_present_disabled`、`future_explicitly_excluded`。Phase 1–6 的 Required 项未实现、未通过门禁或未签字即阻断 V1，不能静默删减；`required_present_disabled` 不计为已交付，除非仅是经过签字的安全 Kill Switch 状态。Future/Optional 能力只有明确列入才属于 V1。
- 治理：Allowlist 必须绑定源码 Tag、Build Hash、Feature Flag、Rule/Skill/Provider/Schema 版本和 Owner；口头指示、演示中临时出现或基线中的未来描述不能改变合同范围。
- 外部签字：PO、TECH、QA；医疗/Provider/数据路径项另需 MD、LEGAL、SEC。

### MAT-001：分阶段资源计划与公开发布前真机矩阵

- 状态：`FROZEN_AFTER_CONFIRMATION`
- 当前阶段：允许先使用用户现有的一台电脑和一台 Android 手机完成架构、Android 首实现、单元/集成、静态分析、模拟器和首轮真机验证；这符合 BND-003 的 Android 首个实现/测试基准。
- 已确认修正：多机及 iOS 真机测试可以延至内测阶段，但必须在公开商店 V1 Go/No-Go 前完成。不得保留“iOS 真机在公开发布后补测”的原选择。
- 最终矩阵：签字前把支持窗口展开为具体 iOS/Android 版本、Android 最低 API、具名设备、内存/存储、刷新率和 Build；每端至少一台上档机和一台最低支持档真机，并覆盖干净安装、升级、最大字号、读屏、Reduce Motion、深浅色、弱网/离线、通知、Widget、安全区与系统备份。远程 Device Lab 可补充覆盖，但不能完全替代关键安全/删除/无障碍的受控真机证据。
- 状态边界：在矩阵未完成前，可以继续开发和内测，但状态必须保持 `RELEASE_NOT_APPROVED`。
- 外部签字：TECH、QA；iOS/Android 安全与备份专项另需 SEC。

### EXIT-001：缺陷出口与专业域不可单独豁免

- 状态：`FROZEN`
- 发布出口：开放 P0/P1 为 0；医疗安全、隐私/未授权出站、数据丢失或错 Episode、迁移/Archive、永久删除、密钥/鉴权/签名/Kill Switch 和关键无障碍 P2 为 0。
- 有限豁免：其他普通 P2 最多 5 个，且逐项具备域 Owner、影响范围、补偿措施、回归计划和不超过 30 天的到期日，不得跨 Major 版本继承；P3 进入具名 Backlog。
- 不可豁免：PO 无权单独豁免任何可能弱化 R2/R3/危机/药物边界、解除真实风险、造成未授权出站/正文日志/删除残留、开放 Critical/High、安全签名或 Key 失败、错误 Episode 写入/健康数据损坏、或阻断关键 Safety/同意/删除流程无障碍的缺陷。相应专业域 No-Go 即整体 No-Go。
- 外部签字：PO、TECH、QA、MD、LEGAL、SEC、ETHICS。

### ACCD-001：Event、迁移、幂等与 Archive 正确性

- 状态：`FROZEN`
- 门槛：所有受支持 Event/Payload/Command/Field/Receipt/Archive 版本的固定 Fixture/Golden 100% 通过；同一 Event 流在 Android/iOS 产生语义等价 Projection；迁移前后语义等价、可恢复/回滚且跨 Episode/Subject 污染为 0。
- 严格一次：重复、乱序、响应丢失、崩溃和重试最多产生一次有效 Command、关联 Event 集、主 Receipt 和用户额度结算。
- Archive：认证完整性、加密、当前及前两个主要版本导入、跨端往返导出、错误输入与原子失败回滚 100% 通过；任何破坏性迁移、丢失原始证据、无法重建 Projection 或无法回环的 Archive 阻断发布。
- 外部签字：TECH、QA、SEC。

### ACCM-001：Medical Safety、AI 与报告 Golden

- 状态：`FROZEN`
- Corpus：使用 MD 批准、版本化且覆盖 R2/R3、心理危机、药物禁改、低置信医学关键字段、Mood 不覆盖 Safety、`dismiss != resolve`、离线/Provider 全断、Partial Stream、Gentle Closure 与多胎适用范围的 Golden Corpus。
- 安全门槛：所有安全红线/临床关键集 100% 通过；C/D 确认或阻断 100%；未经确认的医学关键字段自动写入为 0。Golden 集零漏项不构成真实世界零误诊、零漏报或医疗保证。
- 解析质量：非关键报告字段精确匹配率 `≥95%`；医学关键字段由 MD 逐字段定义样本、标准、阈值与低置信确认策略。指标必须冻结规范化、分母、置信区间和失败分类，不能用整体平均掩盖关键字段。
- 回归触发：Rule、Model、Provider、Skill、Prompt、Schema、Policy、受控文案或译文变化均运行受影响范围的全量 Golden；医疗红线变化必须重新取得 MD 签字。
- 外部签字：MD、QA、LEGAL；安全执行链另需 SEC。

### ACCS-001：隐私、安全、删除与独立渗透出口

- 状态：`FROZEN`
- 零容忍指标：客户端/Gateway/Proxy/WAF/APM/Crash/Provider Adapter 正文或 Key 泄漏为 0；无同意、撤回后或数据路径实质变化未重新确认的出站为 0；BYOK 经 Gateway、Safety/危机进入 Pending Queue、静默文件上传、静默 Fallback、未签名 Rule 接受、鉴权绕过和 Kill Switch 后新请求均为 0。
- 删除验收：永久删除自动化路径 100% 通过，并在 iOS/Android 真机取证复核 DB/WAL/SHM、Attachment、Thumbnail、Cache、OCR/Temp、Index/Vector、Projection、Widget/App Group、Pending Queue、通知和 Key 的不可访问/失效；不虚构移动闪存逐比特覆盖。
- 渗透门槛：公开发布前完成独立专业渗透测试与复测；开放 Critical 为 0、High 为 0，Medium 必须有书面整改计划、Owner、补偿控制和期限。仅内部代码审查不能替代运行时、移动端与云端渗透证据。
- 外部签字：LEGAL、SEC、QA；删除实现与修复另需 TECH。

### ACCU-001：无障碍、Widget 与视觉验收

- 状态：`FROZEN`
- 无障碍：iOS/Android/Widget 的 100% P0 流程通过 VoiceOver/TalkBack、平台最大字号且至少 200%、对比度、色觉差异、Reduce Motion、焦点和非手势操作；Safety、Consent、删除与 Gentle Closure 关键流程 100% 可完成。
- 视觉：固定设备关键内容区为 0 缺字/遮挡/错层，Golden 感知相似度 `≥0.99`。动态粒子区可使用受审 Mask，但 Risk、Receipt、文字、焦点、导航、确认和 Widget 隐私区不得 Mask；相似度算法、基线版本、分辨率与容差必须写入测试附件。
- 双端义务：Android 验收不替代 iOS；每个平台和 Widget 分别提交可追溯报告，并绑定 MAT-001 的具名设备与最终 Build。
- 外部签字：MD、TECH、QA、ETHICS；Widget 隐私另需 LEGAL、SEC。

### ACCP-001：性能、稳定性与离线验收

- 状态：`FROZEN`
- 上档设备：60 Hz 参考机帧时长 p95 `≤16.7 ms`，`>33.3 ms` 严重卡顿帧 `≤1%`。
- 最低支持档：帧时长 p95 `≤33.3 ms`，`>33.3 ms` 帧 `≤5%`。双端冷启动 p95 `≤3 秒`，Android/iOS 分别达到 Crash-free Sessions `≥99.5%`；飞行模式 P0 本地清单 100% 通过。
- 测量合同：指标绑定 MAT-001 的具名设备、OS、刷新率、Release Build、数据集、采样窗口、冷热状态与测量脚本。若真实原型需要调整，只能在代码冻结前由 TECH/QA 书面变更；不得在验收失败后单方放宽。
- 外部签字：TECH、QA。

### CHG-001：书面变更、重新签字与限时豁免

- 状态：`FROZEN`
- 必须变更：新增法域/未成年人/平台、远程家庭共享、健康云存储/同步、Provider 法律实体/地域/保留训练/分包商、数据类别/Context、第三方 SDK/广告/遥测、备份/删除/导出、Breaking Schema/Token、医疗人群/阈值/时间窗、Rule/Model/Skill/Prompt/译文、危机/Gentle Closure/事故文案或降低安全/无障碍门槛，均须书面变更并重新取得对应专业签字。
- 主动复审：Rule Pack 至少每 6 个月由 MD 复审；法律/隐私意见和独立渗透至少每年复审，或在法规、商店规则、重大事故/证据或架构变化时提前复审。Owner 可设更短周期，过期不得静默继续。
- 豁免：有效豁免必须列风险、Owner、影响范围、补偿措施、监控、回归计划和不超过 30 天的到期日，不跨 Major 继承；到期自动恢复为发布阻塞。PO 可共同接受普通风险，但不能覆盖专业域 No-Go。
- 外部签字：PO、TECH、QA、MD、LEGAL、SEC、ETHICS。

### SIGN-001：同一构建的七方 Go/No-Go 与证据包

- 状态：`FROZEN`
- 选择：PO、TECH、QA、MD、LEGAL、SEC、ETHICS 对同一源码 Tag/Build Hash，以及同一 Rule/Skill/Policy/Consent/Provider/Token/Schema 清单共同签署最终 Readback；任一专业域 No-Go 即整体 No-Go。
- 证据包：至少包含 Scope 四列表、R1–R10 决策、OS/设备矩阵、需求追踪、全部 Golden、迁移/Archive、删除取证/抓包、独立渗透复测、SBOM/签名/Provenance、SLO/恢复/演练、开放缺陷/豁免、回滚/Kill Switch，以及应用市场、法律、隐私和临床意见。
- 状态语义：缺签、证据漂移到不同 Build、无 Owner 未决项或 MAT-001 矩阵未完成时，只能标记“产品决策已冻结 / 发布未批准”。灰度、免责声明、内测表现或 PO 单签不能替代专业证据。
- 外部签字：PO、TECH、QA、MD、LEGAL、SEC、ETHICS。

## 13. 组合检查

### 第 1 轮

结论：`NO_CONFLICT`。

“Android 单端先行”与“双端统一合同”不冲突：前者描述实现和测试顺序，后者描述架构、数据和业务合同的最终范围。公开商店 V1、单一中国大陆法域与 Phase 1–6 全闭环也可组合，但会把合规、医学、安全、运维和测试门槛全部提升为首发阻塞项，而不是后续优化项。

### 第 2 轮

结论：`NO_CONFLICT`。

单一 Active Episode 与 `1..N BabySubject` 分别解决“多次妊娠历史”和“一次妊娠内多胎”，语义不冲突。有限生命周期与 Outcome 枚举采用两个正交字段：前者驱动产品状态，后者记录经确认的结局。DadEntry 的同设备形态可承载最小分类权限，也不违反 No Health Data Backend；权限撤销对 App 内未来访问生效，但不能追回已经离开设备的分享副本。

### 第 3 轮

结论：`NO_CONFLICT`。

消费级照料、确定性 Rule Pack、四级风险、逐类启用和禁止诊断/改药形成一致的安全闭环。多胎数据模型与临床适用范围不冲突：YunMom 可以正确存储多胎数据，但只有明确验证为适用于多胎的规则才能给出对应 Safety 结论。报告、药物和心理危机均保持受控边界，没有触发医疗诊断、治疗、LLM 主判或全人群适用的重大监管分支。

### 第 4 轮

结论：`NO_CONFLICT`。

五级数据分级、匿名 Local-first、分层同意、字段级 Context、文件逐次确认、Provider 白名单、禁止自动 Fallback、设备直连 BYOK 与无内容遥测共同强化了既有 No Health Data Backend 和最小出站红线。撤回同意与文件禁止静默重试也保持一致：撤回清除所有待发任务；网络恢复后的文件任务必须由用户重新确认。没有引入健康云档案、完整 Episode 出站、静默跨 Provider、BYOK Key 上传或健康内容训练。

### 第 5 轮

结论：`NO_CONFLICT`。

Event Store 唯一事实源、实体/索引均为 Projection、Command 原子写入、全持久化动作 Receipt 和版本化 Schema Registry 形成单一且可重放的写入闭环，没有引入双事实源、覆盖 Event、服务器生效前提、无 Receipt 或无版本 Schema。Append-only 约束正常业务历史，与永久删除不冲突：后者是用户明确发起、经过独立确认并清除可恢复健康正文的不可逆命令。稳定 Aggregate/Envelope 与纯函数 Upcaster 也满足双端统一合同；Android 仅是首个实现与测试端，不成为私有格式的权威。

### 第 6 轮

结论：`NO_CONFLICT`。

分 Episode 密钥是物理隔离，不改变 EVT-001 的单一逻辑 Event Store；正常历史仍保持不可变，明确永久删除则作为独立隐私 Purge 清除目标 Canonical Event 和全部派生副本。系统自动备份全面排除、Archive 密钥零托管、账号/商业身份不进 Archive 均强化 IDN-001 与 No Health Data Backend。Canonical Event 是导入后的恢复依据，携带的 Projection 只作可验证互操作视图，不形成第二事实源。统一 Archive/Crypto 测试向量和平台 Adapter 分层满足双端统一合同；Android 首验不替代 iOS Keychain、备份、卸载与导入验收。没有选择服务器托管恢复密钥、系统健康云自动备份、仅 Tombstone、闪存覆盖作为唯一删除机制或静默合并/覆盖 Archive。

### 第 7 轮

结论：`NO_CONFLICT`。

Pending Queue 仅是设备本地、用户可见且可取消的非时效任务状态，不成为云端事实源，符合 Local-first 与 No Health Data Backend。Safety/危机永不排队，文件始终前台确认且不自动重试，符合 MED-002、MED-008 与 FILE-001；所有自动重试固定原 Provider，用户主动换 Provider 时重新确认，符合 PROV-002。BYOK 仍设备直连且不进入官方计量，符合 BYOK-001。Partial Stream、取消或 Provider 成功均不能绕过完整结果复核、Typed Command 和 Receipt；分层不透明 ID 使一次用户意图最多产生一次 Event/Receipt/额度结算，强化 CMD-001/RCT-001。没有选择云端健康任务队列、Safety/危机延迟排队、文件静默出站、自动跨 Provider、BYOK 经 Gateway、记录原始错误正文、Partial Stream/取消后写入、重复扣费或无端到端幂等。

### 第 8 轮

结论：`NO_CONFLICT`。

统一无障碍语义和验收门槛延续 BND-003 的双端统一合同，平台差异仍位于 Adapter；Safety 的文字、图标、读屏与行动优先于颜色和装饰动效，强化 MED-002/003/008。WidgetState 明确为 Event Store 生成的最小只读 Projection，不写库、不从 Gateway 拉取健康状态，也不形成第二事实源。默认关闭、逐字段授权、专用加密共享容器、备份排除和 24 小时硬过期符合 DATA-001、BAK-001 与 No Health Data Backend；撤回、Gentle Closure 和永久删除均触发 Widget 级联清理，符合 DEL-002/003。机器可读 Token SSOT 与固定状态优先级保证装饰层不能覆盖 Safety。没有选择两端不同无障碍合同、Safety 仅靠颜色/动画、Widget 默认展示健康详情或直接写库、Gateway 健康状态、明文/可备份共享容器、删除后保留旧 Widget、多个 Token 事实源或装饰覆盖 Safety。

### 第 9 轮

结论：`NO_CONFLICT`。

中国大陆单主区域双 AZ 只承载身份、权益、计量和无正文 Gateway，符合首发单法域与 No Health Data Backend；AZ/Gateway/Provider 故障不影响本地 Event Store、Planner、Archive 或确定性 Safety，强化 Local-first。Provider 故障不自动 Fallback，BYOK 仍设备直连，符合 PROV-001/002、BYOK-001 与 GWY-001。全链路字段白名单、无正文留存、用户主动诊断包和无正文事故证据符合 TEL-001。签名 Rule/配置、Last-Known-Good、分层 Kill Switch 和双事故通道保持临床与安全治理分离但可协同。没有选择单 AZ、后台故障阻止本地/Safety、备用健康云或跨 Provider、无量化 SLO、正文/全量采集、共享生产密钥、长期管理员、未签名 Rule/配置、全量无回滚、关闭本地 Safety、普通 Bug/客服替代事故流程或无 7×24 P0 响应。

### 第 10 轮

结论：`NO_CONFLICT_AFTER_CONFIRMED_AMENDMENT`。

原第 2 项“只用 Android 模拟器和一台开发机验收，iOS 真机在公开发布后补测”与 BND-001/BND-003、ACCD-001、ACCS-001、ACCU-001、ACCP-001 和 SIGN-001 冲突。用户已明确确认修正为：当前利用一台电脑和一台 Android 手机推进；多机与 iOS 真机可延至内测，但必须在公开商店 Go/No-Go 前完成。修正后的 MAT-001 同时尊重当前资源、Android 首行顺序和双端公开验收。

其余九项互相一致：签名 Scope 防止 BND-004 被静默删减；严格缺陷出口、数据/Archive Golden、Medical/AI Golden、零容忍隐私安全性质、无障碍/视觉和性能门槛形成完整证据链；CHG-001 阻止专业红线被 PO 口头豁免；SIGN-001 把全部证据绑定到同一构建。没有开放 P1/高风险 P2、跳过历史迁移、只看整体模型准确率、上线后渗透/删除、无障碍后置、无性能门槛、PO 单独豁免/签字或先上线后补证据。

### R1–R10 最终交叉审计

结论：`PRODUCT_DECISIONS_COHERENT` / `RELEASE_NOT_APPROVED`。

- 事实与写入链：Local-first Event Store → Projection → Typed Command/Policy → Event/Receipt/Provenance → 可重放/可迁移，单一且一致。
- 医疗链：本地签名 Rule Pack 是 Safety 权威；AI 只提取/表达；危机、药物、报告、Partial Stream、Queue、Widget 和 Incident 均不能绕过规则与专业签字。
- 隐私链：健康正文默认本地；出站按目的/字段/Provider 同意；Gateway、日志、遥测、计量和事故证据无正文；BYOK 设备直连；撤回停止未来处理。
- 删除/恢复链：普通历史 Append-only，用户永久删除是独立 Purge；加密、备份排除、Archive、Widget、Queue、索引和残留验证语义一致。
- 双端链：统一 Domain/Schema/Archive/Token/验收合同，Android 先实现；iOS 和完整真机矩阵在公开发布前仍是硬门槛。
- 生产链：单主区域双 AZ、可量化 SLO、供应链签名、Canary/Kill Switch、双事故通道和 7×24 响应只保障云能力，不反向削弱本地 Safety。
- 最终状态：十轮产品选择已经冻结；专业签字、正式附件、实现和证据尚未齐全，不能宣告 Production Ready 或提交公开商店。

## 14. 发布前必须产出的工程与专业附件

- 中国大陆公开发布的法律与产品分类意见、敏感个人信息处理和 AI/Provider 数据路径专项审查。
- Android 最低 API、目标设备矩阵、厂商推送/应用市场矩阵；iOS 后续最低版本与参考设备。
- 30 个 Skill 的首发启用白名单及每个 Skill 的 Manifest、Context、Command、Risk、Confirmation 和测试合同。
- P0 无障碍用户旅程清单、语义/焦点/读屏脚本、平台最大字号设备矩阵、对比度与 Reduce Motion 自动/人工验收规范。
- Widget Field Allowlist、逐字段 Authorization、`WidgetProjection` Schema、Extension/App Group 加密、24 小时硬过期、通用占位与全生命周期清理矩阵。
- 语义 Design Token Schema、生成器、Flutter/Rive/iOS Widget/Android Widget 映射、状态组合矩阵、版本发布与 Golden Corpus。
- `BabySubject` 正式 Schema、多胎报告字段、个体结局状态及 Episode/Subject 级联删除矩阵。
- 中国大陆公开版本对《人工智能拟人化互动服务管理暂行办法》的适用性法律意见。YunMom 具有持续照料、陪伴与人格化表达，可能落入其适用范围；必须由 LEGAL 作正式判断，并落实 AI 身份提示、安全评估、心理健康保护、退出与投诉机制等适用义务。
- Data Registry、Consent Record、Skill Context Manifest、Provider Contract Sheet、Egress Audit 与文件临时数据生命周期的正式 Schema。
- Rule Pack、Golden Set、风险状态机、字段级适用矩阵、Feature Flag 与紧急 Kill Switch 的正式 Schema 和发布流程。
- Event/Payload/Command/Field/Receipt 的正式 Schema Registry、跨端代码生成与 Conformance Fixture；Reducer、Upcaster、Projection 重建、幂等与冲突解决的参考实现和 Golden Corpus。
- Attachment 内容寻址/完整性、加密引用、Event 与文件原子提交或补偿，以及永久删除级联的正式合同。
- 版本化 Crypto Profile：具体 SQLite 加密实现、AEAD/KDF、参数、库版本、随机数、Key Slot、轮换窗口、硬件降级和跨端测试向量。
- Key/Installation/Purge 状态机、逐存储位置删除矩阵、无正文删除结果 Schema、残留扫描工具及故障恢复流程。
- Android/iOS 系统备份排除、共享容器、Keychain/Keystore、卸载重装和恢复缺钥的逐版本真机矩阵。
- Archive Container/Manifest/加密/兼容规范、恶意包资源上限、当前及前两个主要版本 Fixture，以及用户口令/恢复码和外部保存风险文案。
- Pending Queue Schema/状态机、Skill 级 `queueable`/时效分类、Context Revision/Diff、文件引用生命周期、TTL 清理与只能收紧的签名配置。
- Provider Adapter 能力表与统一错误注册表：精确模型、幂等、取消、结果查询、流式、限流、错误映射和 `outcome_unknown` 行为。
- Gateway 无正文运行时基线、Proxy/WAF/APM/Crash 字段白名单、内存/请求体/并发上限及原始错误体清洗测试。
- Operation/Attempt/Command/Receipt/Metering 的正式 Schema、唯一约束、Reservation/Settlement 状态机、对账与争议处理。
- 中国大陆云厂商/主区域/AZ、网络与数据库具体选型，版本化 IaC、容量模型、成本预算、加密备份和双 AZ 故障矩阵。
- 正式 SLI/Error Budget Schema、Gateway/Provider/客户端/Rule Engine 仪表盘、RTO/RPO 恢复 Runbook 与证据。
- Retention Schedule、Telemetry Allowlist/Schema、诊断包 Manifest、环境/IAM/KMS/Break-glass 矩阵与生产访问复核流程。
- SBOM/Provenance/签名体系、第三方 SDK 清单、漏洞门禁、Canary/分阶段发布、熔断/Kill Switch 与 Last-Known-Good Runbook。
- 隐私/安全和医疗安全 Incident Runbook、值班表、严重度矩阵、预审通知模板、演练日历、RCA/CAPA 模板与法定通知清单。
- 签名 Scope/Allowlist 四列表，以及与 Phase 1–6、30 个 Skill、Provider/Model、Rule、Widget、Export/Archive 和平台状态的逐项映射。
- 具体 OS/API 与具名真机矩阵；当前一台电脑和一台 Android 可用于开发/首测，但 iOS 与多机证据必须在公开 Go/No-Go 前补齐。
- Requirements Traceability Matrix、缺陷等级/出口/豁免登记表，以及 ACCD/ACCM/ACCS/ACCU/ACCP 的量化测试计划和结果。
- 绑定同一 Build Hash 的最终证据 Manifest、七方签字页和 Go/No-Go 记录。

## 15. 当前外部规范核对

以下仅登记需要进入合同的当前规范触发点，不替代专业法律意见：

- [《中华人民共和国个人信息保护法》](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm)：医疗健康属于敏感个人信息；敏感个人信息处理具有特定目的、充分必要性、严格保护、单独同意和影响告知等要求。
- [《人工智能拟人化互动服务管理暂行办法》](https://www.cac.gov.cn/2026-04/10/c_1777558395078289.htm)：自 2026-07-15 起施行；YunMom 是否构成持续性拟人化情感互动服务须由中国大陆法律顾问根据最终功能与文案确认。
- [生成式人工智能服务备案信息公告](https://www.cac.gov.cn/2024-04/02/c_1713729983803145.htm)：公开版本使用的生成式人工智能服务及其公示、备案/登记路径需在 Provider 准入轮次逐项核对。
- [国家药监局医疗器械分类服务](https://zwfw.nmpa.gov.cn/web/taskview/11100000MB0341032Y100207202300001)：若产品能力可能进入诊断、治疗或临床决策支持范围，应取得正式产品分类/监管路径意见，不以产品免责声明自行判定。

## 16. 最终 Go/No-Go 发布阻塞矩阵

以下事项在签字完成前均为公开商店 V1 的发布阻塞项；产品选择已冻结不代表专业批准已取得。

当前统一状态：`NO-GO / PENDING EVIDENCE AND SIGNATURES`。

### MD 临床安全签字

- MED-001 的消费级照料/Safety Signposting 边界及产品分类输入。
- MED-003 的 R0–R3 定义、每级临床时间窗、升级/降级/解除条件和允许动作。
- MED-004/005 的每条规则适用孕周、人群、单胎/多胎、排除条件和 Feature Flag。
- MED-006 的医学关键字段清单、低置信确认阈值、报告解释模板。
- MED-007 的药物受控语言、禁止动作和转介条件。
- MED-008 的危机触发、资源、文案和回退。
- MED-009 的 Rule Pack、Golden Set、误报/漏报门槛、复审周期与医疗事故响应。
- CTX-001 中每个医疗 Skill 出站字段的临床必要性，以及报告/药物/Safety 所需最小上下文。
- FLD-002 的规范单位、医学值精度/范围、关键字段与统一 Provenance；CFL-001 中哪些医学冲突禁止自动合并及允许的用户解决方式。
- QUE-001 的不可排队医疗/危机/时效任务白名单、陈旧输入重新确认阈值，以及离线 Safety/“云 AI 尚未进行”文案。
- RES-001 的 Partial Stream 不可作为医疗事实、完整结果接纳门槛和风险相关迟到结果处理。
- A11Y-002/003 的 P0 临床可达性、R0–R3 文字/图标/朗读顺序、行动按钮、最大字号与 Reduce Motion 语义。
- WGT-001/002 的禁止字段、Widget 非 Safety/持续监护渠道；TOK-002/003 的 Safety Token 映射及变更签字。
- SAFEOPS-001 的 Rule Engine 工程 SLO、关键 Golden Set、Fail-safe 文案与 Last-Known-Good 选择/回滚。
- REL-001/INC-001/OPS-001 的危险输出熔断、医疗 P0 定义、既往建议安全更正、临床升级联系人、响应时限与医疗事故演练。
- ACCM-001 的 Clinical Golden Corpus、关键集 100%、报告字段阈值与变更后回归；对最终 Build/Rule/Skill/Prompt/译文清单签字。
- EXIT-001/CHG-001 中所有医学不可豁免项，以及 SIGN-001 最终 Go/No-Go。

### LEGAL 法律/隐私/监管签字

- 中国大陆最终产品分类与医疗器械/健康服务监管路径书面意见。
- 应用市场、营销、免责声明、Safety、报告、药物、紧急行动与危机文案的法律审核。
- 《个人信息保护法》下医疗健康敏感个人信息的目的、必要性、影响告知、单独同意和撤回机制。
- YunMom 对《人工智能拟人化互动服务管理暂行办法》及生成式 AI 备案/登记、公示要求的适用性与落实清单。
- 中国大陆紧急与心理危机资源、用户主动外发就医摘要及第三方数据路径的责任边界。
- DATA-001 的 Data Registry、CONSENT-001/EGRESS-001 的同意与撤回文案、记录和重新同意触发器。
- FILE-001、PROV-001/002、BYOK-001 的数据地域、Provider/分包商合同、保留/训练、删除、备案/登记与公示清单。
- TEL-001 的遥测字段、留存、用户控制以及未来研究/训练的禁止与例外流程。
- DEL-001/002/003 的隐藏、Undo、永久删除、不可撤回确认、完成状态、外部副本/Provider 已接收数据边界和无正文删除结果文案。
- BAK-001 的系统自动备份排除承诺，以及用户主动将加密 Archive 保存至自选云盘、介质或第三方后的责任与风险披露。
- ARC-001/002/003 的导出内容、Conversation 单独选择、口令/恢复码丢失不可找回、旧同意不继承、兼容窗口和导入冲突文案。
- QUE-001 至 QUE-004、CONSENT-002 的延迟处理/自动重试同意、TTL、取消、Context 变化、文件逐次确认、Provider 变化重新同意与已送达第三方边界。
- GWY-001 的官方/BYOK 数据路径、无正文错误披露和第三方原始错误处理；MTR-001 的额度预估、一次结算、失败释放、争议与 BYOK 分账条款。
- A11Y-001 的中国大陆公开发布、应用市场和适用无障碍义务核对。
- WGT-001/004 的孕周等生殖健康字段分类、逐字段授权、锁屏/桌面披露、通知分离、撤回、系统截图现实边界和 Gentle Closure 清除文案。
- TOP-001 的中国大陆云地域、子处理者、跨 AZ/备份路径和监管/合同清单；SLO-001 的用户承诺与权益边界。
- LOG-001/OBS-001 的 Retention Schedule、假名化、Legal Hold、Telemetry 字段、诊断包和生产访问证据处理。
- INC-001/OPS-001 的事故分级、证据保留、Provider 责任、监管/用户通知阈值与法定时限。
- SCP-001 Scope、ACCM-001 医疗/AI 验收声明、ACCS-001 隐私/出站/删除/渗透结果、应用市场材料和最终同一 Build 的产品分类/隐私法律意见。
- EXIT-001/CHG-001 中所有法律/隐私不可豁免项，以及 SIGN-001 最终 Go/No-Go。

### SEC 安全签字

- Rule Pack 的签名、完整性、版本发布、回滚、Kill Switch、最小权限和防篡改审计。
- LLM/Provider 无法越权设置或解除 `risk_state` 的 Policy 与测试证据。
- 医疗安全事件诊断包、日志与排障流程无健康正文泄漏的验证。
- DATA-001 的字段级策略执行与防止高敏字段进入日志/遥测的自动化证据。
- CTX-001/FILE-001 的 Egress Policy、EXIF/临时文件清理、网络抓包与正文零日志验证。
- PROV-001/002 的 Adapter 隔离、Provider 变更、无自动 Fallback、重复计费/重复写入防护。
- BYOK-001 的 Key 安全区、设备直连、零 Gateway 路径与自定义端点关闭验证。
- TEL-001 的第一方字段白名单、SDK/Session Replay 禁用与健康行为不可推断性评审。
- EVT-002 的 Attachment 引用完整性、Event/文件提交失败模型与防孤儿数据控制。
- EVT-004/CMD-001/RCT-001 的事件完整性、Actor/Device 防伪、幂等、防重放、Policy 版本绑定和 Receipt 最小化验证。
- EVT-003/CFL-001/SCH-001 在撤销、冲突、迁移、备份与永久删除中的安全边界。
- KEY-001/002 与 CRYPTO-001 的密钥威胁模型、Secure Storage 属性、精确 Crypto Profile、硬件降级、随机数、轮换和密钥失效验证。
- DEL-001/002/003 的 crypto-shred 能力边界、Purge 权限与幂等、WAL/SHM/空闲页/临时文件清理、残留扫描和无正文审计。
- BAK-001 的备份属性、共享容器、恢复缺钥、卸载残留与备份提取验证。
- ARC-001/002/003 的容器加密、口令暴力防护、恢复码、Manifest、完整性、恶意 Archive、资源耗尽和旧同意失效验证。
- QUE-001 至 QUE-004 的本地加密、文件引用/哈希、TTL 擦除、取消/撤回竞态、Key 引用和只能收紧的签名配置。
- CONSENT-002/GWY-001 的授权失效、BYOK 零 Gateway、全链路正文零落盘、原始错误体清洗、Core Dump/Trace/Proxy/WAF/APM 控制。
- RETRY-001/RES-001/IDEMP-001 的防重放、乱序/迟到结果抑制、不透明 ID、Provider 幂等能力降级和严格一次提交。
- MTR-001 的无正文计量元数据、Reservation/Settlement 防篡改、防重复扣费、留存和最小权限。
- WGT-001 至 WGT-004 的 Field Allowlist、共享容器/扩展专用密钥、深链不透明化、备份/搜索/遥测/日志排除、TTL 与清除证明。
- TOK-001 至 TOK-003 的 Token 供应链完整性、生成器输入验证、Safety 语义不可被未签字资源覆盖和版本回滚。
- TOP-001/IAM-001 的云威胁模型、网络区、KMS/HSM、加密备份、JIT/Break-glass、职责分离和跨 AZ 故障控制。
- LOG-001/OBS-001 的字段白名单、未知丢弃、原始错误体/Stack Locals/Session Replay 禁用与留存删除证明。
- SUP-001/REL-001 的签名、SBOM/Provenance、漏洞门禁、远程配置、熔断/Kill Switch、双人恢复和 LKG 防篡改。
- INC-001/OPS-001 的无正文取证、24×7 安全响应、证据访问、通知通道和演练安全。
- MAT-001 的 Keychain/Keystore/备份/卸载真机矩阵；ACCD-001 的跨端完整性与幂等；ACCS-001 的零容忍验证、删除取证、独立渗透复测和 Critical/High 清零。
- EXIT-001/CHG-001 中所有安全不可豁免项，以及 SIGN-001 最终 Go/No-Go。

### TECH 技术签字

- Event/Payload/Command/Field/Receipt 的规范 Schema Registry、兼容策略、跨端代码生成和唯一版本发布流程。
- EVT-001/003/004 的 Event Store 原子性、稳定排序、不可变约束、确定性 Reducer 与全 Projection 重建能力。
- CMD-001/RCT-001 的事务边界、乐观并发、幂等重试、零部分写入、Receipt/Undo 关联及崩溃恢复。
- EVT-002 的 Attachment 加密引用、内容完整性、孤儿回收与 Event/文件失败补偿。
- CFL-001 的 Conflict Set/Resolution Event 语义；SCH-001 的纯函数 Upcaster、迁移回滚与 Android/iOS/Archive Conformance。
- KEY-001/002 的逻辑 Event Store/物理密钥分区、Key Slot/Installation 状态机与 Android/iOS Secure Storage Adapter。
- CRYPTO-001 的断点轮换、崩溃重入、失败回滚、版本兼容和 Crypto Profile 升级实现。
- DEL-001/002/003 的原子确认、幂等 Purge、级联清理、Projection 重建、残留扫描和不可恢复完成状态机。
- BAK-001 与 ARC-001/002/003 的备份排除、容器/Manifest、跨端字节格式、离线预检、原子导入和当前/前两个主要版本支持。
- QUE-001 至 QUE-004/CONSENT-002 的状态机、崩溃恢复、Context Diff、TTL、取消、输入删除/Key 失效和配置治理实现。
- GWY-001/RETRY-001/RES-001 的无状态流式转发、错误 Registry、Partial Stream、取消、乱序/迟到结果与 `outcome_unknown` 实现。
- MTR-001/IDEMP-001 的 Operation/Attempt/Command 分层、唯一约束、Reservation/Settlement 对账和 Event/Receipt/额度严格一次实现。
- A11Y-001 至 A11Y-003 的双端语义组件、焦点/字体重排、非手势替代和 Reduce Motion 平台 Adapter。
- WGT-001 至 WGT-004 的最小 Projection、逐字段授权、专用密钥、深链、过期占位、主动刷新和删除级联实现。
- TOK-001 至 TOK-003 的机器可读 Schema、代码生成、平台/Rive 映射、状态解析优先级、SemVer 与回滚实现。
- TOP-001/SLO-001 的 IaC、双 AZ、自动扩缩、依赖降级、SLI/Error Budget、备份恢复和容量实现。
- SAFEOPS-001/REL-001 的本地 Rule SLO、签名/LKG、Canary、分阶段发布、熔断、Kill Switch 延迟和重新启用流程。
- IAM-001/SUP-001 的环境隔离、KMS/HSM、JIT、签名、SBOM、可重现构建和制品追溯工具链。
- INC-001/OPS-001 的 Incident 工具、低敏设备通知、升级表、值班和 RCA/CAPA 工作流。
- SCP-001 的技术范围映射、MAT-001 的具体 OS/API/设备表、ACCD-001 数据/迁移/Archive、ACCP-001 性能/稳定性，以及最终 Build、SBOM、IaC、回滚和证据 Manifest。
- EXIT-001/CHG-001 技术风险与限时豁免，以及 SIGN-001 最终 Go/No-Go。

### QA 质量签字

- 固定 Event Replay/Reducer/Projection Golden Corpus，验证不同设备与两端对同一 Event 流产生等价结果。
- Command 重复提交、Revision 冲突、事务中断、磁盘写满、崩溃恢复和附件部分失败的零重复/零部分成功测试。
- A/B/C/D 全矩阵及每个持久化动作的 Receipt、Undo、C 确认、D 拒绝与 Provenance 可追溯测试。
- 单位往返、原始精度、22 类 Field、低置信确认、Conflict Set 和 Resolution Event 的固定 Fixture。
- 当前及历史 Schema、Upcaster、迁移回滚、完整 Projection 重建和跨端 Archive 兼容回归。
- KEY/CRYPTO 的错误口令、缺钥、密钥残留、硬件不可用、轮换各阶段强杀进程、断电模拟、磁盘满和跨端向量验收。
- DEL 的每种 Scope、取消/不可取消边界、失败重入，以及 DB/WAL/SHM、Attachment、RAG/Vector、Widget、通知、Queue 和临时文件零可访问残留验收。
- BAK 的备份提取、系统恢复、升级、卸载重装、Keychain 残留和孤儿清理真机验收。
- ARC 的错误口令/恢复码、篡改/截断/恶意包、重复导入、版本边界、Active Episode 冲突、原子回滚、Consent 重置和 Android/iOS 往返验收。
- Queue 的离线/恢复、进程强杀、容量/TTL、取消/撤回竞态、输入或文件变化、文件禁止自动发送、Provider/Key 失效和配置只能收紧验收。
- Gateway/Provider 的 Timeout/限流/故障、原始错误体、Partial Stream、取消后迟到、重复/乱序回调、`outcome_unknown` 和 BYOK 零 Gateway 验收。
- Metering/Idempotency 的预占释放、对账、响应丢失、重复 Attempt、重复扣费、重复 Event/Receipt 与主 Receipt 唯一性验收。
- A11Y 的 VoiceOver/TalkBack、平台最大字号/至少 200%、小屏/横屏/中文长文、焦点、对比、色觉差异、非手势替代和 Reduce Motion P0 验收。
- Widget 的默认关闭、逐字段授权、锁屏/桌面、离线/陈旧/24 小时过期、重启、撤回、Episode 切换/Archive/Delete、Gentle Closure、系统预览和零可访问残留验收。
- Token 的 Schema/生成器、双端/Rive/Widget 映射、所有受支持状态组合、Golden Mask 边界、对比/读屏/焦点与版本升级/回滚验收。
- TOP/SLO 的单节点/AZ/数据库/网络故障、容量与恢复计时；Android/iOS Crash-free 和 Gateway p95/可用性 SLI 验收。
- SAFEOPS/REL 的全断网、Gateway/Provider 全断、Rule 签名失败/损坏/过期、LKG、熔断阈值、Kill Switch ≤1分钟/客户端p95≤5分钟和重新启用验收。
- LOG/OBS/IAM/SUP 的正文零日志、留存删除、诊断包、JIT/Break-glass、密钥不可导出、环境隔离、SBOM/签名/Provenance 和漏洞门禁验收。
- INC/OPS 的隐私与医疗双通道、值班响应计时、低敏通知、既往建议更正、无正文取证、多 AZ/恢复/Kill Switch 演练和 RCA/CAPA 验收。
- SCP-001 需求追踪、MAT-001 双端具名真机、EXIT-001 开放缺陷、ACCD/ACCM/ACCS/ACCU/ACCP 全部量化报告，以及证据与 Build Hash 一致性。
- CHG-001 回归/豁免到期执行，以及 SIGN-001 最终 Go/No-Go。

### ETHICS 科技伦理签字

- MED-008 心理危机协议及 YunMom 人格在危机时的情感边界。
- EPI-004 Gentle Closure、特殊结局确认和多胎个体结局的克制表达。
- 拟人化互动中的依赖、操控、退出、投诉与脆弱用户保护机制。
- TEL-001 的健康内容不训练承诺及任何未来研究的独立伦理方案。
- A11Y-003 的危机朗读、动效和人格表达不制造恐慌或羞辱。
- WGT-004 在妊娠失去、Gentle Closure 和特殊结局后不残留倒计时、成长文案、Baby 进度或旧健康内容。
- INC-001/OPS-001 的危机、妊娠失去、医疗错误与隐私事故通知模板避免恐吓、弱化或二次伤害，同时不阻止立即止血。
- ACCM-001/ACCU-001 中危机、Gentle Closure、无障碍与人格表达；EXIT-001/CHG-001 的伦理不可豁免项；SIGN-001 最终 Go/No-Go。

### PO 产品签字

- SCP-001 的 Phase 1–6 Scope/Allowlist、明确排除项、预算/资源和交付顺序；不得把 `required_present_disabled` 冒充已交付。
- MAT-001 的阶段计划：当前资源可推进开发，但为内测和公开 Go/No-Go 获取 iOS/多机/专业测试资源。
- EXIT-001 的开放缺陷与普通 P2 限时豁免、CHG-001 的书面变更，以及全部 Release Evidence 与同一 Build 的对应关系。
- 只有 MD、LEGAL、SEC、TECH、QA、ETHICS 均为 Go 时，方可签署 SIGN-001 的 PO Go；PO 签字不能覆盖任何专业 No-Go。

## 17. 变更历史

| 日期 | 轮次 | 记录 |
|---|---|---|
| 2026-08-10 | 1 | 冻结 BND-001 至 BND-004；组合检查无冲突；将“双端统一合同、Android 首个实现与验收基准”作为 BND-003 的规范解释。 |
| 2026-08-10 | 2 | 冻结 EPI-001 至 EPI-004、USR-001、FAM-001 至 FAM-003；组合检查无冲突；登记外部分享不可追回边界。 |
| 2026-08-10 | 3 | 冻结 MED-001 至 MED-009；组合检查无冲突；建立 MD、LEGAL、SEC、ETHICS 发布签字阻塞清单。 |
| 2026-08-11 | 4 | 冻结 DATA-001、IDN-001、CONSENT-001、EGRESS-001、CTX-001、FILE-001、PROV-001/002、BYOK-001、TEL-001；组合检查无冲突；扩展数据、Provider 与遥测签字阻塞项。 |
| 2026-08-11 | 5 | 冻结 EVT-001 至 EVT-004、CMD-001、RCT-001、FLD-001/002、CFL-001、SCH-001；组合检查无冲突；新增 TECH、QA 发布签字阻塞清单。 |
| 2026-08-11 | 6 | 冻结 KEY-001/002、CRYPTO-001、DEL-001 至 DEL-003、BAK-001、ARC-001 至 ARC-003；组合检查无冲突；扩展 LEGAL、SEC、TECH、QA 发布阻塞项。 |
| 2026-08-11 | 7 | 冻结 QUE-001 至 QUE-004、CONSENT-002、GWY-001、RETRY-001、RES-001、MTR-001、IDEMP-001；组合检查无冲突；扩展 MD、LEGAL、SEC、TECH、QA 发布阻塞项。 |
| 2026-08-11 | 8 | 冻结 A11Y-001 至 A11Y-003、WGT-001 至 WGT-004、TOK-001 至 TOK-003；组合检查无冲突；扩展 MD、LEGAL、SEC、TECH、QA、ETHICS 发布阻塞项。 |
| 2026-08-11 | 9 | 冻结 TOP-001、SAFEOPS-001、SLO-001、LOG-001、OBS-001、IAM-001、SUP-001、REL-001、INC-001、OPS-001；组合检查无冲突；扩展 MD、LEGAL、SEC、TECH、QA、ETHICS 发布阻塞项。 |
| 2026-08-11 | 10 | 冻结 SCP-001、MAT-001、EXIT-001、ACCD/ACCM/ACCS/ACCU/ACCP-001、CHG-001、SIGN-001；原真机条款经用户确认修正后无冲突；十轮产品决策冻结，发布状态保持未批准。 |
