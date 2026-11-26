"""Verify Figure 1 or test the general fence construction (Python 3.8+, standard library).

    python verify_figure.py
    python verify_figure.py --rows
    python verify_figure.py --export path/to/directory
    python verify_figure.py --exhaustive
    python verify_figure.py --random 300 --seed 42
    python verify_figure.py --case 3 5 14

Coordinates are zero-based; y=0 is the bottom row. Row endpoints are inclusive.
"""

import argparse
import csv
import random
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
WIDTH, HEIGHT, K = 55, 7, 10
SOURCE_FILE = "figure-1-sources.csv"
ROWS_FILE = "figure-1-rows.csv"
CELLS_FILE = "figure-1-cells.csv"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_table(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def construct_strip(p, h, k):
    """Construct in untranslated strip coordinates, then shift the left edge to 0."""
    require(1 <= p <= h <= 2 * p and k >= 3 * p + 1,
            "expected 1 <= p <= h <= 2*p and k >= 3*p+1")
    d = h - p
    big_radii = list(range(k - 1, 2 * p - 1, -1))
    centers = {}
    x = 0
    left = x - (big_radii[0] - (h + p))
    for i, r in enumerate(big_radii):
        centers[r] = (x, d + min(i, p))
        if i == len(big_radii) - 1:
            break
        s = big_radii[i + 1]
        if i < p:
            centers[i] = (x + r - d + 1, 0)
            centers[2 * p - 1 - i] = (x + r - d, 2 * h)
            x += r + s - 2 * d + 1
        else:
            x += r + s - 2 * h + 1
    right = x + big_radii[-1] - h
    require(set(centers) == set(range(k)), "construction radius mismatch")
    sources = [(k - r, centers[r][0] - left, centers[r][1], r)
               for r in reversed(range(k))]
    return left, right, sources


def constructed_sources():
    """The original Figure 1 certificate, in translated coordinates."""
    left, right, sources = construct_strip(3, 3, K)
    require((left, right, right - left + 1) == (-3, 51, WIDTH), "wrong Figure 1 outer columns")
    return sources


def check_row_coverage(sources, width, height):
    """Merge closed integer intervals. Overlaps are allowed for the general theorem."""
    for y in range(height):
        intervals = []
        for _, x, center_y, r in sources:
            reach = r - abs(y - center_y)
            if reach >= 0:
                intervals.append((max(0, x - reach), min(width - 1, x + reach)))
        next_x = 0
        for lo, hi in sorted(intervals):
            if lo > next_x:
                break
            next_x = max(next_x, hi + 1)
        if next_x < width:
            raise ValueError(f"interval check: uncovered vertex ({next_x}, {y})")


def check_fire_spread(sources, width, height):
    """Simulate prescribed ignitions. Each bit is one vertex; bit 0 is the left edge."""
    full_row = (1 << width) - 1
    rows = [0] * height
    for _, x, y, _ in sources:
        # Pad with two empty rows. All four neighbors come from the previous round.
        old = [0] + rows + [0]
        rows = [((mid << 1) | mid | (mid >> 1) | above | below) & full_row
                for below, mid, above in zip(old, old[1:], old[2:])]
        # If the prescribed center is already burning, this adds no new cells.
        # In particular a replacement ignition cannot mask a hole in the construction.
        rows[y] |= 1 << x
    for y, row in enumerate(rows):
        if row != full_row:
            missing = full_row ^ row
            x = (missing & -missing).bit_length() - 1
            raise ValueError(f"spread check: uncovered vertex ({x}, {y})")


def verify_case(p, h, k):
    """Check every vertex of the full rectangle promised by formula (6)."""
    try:
        left, right, sources = construct_strip(p, h, k)
        width = k*k - 2*h*k + 4*h*p - 2*p*p - p
        height = 2*h + 1
        require(right - left + 1 == width,
                f"endpoint width {right-left+1} differs from formula (6): {width}")
        require(len(sources) == k, f"expected {k} sources, got {len(sources)}")
        for expected_t, (t, x, y, r) in enumerate(sources, 1):
            require(t == expected_t and r == k - t, f"inconsistent round/radius: t={t}, r={r}")
            require(0 <= x < width and 0 <= y < height,
                    f"center ({x}, {y}) at round {t} outside {width} x {height}")
        check_row_coverage(sources, width, height)
        check_fire_spread(sources, width, height)
    except ValueError as exc:
        raise ValueError(f"p={p}, h={h}, k={k}: {exc}. "
                         f"Reproduce: python verify_figure.py --case {p} {h} {k}") from exc
    return width, height


def parameter_grid(max_p, max_extra):
    """Yield every admissible triple with k = 3*p+1+extra in the requested bounds."""
    require(max_p >= 1 and max_extra >= 0, "max-p must be positive and max-extra nonnegative")
    for p in range(1, max_p + 1):
        for h in range(p, 2*p + 1):
            for extra in range(max_extra + 1):
                yield p, h, 3*p + 1 + extra


def sampled_cases(count, seed, max_p, max_extra):
    population = list(parameter_grid(max_p, max_extra))
    require(1 <= count <= len(population),
            f"random count must be between 1 and {len(population)} (sampling without replacement)")
    return random.Random(seed).sample(population, count)


def simulate(sources, board):
    """Independent round-by-round spread; a new ignition waits until the next round to spread."""
    burned = set()
    first = {}
    new_counts = []
    for t, x, y, _ in sources:
        require((x, y) not in burned, f"source {t} burned before round {t}")
        after = burned | {(x, y)}
        for u, v in burned:
            for nb in ((u-1, v), (u+1, v), (u, v-1), (u, v+1)):
                if nb in board:
                    after.add(nb)
        new_cells = after - burned
        new_counts.append(len(new_cells))
        first.update((point, t) for point in new_cells)
        burned = after
    require(burned == board and max(first.values()) == K, "spread did not finish in round 10")
    return first, new_counts


def verify():
    raw = read_table(HERE / SOURCE_FILE)
    require(raw[0] == ["round", "x", "y", "radius"], "unexpected source table header")
    sources = [tuple(map(int, row)) for row in raw[1:]]
    require(sources == constructed_sources(), "source list disagrees with the construction")
    require(all(0 <= x < WIDTH and 0 <= y < HEIGHT and r == K-t for t, x, y, r in sources),
            "out-of-bounds center or inconsistent radius")
    board = {(x, y) for y in range(HEIGHT) for x in range(WIDTH)}
    first, new_counts = simulate(sources, board)
    row_table = [["y", "round", "x_min", "x_max", "count"]]
    cell_table = [["x", "y", "owner_round", "first_burn_round"]]
    totals = Counter()
    for y in range(HEIGHT):
        owners = {x: [] for x in range(WIDTH)}
        for t, u, v, r in sources:
            half = r - abs(y-v)
            lo, hi = max(0, u-half), min(WIDTH-1, u+half)
            if lo > hi:
                row_table.append([y, t, "", "", 0])
                continue
            row_table.append([y, t, lo, hi, hi-lo+1])
            for x in range(lo, hi+1):
                owners[x].append(t)
        for x in range(WIDTH):
            direct = [t for t, u, v, r in sources if abs(x-u)+abs(y-v) <= r]
            require(owners[x] == direct and len(direct) == 1,
                    f"gap, overlap or interval error at {(x,y)}: {direct}")
            arrival = min(t + abs(x-u) + abs(y-v) for t, u, v, _ in sources)
            require(arrival == first[x, y], f"arrival disagrees at {(x,y)}")
            cell_table.append([x, y, direct[0], arrival])
            totals[direct[0]] += 1

    # Directly maximize the number of boundary vertices a single radius-r ball
    # can cover over every possible center; the sum bounds every 9-round schedule.
    boundary = [(x, y) for x in range(WIDTH) for y in (0, HEIGHT-1)]
    caps = [max(sum(abs(x-u)+abs(y-v) <= r for x, y in boundary) for u, v in board)
            for r in range(K-1)]
    require(sum(caps) == 90 < len(boundary), "nine-round obstruction failed")
    return {ROWS_FILE: row_table, CELLS_FILE: cell_table}, new_counts, totals, caps


def run_figure(args):
    tables, new_counts, totals, caps = verify()
    for name, table in tables.items():
        strings = [list(map(str, row)) for row in table]
        if args.export is None:
            require(strings == read_table(HERE / name), f"published table differs: {name}")
        else:
            args.export.mkdir(parents=True, exist_ok=True)
            with (args.export / name).open("w", newline="", encoding="utf-8") as f:
                csv.writer(f, lineterminator="\n").writerows(strings)
    if args.rows:
        for y in range(HEIGHT):
            filled = sorted((lo, hi, t) for row_y, t, lo, hi, n in tables[ROWS_FILE][1:]
                            if row_y == y and n)
            print(f"y={y}: " + " ".join(f"[{lo},{hi}](t={t})" for lo, hi, t in filled))
    print("PASS: 10 source coordinates; raw x-range [-3,51], translated range [0,54].")
    print("PASS: all 385 vertices covered exactly once; all 7 rows have 55 vertices.")
    print("Vertices by final ball:", [totals[t] for t in range(1, K+1)])
    print("New vertices by round:", new_counts)
    print("Nine-round boundary maxima:", caps, f"(sum {sum(caps)} < 110).")
    print("PASS: burning number = 10.")
    print("Verification tables regenerated." if args.export else "Published verification tables match.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rows", action="store_true", help="print nonempty intervals in each Figure 1 row")
    parser.add_argument("--export", metavar="DIR", type=Path, help="write regenerated Figure 1 tables")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--case", metavar=("P", "H", "K"), type=int, nargs=3, help="verify one triple")
    mode.add_argument("--exhaustive", action="store_true", help="enumerate the parameter grid (default: 352 cases)")
    mode.add_argument("--random", metavar="N", type=int, help="sample N distinct parameter triples")
    parser.add_argument("--seed", type=int, help="random seed (default: 42)")
    parser.add_argument("--max-p", type=int, help="largest p (exhaustive: 8; random: 12)")
    parser.add_argument("--max-extra", type=int, help="largest k-(3*p+1) (exhaustive: 7; random: 15)")
    args = parser.parse_args()
    suite = args.exhaustive or args.random is not None
    if (args.rows or args.export is not None) and (suite or args.case is not None):
        parser.error("--rows and --export are Figure 1 options")
    if not suite and (args.max_p is not None or args.max_extra is not None):
        parser.error("--max-p and --max-extra require --exhaustive or --random")
    if args.seed is not None and args.random is None:
        parser.error("--seed requires --random")
    if args.case is not None:
        width, height = verify_case(*args.case)
        print(f"PASS: (p,h,k)={tuple(args.case)}, {width} columns x {height} rows.")
    elif suite:
        max_p = args.max_p if args.max_p is not None else (8 if args.exhaustive else 12)
        max_extra = args.max_extra if args.max_extra is not None else (7 if args.exhaustive else 15)
        if args.exhaustive:
            cases = parameter_grid(max_p, max_extra)
            name = "exhaustive"
        else:
            seed = 42 if args.seed is None else args.seed
            cases = sampled_cases(args.random, seed, max_p, max_extra)
            name = f"random (seed={seed})"
        count = 0
        vertices = 0
        for triple in cases:
            width, height = verify_case(*triple)
            count += 1
            vertices += width * height
        print(f"PASS: {name}, {count} grids, {vertices:,} vertices; "
              f"row coverage and synchronous spread agree (max-p={max_p}, max-extra={max_extra}).")
    else:
        run_figure(args)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        sys.exit(f"FAIL: {error}")
