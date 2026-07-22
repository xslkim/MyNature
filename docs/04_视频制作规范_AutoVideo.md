# 视频制作规范（AutoVideo）

> 每集教程视频通过 **AutoVideo** 流水线产出：编写 `meta.md` + `script.md` → 构建 MP4。
> 格式细节以 `g:\Na\AUTHORING.md` 为准，本文档只规定**本项目怎么用**，不重复格式定义。
>
> 配套：`03_教程大纲_逐集产出.md`（每集内容与素材清单）。

---

## 1. 目录约定

视频工程与 Unity 工程分离，统一放 `g:\Na\videos\`：

```
g:\Na\videos\
├── voice.wav                  ← ⚠️ 参考音色（需用户提供，10-30s 清晰人声）
├── shared\
│   └── html\                  ← 跨集复用的 HTML 图示源文件
├── E01_project_skeleton\
│   ├── meta.md                ← 视频元数据
│   ├── script.md              ← 视频脚本（>>> 分块）
│   ├── clips\                 ← Unity 录屏（本集专用）
│   │   ├── 01_demo_hook.mp4
│   │   └── 02_skeleton.mp4
│   └── shots\                 ← HTML 截图（本集专用）
│       ├── four_pillars.html  ← 截图源文件
│       └── four_pillars.png
├── E02_scene_skeleton\
│   └── ...
└── ...E18
```

- 文件夹命名：`E{两位集号}_{英文短名}`，与 `03` 大纲的 commit 标签对应
- `meta.md` 的 `slug` 与文件夹英文名一致（如 `e01-project-skeleton`）
- `voiceRef` 统一相对引用：`../voice.wav`

---

## 2. 画面素材四级优先级（用户已定）

> 原则：**能用真实画面就不用生成画面**。AutoVideo 每个块按以下顺序选择视觉模式。

| 优先级 | 素材类型 | script.md 写法 | 用途 |
|---|---|---|---|
| ① 首选 | **Unity 录屏** | `@visual: video(./clips/xx.mp4)` | 编辑器操作、运行效果、漫游、参数调节、前后对比 |
| ② 次选 | **HTML 截图** | `@visual: image(./shots/xx.png)` | 架构图、契约表、流程图、代码对照、参数清单 |
| ③ 再次 | **文生图** | `@visual: image` | 无实物可录的概念示意（如风格意向图） |
| ④ 兜底 | **Remotion 动画** | `@visual: animation` | 必须动态演示的抽象原理（如噪声场随时间流动） |

**典型配比**（一集 20 分钟的视频）：
- 录屏块占 60-75%（这是"跟着做"的主体）
- HTML 截图块占 20-30%（讲原理/契约/清单）
- 文生图/动画块 < 10%（能不用就不用）

---

## 3. 录屏规范（① 主力素材）

### 3.1 技术标准

| 项 | 标准 | 说明 |
|---|---|---|
| 分辨率 | **1920×1080** | 与视频输出 16:9 一致 |
| 帧率 | **30fps** | 与 meta `fps: 30` 一致 |
| 格式 | **mp4（H.264 + yuv420p）** | AUTHORING.md 硬性要求 |
| 音频 | 不录解说，只录环境音/操作音（可选） | 解说由 AutoVideo TTS 后配 |
| 光标 | 保留（操作演示需要），避免快速晃动 | |

### 3.2 录制工具

| 场景 | 工具 | 自动化率 | 说明 |
|---|---|---|---|
| Play 模式漫游/效果演示 | **Unity Recorder API 脚本驱动**（首选） | ~90% | Editor 脚本用 `RecorderController` 启停录制 + 代码驱动相机路径，batchmode 直接出 1080p30 mp4（见 §3.4） |
| Play 模式漫游（手动备选） | OBS 录 Game 视图 | 0% | 脚本路线不可用时的保底 |
| Unity 编辑器 UI 操作演示 | Editor 脚本预演 + **OBS 人工录** | ~30% | 操作由脚本半自动执行，人按 OBS 启停（见 §3.4） |
| Blender 操作 | OBS 窗口采集 | 0% | |
| 终端/Python 运行 | OBS 窗口采集 | 0% | 深色终端主题 |

> OBS 参考设置：输出 1920×1080、30fps、x264、CRF 18-20；录完后如需转 yuv420p：`ffmpeg -i in.mp4 -pix_fmt yuv420p -c:v libx264 out.mp4`

> Unity Recorder 需安装 `com.unity.recorder` 包（E01 环境检查时一并装）。

### 3.3 录制内容规范

- **一段素材一个主题**：每段 5-30 秒，对应 script.md 的一个块；不录"全过程长片"再剪
- **操作前先想好脚本**：按 `03` 附录 E 的素材清单逐条录制
- **命名**：`clips/{两位序号}_{语义}.mp4`，如 `01_demo_hook.mp4`、`05_snow_slider.mp4`
- **对比画面**：同机位、同视角录"前/后"两段，时长尽量一致
- **封面素材**：`03` 大纲标注"封面素材"的片段，单独多录一条高质量版（Recorder 输出、运镜平稳）
- **编辑器观感**：深色主题；Scene/Game 视图最大化录制；隐藏无关窗口；暂停时手离开鼠标

### 3.4 自动化录屏分级（配合 02 §4A）

录屏素材按"能不能脚本化"分两级处理：

**A. 可全自动：漫游 / 效果演示类**（约占录屏素材 70%，含全部封面素材）

- 原理：录的是 **Game 视图**——相机路径、参数滑杆、季节切换都能用代码驱动，无需人碰编辑器
- 实现：`Scripts/Editor/MyNatureBuilder_Recorder.cs`
  - 相机路径：`AnimationCurve` / 航点列表插值驱动漫游相机
  - 效果演示：脚本控制 `Snow=0→1`、ColorManager 切 slot、TimeOfDay 变化等
  - Recorder：`RecorderControllerSettings` 配 MovieRecorder（1080p30 H.264）→ `Prepare/StartRecording` → 播完 `StopRecording`
- 触发：`-batchmode -executeMethod MyNature.Builder.RecordClips -quit`（带 GPU，**不加** `-nographics`）
- 产出直接落 `videos/E{xx}/clips/`，人只做验收挑选
- ⚠️ batchmode 下 Recorder 渲染依赖 GPU 可用；个别机器若失败，退化 OBS 手动录 Game 视图

**B. 半自动：编辑器 UI 操作演示类**（约占 20-30%，教学"跟着做"镜头）

- 原理：教学需要**看到**菜单被点、Inspector 变化——这类画面必须录编辑器 UI，无法无头
- 半自动做法：
  1. Editor 脚本写一个"演示驱动器"：按预定节奏自动执行操作（`EditorApplication.ExecuteMenuItem`、选中资产、PingObject、改 Inspector 值），步进间隔留 1-2 秒
  2. 人只负责：OBS 开始 → 跑驱动器 → OBS 停止
- 人仍需在场，但操作零失误、可反复重录，单条素材实际人工耗时 ≈ 1 分钟

> 结论：**全部封面素材与漫游素材可无人值守产出**；需人介入的只剩 B 类短镜头，每集约 5-10 条。

---

## 4. HTML 截图规范（② 原理讲解素材）

用本地 HTML 渲染图示再截图，**不调任何 AI 服务**，风格与视频主题 `dark-code` 统一。

### 4.1 制作流程

1. 写 `shots/xx.html`（单文件、内联样式，见 §4.2 模板）
2. 浏览器打开，窗口调至 1920×1080（或用无头浏览器 `chrome --headless --screenshot --window-size=1920,1080`）
3. 截图存为 `shots/xx.png`
4. script.md 中 `@visual: image(./shots/xx.png)`

### 4.2 视觉规范（与 dark-code 主题一致）

```
背景      #0d1117（深）
主文字    #e6edf3
次文字    #8b949e
强调色    #58a6ff（与字幕高亮同色）
代码底色  #161b22
关键字    #ff7b72 / 字符串 #a5d6ff / 注释 #8b949e
字体      中文 Noto Sans SC / 代码 JetBrains Mono
```

- 一页只讲一件事；标题 ≥ 56px、正文 ≥ 32px（1080p 远距离可读）
- 内容区占画布 ≥ 80%，外边距 ≤ 65px
- 适用内容：架构图、全局变量契约表、流程图、代码左右对照、参数清单、检查单

---

## 5. meta.md 模板（每集统一）

```yaml
--- meta ---
title: MyNature 复刻教程 E01 - 项目全景与工程骨架
aspect: 16:9
theme: dark-code
fps: 30
slug: e01-project-skeleton
voiceRef: ../voice.wav
---
```

- `title` 格式：`MyNature 复刻教程 E{集号} - {集标题}`
- `slug` 格式：`e{两位集号}-{英文短名}`，全系列唯一
- `voiceRef`：统一 `../voice.wav`（⚠️ **需用户提供参考音色 WAV 后此配置才可用**）

---

## 6. script.md 写作约定（本项目专用）

格式定义见 AUTHORING.md，以下是本系列统一约定：

### 6.1 块结构模板

**录屏块**（主力）：
```markdown
>>> 演示：雪量滑杆一键入冬 #B07
@enter: fade
@exit: fade
@visual: video(./clips/05_snow_slider.mp4)

