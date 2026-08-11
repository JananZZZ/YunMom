# 云妈妈 YunMom · 完整技术架构 V1.0.0

> **目标**：为“前台极简、后台极深”的 YunMom 提供可替换模型、Local-first、事件溯源、可审计、可逆、低功耗、跨平台的工程架构。
>
> **核心约束**：**No Health Data Backend + Minimal AI Gateway + BYOK + Skill OS + Event Sourcing + Local Planner**。

---

# 1. 技术设计原则

1. **Local-first**：完整孕期数据库、报告、照片、聊天、日记、RAG 索引默认只在设备。
2. **No Health Data Backend**：YunMom 自有后台不得保存孕期健康内容。
3. **Minimal AI Gateway**：官方 AI 请求只做鉴权、计费、限流、路由和流式转发。
4. **BYOK**：用户始终可使用自己的模型 Key。
5. **模型可替换**：业务 Skill 不依赖 DeepSeek/GLM/MiMo/MiniMax/Qwen 的具体 API。
6. **LLM 不直接操作 DB**：所有持久化动作必须走 Typed Command → Validation → Policy → Event Store。
7. **AI 写入可逆**：Event Sourcing + Undo。
8. **主动管理本地优先**：孕周、产检计划、星星、药物提醒、Silent Day 不依赖云端常驻模型。
9. **UI 与数据解耦**：Living World 只消费结构化 `LivingWorldState`。
10. **医学风险 Skill 与情绪 Skill 分离**。
11. **请求最小化出站**：每次 AI 只发送当前任务必要的 Context Capsule。
12. **弱网可用**：查看、记录、Timeline、Planner、通知、附件保存可离线。
13. **性能优先**：YunMom 是 Ambient UI，不是全时运行的 3D 游戏。
14. **隐私基础设施优先**：不能“代码不存正文，但代理/APM 偷偷记录 body”。
15. **所有外部域隔离**：天气、地图、支付、AI 不共享健康上下文。

---

# 2. 推荐技术栈

## 2.1 客户端
- **Flutter**：主 UI、路由、业务逻辑、数据层、绝大多数交互。
- **Rive Runtime**：YunMom / Baby / 星星的交互动画与状态机。
- **Flutter CustomPainter / Fragment Shader**：天空、天气、光、粒子、柔和环境。
- **Native Extensions**：
  - iOS WidgetKit；
  - Android Glance/App Widget；
  - iOS Keychain / Android Keystore；
  - 原生本地通知；
  - Camera / Photos / File Picker；
  - 必要时系统健康数据桥接。

## 2.2 本地数据库
推荐：
- SQLite 为核心；
- Dart 层使用成熟 DAO/ORM；
- 数据库文件加密；
- 附件独立 Encrypted File Store；
- 密钥保存在系统安全区。

## 2.3 本地 RAG
- Local document store；
- Local vector index；
- Embedding Model Adapter；
- 文档元数据与版本追踪；
- 不把整套知识库和用户健康数据上传 YunMom 后台。

## 2.4 AI Provider
官方推荐首批：
- DeepSeek
- GLM
- MiMo
- MiniMax
- Qwen

后续可增更多 Provider 或 OpenAI-compatible 自定义端点。

---

# 3. 总体架构

```text
┌──────────────────────────── DEVICE ────────────────────────────┐
│                                                               │
│                     YunMom Living World                       │
│  PregnancyTime / Ambient / YunMom / Baby / Stars / Risk       │
│                          │                                    │
│                 Navigation & Gestures                         │
│                          │                                    │
│                 YunMom AI Overlay                             │
│          Voice / Camera / Text / File                         │
│                          │                                    │
│              Pregnancy Execution Harness                      │
│                                                               │
│  Intent Router / Context Builder / Planner / Policy Engine     │
│  Skill Registry / Command Bus / Scheduler / Model Adapter      │
│                          │                                    │
│                    Typed Commands                             │
│                          │                                    │
│              Schema + Policy Validation                       │
│                          │                                    │
│                  Pregnancy Event Store                        │
│                                                               │
│ Profile / Observation / Task / Report / Diary / Medication     │
│ Nutrition / Activity / Appointment / Conversation / Memory     │
│                          │                                    │
│             ┌────────────┴────────────┐                       │
│             ↓                         ↓                       │
│    Encrypted Attachment Store     Local RAG Index              │
│             └────────────┬────────────┘                       │
│                          ↓                                    │
│                 Derived Snapshot                             │
│                          ↓                                    │
│                  Living World State                           │
└──────────────────────────┬────────────────────────────────────┘
                           │ explicit user-authorized AI request
                           ↓
                 Minimal Context Capsule
                     ┌─────┴─────┐
                     ↓           ↓
                 BYOK Direct  YunMom Gateway
                                  ↓
              DeepSeek / GLM / MiMo / MiniMax / Qwen

External isolated domains:
Weather API  ← city/weather only
Maps API     ← place/route only
Payment      ← entitlement & metering only
```

