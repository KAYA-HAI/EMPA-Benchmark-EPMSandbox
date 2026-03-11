<p align="right">
  <a href="README.md">English</a>  |  <a href="README_zh.md">中文</a>
</p>

<p align="center">
  <img src="assets/empa_logo.png" alt="EMPA Logo" width="180">
</p>

<h1 align="center">EMPA：人格对齐共情的过程化评估</h1>

<p align="center">
  <b>共情势能建模与评估（Empathy Potential Modeling and Assessment）</b>
</p>

<p align="center">
  <a href="https://arxiv.org/abs/2603.00552"><img src="https://img.shields.io/badge/arXiv-2603.00552-b31b1b.svg" alt="arXiv"></a>
  <img src="https://img.shields.io/badge/许可证-CC_BY--NC_4.0-lightgrey.svg" alt="License">
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB.svg" alt="Python">
  <img src="https://img.shields.io/badge/已评估模型-16-green.svg" alt="Models">
  <img src="https://img.shields.io/badge/场景数-1010-orange.svg" alt="Scenarios">
  <a href="https://huggingface.co/datasets/SalmonTell/EMPA-character_card"><img src="https://img.shields.io/badge/🤗_HuggingFace-数据集-FFD21E.svg" alt="Dataset"></a>
</p>

<p align="center">
  <a href="https://arxiv.org/abs/2603.00552">论文</a>  | 
  <a href="https://huggingface.co/datasets/SalmonTell/EMPA-character_card">数据集</a>  | 
  <a href="#-排行榜">排行榜</a>  | 
  <a href="#-快速开始">快速开始</a>  | 
  <a href="#-框架">框架</a>  | 
  <a href="#-命令行参考">命令行参考</a>  | 
  <a href="#-引用">引用</a>
</p>

---

## 目录

