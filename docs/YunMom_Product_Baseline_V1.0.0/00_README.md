# 云妈妈 YunMom · 产品基线文档包 V1.0.0

> **这是后续项目开发的统一基线。**  
> 除非产品负责人明确提出变更，否则任何视觉、交互、客户端、AI、医学内容与测试工作都不得擅自改变已锁定方向。

## 文档目录

1. **01_YunMom_完整产品设计规格.md**  
   产品灵魂、首页、Pregnancy Time、Silent Day、三方向导航、YunMom 交互、星星、Bento、风险提示、知识、时间线、产检、报告、饮食、运动、药物、购物、小工具、爸爸、Onboarding、天气、Widget、主动智能、Gentle Closure、孕期总结、商业模式与开发阶段。

2. **02_YunMom_完整技术架构.md**  
   Flutter + Rive + Native、Event Sourcing、Universal Health Field、Pregnancy Time Engine、Skill OS、Typed Command、Model Adapter、AI Gateway、BYOK、本地 Planner、RAG、附件、通知、Widget、加密、离线、测试与技术红线。

3. **03_YunMom_形象设计与视觉角色圣经.md**  
   YunMom 云枕形象、Baby 孕周资产、短绒 3D 毛绒材质、Cloud Puff、星星、道具、App Icon、色彩、光照、天气、Gentle Closure 视觉、美术生成与审核。

4. **04_YunMom_动效与交互规范.md**  
   全局 Motion Language、空间切换、Bento Morph、Pregnancy Time、长按语音、Camera Drag、AI Receipt、星星、风险、Silent Day、天气、音效、Haptic 和性能降级。

5. **05_YunMom_AI_Skill_OS与人格规范.md**  
   YunMom Persona、Care/Professional/Safety、Skill Manifest、自动执行分级、Action Receipt、医疗与情绪 Skill 分离、多轮对话、RAG、报告解析、Gentle Closure。

6. **06_YunMom_数据隐私安全与异常场景.md**  
   No Health Data Backend、Minimal AI Gateway、BYOK、日志安全、本地加密、权限、无网、Provider 故障、冲突、备份、迁移、第三方 SDK 红线。

7. **07_YunMom_页面状态矩阵与验收基线.md**  
   把产品原则落实到具体页面与状态；高保真原型必须覆盖的 13 个关键状态。

## 参考素材

`references/yunmom_cloud_pillow_reference.png`  
用户提供的短绒云枕抱宝宝视觉参考。只抽取“柔软、安全、短绒、高级、宝宝被承托”的方向，不要求逐像素复刻。

## 已冻结的最重要决策

- 中文名 **云妈妈**，英文名 **YunMom**
- 图标：**云抱星星**
- 首页：**Pregnancy Time 在上，YunMom + Baby 在中央**
- 云妈妈：**白色大型短绒 3D 云枕，有极简脸，无人体/传统手臂**
- Baby：**同风格，孕周科学形态渐进变化**
- 主导航：**无 Bottom Tab；右滑回忆、左滑 Bento、上滑了解**
- AI：**单击 YunMom 轻提示；长按语音；向右上拖相机**
- AI 持久化写入：**必须 ✏️ + 🗑**
- 普通待办：**云上的立体星星**
- 风险：**首页右下角温和红/珊瑚 `!`**
- Silent Day：**无星星、无轮播，只有云、宝宝与环境**
- 数据：**Local-first / No Health Data Backend**
- 官方 AI：**Minimal Gateway**
- BYOK：**DeepSeek / GLM / MiMo / MiniMax / Qwen**
- Agent：**YunMom + Pregnancy Execution Harness 两层**
- Safety 与 Mood：**独立 Skill**
- 孕期从确认怀孕开始
- 产后：导出到下一应用，不在 YunMom 继续重型 0–1 岁
- 商业：**本体买断 + AI 单独计量 / BYOK**
- 不良妊娠结局：**Gentle Closure / Quiet Archive**

## 修改规则

任何冻结项修改必须：
1. 提出变更理由；
2. 写清对产品、UI、AI、数据、医学与测试的影响；
3. 修改相应文档；
4. 提升版本号；
5. 更新 CHANGELOG；
6. 重新通过关键状态验收。
