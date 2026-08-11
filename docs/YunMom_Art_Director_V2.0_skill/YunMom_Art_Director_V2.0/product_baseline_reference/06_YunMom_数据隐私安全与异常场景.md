# 云妈妈 YunMom · 数据隐私、安全与异常场景规范 V1.0.0

> 本文档将“隐私不是宣传语，而是架构”作为基线。YunMom 的目标不是把所有数据送上服务器再声称加密，而是从系统设计上尽量让完整孕期数据不进入 YunMom 后台。

---

# 1. 核心隐私承诺

## 1.1 No Health Data Backend
YunMom 自有管理后台不得保存用户完整健康内容，包括但不限于：
- 孕周历史；
- 预产期；
- 医院；
- 医生；
- 检查报告；
- B 超/化验附件；
- 症状；
- 体重；
- 血压；
- 血糖；
- 胎动；
- 药物；
- 饮食；
- 心情；
- 日记；
- AI 对话正文；
- 照片；
- 产检结果。

## 1.2 Local-first
上述内容默认存储在用户设备本地。

## 1.3 官方 AI 是“按请求最小出站”
用户主动发起 AI 任务时，仅发送完成该任务必要的最小上下文。

## 1.4 BYOK
用户可以把自己的 AI Provider API Key 放在设备安全区，直接调用 Provider。

---

# 2. Minimal AI Gateway

## 2.1 只做
- 鉴权；
- 权益；
- 限流；
- Token 计量；
- 计费；
- Provider 路由；
- Streaming；
- 错误码归一化。

## 2.2 绝不做
- Prompt 持久化；
- Response 持久化；
- 图片归档；
- 报告归档；
- 健康 Profile；
- 内容分析；
- Session Replay；
- 把请求正文用于模型训练或运营分析。

---

# 3. 网关日志规范

允许：
- Request ID
- Anonymous/account ID
- Provider
- Model
- Input/output token count
- Cost
- Latency
- HTTP status
- Error code

禁止：
- Prompt
- Response
- Image body
- File
- OCR text
- Health fields
- API Key

---

# 4. 基础设施日志审查

上线前逐项检查：
- Reverse Proxy
- Nginx / Envoy
- CDN
- WAF
- Cloud Load Balancer
- APM
- Distributed Trace
- Serverless logs
- Error reporting
- Crash platform

要求：
> **即使应用代码不写 body，基础设施也不得偷偷记录 body。**

---

# 5. 本地数据安全

## 5.1 数据库
- 加密；
- 不把健康字段写普通 SharedPreferences；
- 数据密钥不硬编码。

## 5.2 附件
- 原图加密；
- PDF 加密；
- thumbnail 也按敏感文件处理；
- 缓存与临时 OCR 文件及时清理。

## 5.3 API Key
- iOS Keychain
- Android Keystore/Secure Storage
- 不进 SQLite 明文
- 不进日志
- 不上传 YunMom

---

# 6. 图片与文件

拍摄报告后：
1. 本地保存原件；
2. 去除不必要 EXIF；
3. 创建加密缩略图；
4. 需要云 AI 时只发送当前文件；
5. 完成后 YunMom Gateway 不保存正文；
6. Provider 的数据处理受其自身政策约束，App 必须在隐私说明中透明告知。

---

# 7. 用户数据控制

App 必须提供：
- 查看；
- 编辑；
- 删除；
- 导出；
- 封存；
- 清空某 Pregnancy Episode；
- 删除全部本地数据。

用户删除应区分：
- 单条事件；
- 附件；
- 整个 Episode；
- AI Provider Key；
- 本地 RAG；
- App 全部数据。

---

# 8. Undo 与真正删除

Event Sourcing 用于可撤销，但用户明确要求彻底删除时必须能物理清除：
- 原始文件；
- thumbnail；
- cache；
- local index；
- derived snapshot；
- vector entry；
- temporary preprocess output。

---

# 9. 备份

YunMom 不提供自营健康云备份。

推荐：
- 用户主动“导出加密备份”；
- 保存到系统 Files 或用户选择的位置；
- 可手动迁移到新手机；
- 可导入下一款宝宝 App。

对于系统层 iCloud/Android backup：
- 敏感目录是否参与备份必须专项确认；
- 不能宣传“绝不离开手机”却默认被系统自动云备份；
- 最终行为要在隐私说明中明确。

---

# 10. Encrypted Pregnancy Archive

至少包含：
- schema_version；
- episode；
- events；
- observations；
- tasks；
- appointments；
- reports metadata；
- encrypted attachments；
- diary；
- memories；
- optional conversations；
- checksums。

导出时：
- 用户主动；
- 可设置密码；
- 明确保存位置。

导入时：
- 校验完整性；
- 校验版本；
- 本地解密；
- 不经 YunMom 服务器。

---

# 11. 权限请求

## 11.1 原则
只在“用户要用”时请求，不在安装后一次索要全部。

## 11.2 相机
触发拍照时请求。
拒绝后：
- 文件上传；
- 文本；
仍可用。

## 11.3 麦克风
首次长按语音时请求。
拒绝：
- 文字输入继续。