- [🍊 概述](#-概述)
- [🌱 最新动态](#-最新动态)
- [🧩 框架](#-框架)
- [🏆 排行榜](#-排行榜)
- [🚀 快速开始](#-快速开始)
- [🥥 命令行参考](#-命令行参考)
- [🍓 工作原理](#-工作原理)
- [🫐 官方最佳实践](#-官方最佳实践)
- [🍍 编程接口](#-编程接口)
- [🍈 仓库结构](#-仓库结构)
- [🍋 常见问题](#-常见问题)
- [🍑 贡献指南](#-贡献指南)
- [🍒 许可证与使用](#-许可证与使用)
- [🍐 引用](#-引用)
- [🍉 联系方式](#-联系方式)

---

## 🍊 概述

**EMPA** 是首个将共情视为 **动态过程（Process）** 而非静态响应的评估基准。我们认为，真正的共情能力潜伏于对话的 **隐式空间（Latent Space）** 中，必须通过多轮交互的轨迹信号来捕捉。

不同于传统基准仅关注单轮回复的情感强度，EMPA 引入了心理物理学的势能模型，量化智能体在 **人格对齐（Persona Alignment）** 约束下的持续做功。这使得我们能够区分“表面动听”与“真正有效”的千人千面的个性化对齐，为构建具备长期策略稳定性的情感智能体提供了严谨的度量标准和可训练改造的沙盒环境和评测接口。

在评估方法论上，EMPA 提出了 **基于评分准则的物理评估范式（Rubric-Grounded Physics Evaluation）**，从根本上区别于两类主流方法：传统的 **准则清单式评分（Rubric Checklist）** 按条目逐项核查后坍缩为标量分数，丢失过程信息；而 **LLM-as-a-Judge** 则由模型黑盒给出最终裁定，容易受到表述风格、回复长度和提示措辞的系统性干扰。EMPA 将二者的长处拆开再重新组合——评分准则专注于从对话中提取可追溯的结构化证据，物理模型则负责沿轨迹聚合这些证据，生成过程级度量。多个实验表明，这种 **证据生成与分数计算的结构性分离** 大幅提高了评估对提示扰动的鲁棒性以及对模型间差异的区分灵敏度。更重要的是，在方法论层面，这一从评分准则中提取结构化证据、再经物理模型聚合为轨迹度量的评估范式具有通用可泛化性——它不依赖于共情这一特定构念，而是适用于一切可被分解并操作化定义的主观心理变量（如信任感、行为动机、认知负荷等）。在工程层面，本仓库提供了开箱即用的 Rubric 套件插拔接口：研究者只需替换评分准则与变量分解模块，即可将自定义的结构化主观心理变量接入 EPM 轨迹引擎，框架代码与对话沙盒层的评估流程无需任何改动。

**EMPA 提供：**

- 🎭 **[1,010 个心理学扎根的场景](https://huggingface.co/datasets/SalmonTell/EMPA-character_card)**，通过 Real-to-Sim 管线从真实交互中提炼，每个场景包含人格卡片、长期记忆、共情阈值和危机叙事。
- 🤖 **非脚本化的多智能体沙盒**，用户智能体、导演智能体、裁判智能体和被测模型在开放式多轮对话中交互——暴露出单轮评估无法发现的策略适应性和失败模式。
- 📐 **共情能量模型（EPM）**——一种轨迹级形式化方法，将共情行为建模为潜在心理状态空间（认知 C × 情感 A × 动机 P）中方向约束的做功，捕捉方向对齐、累积影响和策略稳定性。
- 📊 **EPM-Q**——一种标准化的、场景归一化的质量指标，包含 3 个维度下的 9 项指标，支持超越二元成功/失败的细粒度跨模型对比。

> *"说得多不等于做得对。"*
> ——EPM 将方向对齐与响应强度分离。情感表达强烈但方向偏离的回复将获得零分或负分；只有持续的、方向正确的支持才能积累走向成功。

<p align="center">
  <img src="assets/storyboard_new1.jpg" alt="EMPA 故事板：为什么标量共情打分会失败" width="900">
</p>

一个真实的 EMPA 沙盒交互，展示了在 EPM 的方向性评估下，高强度但方向偏离的回复如何失败——看似优秀的共情支持，在以人格需求为标准衡量时实际上表现很差。
完整技术细节请参阅论文：**[EMPA: Evaluating Persona-Aligned Empathy as a Process](https://arxiv.org/abs/2603.00552)**（arXiv:2603.00552）。

## 🌱 最新动态

- **2026-03-11** 🚀

  - **EMPA 首次正式开源发布** — 包含 1,010 个场景、16 模型排行榜、完整 CLI 和评估工具包。
- **2026-03-06** 🤝

  - **[MAPO: Mixed Advantage Policy Optimization](https://arxiv.org/abs/2603.06194)** — 将 EMPA 作为多轮对话 RL 的实时训练环境。在 7B–32B 多个模型尺度上，无论是 outcome-only GRPO 还是更先进的 MAPO 算法，均从 EMPA 的过程级奖励信号中获得了稳定的训练收益（EMPA 分数最高提升 +43.2），验证了 EMPA 对 RL 训练的鲁棒支撑能力，并泛化至 EmoBench 与 EQ-Bench。
- 🔥🔥 **2026-03-01** 🔥🔥

  - **[EMPA: Evaluating Persona-Aligned Empathy as a Process](https://arxiv.org/abs/2603.00552)** — **核心论文发布**。
  - 我们提出了首个 **RL-Friendly（强化学习友好）** 的主观对话评估基准。EMPA 围绕共情场景构建，内置 1,010 个心理学扎根的 Persona-Aligned 场景与经过校准的评估量规，提供开箱即用的人格对齐共情最佳实践。通过引入物理学 EPM 轨迹形式化方法，我们将隐空间中的用户状态转化为逐轮可计算、可优化的过程级信号，同时支持**可复现的模型对比**与**下游强化学习优化**。该范式可推广至一切受隐变量动态和弱验证反馈驱动的智能体场景。 [[论文]](https://arxiv.org/abs/2603.00552)
- **2025-11-29** 🧪

  - **[Echo-N1: Affective RL Frontier](https://arxiv.org/abs/2512.00344)** — 首次采用 EMPA 评估经 RL 训练的情感智能体，证明了主观对话领域的 RL 是一个可解且具有变革意义的问题。

---

## 🧩 框架

<p align="center">
  <img src="assets/empa_framework.png" alt="EMPA 框架概览" width="900">
</p>

EMPA 由四个集成组件构成：

<table>
  <thead>
    <tr>
      <th width="5%" align="center">#</th>
      <th width="20%">组件</th>
      <th width="75%">描述</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><strong>1</strong></td>
      <td><strong>数据管线：Real-to-Sim</strong></td>
      <td>通过去语境化、再语境化和验证，将众包对话提炼为心理学扎根的场景。全部 <strong>1,010 个场景</strong>及预计算的 IEDR 向量随包发布在 <a href="empa/data/"><code>empa/data/</code></a>。完整的人格卡片数据集也已发布在 <a href="https://huggingface.co/datasets/SalmonTell/EMPA-character_card">🤗 HuggingFace</a>。</td>
    </tr>
    <tr>
      <td align="center"><strong>2</strong></td>
      <td><strong>多智能体沙盒</strong></td>
      <td>四角色架构——<strong>用户智能体</strong>（人格 + 记忆库）、<strong>导演智能体</strong>（中央控制器，观察→决策→执行）、<strong>裁判智能体</strong>（基于rubics的证据裁决者）和<strong>被测模型</strong>。交互非脚本化、完全开放。</td>
    </tr>
    <tr>
      <td align="center"><strong>3</strong></td>
      <td><strong>EPM 编排器</strong></td>
      <td>在潜在心理状态空间 <b>P</b><sub>t</sub> ∈ ℝ³（认知 × 情感 × 动机）中运行。计算向量化共情做功 ΔE<sub>t</sub> = ‖<b>v</b><sub>t</sub>‖ · cos θ<sub>t</sub>，并执行能量门控三元成功判定。</td>
    </tr>
    <tr>
      <td align="center"><strong>4</strong></td>
      <td><strong>标准化 EPM-Q 指标</strong></td>
      <td>按每个案例的初始赤字 r₀ = ‖<b>P</b>₀‖ 逐案归一化。三个评估维度——结果质量、过程效率、策略稳定性——综合为最终加权 EPM-Q 分数。</td>
    </tr>
  </tbody>
</table>

### 包结构

```
empa/
├── core/            # 向量引擎、能量动力学、EPM 评分
├── rubric/          # RubricConfig 接口 + empathy_v2 量规（IEDR、MDEP-PR）
├── agents/          # 用户智能体、导演智能体、裁判智能体、被测模型
├── orchestrator/    # 对话循环 + EPM 状态管理
├── evaluation/      # EPM-Q 计算 + 描述性统计
├── visualization/   # 3D 轨迹图、柱状图/雷达图、汇总表
├── llm/             # LLM 适配器（OpenAI 兼容 API）
├── data/            # 1,010 个基准场景 + 预计算 IEDR 向量
│   ├── cases/       # 人格卡片、危机叙事、场景元数据
│   ├── scenarios/   # 结构化场景配置
│   └── precomputed/ # 预标注 IEDR 赤字向量
└── cli.py           # 命令行入口
```

---

## 🏆 排行榜

官方 30 案例基准测试的 EPM-Q 分数。
**配置：** K=1（每轮评估）、max_turns=45、基础设施模型：Gemini 2.5 Pro。

<table>
  <thead>
    <tr>
      <th rowspan="2">排名</th>
      <th rowspan="2">模型</th>
      <th colspan="3">结果质量</th>
      <th colspan="3">过程效率</th>
      <th colspan="3">策略稳定性</th>
      <th rowspan="2">EPM-Q</th>
    </tr>
    <tr>
      <th>RDI</th>
      <th>E<sub>tot</sub></th>
      <th>S<sub>net</sub></th>
      <th>ρ</th>
      <th>S<sub>proj</sub></th>
      <th>τ</th>
      <th>R<sub>pos</sub></th>
      <th>Align</th>
      <th>Pen</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center">1</td>
      <td>Claude 4.6 Opus</td>
      <td align="center">99.5</td>
      <td align="center">117.6</td>
      <td align="center">122.0</td>
      <td align="center">139.0</td>
      <td align="center">128.4</td>
      <td align="center">96.9</td>
      <td align="center">91.5</td>
      <td align="center">92.4</td>
      <td align="center">98.9</td>
      <td align="center"><strong>107.2</strong></td>
    </tr>
    <tr>
      <td align="center">2</td>
      <td>Gemini 3 Pro Preview</td>
      <td align="center">98.1</td>
      <td align="center">100.3</td>
      <td align="center">113.9</td>
      <td align="center">111.4</td>
      <td align="center">103.4</td>
      <td align="center">95.8</td>
      <td align="center">90.7</td>
      <td align="center">92.2</td>
      <td align="center">97.8</td>
      <td align="center"><strong>99.8</strong></td>
    </tr>
    <tr>
      <td align="center">3</td>
      <td>GPT-5.2 Pro</td>
      <td align="center">97.7</td>
      <td align="center">95.5</td>
      <td align="center">113.4</td>
      <td align="center">102.5</td>
      <td align="center">95.3</td>
      <td align="center">94.2</td>
      <td align="center">89.9</td>
      <td align="center">91.7</td>
      <td align="center">97.9</td>
      <td align="center"><strong>97.6</strong></td>
    </tr>
    <tr>
      <td align="center">4</td>
      <td>Gemini 2.5 Pro</td>
      <td align="center">92.6</td>
      <td align="center">90.1</td>
      <td align="center">124.2</td>
      <td align="center">65.5</td>
      <td align="center">62.2</td>
      <td align="center">81.4</td>
      <td align="center">88.2</td>
      <td align="center">87.1</td>
      <td align="center">93.8</td>
      <td align="center"><strong>90.7</strong></td>
    </tr>
    <tr>
      <td align="center">5</td>
      <td>Qwen 3 235B</td>
      <td align="center">92.0</td>
      <td align="center">91.7</td>
      <td align="center">121.3</td>
      <td align="center">88.3</td>
      <td align="center">82.6</td>
      <td align="center">74.0</td>
      <td align="center">80.2</td>
      <td align="center">82.0</td>
      <td align="center">82.3</td>
      <td align="center"><strong>89.6</strong></td>
    </tr>
    <tr>
      <td align="center">6</td>
      <td>Seed 2.0</td>
      <td align="center">90.9</td>
      <td align="center">87.2</td>
      <td align="center">134.2</td>
      <td align="center">55.7</td>
      <td align="center">53.1</td>
      <td align="center">70.8</td>
      <td align="center">83.1</td>
      <td align="center">84.0</td>
      <td align="center">88.1</td>
      <td align="center"><strong>87.6</strong></td>
    </tr>
    <tr>
      <td align="center">7</td>
      <td>Kimi k2</td>
      <td align="center">87.3</td>
      <td align="center">86.6</td>
      <td align="center">123.2</td>
      <td align="center">72.6</td>
      <td align="center">68.3</td>
      <td align="center">70.2</td>
      <td align="center">80.1</td>
      <td align="center">81.6</td>
      <td align="center">82.1</td>
      <td align="center"><strong>86.2</strong></td>
    </tr>
    <tr>
      <td align="center">8</td>
      <td>Claude 3.5 Sonnet</td>
      <td align="center">91.9</td>
      <td align="center">83.3</td>
      <td align="center">128.3</td>
      <td align="center">54.8</td>
      <td align="center">52.2</td>
      <td align="center">72.3</td>
      <td align="center">79.1</td>
      <td align="center">81.5</td>
      <td align="center">84.7</td>
      <td align="center"><strong>85.1</strong></td>
    </tr>
    <tr>
      <td align="center">9</td>
      <td>DeepSeek V3</td>
      <td align="center">84.3</td>
      <td align="center">78.8</td>
      <td align="center">119.7</td>
      <td align="center">58.4</td>
      <td align="center">55.3</td>
      <td align="center">58.6</td>
      <td align="center">71.5</td>
      <td align="center">73.8</td>
      <td align="center">74.0</td>
      <td align="center"><strong>78.4</strong></td>
    </tr>
    <tr>
      <td align="center">10</td>
      <td>Seed 1.6</td>
      <td align="center">28.3</td>
      <td align="center">21.6</td>
      <td align="center">74.6</td>
      <td align="center">8.4</td>
      <td align="center">8.1</td>
      <td align="center">46.4</td>
      <td align="center">48.4</td>
      <td align="center">57.5</td>
      <td align="center">61.6</td>
      <td align="center"><strong>43.1</strong></td>
    </tr>
    <tr>
      <td align="center">11</td>
      <td>Llama 3.3 70B</td>
      <td align="center">27.0</td>
      <td align="center">10.0</td>
      <td align="center">76.0</td>
      <td align="center">5.2</td>
      <td align="center">5.0</td>
      <td align="center">30.1</td>
      <td align="center">48.3</td>
      <td align="center">55.5</td>
      <td align="center">52.2</td>
      <td align="center"><strong>38.5</strong></td>
    </tr>
    <tr>
      <td align="center">12</td>
      <td>GPT-4o</td>
      <td align="center">18.7</td>
      <td align="center">14.3</td>
      <td align="center">61.4</td>
      <td align="center">5.7</td>
      <td align="center">5.5</td>
      <td align="center">58.4</td>
      <td align="center">38.2</td>
      <td align="center">47.0</td>
      <td align="center">38.7</td>
      <td align="center"><strong>33.7</strong></td>
    </tr>
    <tr>
      <td align="center">13</td>
      <td>Doubao 1.5</td>
      <td align="center">23.8</td>
      <td align="center">12.3</td>
      <td align="center">46.3</td>
      <td align="center">5.2</td>
      <td align="center">5.0</td>
      <td align="center">47.9</td>
      <td align="center">36.5</td>
      <td align="center">41.1</td>
      <td align="center">37.8</td>
      <td align="center"><strong>30.2</strong></td>
    </tr>
    <tr>
      <td align="center">14</td>
      <td>Qwen 3 32B</td>
      <td align="center">5.4</td>
      <td align="center">0.0</td>
      <td align="center">7.7</td>
      <td align="center">0.0</td>
      <td align="center">0.0</td>
      <td align="center">77.7</td>
      <td align="center">20.9</td>
      <td align="center">30.0</td>
      <td align="center">7.9</td>
      <td align="center"><strong>14.8</strong></td>
    </tr>
    <tr>
      <td align="center">15</td>
      <td>Llama 3.1 8B</td>
      <td align="center">2.6</td>
      <td align="center">0.0</td>
      <td align="center">0.4</td>
      <td align="center">0.0</td>
      <td align="center">0.0</td>
      <td align="center">82.6</td>
      <td align="center">19.5</td>
      <td align="center">27.7</td>
      <td align="center">15.8</td>
      <td align="center"><strong>14.3</strong></td>
    </tr>
    <tr>
      <td align="center">16</td>
      <td>Qwen 3 8B</td>
      <td align="center">1.2</td>
      <td align="center">0.0</td>
      <td align="center">0.9</td>
      <td align="center">0.0</td>
      <td align="center">0.0</td>
      <td align="center">85.0</td>
      <td align="center">16.1</td>
      <td align="center">25.5</td>
      <td align="center">5.0</td>
      <td align="center"><strong>12.2</strong></td>
    </tr>
  </tbody>
</table>

> $\text{EPM-Q} = 0.4 \times \text{Outcome} + 0.2 \times \text{Efficiency} + 0.4 \times \text{Stability}$

全部 16 个模型的逐指标明细、逐案例对话记录和描述性统计报告见 [`results/benchmark_runs/epm-bench/`](results/benchmark_runs/epm-bench/)。

### EPM 轨迹全景

上方的数字在隐空间轨迹中得以具象化。每条线代表一个案例；蓝色为成功、红色为失败。强模型的轨迹果断地远离原点；弱模型则产生分散、无方向的路径。

<p align="center">
  <img src="results/benchmark_runs/epm-bench/analysis_figures/05_model_comparison/fig_trajectory_grid_cover_3x4.png" alt="EPM 轨迹网格 — 12 模型 × 30 案例" width="900">
</p>

<details>
<summary><b>更多可视化：9 维指标分解 & 人格韧性雷达图</b></summary>

<p align="center">
  <img src="results/benchmark_runs/epm-bench/analysis_figures/02_bar_charts/fig_epmq_errorbar_bars.png" alt="EPM-Q 9 维指标柱状图（均值 ± 标准差）" width="900">
</p>

<p align="center">
  <img src="results/benchmark_runs/epm-bench/analysis_figures/03_radar_charts/fig_epmq_radar_grid_persona.png" alt="人格韧性画像 — 雷达图" width="900">
</p>

</details>

---

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/your-org/empa.git
cd empa
pip install -e ".[all]"       # 核心 + 评估 + 可视化
```

最小安装（仅运行基准测试，不含绘图）：

```bash
pip install -e .
```

**依赖概览：**

<table>
  <thead>
    <tr>
      <th width="15%">安装选项</th>
      <th width="35%">包</th>
      <th width="50%">用途</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><i>（核心）</i></td>
      <td><code>openai</code>、<code>httpx</code>、<code>python-dotenv</code></td>
      <td>LLM API 调用与编排</td>
    </tr>
    <tr>
      <td><code>evaluation</code></td>
      <td><code>numpy</code>、<code>pandas</code>、<code>openpyxl</code></td>
      <td>EPM-Q 计算、统计分析、Excel 报告</td>
    </tr>
    <tr>
      <td><code>visualization</code></td>
      <td><code>matplotlib</code>、<code>scipy</code>、<code>numpy</code></td>
      <td>3D 轨迹图、柱状图/雷达图</td>
    </tr>
    <tr>
      <td><code>all</code></td>
      <td>以上全部</td>
      <td>完整功能</td>
    </tr>
  </tbody>
</table>

### 环境配置

EMPA 默认使用 [OpenRouter](https://openrouter.ai/) 作为统一的 LLM 网关。所有模型——基础设施智能体和被测模型——均通过 OpenRouter 访问。

```bash
export OPENROUTER_API_KEY="sk-or-..."
```

也可以在项目根目录创建 `.env` 文件：

```
OPENROUTER_API_KEY=sk-or-...
```

**自定义端点** — 测试本地部署的模型（如 vLLM、SGLang 或 Ollama）：

```bash
empa run --model default \
    --test-base-url http://localhost:8000/v1 \
    --test-api-key EMPTY
```

### 运行基准测试

```bash
# 对某个模型运行官方 30 案例基准测试
empa run --model openai/gpt-4o

# 仅运行指定案例
empa run --model openai/gpt-4o --cases script_003,script_010

# 列出所有可用的基准案例
empa list-cases
```

默认配置（与论文一致）：

<table>
  <thead>
    <tr>
      <th width="20%">参数</th>
      <th width="25%">默认值</th>
      <th width="55%">说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>K</strong></td>
      <td><code>1</code></td>
      <td>评估间隔（每轮评估）</td>
    </tr>
    <tr>
      <td><strong>max_turns</strong></td>
      <td><code>45</code></td>
      <td>达到最大轮次后截断对话</td>
    </tr>
    <tr>
      <td><strong>基础设施模型</strong></td>
      <td><code>google/gemini-2.5-pro</code></td>
      <td>用户智能体、裁判智能体、导演智能体的模型</td>
    </tr>
    <tr>
      <td><strong>EPM 能量动力学</strong></td>
      <td><code>启用</code></td>
      <td>完整的能量门控成功/失败检测</td>
    </tr>
  </tbody>
</table>

---

## 🥥 命令行参考

### `empa run`

对一个或多个模型运行基准测试。

```bash
empa run --model <model_id> [options]
```

<table>
  <thead>
    <tr>
      <th width="20%">选项</th>
      <th width="80%">说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>--model</code></td>
      <td>OpenRouter 模型 ID（如 <code>openai/gpt-4o</code>、<code>anthropic/claude-4.6-opus</code>）</td>
    </tr>
    <tr>
      <td><code>--cases</code></td>
      <td>逗号分隔的案例 ID（默认：全部 30 个案例）</td>
    </tr>
    <tr>
      <td><code>--output-dir</code></td>
      <td>输出目录（默认：<code>results/benchmark_runs/</code>）</td>
    </tr>
    <tr>
      <td><code>--test-base-url</code></td>
      <td>被测模型的自定义 API 基础 URL</td>
    </tr>
    <tr>
      <td><code>--test-api-key</code></td>
      <td>自定义被测模型端点的 API Key</td>
    </tr>
  </tbody>
</table>

### `empa evaluate`

为已完成的基准测试运行生成描述性统计报告。

```bash
# 输出：<model_dir>/descriptive_statistics.{csv,xlsx,md}
empa evaluate results/benchmark_runs/epm-bench/claude-4.6-opus/
```

生成 CSV、Excel（含格式化表头）和 Markdown 报告，包含 EPM-Q 指标、场景元数据、SP 特征和逐案例分析。

### `empa visualize`

为某个模型生成多视角 3D 轨迹可视化。

```bash
# 输出：<model_dir>/<model>_trajectory.{png,pdf}
empa visualize results/benchmark_runs/epm-bench/claude-4.6-opus/
```

生成出版级 2×2 布局：3D 总览 + XY（认知–情感）、XZ（认知–前摄）、YZ（情感–前摄）投影，含 B 样条平滑轨迹。

### `empa compare`

生成多模型对比图表和表格。

```bash
empa compare <benchmark_dir> --chart <type> [options]
```

<table>
  <thead>
    <tr>
      <th width="15%">选项</th>
      <th width="35%">可选值</th>
      <th width="50%">说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>--chart</code></td>
      <td><code>bars</code>、<code>radar</code>、<code>table</code>、<code>summary</code>、<code>all</code></td>
      <td>要生成的图表类型</td>
    </tr>
    <tr>
      <td><code>--models</code></td>
      <td><code>"model1,model2,..."</code></td>
      <td>模型子集（默认：所有已发现模型）</td>
    </tr>
    <tr>
      <td><code>--radar-type</code></td>
      <td><code>categories</code>、<code>mechanism</code>、<code>persona</code></td>
      <td>雷达图分组方式</td>
    </tr>
  </tbody>
</table>

**示例：**

```bash
# 一次性生成全部对比输出
empa compare results/benchmark_runs/epm-bench/ --chart all

# 仅生成误差棒图
empa compare results/benchmark_runs/epm-bench/ --chart bars

# 雷达图 — 指定分组
empa compare results/benchmark_runs/epm-bench/ --chart radar --radar-type persona

# 选择特定模型进行对比
empa compare results/benchmark_runs/epm-bench/ \
    --models "claude-4.6-opus,gpt-5.2-pro,gemini-2.5-pro" --chart all

# EPM-Q 汇总表（合并 Excel + CSV）
empa compare results/benchmark_runs/epm-bench/ --chart summary
```

### `empa list-cases`

列出所有可用的基准案例及元数据。

```bash
empa list-cases
```

---

## 🍓 工作原理

EMPA 将共情支持概念化为*对潜在心理状态的持续干预*，而非孤立的情感反应。完整技术细节请参阅[论文](https://arxiv.org/abs/2603.00552)。

### 共情能量模型（EPM）

**1. 潜在状态初始化** — 对话开始前，裁判智能体填写初始共情赤字评级（IEDR），生成三维空间中的起始赤字向量 $\mathbf{P}_0 = (C_0,\; A_0,\; P_0)$。到原点（平衡态）的距离 $\lVert \mathbf{P}_0 \rVert$ 量化了基线阻力。

**2. 多智能体对话** — 每轮中，用户智能体发言（由导演智能体的剧情控制和记忆释放引导），被测模型回复。交互是非脚本化的开放式对话。导演执行"观察→决策→执行"循环，通过函数调用（而非提示词）进行记忆注入、策略调整、节奏控制或终止。

**3. 基于量规的证据评估** — 每 K 轮，裁判智能体使用多维共情进展量规（MDEP-PR）评估最近的对话窗口，输出每个维度的证据、推理、进展等级和退步等级。证据可追溯且可归因到具体的模型行为。

**4. 轨迹更新** — 评分引擎将量规输出映射为动作向量 $\vec{v}_t$，然后计算有效共情做功 $\Delta E_t = \lVert \vec{v}_t \rVert \cdot \cos\theta_t$，其中 $\cos\theta_t$ 是动作与理想共情方向 $\vec{v}_t^* = \text{Normalize}(-\mathbf{P}_t)$ 之间的对齐度。位置更新为 $\mathbf{P}_t = \mathbf{P}_{t-1} + \vec{v}_t$。

**5. 能量门控终止** — 成功需要通过累积能量门（$E_{\text{total}} > \epsilon_{\text{energy}}$）*并且*满足以下之一：

- **结果成功**：$\lVert \mathbf{P}_T \rVert < \epsilon_{\text{dist}}$（状态趋近平衡态），或
- **过程成功**：$\cos\theta > \tau_{\text{align}}$（尽管阻力大，仍保持持续的方向对齐）。

三个失败检测器捕捉：方向崩塌、停滞和持续性退步。

### EPM-Q 评分

9 项场景归一化指标表征交互质量：

<table>
  <thead>
    <tr>
      <th width="20%">维度</th>
      <th width="15%">指标</th>
      <th width="65%">衡量内容</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="3"><strong>结果质量</strong><br>(w = 0.4)</td>
      <td align="center">RDI</td>
      <td rowspan="3">模型是否化解了赤字？做了多少有效功？</td>
    </tr>
    <tr>
      <td align="center">E<sub>total</sub></td>
    </tr>
    <tr>
      <td align="center">S<sub>net</sub></td>
    </tr>
    <tr>
      <td rowspan="3"><strong>过程效率</strong><br>(w = 0.2)</td>
      <td align="center">ρ</td>
      <td rowspan="3">到达目标的效率如何？是否存在策略性迂回？</td>
    </tr>
    <tr>
      <td align="center">S<sub>proj</sub></td>
    </tr>
    <tr>
      <td align="center">τ</td>
    </tr>
    <tr>
      <td rowspan="3"><strong>策略稳定性</strong><br>(w = 0.4)</td>
      <td align="center">R<sub>pos</sub></td>
      <td rowspan="3">方向对齐的一致性如何？是否存在表演性或有害行为？</td>
    </tr>
    <tr>
      <td align="center">Align</td>
    </tr>
    <tr>
      <td align="center">R<sub>pen</sub></td>
    </tr>
  </tbody>
</table>

$$
\text{EPM-Q} = 0.4 \times \text{Outcome} + 0.2 \times \text{Efficiency} + 0.4 \times \text{Stability}
$$

所有指标均按每个案例的初始赤字半径 $r_0 = \lVert \mathbf{P}_0 \rVert$ 归一化，防止简单场景获得不公平优势。

---

## 🫐 官方最佳实践

### EPM 参数

以下参数在官方基准测试中已固定，为保证可复现的对比**不应修改**。定义在 `empa/rubric/empathy_v2/config.py` 和 `empa/rubric/base.py` 中。

<table>
  <thead>
    <tr>
      <th width="25%">参数</th>
      <th width="15%">值</th>
      <th width="60%">含义</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>K</strong>（eval_interval）</td>
      <td align="center"><code>1</code></td>
      <td>裁判<strong>每轮</strong>评估（最小粒度）</td>
    </tr>
    <tr>
      <td><strong>max_turns</strong></td>
      <td align="center"><code>45</code></td>
      <td>第 45 轮前未终止则截断对话</td>
    </tr>
    <tr>
      <td><strong>min_turns</strong></td>
      <td align="center"><code>12</code></td>
      <td>第 12 轮前不能宣告成功/失败</td>
    </tr>
    <tr>
      <td><strong>alpha</strong></td>
      <td align="center"><code>0.05</code></td>
      <td>相对于 ‖<b>P</b>₀‖ 的 epsilon 阈值缩放因子</td>
    </tr>
    <tr>
      <td><strong>collapse_window</strong></td>
      <td align="center"><code>5</code></td>
      <td>连续 5 轮负能量触发方向崩塌</td>
    </tr>
    <tr>
      <td><strong>stagnation_window</strong></td>
      <td align="center"><code>5</code></td>
      <td>最近 5 次评估中 ‖<b>P</b><sub>t</sub>‖ 方差低于阈值触发停滞</td>
    </tr>
    <tr>
      <td><strong>stagnation_threshold</strong></td>
      <td align="center"><code>0.5</code></td>
      <td>停滞检测的标准差阈值</td>
    </tr>
    <tr>
      <td><strong>regression_window</strong></td>
      <td align="center"><code>8</code></td>
      <td>持续性退步的回溯窗口</td>
    </tr>
    <tr>
      <td><strong>regression_ratio</strong></td>
      <td align="center"><code>0.7</code></td>
      <td>最近 8 次评估中 70%+ 为负能量则触发退步失败</td>
    </tr>
    <tr>
      <td><strong>EPM-Q 权重</strong></td>
      <td align="center"><code>0.4</code> / <code>0.2</code> / <code>0.4</code></td>
      <td>结果 / 效率 / 稳定性</td>
    </tr>
  </tbody>
</table>

每个案例的能量阈值（$\epsilon_{\text{dist}}$、$\epsilon_{\text{energy}}$）从该场景的初始 IEDR 赤字预计算得出，存储在 `empa/data/precomputed/iedr_batch_results.json` 中。修改这些值将使跨模型对比失效。

### 官方 30 案例抽样逻辑

30 个官方基准案例**并非随机抽样**。它们从完整的 1,010 场景池中通过**分层抽样**选取，以确保在三个正交轴上的均衡覆盖。抽样约束（定义在 `empa/data/case_metadata.json` 中）如下：

<table>
  <thead>
    <tr>
      <th width="20%">轴</th>
      <th width="40%">分层</th>
      <th width="40%">分布</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>场景类别</strong></td>
      <td>生活、健康、休闲、价值观、人际关系、生涯发展</td>
      <td>每类 5 个（均匀）</td>
    </tr>
    <tr>
      <td><strong>难度</strong></td>
      <td>
        简单：‖<b>P</b>₀‖ ≤ 27（4 个）<br>
        中等：27 < ‖<b>P</b>₀‖ ≤ 32（10 个）<br>
        困难：32 < ‖<b>P</b>₀‖ ≤ 36（11 个）<br>
        极难：‖<b>P</b>₀‖ > 36（5 个）
      </td>
      <td>基于初始赤字距离定义；偏向较难案例</td>
    </tr>
    <tr>
      <td><strong>主导共情维度</strong></td>
      <td>C / A / P</td>
      <td>每维度 10 个（均匀）</td>
    </tr>
  </tbody>
</table>

30 个案例 ID 固定在 `empa/data/official_cases.txt` 中并硬编码在 `empa/cli.py` 中。如果你希望扩展测试集，**必须**保持相同的分层逻辑——类别和主导维度均匀、难度分布反映完整场景池——以确保与已发布结果的统计可比性。

### 裁判智能体模型 — 基准测试强烈建议保持

为了**基准测试的信效度和跨模型可比性**，我们强烈建议保持指定的基础设施模型（`google/gemini-2.5-pro`）作为裁判智能体。原因如下：

- `empa/rubric/empathy_v2/mdep_prompt.py` 中的 IEDR 和 MDEP-PR 提示词包含专门为该模型调校的**校准指令**——包括客观校准准则、反宽大偏见约束（提示词明确指示裁判打负分应该是常态而非例外）、以及严重性锚定（-1 分对应任何可识别的问题；-2 分保留给严重问题）。
- 裁判通过 `response_format={"type": "json_object"}` 输出严格 JSON，IEDR 含 27 个字段、MDEP-PR 含 18 个字段。不同模型的 JSON 合规率和打分分布存在差异，直接影响 EPM 轨迹计算。
- 排行榜上所有 16 个模型均由同一裁判模型评分。更换裁判将使跨模型对比失效。
- 导演智能体和用户智能体的敏感性较低，但为完全可复现仍建议保持相同的基础设施模型。

> **对于非基准测试用途**（如沙盒模拟、奖励信号生成、自定义研究管线），你可以自由将裁判模型替换为任何支持 JSON 模式的 OpenAI 兼容模型。请注意打分分布可能发生偏移，结果将无法与官方排行榜直接对比。

### 为什么强烈建议安装可视化（`pip install -e ".[all]"`）

EPM-Q 分数告诉你模型**整体表现如何**——但无法告诉你**哪里失败**。可视化揭示了聚合分数无法呈现的逐案例轨迹模式：

- **3D 轨迹图**（`empa visualize`）暴露模型的成功是来自持续的方向对齐，还是来自少数高能量轮次掩盖了其他案例中的持续漂移。
- **雷达图画像**（`empa compare --chart radar`）将表现分解到场景类别、共情机制（C/A/P × 常规 vs. 困难）和用户画像类型（主导需求 × 共情阈值）。这揭示了**特定画像的盲区**——例如，某个模型可能整体得分很高，但在高阈值的前摄主导案例上持续失败，或在生涯发展相关场景上表现不佳。
- **误差棒对比图**（`empa compare --chart bars`）展示 3×3 网格的方差：结果（距离改善率、总能量、净分）、效率（每轮得分、有效投影、曲折度）、稳定性（正能量占比、对齐度、惩罚率）——便于发现高 EPM-Q 是否掩盖了巨大的案例间差异。

简而言之，EMPA 不仅回答"哪个模型更好"，更回答"每个模型在哪些用户和场景上失败、为什么失败"。可视化工具让这些洞察变得可操作。

---

## 🍍 编程接口

```python
from empa.llm import OpenAICompatibleClient
from empa.agents import Actor, Director, Judger, TestModel
from empa.rubric.empathy_v2.config import EmpathyRubricV2
from empa.data.loader import load_config
from empa.orchestrator.chat_loop import run_chat_loop

rubric = EmpathyRubricV2()
config = load_config("script_003")

# LLM 客户端
test_llm = OpenAICompatibleClient("openai/gpt-4o", api_key="...")
infra_llm = OpenAICompatibleClient("google/gemini-2.5-pro", api_key="...")

# 智能体
actor = Actor(infra_llm)                          # 用户智能体
judger = Judger(infra_llm)                        # 裁判智能体
director = Director(infra_llm,                    # 导演智能体
                    scenario=config["scenario"],
                    actor_prompt=config["actor_prompt"])
test_model = TestModel(test_llm,
                       system_prompt=rubric.generate_test_model_system_prompt())

# 运行单个案例
result = run_chat_loop(
    actor=actor, director=director, judger=judger,
    test_model=test_model, rubric=rubric,
    script_id="script_003",
)
```

**自定义量规** — EMPA 支持可插拔量规。实现 `RubricConfig` 接口即可定义自己的评估标准：

```python
from empa.rubric import RubricConfig

class MyCustomRubric(RubricConfig):
    ...  # 参见 examples/custom_rubric.py
```

更多使用示例见 [`examples/`](examples/)。

---

## 🍈 仓库结构

```
.
├── empa/                               # Python 包
│   ├── core/                           #   向量引擎、能量动力学、评分
│   ├── rubric/                         #   量规接口 + empathy_v2（IEDR、MDEP-PR）
│   ├── agents/                         #   用户智能体、导演智能体、裁判智能体、被测模型
│   ├── orchestrator/                   #   对话循环 + EPM 状态管理
│   ├── evaluation/                     #   EPM-Q 计算 + 描述性统计
│   ├── visualization/                  #   轨迹图、柱状图/雷达图、汇总表
│   ├── llm/                            #   LLM API 适配器
│   ├── data/                           #   1,010 个场景 + 预计算 IEDR
│   └── cli.py                          #   命令行入口
├── examples/                           # 使用示例
├── results/
│   └── benchmark_runs/
│       └── epm-bench/                  # 官方结果（16 模型 × 30 案例）
│           ├── <model>/
│           │   ├── script_*_result.json    # 逐案例对话 + EPM 轨迹
│           │   └── descriptive_statistics.{csv,xlsx,md}
│           ├── analysis_figures/
│           │   ├── 01_tables/              # EPM-Q 汇总表
│           │   ├── 02_bar_charts/          # 误差棒对比图
│           │   └── 03_radar_charts/        # 雷达图画像
│           └── MODEL_COMPARISON_BY_CASE.xlsx
├── pyproject.toml                      # 包配置 + 依赖
├── LICENSE                             # CC BY-NC 4.0
└── README.md
```

---

## 🍋 常见问题

<details>
<summary><strong>Q：完整的 30 案例基准测试运行一次大约多少钱？</strong></summary>
A：费用因模型而异。以 Gemini 2.5 Pro 作为基础设施、GPT-4o 作为被测模型为例，通过 OpenRouter 运行 30 个案例大约需要 15–20 美元。
</details>
<details>
<summary><strong>Q：EMPA 可以用于强化学习或智能体优化吗？</strong></summary>
A：可以。EMPA 的评估接口输出结构化的逐轮过程信号——ΔE<sub>t</sub>、cos θ<sub>t</sub>、状态向量 <b>P</b><sub>t</sub>——可以作为下游优化的奖励或监督信号，包括强化学习（RL）、奖励建模、偏好学习和策略优化。详见<a href="https://arxiv.org/abs/2603.00552">论文</a> 3.4 节关于 RL 友好接口的设计。
</details>
<details>
<summary><strong>Q：我可以添加自己的场景吗？</strong></summary>
A：可以。将新场景文件按照现有格式放置在 <code>empa/data/cases/</code> 中。EMPA 支持基于提示词驱动的扩展管线，用于受控的场景演化。
</details>
<details>
<summary><strong>Q：量规系统是如何设计的？</strong></summary>
A：EMPA 的评估方法——IEDR 初始评估、MDEP-PR 进展量规、导演控制工具和评分映射——封装为 <code>empa/rubric/empathy_v2/</code> 中的内聚模块。这种设计是有意为之的：这些组件构成一个紧密耦合的评估范式，提示词、评分键和控制逻辑必须保持一致。<code>empa/rubric/base.py</code> 中的 <code>RubricConfig</code> 基类文档化了构建替代评估范式的完整接口。EPM 向量引擎和编排器是维度无关的，可与任意数量的评估维度配合工作。
</details>
<details>
<summary><strong>Q：为什么 EPM-Q 要做场景归一化？</strong></summary>
A：不同场景的初始赤字量 ‖<b>P</b><sub>0</sub>‖ 不同。不做归一化的话，模型在简单场景上会获得更高分数。除以 r<sub>0</sub> 确保了跨难度级别的公平对比。
</details>
<details>
<summary><strong>Q：应该使用什么基础设施模型？</strong></summary>
A：我们推荐 Gemini 2.5 Pro 用于用户智能体、裁判智能体和导演智能体。它在成本、质量和一致性方面提供了良好的平衡。排行榜中的所有结果均使用此配置。
</details>

---

## 🍑 贡献指南

欢迎贡献！以下是一些参与方式：

- **提交新模型结果** — 在新模型上运行基准测试并提交 PR。
- **添加场景** — 按照数据格式贡献心理学扎根的场景。
- **改进量规** — 提出 IEDR/MDEP-PR 量规的改进建议或贡献新的量规类型。
- **Bug 报告** — 遇到问题请提 issue。

---

## 🍒 许可证与使用

本仓库——包括源代码、基准数据、量规、提示词和结果——均以 **知识共享 署名-非商业性使用 4.0 国际许可协议**（[CC BY-NC 4.0](LICENSE)）发布。

**面向研究者** — 你可以自由地在自己的模型上运行基准测试、将 EMPA 用作强化学习和智能体优化的沙盒、修改评分引擎或量规用于实验、在论文中使用结果和排行榜数据，以及在相同的 CC BY-NC 4.0 条款下再分发修改后的版本。

**面向商业使用** — 如需在商业产品或服务中使用本仓库的任何部分（代码、数据、量规提示词或评估结果），请联系我们获取商业授权。

---

## 🍐 引用

如果您在研究中使用了 EMPA，请引用：

```bibtex
@article{zhang2026empa,
  title   = {EMPA: Evaluating Persona-Aligned Empathy as a Process},
  author  = {Zhang, Shiya and Zhan, Yuhan and Su, Ruixi and Sun, Ruihan and Song, Ziyi and Chen, Zhaohan and Zhang, Xiaofan},
  journal = {arXiv preprint arXiv:2603.00552},
  year    = {2026}
}
```

---

## 🍉 联系方式

- **论文**：[arXiv:2603.00552](https://arxiv.org/abs/2603.00552)
- **邮箱**：zhangshiya@natureselect.ai · zhangshiya1999@gmail.com
- **团队**：[Team Echo](https://www.natureselect.ai)，Nature Select
