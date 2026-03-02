<div align="center">

# 🔍 fineprint

**帮你看合同细则的 AI Agent，再也不用盲签了。**

上传任意合同 → 秒级识别霸王条款、不公平条款，用大白话解释给你听。

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/universeplayer/fineprint/actions/workflows/ci.yml/badge.svg)](https://github.com/universeplayer/fineprint/actions)

**[English](README.md) | [中文](README_CN.md)**

</div>

---

## 痛点

你即将签一份租房合同、保密协议或劳动合同。15 页密密麻麻的法律条文，你有两个选择：

1. **花 300-500 元/小时请律师** 帮你审
2. **闭眼签字**，祈祷没坑

大多数人选了 2。**fineprint** 给你第三个选择：

```bash
fineprint scan 租房合同.pdf
```

```
✔ 已解析 租房合同.pdf（4,521 字符）

┌────────────────────────────────────────┐
│  FINEPRINT 合同分析报告                │
│  合同类型：租赁合同                    │
└────────────────────────────────────────┘

⬤ 红旗警告（发现 5 项）
==================================================

  1. 押金不退
     条款：第三条
     "押金不予退还，合同终止时由出租方保留"
     大部分地区法规要求押金可退。
     此条款可能违法。
     建议：删除"不予退还"表述。

  2. 房东可随时进入无需通知
     条款：第五条
     "出租方有权随时进入房屋，无需提前通知"
     法律通常要求提前24小时书面通知。
     建议：增加"需提前24小时书面通知"

  3. 租客承担房屋结构维修
     ...

⚠ 注意事项（发现 3 项）
==================================================
  ...

✔ 保护条款（发现 2 项）
==================================================
  ...

╭─ 公平性评分 ──────────────────────────────────────╮
│  ████████████░░░░░░░░░░░░░░  D  (28/100)           │
│                                                      │
│  5 项红旗  3 项注意  2 项保护  4 项缺失              │
╰──────────────────────────────────────────────────────╯
```

## 快速上手

### 安装

```bash
pip install fineprint-ai
```

### 配置 API Key

fineprint 兼容任何 OpenAI 协议的 API。推荐使用 [OpenRouter](https://openrouter.ai/)（支持 Claude、GPT-4、DeepSeek 等 100+ 模型）：

```bash
export OPENROUTER_API_KEY=sk-or-...
```

也可以直接用 OpenAI：
```bash
export OPENAI_API_KEY=sk-...
export OPENAI_BASE_URL=https://api.openai.com/v1
```

或者用本地模型（Ollama），数据完全不出本机：
```bash
export OPENAI_BASE_URL=http://localhost:11434/v1
export OPENAI_API_KEY=ollama
fineprint scan contract.pdf --model llama3.1
```

### 扫描合同

```bash
# 扫描 PDF 合同
fineprint scan 租房合同.pdf

# 扫描 Word 文档
fineprint scan 劳动合同.docx

# 扫描文本文件
fineprint scan 保密协议.txt

# 指定模型
fineprint scan contract.pdf --model openai/gpt-4o

# 保存 Markdown 报告
fineprint scan contract.pdf -o report.md

# 输出原始 JSON
fineprint scan contract.pdf --json
```

### Python API

```python
from fineprint.analyzer import analyze_contract
from fineprint.parser import extract_text

text = extract_text("租房合同.pdf")
result = analyze_contract(text)

print(f"公平性: {result.fairness_grade} ({result.fairness_score}/100)")
for flag in result.red_flags:
    print(f"🔴 {flag.title}: {flag.explanation}")
```

## 支持的文件格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| PDF | `.pdf` | 文字型 PDF（扫描件需要 `--ocr`） |
| Word | `.docx` | Microsoft Word 文档 |
| 文本 | `.txt` | 纯文本文件 |
| Markdown | `.md` | Markdown 文件 |

## 支持的合同类型

fineprint 自动识别合同类型并调整分析策略：

- 🏠 **租赁合同** — 租金、押金、维修责任、出入权
- 📝 **保密协议（NDA）** — 保密范围、期限、竞业限制
- 💼 **劳动合同** — 竞业禁止、知识产权归属、解约条款
- 🤝 **自由职业/外包合同** — 付款条款、知识产权归属
- 📱 **SaaS 服务条款** — 数据所有权、责任限制、自动续费
- 💰 **贷款合同** — 利率、提前还款违约金、违约条款
- 🛒 **买卖合同** — 保修、退换货、争议解决

## 工作原理

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌─────────────┐
│  上传        │────▶│  解析        │────▶│  AI 分析     │────▶│  生成报告   │
│  合同文件    │     │  提取文本    │     │  逐条审查    │     │  风险评分   │
│  (PDF/DOCX)  │     │              │     │              │     │             │
└─────────────┘     └──────────────┘     └──────────────┘     └─────────────┘
```

1. **解析** — 从 PDF、DOCX 或 TXT 文件中提取文本
2. **识别** — 自动判断合同类型
3. **分析** — AI Agent 逐条审查每个条款：
   - 红旗警告（可能造成经济损失或权益受损的严重问题）
   - 注意事项（值得协商但不至于致命的问题）
   - 保护条款（对你有利的条款）
   - 缺失保护（标准合同中应有但缺失的条款）
4. **评分** — 生成公平性等级（A+ 到 F）
5. **报告** — 终端美化输出或导出 Markdown 报告

## 试用示例合同

```bash
# 克隆仓库
git clone https://github.com/universeplayer/fineprint.git
cd fineprint

# 安装
pip install -e .

# 扫描示例租赁合同（故意包含很多坑）
export OPENROUTER_API_KEY=sk-or-...
fineprint scan examples/sample_lease.txt

# 扫描示例保密协议
fineprint scan examples/sample_nda.txt
```

## 常见问题

**这算法律建议吗？**
不算。fineprint 是帮你理解合同条款的教育工具。正式的法律建议请咨询专业律师。

**我的合同数据会上传到云端吗？**
合同文本会发送到你配置的 LLM 服务商（OpenRouter、OpenAI 等）。如果对隐私有要求，可以通过 Ollama 使用本地模型，数据完全不出本机。

**准确率怎么样？**
fineprint 使用最先进的大模型（Claude、GPT-4），它们在法律文本分析上表现出色。但可能会遗漏人类律师能发现的细微问题。把它当作第一道筛查，而不是律师的替代品。

**支持中文合同吗？**
支持！fineprint 支持底层大模型所支持的任何语言。中英文合同均可分析。

## 贡献

欢迎贡献代码！详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

[MIT](LICENSE) — 随意使用。

---

<div align="center">

**如果 fineprint 帮你避开了一份坑人合同，请给个 ⭐**

[报告问题](https://github.com/universeplayer/fineprint/issues) · [功能建议](https://github.com/universeplayer/fineprint/issues)

</div>
