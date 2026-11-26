# Burning Number of Narrow Fence Grids / 窄栅栏网格的燃烧数

Codex (OpenAI AI model) · Corresponding author / 通讯作者Wei Lin

> **Note on Provenance & Status / 来源与状态说明**  
> This repository contains a constructive mathematical note and a reproducible verification script exploring the burning number of rectangular grid / fence graphs $G_{m,n}$, originally drafted with AI assistance and independently checked via Python scripts and manual review. It has **not** yet undergone formal peer review, and prior literature / originality should be independently verified by domain researchers. We do not claim the lower-bound leading coefficient itself as a new result; our contribution is an explicit covering construction whose upper bound matches that leading term for $0 < c \le 2/\sqrt{5}$ and lowers the explicit upper-bound coefficient at $c = 1$ from $1.468246$ to $1.368250$. Feedback, counterexamples, or citations to related work are very welcome.  
> 本仓库收录了一份围绕矩形栅栏网格 $G_{m,n}$ 燃烧数展开的构造性研究短稿与可复现验证脚本，初稿由 AI 辅助生成，并辅以 Python 脚本与人工核对。该文稿**尚未经过同行评审**，相关文献查重与结论首创性仍有待领域研究者独立核实。本文不声称下界系数本身为新结果；贡献在于给出一个显式覆盖构造，使上界在 $0<c\le 2/\sqrt{5}$ 内达到该下界的首项，并在 $c=1$ 时将显式上界系数从 $1.468246$ 降至 $1.368250$。欢迎指正、提供相关文献线索或开展复核。

## Overview / 简介

Given an $m \times n$ grid graph $G_{m,n}$, we study explicit diamond-covering constructions and asymptotic upper bounds for the burning number $b(G_{m,n})$, following open questions in Bonato, English, Kay, and Moghbel (2021):

- **Theorem 1:** For $0 < c \le 2/\sqrt{5}$ and $m = \lfloor c\sqrt{n} \rfloor$, we give an explicit covering construction whose upper bound matches the leading-term coefficient from the boundary counting argument of [1] with an $O_c(1)$ remainder.
- **Theorem 2:** For $c = 1$, letting $\beta = (3 + \sqrt{261})/14 \approx 1.368250$, we obtain an improved explicit upper bound $b(\lfloor\sqrt{n}\rfloor, n) \le \lceil\beta\sqrt{n}\rceil + 2$ for sufficiently large $n$ (compared to $(2+\sqrt{15})/4 \approx 1.468246$ in [1]).

---

## 仓库文件与说明

解压到同一文件夹。正文与数据文件均为 UTF-8。

## 阅读和排版

- `manuscript.md` 为完整 Markdown 稿，适用于支持美元符号数学公式的阅读器。
- `manuscript.tex` 为对应的 LaTeX 稿，公式用自动编号和交叉引用。在含 `ctex` 与 Fandol 字体的 TeX Live 环境中，用 XeLaTeX 连续编译两次。在线编辑器可选择 XeLaTeX 编译器。
- `figure-1.png` 是两种格式共用的插图。将它与正文保存在同一目录中。

```sh
xelatex -halt-on-error manuscript.tex
xelatex -halt-on-error manuscript.tex
```

## 复核图 1

验证程序只需要 Python 3.8 或更高版本的标准库。默认会核对随稿提供的所有数据。下列第二条命令还会逐行列出非空区间；第三条命令会把重新计算的两张明细表写入指定目录。

```sh
python verify_figure.py
python verify_figure.py --rows
python verify_figure.py --export regenerated
```

三份表格使用同一个坐标系：左下角为 $(0,0)$，右上角为 $(54,6)$。行、列下标从 $0$ 开始，点火轮次从 $1$ 开始。

| 文件 | 数据行数 | 字段释义 |
|---|---:|---|
| `figure-1-sources.csv` | 10 | `round` 为点火轮次，`x,y` 为中心坐标，`radius` 为第 10 轮结束时的半径。 |
| `figure-1-rows.csv` | 70 | 每一行与每个火源的一次组合。`x_min,x_max` 是裁切到矩形后的闭区间端点；空截面记两个空字段和 `count=0`。 |
| `figure-1-cells.csv` | 385 | 每个格点的坐标、覆盖该点的唯一最终球的点火轮次 `owner_round`，以及该点的首次燃烧轮次 `first_burn_round`。 |

脚本从正文递推式独立计算十个中心，再与输入清单比较。它逐行构造区间，同时按曼哈顿距离枚举整个矩形，又用前一轮的已燃集合模拟同步传播。九轮的必要条件也单独枚举验证。在所有中心中分别最大化半径 $0$ 至 $8$ 能覆盖的上下边界点数，得到 $1、3、5、7、9、11、14、18、22$，合计 $90$，小于两条边界的 $110$ 个顶点。

通过时可见 `PASS: burning number = 10.`。清单缺失、坐标不符、缺点、重叠或传播时序不符均使默认命令以非零状态退出。这个有限算例验证的是图 1；一般参数的论证见正文第 2 至 4 节。

## 测试一般参数

在本目录运行以下命令。第一条适合作为 GitHub Actions 的测试步骤，会自动发现 `test_fence.py`。它运行两套覆盖测试，并检查最小参数、非法参数和人为制造的单点缺口。单独运行第二条可同时核对随稿发布的图 1 CSV。

```sh
python -m unittest -v
python verify_figure.py
```

也可直接调用脚本选择测试范围。一般参数模式只需 `verify_figure.py` 单个文件。

```sh
python verify_figure.py --exhaustive
python verify_figure.py --random 300 --seed 42
python verify_figure.py --case 3 5 14
python verify_figure.py --exhaustive --max-p 10 --max-extra 12
```

- **遍历。** 默认遍历 $1\le p\le8$、$p\le h\le2p$、$0\le k-(3p+1)\le7$ 的所有 $352$ 个三元组，包含高度和轮数的边界值。
- **随机。** 默认从 $1\le p\le12$、$p\le h\le2p$、$0\le k-(3p+1)\le15$ 的 $1,440$ 个合法三元组中等概率无放回抽样。可指定数量、种子及与遍历相同的范围选项；固定 Python 版本、参数和种子可以重现抽样。两套测试的参数可能相交。
- **判定。** 对每一组，用构造的左右端点独立核对公式 (6) 的列数 $W=k^2-2hk+4hp-2p^2-p$，检查全部 $k$ 个火源的坐标、顺序和半径。第一种覆盖检查合并每行的闭整数区间，检查所有 $W$ 列；第二种用位图从空网格逐轮模拟四邻传播，检查末轮的全部 $(2h+1)W$ 个顶点。一般构造允许重叠。模拟按预定位置点火，已燃中心的重复点火不增加覆盖。
- **失败。** 脚本以非零状态退出，打印三元组与可直接运行的 `--case P H K` 命令。覆盖失败还会报告第一个漏点的零基坐标。回归测试将图 1 的最后一个火源从 $(13,0)$ 移到 $(12,0)$，要求两种检查都报告漏点 $(13,0)$。