---

# 4. 客户端分层

## 4.1 Presentation Layer
负责：
- HOME；
- MEMORY；
- CARE/Bento；
- KNOW；
- AI Overlay；
- Action Receipt；
- Risk Indicator；
- Widget ViewModel；
- Settings。

不直接访问数据库，不写 SQL。

## 4.2 Living World Layer
输入结构化状态，输出视觉状态。

`LivingWorldState` 至少：
```text
pregnancy_time
days_to_edd
time_of_day
weather
ambient_variant
yunmom_state
baby_stage
baby_action
task_stars
risk_indicator
silent_day
temporary_overlay
interaction_mode
```

## 4.3 Application Layer
- Use Cases；
- Timeline Query；
- Snapshot Builder；
- Pregnancy Time Engine；
- Action Receipt Controller；
- Navigation Orchestrator；
- Planner。

## 4.4 Execution Harness
- Intent Router；
- Skill Registry；
- Context Builder；
- Policy Engine；
- Command Bus；
- Scheduler；
- Model Adapter；
- Safety Gate；
- Result Normalizer。

## 4.5 Domain Layer
核心实体：
- PregnancyEpisode
- Event
- Observation
- Task
- Appointment
- Document
- Medication
- DiaryEntry
- Conversation
- Memory
- Actor
- Permission
- ProviderConfig
- Hospital
- NotificationSchedule

## 4.6 Infrastructure Layer
- DB；
- Attachment Store；
- Secure Storage；
- RAG；
- Notification Adapter；
- Weather Adapter；
- Map Adapter；
- AI Provider Client；
- Gateway Client；
- Camera/File；
- OCR/Vision Preprocessor。

---

# 5. Event Sourcing

YunMom 不是“当前字段覆盖历史”，而是“历史事件计算当前状态”。

## 5.1 基本关系
```text
PregnancyEpisode
 ├── Event
 ├── Observation
 ├── Task
 ├── Appointment
 ├── Document
 ├── DiaryEntry
 ├── Medication
 ├── Conversation
 └── Memory
```

## 5.2 Event 基础结构
建议：
```json
{
  "id": "uuid",
  "episode_id": "uuid",
  "event_type": "weight_recorded",
  "occurred_at": "ISO8601",
  "effective_at": "ISO8601",
  "source_type": "voice|camera|report|manual|device|ai",
  "source_id": "optional_uuid",
  "payload": {},
  "confidence": 0.98,
  "user_verified": false,
  "created_at": "ISO8601",
  "schema_version": 1,
  "is_reverted": false
}
```

## 5.3 当前 Snapshot
`PregnancySnapshot = reduce(valid_events)`

例如：
- 当前体重 = 最近有效 Weight Observation；
- 当前医院 = 最近有效 Hospital Assignment；
- 当前过敏 = 所有未撤销 Allergy Event；
- 当前 EDD = 当前生效的 EDD Event。

## 5.4 删除与撤销
关键数据尽量使用撤销事件而不是物理抹除：
`revert_event(original_event_id)`

用户 UI 看起来可删除，但内部保留可审计历史。
对于用户要求彻底删除的数据和附件，必须支持真正物理清除。

---

# 6. Universal Health Field System

避免每个模块自己造字段。

## 6.1 FieldDefinition
```json
{
  "field_id": "blood_pressure",
  "type": "composite_measurement",
  "required": false,
  "validation": {},
  "display": {},
  "medical_semantics": {}
}
```

## 6.2 支持类型
- number_unit
- text
- boolean
- tristate
- enum
- multienum
- tag
- date
- datetime
- duration
- range
- count
- composite_measurement
- symptom_event
- medication
- food_event
- activity_event
- location
- attachment
- timeseries
- derived
- custom

