# Burning Number of Narrow Fence Grids / 窄栅栏网格的燃烧数

Codex (OpenAI AI model) · Corresponding author / 通讯作者 Wei Lin

> **Note on Provenance & Status / 来源与状态说明**
>
> This repository contains a constructive mathematical note and a reproducible verification script exploring the burning number of rectangular grid / fence graphs $G_{m,n}$, originally drafted with AI assistance and independently checked via Python scripts and manual review. It has **not** yet undergone formal peer review, and prior literature / originality should be independently verified by domain researchers. We do not claim the lower-bound leading coefficient itself as a new result; our contribution is an explicit covering construction whose upper bound matches that leading term for $0 < c \le 2/\sqrt{5}$ and lowers the explicit upper-bound coefficient at $c = 1$ from $1.468246$ to $1.368250$. Feedback, counterexamples, or citations to related work are very welcome.
>
> 本仓库收录了一份围绕矩形栅栏网格 $G_{m,n}$ 燃烧数展开的构造性研究短稿与可复现验证脚本，初稿由 AI 辅助生成，并辅以 Python 脚本与人工核对。该文稿**尚未经过同行评审**，相关文献查重与结论首创性仍有待领域研究者独立核实。本文不声称下界系数本身为新结果；贡献在于给出一个显式覆盖构造，使上界在 $0<c\le 2/\sqrt{5}$ 内达到该下界的首项，并在 $c=1$ 时将显式上界系数从 $1.468246$ 降至 $1.368250$。欢迎指正、提供相关文献线索或开展复核。

## Overview / 简介

Given an $m \times n$ grid graph $G_{m,n}$, we study explicit diamond-covering constructions and asymptotic upper bounds for the burning number $b(G_{m,n})$, following open questions in Bonato, English, Kay, and Moghbel (2021):

* **Theorem 1:** For $0 < c \le 2/\sqrt{5}$ and $m = \lfloor c\sqrt{n} \rfloor$, we give an explicit covering construction whose upper bound matches the leading-term coefficient from the boundary counting argument of [1] with an $O_c(1)$ remainder.
* **Theorem 2:** For $c = 1$, letting $\beta = (3 + \sqrt{261})/14 \approx 1.368250$, we obtain an improved explicit upper bound $b(\lfloor\sqrt{n}\rfloor, n) \le \lceil\beta\sqrt{n}\rceil + 2$ for sufficiently large $n$ (compared to $(2+\sqrt{15})/4 \approx 1.468246$ in [1]).

## Files & Typesetting / 仓库文件与排版

Keep all files in the same directory; text and data files are encoded in UTF-8. / 请将所有文件放在同一目录中，正文与数据文件均为 UTF-8 编码。

* `manuscript.md` — Full Markdown draft for readers supporting dollar-sign math / 完整 Markdown 稿，适用于支持美元符号数学公式的阅读器。
* `manuscript.tex` — LaTeX source with automatic numbering and cross-references. Compile twice with `xelatex` in a TeX Live setup with `ctex` and Fandol fonts (or select XeLaTeX in an online editor) / 对应的 LaTeX 稿，支持自动编号与交叉引用；在含 `ctex` 与 Fandol 字体的 TeX Live 环境或在线编辑器中建议用 XeLaTeX 连续编译两次。
* `figure-1.png` — Shared illustration referenced by both formats; keep it alongside the manuscript / 两种格式共用的插图，须与正文件保存在同一目录。

```sh
xelatex -halt-on-error manuscript.tex
xelatex -halt-on-error manuscript.tex
```

## Verifying Figure 1 / 复核图 1

The verification script uses only the Python 3.8+ standard library and checks all published certificate files by default. The second command prints non-empty intervals row by row; the third exports recomputed tables to a target directory. / 验证程序仅需 Python 3.8+ 标准库，默认会核对随稿提供的全部数据；第二条命令逐行列出非空区间，第三条命令把重新计算的两张明细表导出到指定目录。

```sh
python verify_figure.py
python verify_figure.py --rows
python verify_figure.py --export regenerated
```

All three tables share the same zero-based coordinate system with bottom-left $(0,0)$, top-right $(54,6)$, and 1-based ignition rounds $t$. / 三份表格使用同一零基坐标系：左下角 $(0,0)$、右上角 $(54,6)$，点火轮次 $t$ 从 $1$ 起算。

