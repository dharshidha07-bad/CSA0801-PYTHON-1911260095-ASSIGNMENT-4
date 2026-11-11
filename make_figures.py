"""Graphs and diagrams for the report (reads the numbers from the program outputs)."""
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(ROOT, "figures")
os.makedirs(FIG, exist_ok=True)


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def box(ax, x, y, w, h, text, fc="#e8f1fb", ec="#2c5d8f", fs=8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02", fc=fc, ec=ec, lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def arrow(ax, p, q, color="#444", style="-|>"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=10, color=color, lw=1.1))


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, name), dpi=150)
    plt.close(fig)


def make_all():
    # Task 2: one pass versus re-reading per student
    rows = re.findall(r"s=\s*(\d+) students.*?one pass=([\d.]+)s\s+re-read per student=([\d.]+)s", read("Task2/output.txt"))
    s = [int(r[0]) for r in rows]
    fig, ax = plt.subplots(figsize=(5.2, 3.3))
    ax.plot(s, [float(r[1]) for r in rows], "o-", label="one pass (dictionary)")
    ax.plot(s, [float(r[2]) for r in rows], "o-", label="re-read for every student")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("students s (= lines per file l; f = 30 files)")
    ax.set_ylabel("time (s)"); ax.set_title("Task 2: monthly attendance", fontsize=10)
    ax.grid(True, which="both", alpha=0.3); ax.legend(fontsize=8)
    save(fig, "task2_timing.png")

    # Task 3: LBYL versus EAFP
    rows = re.findall(r"([\d.]+)%\s+(\d+) ns\s+(\d+) ns", read("Task3/lbyl_output.txt"))
    x = [float(r[0]) for r in rows]
    fig, ax = plt.subplots(figsize=(5.2, 3.3))
    ax.plot(range(len(x)), [int(r[1]) for r in rows], "o-", label="EAFP: try / except")
    ax.plot(range(len(x)), [int(r[2]) for r in rows], "o-", label="LBYL: if checks")
    ax.set_xticks(range(len(x))); ax.set_xticklabels([f"{v:g}%" for v in x])
    ax.set_xlabel("share of bad lines"); ax.set_ylabel("ns per line"); ax.set_ylim(0)
    ax.set_title("Task 3: cost per line", fontsize=10); ax.grid(True, alpha=0.3); ax.legend(fontsize=8)
    save(fig, "task3_timing.png")

    # Task 6: set versus list search
    rows = re.findall(r"\s*(\d+)\s+([\d.]+)s\s+([\d.]+)s\s+\d+x", read("Task6/output.txt"))
    n = [int(r[0]) for r in rows]
    fig, ax = plt.subplots(figsize=(5.2, 3.3))
    ax.plot(n, [float(r[1]) for r in rows], "o-", label="set of seen register numbers")
    ax.plot(n, [float(r[2]) for r in rows], "o-", label="search a list")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("registrations n"); ax.set_ylabel("time (s)")
    ax.set_title("Task 6: duplicate detection", fontsize=10); ax.grid(True, which="both", alpha=0.3); ax.legend(fontsize=8)
    save(fig, "task6_timing.png")

    # Task 6: processing flow
    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.set_xlim(0, 20); ax.set_ylim(0, 10.8); ax.axis("off")
    box(ax, 0.2, 7.6, 3.4, 2.6, "5 department files\nregistrations_<dept>.txt\n(cse, it, ece, mech, civil)", fc="#fff3cd", ec="#a07800")
    box(ax, 4.6, 7.6, 3.0, 2.6, "READ line by line\nreaders.read_lines\n(skip blank lines)")
    box(ax, 8.6, 7.6, 3.0, 2.6, "VALIDATE\nvalidators.parse_\nregistration\n(5 fields, number,\nname, events)")
    box(ax, 12.6, 7.6, 3.0, 2.6, "VALIDATE E-MAIL\nvalid_email\n(string methods)")
    box(ax, 16.4, 7.6, 3.4, 2.6, "DUPLICATE?\nregister number in\nset 'seen'")
    for a, b in ((3.6, 4.6), (7.6, 8.6), (11.6, 12.6), (15.6, 16.4)):
        arrow(ax, (a, 8.9), (b, 8.9))
    box(ax, 4.6, 3.6, 3.0, 2.0, "MISSING / UNREADABLE\nfile -> log, go on to\nthe next file", fc="#fde2e2", ec="#b00020")
    box(ax, 10.0, 3.6, 4.4, 2.0, "DAMAGED LINE / INVALID E-MAIL /\nDUPLICATE -> error record\n(file, line no., kind, reason, text)", fc="#fde2e2", ec="#b00020")
    arrow(ax, (6.1, 7.6), (6.1, 5.6), "#b00020")
    arrow(ax, (10.1, 7.6), (11.6, 5.6), "#b00020")
    arrow(ax, (14.1, 7.6), (12.9, 5.6), "#b00020")
    arrow(ax, (18.0, 7.6), (14.4, 5.2), "#b00020")
    box(ax, 16.4, 3.6, 3.4, 2.0, "ACCEPT\nadd to master list,\nevent index, counters", fc="#e3f6e3", ec="#2e7d32")
    arrow(ax, (19.0, 7.6), (19.0, 5.6), "#2e7d32")
    box(ax, 0.6, 0.2, 3.9, 1.5, "master_list.csv", fc="#e3f6e3", ec="#2e7d32")
    box(ax, 5.0, 0.2, 3.9, 1.5, "events/<event>.txt", fc="#e3f6e3", ec="#2e7d32")
    box(ax, 9.4, 0.2, 3.9, 1.5, "summary.txt", fc="#e3f6e3", ec="#2e7d32")
    box(ax, 13.8, 0.2, 3.9, 1.5, "errors.log", fc="#fde2e2", ec="#b00020")
    arrow(ax, (17.4, 3.6), (2.6, 1.7), "#2e7d32")
    arrow(ax, (17.4, 3.6), (7.0, 1.7), "#2e7d32")
    arrow(ax, (17.4, 3.6), (11.3, 1.7), "#2e7d32")
    arrow(ax, (12.2, 3.6), (15.4, 1.7), "#b00020")
    arrow(ax, (6.1, 3.6), (14.4, 1.7), "#b00020")
    ax.text(10, 10.55, "Stage 2: from input files to output files (red = problems, nothing stops the run)", ha="center", fontsize=10)
    save(fig, "task6_flow.png")

    # Task 5: package structure picture
    fig, ax = plt.subplots(figsize=(9, 3.4))
    ax.set_xlim(0, 12); ax.set_ylim(0, 5); ax.axis("off")
    box(ax, 0.1, 1.8, 2.2, 1.4, "main.py\nrun(data, out)", fc="#fff3cd", ec="#a07800")
    box(ax, 3.2, 0.3, 8.6, 4.4, "", fc="#f7f9fc")
    ax.text(7.5, 4.35, "package attendance/", ha="center", fontsize=9, weight="bold")
    box(ax, 3.6, 2.8, 2.4, 1.1, "__init__.py\n(marks the folder\nas a package)", fc="#eeeeee", ec="#777")
    box(ax, 6.4, 2.8, 2.4, 1.1, "reader.py\ncheck_line, read_month")
    box(ax, 9.2, 2.8, 2.4, 1.1, "stats.py\ncount_attendance,\npercentages, ...", fc="#e3f6e3", ec="#2e7d32")
    box(ax, 6.4, 0.7, 2.4, 1.1, "report.py\nwrite_summary, ...", fc="#f3e8fd", ec="#6a1b9a")
    ax.text(10.4, 1.2, "import attendance.stats\nfrom attendance import stats\nfrom attendance.stats import percentages", ha="center", va="center", fontsize=7.5, family="monospace")
    for y in (3.2, 2.6, 2.0):
        arrow(ax, (2.3, 2.5), (3.2, y), style="-")
    save(fig, "task5_package.png")


if __name__ == "__main__":
    make_all()
    print("Figures saved in", FIG)