## 11.4 定位
只为天气/地图辅助。
拒绝：
- 本地时间 Ambient；
- 手动城市。

## 11.5 通知
拒绝：
- App 内星星继续；
- 首页提醒继续。

## 11.6 权限前解释
先由 YunMom 用一句人话解释：
> “如果允许定位，我可以按你所在城市的天气调整今天的云和光。”

再弹系统权限。

---

# 12. 无网络

无网不能让产品变“不可用”。

仍可：
- HOME；
- Pregnancy Time；
- 本地天气缓存；
- Timeline；
- Calendar；
- Profile；
- Planner；
- 通知；
- 记录；
- 拍照保存；
- 日记；
- Silent Day。

需要 AI 的任务：
- 保存在 Pending AI Queue；
- 明确“还没有完成分析”；
- 用户可取消；
- 网络恢复后按用户设置处理；
- 不静默把大量旧照片上传。

---

# 13. Provider 故障

## 13.1 不能丢原始输入
报告照片先本地存好。

## 13.2 用户文案
> “刚才那次分析没有完成，原来的记录已经留在手机里。稍后可以再试。”

不说：
> “系统异常，请联系管理员。”

## 13.3 Fallback
如果未来允许官方多 Provider 自动 fallback：
- 必须只发送同一 Minimal Context；
- 用户设置可关闭；
- 账单透明；
- 不更改 Persona。

---

# 14. AI 识别错误

防线：
1. Confidence；
2. Schema Validation；
3. Policy；
4. C 级确认；
5. Action Receipt；
6. ✏️ / 🗑；
7. Undo History。

医学关键字段不能仅凭一次低置信 OCR 自动写成“已确认事实”。

---

# 15. 数据冲突

示例：
用户语音：58.3 kg  
照片识别：53.8 kg

YunMom：
> “你之前说的是 58.3 kg，这张图看起来像 53.8 kg。要保存哪一个？”

不擅自选择。

---

# 16. Medical Risk 的隐私与状态

风险事件保留：
- trigger；
- source；
- time；
- severity；
- user viewed；
- dismiss reason；
- follow-up。

用户“暂时关闭提示”只改变 UI 状态，不自动把风险标记为安全。

---

# 17. Gentle Closure 数据规范

确认不良妊娠结局后：
- 停止所有成长型未来任务；
- 清理不合适本地通知；
- Episode 进入 Quiet Archive；
- 现有数据封存；
- 不自动删除；
- 用户可导出/删除。

不得：
- 自动创建“下一胎” Episode；
- 自动推备孕；
- 自动把 Baby 改成天使符号。

---

# 18. 身份域与健康域隔离

## 18.1 Identity / Commerce
服务器可保存：
- account/anonymous id；
- purchase；
- entitlement；
- AI quota；
- usage metering。

## 18.2 Health
只在本地。

商业后端不应存在可联表获取健康内容的结构。

---

# 19. Weather 隔离

Weather API 仅获得：
- city/city_id；
- locale；
- time。

不获得：
- 孕周；
- 报告；
- 症状；
- 检查计划。

---

# 20. Maps 隔离

Map API 仅获得必要地点/路线。

不附加：
> “孕 19+3、要去做 XX 检查”

这类健康语义。

---

# 21. Notification 隐私

锁屏默认采用低敏文案：
> “云妈妈提醒你有一件安排。”

用户可设置：
- 隐藏详细内容；
- 显示详细内容。

药名、检查名、医院等敏感信息是否展示由用户选择。

---

# 22. 第三方 SDK

默认禁止：
- Session Replay；
- 屏幕录制分析；
- 输入框采集；
- 健康内容埋点；
- 剪贴板读取分析；
- 可识别用户健康路径的第三方行为 SDK。

若未来必须接入：
- 单独评估；
- 最小化；
- 明确权限与隐私文档。

---

# 23. 商业模式与隐私

## 本体买断
本地能力不依赖持续云账号才能查看。

## AI
- 官方额度；
- 加油包；
- BYOK。

即使用户不续 AI：
- 本地数据仍然可访问；
- 时间线仍可看；
- 本地提醒仍工作；
- 导出仍可用。

---

# 24. Gentle Closure 文案红线

建议：
> “我先把后面的孕期提醒都停下来。之前留下的东西还在，你不用现在处理。”

禁止：
- “你要坚强”
- “下次一定会好”
- “宝宝成为小天使”
- “这是命运/上天的安排”
- 自动安利备孕产品

---

# 25. 最坏情况设计原则

遇到任何技术/AI/网络/数据问题时优先顺序：
1. 不丢原始数据；
2. 不假装成功；
3. 不隐藏不确定；
4. 不制造恐慌；
5. 不弱化明确医疗风险；
6. 不把系统故障变成孕妈妈的任务；
7. 不为调试牺牲隐私。

---

# 26. 上线前专项审查

必须至少有：
- 隐私审查；
- 网关日志审查；
- Provider 数据路径审查；
- 医疗边界审查；
- Gentle Closure 审查；
- Risk 文案审查；
- 权限审查；
- App Store/应用市场合规审查；
- 数据删除审查；
- 备份审查；
- 安全渗透测试。

