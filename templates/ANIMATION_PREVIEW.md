# 模板动画效果预览说明

## 一、动画库文件

### 1. 文字动画库
**文件**: `templates/animations/text-animations.css`

**包含动画**:
- 淡入效果 (fadeIn, fadeInUp, fadeInDown, fadeInLeft, fadeInRight)
- 滑入效果 (slideInUp, slideInDown, slideInLeft, slideInRight)
- 发光脉冲 (textGlowPulse, textGlowPulseAccent)
- 打字机效果 (typewriter, typewriterCursor)
- 缩放入场 (scaleIn, scaleInBounce)
- 文字描边 (textReveal)
- 行逐一出现 (lineReveal)
- 文字呼吸 (textBreath)

**使用方式**:
```html
<link rel="stylesheet" href="../animations/text-animations.css">
<div class="title animate-fade-in-up delay-300">标题</div>
```

---

### 2. 图片动画库
**文件**: `templates/animations/image-animations.css`

**包含动画**:
- 缩放入场 (zoomIn, zoomInSlow, zoomOut)
- 渐显动画 (imageFadeIn, imageFadeInUp, imageFadeInDown, imageFadeInScale)
- Ken Burns 效果 (kenBurnsLeft, kenBurnsRight, kenBurnsUp, kenBurnsDown, kenBurnsZoom, kenBurnsPan)
- 轻微浮动 (imageFloat, imageFloatScale)
- 边框动画 (frameReveal, frameExpand)
- 图片旋转 (imageRotateIn, imageRotateSlow)
- 图片滑入 (imageSlideInLeft, imageSlideInRight, imageSlideInUp)
- 脉冲效果 (imagePulse)

**使用方式**:
```html
<link rel="stylesheet" href="../animations/image-animations.css">
<img class="animate-ken-burns-zoom" src="image.jpg">
```

---

### 3. 背景动画库
**文件**: `templates/animations/background-animations.css`

**包含动画**:
- 渐变流动 (gradientFlow, gradientFlowVertical, gradientFlowDiagonal)
- 光晕脉冲 (orbPulse, orbPulseGlow, orbPulseBright)
- 浮动动画 (float, floatHorizontal, floatDiagonal, floatRandom)
- 粒子动画 (particleFloat, particleDrift, particleOrbit)
- 装饰线动画 (lineExpand, lineSlide, linePulse, lineGlow)
- 几何形状动画 (shapeRotate, shapeRotateReverse, shapeScale, shapeMorph)
- 背景遮罩动画 (overlayFadeIn, overlayPulse)
- 霓虹效果 (neonFlicker, neonGlow, neonScan)
- 波浪动画 (waveMove, wavePulse)
- 呼吸效果 (breath, breathSlow)

**使用方式**:
```html
<link rel="stylesheet" href="../animations/background-animations.css">
<div class="orb animate-orb-pulse-glow"></div>
```

---

## 二、已添加动画的模板

### 1. 文艺风格 - 图书摘抄
**文件**: `templates/1080x1920/static_excerpt_animated.html`

**动画效果**:
- ✅ 背景遮罩淡入 (1.5秒)
- ✅ 标题淡入下落 (1秒，延迟0.3秒)
- ✅ 下划线从中心展开 (1秒，延迟0.8秒)
- ✅ 文字逐行出现 (1.2秒，延迟0.6秒)
- ✅ 署名淡入 (1秒，延迟1.2秒)
- ✅ 签名上滑淡入 (1秒，延迟1.5秒)
- ✅ 文字轻微呼吸效果 (持续，5秒周期)

**视觉流程**:
```
0.0s - 背景遮罩淡入
0.3s - 标题从上淡入下落
0.6s - 文字从下淡入上滑
0.8s - 下划线从中心展开
1.2s - 署名淡入
1.5s - 签名上滑淡入
持续 - 文字呼吸效果
```

**适合场景**: 文艺、书摘、语录、诗词

---

### 2. 极简风格 - 黑白简单
**文件**: `templates/1080x1920/image_simple_black_animated.html`

**动画效果**:
- ✅ 标题快速淡入 (0.8秒，延迟0.2秒)
- ✅ 标题轻微脉冲 (持续，4秒周期)
- ✅ 图片从黑色中渐显缩放 (1.2秒，延迟0.5秒)
- ✅ Footer 上滑入场 (1秒，延迟1.5秒)
- ✅ Logo 点依次点亮 (持续，2秒周期)

