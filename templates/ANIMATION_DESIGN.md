# 模板动画设计方案

## 一、设计原则

### 1.1 核心目标
- **视觉冲击**：通过动画增强第一印象
- **信息层次**：引导观众注意力从标题→图片→文字→署名
- **情感共鸣**：根据内容风格匹配相应的动画氛围

### 1.2 技术约束
- ✅ 纯 CSS3 动画（@keyframes）
- ✅ 兼容 ffmpeg 视频渲染
- ✅ 性能优先（避免复杂计算）
- ❌ 不使用 JavaScript 动画库
- ❌ 不使用 canvas/webgl

### 1.3 时间控制
- **入场动画**：0-3秒（元素逐一出现）
- **持续动画**：3-10秒（呼吸/脉冲/流动效果）
- **推荐总时长**：5-8秒（适合短视频节奏）

---

## 二、动画类型分类

### 2.1 文字动画

#### A. 淡入效果 (Fade In)
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```
- **适用场景**：标题、作者名
- **时长**：0.6-1.2秒
- **缓动函数**：ease-out

#### B. 滑入效果 (Slide In)
```css
@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```
- **适用场景**：正文、描述文字
- **方向**：从下至上（Up）、从左至右（Left）
- **时长**：0.8-1.5秒

#### C. 打字机效果 (Typewriter)
- **适用场景**：短句、金句
- **实现**：width 动画 + overflow hidden
- **时长**：逐字显示，总长2-4秒

#### D. 文字发光脉冲 (Glow Pulse)
```css
@keyframes textGlowPulse {
  0%, 100% {
    text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
  }
  50% {
    text-shadow: 0 0 20px rgba(255, 255, 255, 0.6);
  }
}
```
- **适用场景**：标题、重点文字
- **周期**：2-4秒

---

### 2.2 图片动画

#### A. 缩放入场 (Zoom In)
```css
@keyframes zoomIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
```
- **时长**：1-1.5秒
- **缓动**：cubic-bezier(0.34, 1.56, 0.64, 1)

#### B. 平移视差 (Ken Burns)
```css
@keyframes kenBurns {
  0% {
    transform: scale(1) translateX(0);
  }
  100% {
    transform: scale(1.1) translateX(-5%);
  }
}
```
- **时长**：8-12秒（持续效果）
- **适用场景**：风景、艺术图片

#### C. 渐显 (Fade In Up)
```css
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```
- **时长**：1-1.2秒

---

### 2.3 背景动画

#### A. 渐变流动 (Gradient Flow)
```css
@keyframes gradientFlow {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}
```
- **时长**：6-10秒循环
- **方向**：水平/垂直/对角线

#### B. 光晕脉冲 (Orb Pulse)
```css
@keyframes orbPulse {
  0%, 100% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.1);
  }
}
```
- **时长**：3-5秒
- **适用场景**：装饰性圆形元素

#### C. 浮动粒子 (Floating Particles)
```css
@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}
```
- **时长**：4-8秒
- **适用场景**：点、圆、几何图形

---

### 2.4 过渡动画

#### A. 元素依次出现 (Stagger)
- **原理**：每个元素使用 animation-delay 递增
- **延迟**：0.2-0.3秒间隔
- **效果**：标题→图片→文字→署名

#### B. 边框描画 (Border Draw)
```css
@keyframes borderDraw {
  from {
    clip-path: inset(0 100% 100% 0);
  }
  to {
    clip-path: inset(0 0 0 0);
  }
}
```
- **时长**：1-1.5秒

#### C. 装饰线伸展 (Line Expand)
```css
@keyframes lineExpand {
  from {
    width: 0;
  }
  to {
    width: 100%;
  }
}
```
- **适用场景**：分隔线、装饰线

---

## 三、模板分类与动画推荐

### 3.1 文艺风格
**代表模板**：`static_excerpt.html`

**推荐动画**：
- 标题：淡入 + 文字发光
- 正文：逐行淡入上滑
- 背景遮罩：从透明到半透明
- 装饰线：从中心向两侧伸展

**配色**：
- 米白色背景 (#e8e5e0)
- 深灰文字 (#2a2a2a)
- 金色装饰线

**氛围**：优雅、文艺、静谧

---

### 3.2 极简风格
**代表模板**：`image_simple_black.html`

**推荐动画**：
- 标题：快速淡入 + 轻微脉冲
- 图片：从黑色中渐显
- Footer：底部上滑入场
- Logo 点：依次点亮

**配色**：
- 纯黑背景 (#000000)
- 纯白文字 (#ffffff)
- 高对比度

**氛围**：现代、简约、专业

---

### 3.3 优雅风格
**代表模板**：`image_elegant.html`

**推荐动画**：
- 背景 orb：浮动 + 脉冲
- 标题：渐变文字 + 发光
- 图片框：缩放入场 + 角标描绘
- 文字区域：从下浮入
- 装饰点：浮动循环

**配色**：
- 柔和渐变（紫-粉-蓝）
- 毛玻璃效果
- 装饰圆角元素

**氛围**：浪漫、梦幻、精致

---

### 3.4 霓虹风格
**代表模板**：`image_neon.html`

**推荐动画**：
- 标题：霓虹发光脉冲（已有）
- 背景元素：扫描线移动
- 圆形装饰：脉冲呼吸
- 图片边框：霓虹闪烁
- 装饰线：发光流动

**配色**：
- 深蓝背景 (#0b0f1a)
- 霓虹青 (#3cf0ff)
- 霓虹粉 (#ff3fe0)
- 霓虹黄 (#f0e130)

**氛围**：赛博朋克、科技、未来

---

### 3.5 电影风格
**代表模板**：`image_film.html`

**推荐动画**：
- 标题：从黑屏淡入 + 缓慢缩放
- 图片：Ken Burns 效果（缓慢推进）
- 文字：底部淡入上滑
- Footer：延迟出现

**配色**：
- 纯黑背景
- 白色/金色文字
- 电影画幅比例

**氛围**：史诗、大气、震撼

---

## 四、实施计划

### 4.1 阶段一：基础动画（优先级高）
1. ✅ 创建通用动画库文件
2. ✅ 为文艺风格模板添加动画
3. ✅ 为极简风格模板添加动画

### 4.2 阶段二：进阶动画
1. ✅ 为优雅风格模板添加装饰元素动画
2. ✅ 优化霓虹风格模板的动画细节

### 4.3 阶段三：高级效果
1. ✅ 电影风格 Ken Burns 效果
2. ✅ 打字机效果实现
3. ✅ 性能测试与优化

---

## 五、性能优化策略

### 5.1 减少重绘
- 使用 `transform` 和 `opacity`（GPU 加速）
- 避免动画 `width`、`height`、`margin`

### 5.2 动画节流
- 限制同时运行的动画数量
- 使用 `animation-play-state: paused` 控制暂停

### 5.3 渲染优化
- 使用 `will-change` 提示浏览器优化
- 避免使用 `box-shadow` 动画（性能杀手）

### 5.4 时间控制
- 入场动画：短促有力（0.5-1.5秒）
- 持续动画：节奏舒缓（3-10秒循环）
- 避免动画时长过长（超过15秒）

---

## 六、验收标准

### 6.1 视觉标准
- ✅ 动画流畅不卡顿
- ✅ 视觉层次清晰
- ✅ 不影响文字可读性

### 6.2 性能标准
- ✅ CPU 占用 < 30%
- ✅ 无明显掉帧
- ✅ ffmpeg 渲染时间合理（< 3秒/帧）

### 6.3 兼容性标准
- ✅ Chrome/Safari/Firefox 正常播放
- ✅ ffmpeg 视频导出正确
- ✅ 不同分辨率模板均可用

---

## 七、动画库文件结构

```
templates/
├── animations/
│   ├── text-animations.css      # 文字动画
│   ├── image-animations.css     # 图片动画
│   ├── background-animations.css # 背景动画
│   └── utils.css                # 工具类
├── 1080x1920/
│   ├── image_elegant_animated.html
│   └── ...
└── 1920x1080/
    └── ...
```

---

## 八、示例代码片段

### 8.1 文字依次出现
```css
.title { animation: fadeIn 0.8s ease-out 0.2s both; }
.text { animation: slideInUp 1s ease-out 0.6s both; }
.author { animation: fadeIn 0.6s ease-out 1.2s both; }
```

### 8.2 图片 Ken Burns
```css
.image {
  animation: kenBurns 10s ease-in-out infinite alternate;
}
```

### 8.3 背景 orb 浮动
```css
.orb {
  animation: orbFloat 6s ease-in-out infinite;
}

@keyframes orbFloat {
  0%, 100% { transform: translate(0, 0); }
  33% { transform: translate(20px, -30px); }
  66% { transform: translate(-15px, 15px); }
}
```