--- visual ---
（仅文档用途）Snow 开关从 0 拖到 1，测试场景植被逐渐被雪覆盖

--- narration ---
现在把 Snow 从零拖到一
注意看树冠和岩石，**雪是按世界法线方向积雪的**
```

**HTML 截图块**（原理讲解）：
```markdown
>>> 全局变量契约 #B03
@enter: fade-up
@exit: fade
@visual: image(./shots/wind_contract.png)

--- visual ---
（仅文档用途）C# 与 shader 的全局变量契约表

--- narration ---
这是整套系统的**契约**
C# 每帧推这些变量，shader 只管读
```

### 6.2 系列统一规则

1. **每集开头**：第 1 块为"本集成果预览"（录屏 hook，先给看成品的 5-10 秒）
2. **每集结尾**：最后 1 块为"本集产出 + 下集预告"
3. **块 ID**：`#B` + 两位数字，集内从 B01 递增（每集独立 script.md，无跨文件重号问题）
4. **旁白**：每行 ≤ 50 中文字；术语首次出现 `**高亮**`；集号/文件名/参数值读法口语化（如 `WindStrenghtFloat` 读"风强度"）
5. **转场**：讲解块用 `fade-up`，演示块用 `fade`，不用花哨转场
6. **录屏块时长**：默认由旁白时长决定；录屏比旁白短会循环、长会截断——剪辑录屏时按旁白秒数预裁（见 AUTHORING.md §3.2）
7. **代码展示**：不直接录 IDE 滚动；关键代码段做 HTML 截图（等宽字体、语法高亮、行号），一次一屏