**视觉流程**:
```
0.2s - 标题快速淡入
0.5s - 图片从黑屏渐显放大
1.5s - Footer 从底部上滑
1.8s - 作者信息淡入
2.0s - Logo 点开始依次点亮
持续 - 标题轻微脉冲 + Logo 点闪烁
```

**适合场景**: 现代、简约、专业、科技

---

### 3. 优雅风格 - 渐变装饰
**文件**: `templates/1080x1920/image_elegant_animated.html`

**动画效果**:

**背景装饰**:
- ✅ Orb 浮动脉冲 (8-10秒周期)
- ✅ 波浪线浮动 (6-7秒周期)
- ✅ 几何形状旋转 (20-25秒周期)
- ✅ 装饰点呼吸 (3秒周期)

**主要内容**:
- ✅ 标题渐变发光 (6秒周期)
- ✅ 标题淡入 (1秒，延迟0.2秒)
- ✅ 图片框缩放入场 (1.2秒，延迟0.5秒)
- ✅ 角标描绘 (0.8秒，延迟0.9-1.2秒)
- ✅ 侧边指示器淡入脉冲 (持续)
- ✅ 文字区域从下浮入 (1秒，延迟0.8秒)
- ✅ 引号标记淡入 (1秒，延迟1.2-1.4秒)
- ✅ 文字条脉动 (持续，4秒周期)
- ✅ Footer 淡入 (1秒，延迟1.5秒)
- ✅ Logo 条脉动 (持续，3秒周期)

**视觉流程**:
```
持续 - 背景元素浮动旋转
0.2s - 标题淡入 + 渐变发光开始
0.5s - 图片框缩放入场
0.8s - 文字区域从下浮入
0.9s - 左上角标描绘
1.0s - 右上角标描绘
1.1s - 右下角标描绘
1.2s - 左下角标描绘 + 引号标记淡入
1.3s - 侧边指示器淡入 + 开始脉冲
1.4s - 右引号标记淡入
1.5s - Footer 淡入 + Logo 条开始脉动
持续 - 所有装饰元素持续动画
```

**适合场景**: 浪漫、梦幻、精致、艺术

---

### 4. 电影风格 - 横屏史诗
**文件**: `templates/1920x1080/image_film_animated.html`

**动画效果**:
- ✅ 标题从黑屏淡入缩放 (1.5秒，延迟0.3秒)
- ✅ 标题缓慢缩放推进 (持续，8秒)
- ✅ 图片 Ken Burns 效果 - 缓慢推进 (持续，10秒)
- ✅ 文字底部淡入上滑 (1.2秒，延迟1.5秒)
- ✅ Footer 延迟淡入 (1秒，延迟2秒)
- ✅ Logo 点依次点亮 (持续，2秒周期)

**视觉流程**:
```
0.3s - 标题从黑屏淡入
0.8s - 图片开始 Ken Burns 推进
2.0s - 标题开始缓慢缩放推进
1.5s - 文字从底部淡入上滑
2.0s - Footer 延迟淡入
2.2s - Logo 点开始依次点亮
持续 - 图片持续推进 + 标题缩放 + Logo 点闪烁
```

**适合场景**: 史诗、大气、震撼、纪录片

---

## 三、动画时间线总览

### 入场动画阶段 (0-3秒)
所有模板都遵循以下顺序：
1. **标题** → 0.2-0.5秒入场
2. **图片** → 0.5-0.8秒入场
3. **文字** → 0.8-1.5秒入场
4. **署名/Footer** → 1.5-2秒入场

### 持续动画阶段 (3秒+)
- 文字呼吸效果
- 图片 Ken Burns 推进
- 背景装饰浮动旋转
- Logo 点闪烁

### 推荐视频时长
- **短视频**: 5-8秒（入场完成 + 少量持续效果）
- **长视频**: 可循环持续动画，或使用 `animation-iteration-count` 控制次数

---

## 四、性能优化建议

### 1. GPU 加速属性
优先使用以下属性（触发硬件加速）：
- ✅ `transform` (translate, scale, rotate)
- ✅ `opacity`
- ❌ 避免使用 `width`, `height`, `margin`, `padding` 做动画

### 2. will-change 提示
对关键动画元素添加：
```css
.title {
  will-change: transform, opacity;
}
```