## 6.3 来源证据
每条值必须携带：
- `source_type`
- `source_id`
- `confidence`
- `attachment_id`
- `user_verified`
- `model_version`（AI 来源）
- `extracted_at`

医院报告值与用户口述值不能混淆来源。

---

# 7. Pregnancy Time Engine

全 App 唯一可信孕周时间源。

## 7.1 输入
可来自：
- 预产期；
- 末次月经；
- 医生校正；
- 报告；
- 用户确认。

## 7.2 校正
任何 EDD 校正写新 Event，不覆盖旧值。

## 7.3 输出
```text
gestational_weeks
gestational_days
ga_string
days_to_edd
trimester
pregnancy_stage
baby_stage_asset_id
```

所有模块只能消费这个 Engine，不得自行重复计算。

---

# 8. Skill OS

每个 Skill 是可控的专门能力，不是无限制 Prompt。

## 8.1 Skill Manifest
示例：
```yaml
id: PrenatalReportParser
version: 1
accepts:
  - image
  - pdf
reads:
  - pregnancy_context
  - active_hospital
writes:
  - document
  - observation
  - timeline_event
risk: medium
confirmation:
  low_confidence: required
knowledge:
  - prenatal_report_rules_v1
forbidden:
  - diagnosis
  - treatment_change
  - medication_change
```

## 8.2 核心 Skill 清单
- PregnancyCore
- GestationalAge
- PregnancyProfile
- PrenatalSchedule
- PrenatalReportParser
- HospitalVisit
- SymptomRecord
- SymptomTriage
- MedicationRecord
- MedicationSafety
- MedicationReminder
- NutritionRecord
- NutritionAnalysis
- WeightTracking
- BloodPressure
- GlucoseTracking
- ActivityRecord
- FetalMovement
- MoodDiary
- PregnancyJournal
- PregnancyKnowledge
- PregnancyRAG
- ShoppingList
- HospitalBag
- MaternityLeave
- WeatherAmbient
- MemoryTimeline
- PregnancySummary
- Export
- DadEntry

后续只增不减，新增 Skill 需 Manifest 和测试。

---

# 9. Typed Command Bus

LLM 不可直接写数据库。

## 9.1 流程
```text
User Input
  ↓
YunMom
  ↓
Intent Router
  ↓
Skill
  ↓
Typed Command
  ↓
Schema Validation
  ↓
Policy Validation
  ↓
Execute
  ↓
Event Store
  ↓
Action Receipt
```

## 9.2 Command 示例
```json
{
  "command": "record_weight",
  "args": {
    "value": 58.3,
    "unit": "kg",
    "recorded_at": "2026-08-10T08:10:00+08:00"
  },
  "source": {
    "type": "voice",
    "confidence": 0.99
  }
}
```

## 9.3 自动执行等级
- **A**：明确、低风险，直接执行；
- **B**：执行 + Action Receipt + 可撤回；
- **C**：必须用户确认后执行；
- **D**：AI 不允许自主执行，只能说明/建议联系专业人员。

药物开始/停止/剂量变更、治疗决策等属于 C/D。

---

# 10. Action Receipt 与 Undo

任何 Persistent Action 必须：
- 产生 Receipt；
- 有 ✏️；
- 有 🗑；
- 记录原值/新值；
- 可追踪 Skill；
- 可追踪来源；
- 可追踪模型版本。

Receipt 淡出不代表不可撤销。
历史应在 Timeline/操作历史中可找回。

---

# 11. Model Adapter

业务层只依赖能力：
```text
reason()
vision()
structured_output()
tool_call()
embed()
```

Provider Adapter：
- DeepSeekAdapter
- GLMAdapter
- MiMoAdapter
- MiniMaxAdapter
- QwenAdapter
- CustomOpenAICompatibleAdapter（后续）

模型切换不能改变：
- Skill 输入输出；
- DB schema；
- YunMom Persona；
- Safety Policy。

---

# 12. YunMom Persona 与模型解耦

Persona 作为独立配置注入：
- identity
- tone
- sentence_length
- terminology
- prohibited_phrases
- medical_language_rules
- safety_language
- user_address
- current_context

底层 Provider 只承担推理与生成，不拥有 YunMom 的“人格”。

---

# 13. Minimal AI Gateway