---

## 7. 每集视频产出 Checklist

```
□ 1. 代码/工程工作完成，该集 commit + tag 已打
□ 2. 按 03 附录 E 清单录完全部 clips（1080p30, yuv420p）
□ 3. 制作全部 HTML 截图 shots（风格符合 §4.2）
□ 4. 写 meta.md（模板 §5）
□ 5. 写 script.md（约定 §6；旁白通读，超 50 字拆行）
□ 6. 检查每个块的 @visual 模式与素材文件路径对应
□ 7. 交给构建 Agent 按 BUILD.md 构建 → 得到 MP4
□ 8. 成片自查：字幕不超行、画面与旁白对得上、无黑屏/素材缺失
□ 9. 归档：视频工程目录随 git 提交（clips 大文件按需取舍）
```

---

## 8. 待办（视频管线启动前）

| 项 | 状态 | 负责 |
|---|---|---|
| 参考音色 `voice.wav`（10-30s 清晰人声） | ⚠️ 待提供 | 用户 |
| OBS / Unity Recorder 安装与 1080p30 预设 | 待确认 | 用户环境 |
| `g:\Na\videos\` 目录创建与 git 纳管 | 待执行 | E01 时一起做 |
| AutoVideo 引擎位置确认（BUILD.md 所在） | 待确认 | 用户 |

---

*相关文档：`03_教程大纲_逐集产出.md`（每集内容与素材清单）、`g:\Na\AUTHORING.md`（格式定义）。*