### 3. 减少重绘
避免频繁改变以下属性：
- `box-shadow` (性能开销大)
- `filter: blur()` (限制 blur 半径 < 100px)
- `background-image` 渐变 (使用 background-position 动画)

### 4. 动画时长控制
- 入场动画：0.8-1.5秒（短促有力）
- 持续动画：3-10秒循环（节奏舒缓）
- 避免动画时长超过 15秒

---

## 五、使用方式

### 方式一：引入动画库
```html
<head>
    <link rel="stylesheet" href="../animations/text-animations.css">
    <link rel="stylesheet" href="../animations/image-animations.css">
    <link rel="stylesheet" href="../animations/background-animations.css">
</head>
<body>
    <div class="title animate-fade-in-up delay-300">标题</div>
    <img class="animate-ken-burns-zoom" src="image.jpg">
    <div class="orb animate-orb-pulse-glow"></div>
</body>
```

### 方式二：直接使用完整动画模板
直接使用 `*_animated.html` 文件，无需额外配置。

### 方式三：自定义动画
从动画库中复制需要的 `@keyframes` 定义到模板中，自定义时长和延迟。

---

## 六、动画效果对比

| 模板风格 | 入场时长 | 持续效果 | 复杂度 | 性能开销 | 适用场景 |
|---------|---------|---------|--------|---------|---------|
| 文艺风格 | 1.5秒 | 文字呼吸 | ⭐⭐ | 低 | 文艺、语录 |
| 极简风格 | 1.5秒 | 标题脉冲 | ⭐⭐ | 低 | 现代、科技 |
| 优雅风格 | 1.5秒 | 多种装饰 | ⭐⭐⭐⭐⭐ | 中高 | 艺术、浪漫 |
| 电影风格 | 2秒 | Ken Burns | ⭐⭐⭐ | 中 | 史诗、纪录 |

---

## 七、测试与验证

### 本地测试
1. 在浏览器中打开 `*_animated.html` 文件
2. 检查动画是否流畅无卡顿
3. 使用 Chrome DevTools Performance 录制分析性能

### ffmpeg 渲染测试
```bash
# 生成测试视频
ffmpeg -loop 1 -i frame.html -t 10 -c:v libx264 output.mp4
```

### 验收标准
- ✅ 动画流畅不卡顿（60fps）
- ✅ CPU 占用 < 30%
- ✅ ffmpeg 渲染时间合理 (< 3秒/帧)
- ✅ 不同分辨率模板均可用

---

## 八、后续扩展

### 可添加的动画效果
1. **打字机效果** - 逐字显示文字
2. **粒子背景** - Canvas 实现粒子动画
3. **SVG 路径动画** - 线条描绘效果
4. **滚动视差** - 多层视差滚动
5. **过渡切换** - 页面切换动画

### 待优化模板
1. `image_neon.html` - 霓虹风格已有部分动画，可增强细节
2. 其他现有模板可按需添加动画

---

## 九、文件清单

### 动画库文件
```
templates/animations/
├── text-animations.css       (已创建)
├── image-animations.css      (已创建)
└── background-animations.css (已创建)
```

### 动画模板文件
```
templates/1080x1920/
├── static_excerpt_animated.html          (已创建)
├── image_simple_black_animated.html      (已创建)
└── image_elegant_animated.html           (已创建)

templates/1920x1080/
└── image_film_animated.html              (已创建)
```

### 文档文件
```
templates/
├── ANIMATION_DESIGN.md        (设计方案)
└── ANIMATION_PREVIEW.md       (本文档)
```

---

## 十、注意事项

### ffmpeg 兼容性
- ✅ 使用纯 CSS3 `@keyframes` 动画
- ✅ 避免使用 JavaScript 控制动画
- ✅ 测试静态帧渲染结果
- ⚠️ 复杂动画可能增加渲染时间

### 浏览器兼容性
- ✅ Chrome 90+（推荐）
- ✅ Safari 14+
- ✅ Firefox 88+
- ⚠️ IE 不支持（项目不支持 IE）

### 性能监控
- 使用 Chrome DevTools Performance 面板录制
- 关注 FPS、CPU、GPU 占用
- 避免同时运行过多复杂动画

---

**生成时间**: 2026-10-25
**作者**: dev-pv-ui-designer
**版本**: v1.0