## 13.1 职责
- Authentication
- Anonymous/account entitlement
- Rate limit
- Token metering
- Billing
- Provider routing
- Streaming proxy
- Error normalization

## 13.2 禁止
- 不保存 Prompt；
- 不保存 Response；
- 不保存图片；
- 不保存报告；
- 不保存健康摘要；
- 不建立服务器端健康档案；
- 不把请求正文送 Analytics；
- 不在 Debug Log 打印正文。

## 13.3 可记录
- Request ID；
- 匿名用户/账号 ID；
- Provider；
- Model；
- token in/out；
- cost；
- duration；
- HTTP status；
- error code（无 body）。

## 13.4 基础设施审查
必须逐项验证：
- Nginx/Envoy access log；
- WAF；
- CDN；
- Load Balancer；
- APM；
- Tracing；
- Serverless invocation log；
- Crash/Error logging；
均不记录 request body。

---

# 14. BYOK

## 14.1 支持首批
- DeepSeek
- GLM
- MiMo
- MiniMax
- Qwen

## 14.2 Key 存储
- iOS Keychain；
- Android Keystore / secure storage；
- 不写普通 SQLite；
- 不上传 YunMom 后台；
- 不进入日志。

## 14.3 网络路径
BYOK 可直接访问 Provider。
YunMom Gateway 不经过正文。

## 14.4 ProviderConfig
```text
provider_type
base_url
model_name
key_reference
capabilities
enabled
created_at
```

---

# 15. Minimal Context Capsule

每次 AI 请求由 Context Builder 选择“最少足够上下文”。

例如血压问题：
```json
{
  "gestational_age": "19+3",
  "question": "...",
  "current_bp": "118/72",
  "recent_bp_trend": [...],
  "relevant_history": [...]
}
```

明确不默认发送：
- 全部日记；
- 全部对话；
- 全部报告；
- 全部照片；
- 完整 Pregnancy DB。

Context 中每个字段应保留 provenance，便于模型区分来源。

---

# 16. 本地主动 Planner

## 16.1 目标
不让云端大模型 24 小时“监控”用户。

## 16.2 输入
- Pregnancy Time；
- Tasks；
- Appointments；
- Doctor Instructions；
- Medication Reminders；
- Recent Observations；
- Hospital Plan；
- User Preferences。

## 16.3 Task 分类
来源：
- national_baseline
- hospital_protocol
- doctor_instruction
- ai_derived
- user_created

重要性：
- required
- recommended
- optional
- personal

## 16.4 Attention Budget
压缩为：
- 0 → Silent Day
- 1 → Today’s One Thing
- 极少 >1 → 星群

---

# 17. Medical Safety

## 17.1 与 Mood 分离
独立：
- SymptomTriage / MedicalSafety
- MoodCare

## 17.2 输出示例
```json
{
  "risk_active": true,
  "severity": "needs_prompt_attention",
  "reason_codes": ["..."],
  "message": "...",
  "recommended_actions": [],
  "must_escalate": true
}
```

UI 只表现右下角温和 `!`，角色不负面化。

## 17.3 关闭提示
用户关闭：
`dismiss_risk_prompt`

不能自动写：
`risk_resolved`

只有新的医疗信息、医生反馈、明确用户说明或规则判断才能改变实际风险状态。

---

# 18. Gentle Closure 状态机

```text
ongoing
  ↓ user explicit statement / confirmed diagnosis
pending_closure_confirmation
  ↓ user confirm
quiet_archive
  ↓ optional export/delete
archived
```

进入 quiet_archive：
- 取消成长 Scheduler；
- 取消水果类比；
- 取消 EDD 倒计时通知；
- 取消胎动提示；
- 取消待产/购物推送；
- 保留历史；
- 清理不合适的未来通知。

---

# 19. 报告处理管线

## 19.1 Local Preprocess
- Crop
- Deskew
- Compress
- Remove EXIF
- Document edge detection
- Optional local OCR

## 19.2 Cloud Vision（必要时）
仅发送：
- 当前图片；
- 当前任务必要孕周上下文。

## 19.3 Structured Result
- document_type
- report_date
- hospital
- gestational_age_if_present
- findings
- flagged_items
- physician_notes_if_readable
- confidence
- next_action_candidates

## 19.4 本地保存
- original
- thumbnail
- extraction JSON
- explanation
- provider/model/version
- parse timestamp

