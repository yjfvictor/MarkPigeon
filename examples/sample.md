# MarkPigeon 综合测试文档

这是一个用于测试 MarkPigeon 各项功能的示例 Markdown 文档，包含图片、公式、外链、代码等多种元素。

## 📷 图片测试

### 本地图片

下面是一张本地图片：

![示例图片](./example.png)

### 网络图片

下面是一张来自网络的图片（不会被打包）：

![GitHub Logo](https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png)

---

## 📐 数学公式

### 行内公式

这是行内公式：$E = mc^2$，描述了质能等价关系。

### 块级公式

高斯定理：

$$
\oint_S \mathbf{E} \cdot d\mathbf{A} = \frac{Q}{\varepsilon_0}
$$

二次方程求根公式：

$$
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$

欧拉恒等式：

$$
e^{i\pi} + 1 = 0
$$

---

## 🔗 外部链接

- [MarkPigeon GitHub](https://github.com/steven-jianhao-li/MarkPigeon) - 项目主页
- [Python 官网](https://www.python.org/) - Python 编程语言
- [Markdown 指南](https://www.markdownguide.org/) - Markdown 语法参考

---

## 💻 代码展示

### Python

```python
def fibonacci(n: int) -> int:
    """计算斐波那契数列第 n 项"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# 使用示例
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

### JavaScript

```javascript
// 异步函数示例
async function fetchData(url) {
    try {
        const response = await fetch(url);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error:', error);
    }
}
```

### Bash

```bash
#!/bin/bash
# 批量转换 Markdown 文件
for file in *.md; do
    echo "Converting: $file"
    markpigeon "$file" --theme github --zip
done
echo "Done!"
```

---

## 📋 表格

| 功能 | 状态 | 优先级 | 说明 |
|------|:----:|:------:|------|
| Markdown 解析 | ✅ | P0 | 支持 CommonMark 标准 |
| 图片提取 | ✅ | P0 | 智能资源隔离 |
| 主题支持 | ✅ | P1 | 兼容 Typora CSS |
| ZIP 打包 | ✅ | P1 | 三种导出模式 |
| 数学公式 | 🔄 | P2 | 需要 MathJax/KaTeX |

---

## 📝 文本格式

- **粗体文本**
- *斜体文本*
- ~~删除线~~
- `行内代码`
- <u>下划线</u>（HTML）
- <mark>高亮文本</mark>（HTML）

---

## 📌 引用

> 📖 "The best way to predict the future is to invent it."
> 
> — Alan Kay

### 嵌套引用

> 这是第一层引用
> > 这是嵌套的第二层引用
> > > 这是第三层引用

---

## ✅ 任务列表

- [x] 完成核心模块开发
- [x] 实现 CLI 接口
- [x] 实现 GUI 接口
- [x] 添加国际化支持
- [ ] 添加数学公式渲染支持
- [ ] 添加代码高亮主题

---

## 📊 列表

### 无序列表

- 苹果 🍎
  - 红富士
  - 青苹果
- 橙子 🍊
- 香蕉 🍌

### 有序列表

1. 第一步：安装依赖
2. 第二步：配置环境
3. 第三步：运行程序
   1. 启动 GUI
   2. 或使用 CLI

---

## 🎯 定义列表

<dl>
  <dt>MarkPigeon</dt>
  <dd>一款功能强大的 Markdown 转 HTML 工具</dd>
  
  <dt>智能资源隔离</dt>
  <dd>自动提取本地图片到独立文件夹，解决分享时图片丢失的问题</dd>
</dl>

---

## 📎 脚注

这是一段带有脚注的文字[^1]。这里还有另一个脚注[^2]。

[^1]: 这是第一个脚注的内容。
[^2]: 这是第二个脚注的内容，包含更多细节。

---

## 🌐 HTML 内嵌

<div style="padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; text-align: center;">
  <h3 style="margin: 0;">MarkPigeon</h3>
  <p style="margin: 10px 0 0 0;">让 Markdown 分享变得优雅简单 ✨</p>
</div>

---

## 🔚 分隔线

以上是各种 Markdown 元素的测试，用于验证 MarkPigeon 的转换功能。

---

*由 MarkPigeon 生成 | [GitHub](https://github.com/steven-jianhao-li/MarkPigeon)*