| File | Rows | Meaning / 字段释义 |
|---|---:|---|
| `figure-1-sources.csv` | 10 | Ignition `round`, center `(x,y)`, and `radius` at the end of round 10 / 点火轮次、中心坐标与第 10 轮结束时的半径。 |
| `figure-1-rows.csv` | 70 | Row-by-source pairs; `x_min,x_max` are clipped closed endpoints, and empty slices leave both blank with `count=0` / 每一行与每个火源的组合；裁切后的闭区间端点，空截面记空字段与 `count=0`。 |
| `figure-1-cells.csv` | 385 | Vertex coordinates, unique final-ball `owner_round`, and `first_burn_round` / 每个格点的坐标、所属最终球的点火轮次 `owner_round` 与首次燃烧轮次 `first_burn_round`。 |

The script independently recomputes the ten centers from the recurrence, checks row intervals and Manhattan distances across the rectangle, simulates round-by-round synchronous spread, and verifies the nine-round boundary obstruction (maxima $1,3,5,7,9,11,14,18,22$, sum $90 < 110$). Passing prints `PASS: burning number = 10.`; this finite certificate checks Figure 1, while general parameters are proved in Sections 2–4. / 脚本从递推式独立重算十个中心，逐行检查区间与全图曼哈顿距离，模拟逐轮同步传播，并枚举验证九轮边界障碍（各半径最大覆盖点数 $1,3,5,7,9,11,14,18,22$，合计 $90 < 110$）。通过会输出 `PASS: burning number = 10.`；有限算例验证图 1，一般参数证明见正文第 2–4 节。

## Testing General Parameters / 测试一般参数

Run the commands below in the repository directory. The first is suited for GitHub Actions and discovers `test_fence.py`; the second also checks the published Figure 1 CSV files. / 在仓库目录运行以下命令。第一条适合作为 GitHub Actions 测试步骤并自动发现 `test_fence.py`；单独运行第二条可同时核对随稿图 1 CSV。

```sh
python -m unittest -v
python verify_figure.py
```

You can also invoke `verify_figure.py` directly for specific parameter ranges. / 也可直接调用 `verify_figure.py` 指定测试范围。

```sh
python verify_figure.py --exhaustive
python verify_figure.py --random 300 --seed 42
python verify_figure.py --case 3 5 14
python verify_figure.py --exhaustive --max-p 10 --max-extra 12
```

* **Exhaustive / 遍历.** Default enumerates all $352$ triples with $1\le p\le8$, $p\le h\le2p$, and $0\le k-(3p+1)\le7$, covering height and round boundaries / 默认遍历 $1\le p\le8$、$p\le h\le2p$、$0\le k-(3p+1)\le7$ 的全部 $352$ 个三元组，含高度与轮数边界。
* **Random / 随机.** Default samples $300$ distinct triples without replacement from the $1,440$ valid triples with $1\le p\le12$, $p\le h\le2p$, and $0\le k-(3p+1)\le15$, reproducible given Python version, arguments, and seed (and possibly overlapping the exhaustive grid) / 默认从 $1\le p\le12$、$p\le h\le2p$、$0\le k-(3p+1)\le15$ 的 $1,440$ 个合法三元组中无放回抽样，固定 Python 版本、参数与种子可重现，且范围可能与遍历有交集。
* **Checks & Failures / 判定与失败.** Independently checks width $W=k^2-2hk+4hp-2p^2-p$ from outer endpoints, verifies all $k$ sources, checks merged row intervals across all $W$ columns, and simulates 4-neighbor spread via bitmaps across all $(2h+1)W$ vertices (overlaps allowed in general constructions; ignitions on already-burning centers add no coverage). On failure, the script exits non-zero with the triple, a `--case P H K` command, and the first uncovered `(x, y)` coordinate; a regression test shifts round 10's source from `(13,0)` to `(12,0)` and expects both checks to flag `(13, 0)` / 用左右端点独立核对列数 $W=k^2-2hk+4hp-2p^2-p$，检查全部 $k$ 个火源，合并每行区间核对全部 $W$ 列，并用位图逐轮模拟四邻传播核对全部 $(2h+1)W$ 个顶点（一般构造允许重叠，已燃中心重复点火不增加覆盖）。失败时以非零状态退出，输出三元组、`--case P H K` 命令与首个漏点 `(x, y)`；回归测试将第 10 轮火源从 `(13,0)` 移至 `(12,0)`，要求两种检查均报漏点 `(13, 0)`。