---

# 20. Local RAG

## 20.1 Document
字段：
- title
- source
- version
- chapter
- page
- topic
- gestational_range
- risk_level
- copyright_status
- checksum

## 20.2 Chunk
- chunk_id
- doc_id
- text
- embedding
- metadata
- checksum

## 20.3 更新
- 文档版本化；
- 可重建索引；
- 老版本引用仍可追踪；
- 不让“新模型”偷偷覆盖旧来源。

---

# 21. 本地附件与加密

## 21.1 文件
- UUID 文件名；
- 不以“NT报告_姓名”明文命名；
- 缩略图也是敏感附件。

## 21.2 密钥
- 安装级主密钥；
- Keychain/Keystore；
- DB 与附件建议分离派生密钥；
- 导出包使用单独加密。

## 21.3 删除
删除附件时：
- 删除原件；
- 删除缩略图；
- 删除缓存；
- 更新 Event；
- 清理临时 OCR 产物。

---

# 22. Identity Domain 与 Health Domain 隔离

## 22.1 Identity/Commercial 后端
可知道：
- purchase
- entitlement
- AI quota
- usage metering
- account/anonymous id

## 22.2 Health
只在本地：
- pregnancy
- reports
- symptoms
- hospital
- diary
- chats
- photos

商业数据库不应存在能直接联表查询健康信息的结构。

---

# 23. Weather Adapter

只传：
- city/city_id；
- locale；
- weather query。

绝不附带：
- 孕周；
- 健康；
- 报告；
- 医院检查语义。

天气本地缓存，减少网络与耗电。

---

# 24. Map Adapter

只传：
- place；
- coordinate；
- route origin/destination。

不传：
> “这是 19+3 孕妇去做 XX 检查。”

地图与健康语义域隔离。

---

# 25. 通知

## 25.1 Local Notification 为主
适用于：
- 产检；
- 药物；
- 用户提醒；
- Planner。

## 25.2 锁屏隐私
默认通知可以泛化：
> “云妈妈提醒你有一件安排。”

设置中可让用户选择“显示详细内容”。

## 25.3 点击
深链：
- HOME 轻浮窗；
- 或用户主动点击的特定详情。

---

# 26. Widget 架构

## 26.1 WidgetState
主 App 生成轻量共享状态：
```json
{
  "ga": "19+3",
  "silent_day": false,
  "star_count": 1,
  "ambient_variant": "sunset_clear",
  "yunmom_pose": "hold_star",
  "baby_stage": "stage_08",
  "risk_active": false
}
```

## 26.2 iOS
WidgetKit Timeline。

## 26.3 Android
Glance/App Widget。

不在 Widget 里跑完整 Rive 60fps。

---

# 27. Navigation State

建议显式状态：
- home
- memory
- care
- know
- detail(route)
- ai_overlay
- camera
- voice

业务详情尽量不超过：
`Bento → Detail → Subdetail`

超过时需要重新审视是否过度复杂。

---

# 28. Rive 与业务隔离

Rive 只消费参数：
```text
gestational_stage
time_of_day
weather
silent_day
task_state
recent_interaction
voice_active
camera_target_active
risk_active
idle_seed
```

Rive 不读取数据库、不理解医学规则。

`LivingWorldController` 负责将业务状态转成动画状态。

---

# 29. 性能与功耗

## 29.1 首页
- 目标高端 60fps；
- 空闲时 CPU/GPU 低负载；
- Ambient 周期长；
- 粒子受控；
- 无实时毛发物理；
- 后台立即暂停不必要动画。

## 29.2 低端降级
允许：
- 降粒子数；
- 降模糊；
- 简化 Shader；
- 减少同时播放的 Ambient Layer。

不能降级掉：
- YunMom 核心动作；
- Pregnancy Time；
- 星星；
- Risk；
- 手势反馈。

## 29.3 资产
按孕周懒加载宝宝资产，不让 15 套全部常驻内存。

---

# 30. 离线模式

无网仍可：
- HOME；
- Pregnancy Time；
- 缓存天气；
- Timeline；
- Calendar；
- 本地资料；
- 本地 Planner；
- 本地通知；
- 文本记录；
- 拍照并保存；
- Silent Day。

需要云 AI：
- 写入 Pending AI Queue；
- 显示“等网络恢复后再处理”；
- 用户可取消；
- 不静默批量上传大量历史。

---

# 31. 数据导出与迁移

## 31.1 导出
- PDF/长图/视频；
- CSV/JSON（高级）；
- Encrypted Pregnancy Archive。

## 31.2 Archive
至少：
- schema_version
- episode metadata
- events
- observations
- appointments
- documents
- attachments
- diary
- memories
- optional conversations
- checksums

## 31.3 导入
未来 App：
- 校验 archive；
- 用户确认；
- 本地解密；
- schema migration；
- 不经过 YunMom 云端。

---

# 32. 备份策略

遵循 No Health Data Backend：
- 用户主动导出加密备份；
- 保存到 Files / 用户自选存储；
- 不提供 YunMom 自营健康云备份；
- 对 iCloud/系统自动备份敏感目录策略做平台专项审查并透明说明。

---

# 33. 日志与可观测性

## 33.1 客户端
默认不上传健康行为分析。

可收集的技术指标必须脱敏：
- app version
- crash code
- render time
- memory pressure
- provider error code

不得包含：
- 对话正文；
- 报告；
- 症状；
- 数值；
- API Key。

## 33.2 诊断包
用户主动导出：
- Device
- OS
- App version
- Technical logs
- Error IDs

默认不含健康内容。

---

# 34. 第三方 SDK 红线

默认不接会采集：
- 屏幕内容；
- Session Replay；
- 表单；
- 剪贴板；
- 健康信息；
- 输入正文
的分析 SDK。

若未来要接，必须单独隐私审查。

---

# 35. 测试策略

## 35.1 单元测试
- Pregnancy Time；
- Snapshot Reducer；
- Field Validation；
- Planner；
- Task Priority；
- Skill Policy；
- Command Validation；
- Risk State；
- Gentle Closure；
- Data Migration。

## 35.2 UI/Golden
- 日出；
- 白天；
- 日落；
- 夜晚；
- 雨；
- Silent Day；
- Risk；
- Pregnancy Time；
- Bento；
- Memory；
- Knowledge；
- Receipt。

## 35.3 动效
- 手势中断；
- 长按；
- Camera Drag；
- Shared Element；
- 低帧率；
- App 进后台；
- 来电；
- 横竖屏策略（若锁竖屏也测试系统中断）。

## 35.4 医疗安全
建立专项测试集：
- 风险表达；
- 模糊表达；
- 用户只是担心但未确认；
- 药物变更；
- 报告低置信；
- Gentle Closure；
- 关闭风险提示但实际风险仍在。

## 35.5 隐私
- Gateway log 无正文；
- Key 不出日志；
- Crash 不抓 Prompt；
- 删除无 thumbnail 残留；
- BYOK 不经过 Gateway；
- Weather/Map 请求不带健康上下文。

---

# 36. 推荐目录

```text
lib/
  app/
  living_world/
    ambient/
    pregnancy_time/
    yunmom/
    baby/
    stars/
    risk/
  spaces/
    home/
    memory/
    care/
    know/
  ai/
    persona/
    harness/
    router/
    skills/
    commands/
    policy/
    adapters/
    context/
  domain/
    pregnancy/
    events/
    fields/
    tasks/
    reports/
    medications/
    diary/
    memory/
  data/
    db/
    files/
    secure_storage/
    rag/
  integrations/
    weather/
    maps/
    notifications/
    ai_providers/
  widgets/
  settings/
  privacy/
  export/
```

Gateway：
```text
gateway/
  auth/
  entitlement/
  metering/
  rate_limit/
  provider_router/
  stream_proxy/
  billing/
  logging_policy/
```

---

# 37. 技术红线

出现以下任一项即视为架构跑偏：
- LLM 可执行任意 SQL；
- YunMom 服务器保存完整孕期记录；
- Request Body 进入日志；
- BYOK Key 上传官方服务器；
- 每日 Planner 依赖云端 AI；
- Skill 绕过 Policy 直接写 DB；
- Provider 替换要改业务 DB；
- UI 直接依赖某模型私有返回格式；
- Receipt 无法撤销；
- “关闭风险”被写成“风险已解除”；
- Gentle Closure 后仍发宝宝成长推送；
- Widget 为了“动态”持续高刷新耗电；
- 医疗 Safety 与 MoodCare 共用一个随意 Prompt。

