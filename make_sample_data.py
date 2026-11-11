"""Creates the sample biometric attendance files used by Task 2 and Task 5 (deterministic)."""
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
STUDENTS = ["192311001", "192311002", "192311003", "192311004", "192311005", "192311006"]
DAYS = [f"2026-10-0{d}" for d in range(1, 9)]          # 8 working days
PATTERN = {                                              # P/A for each of the 8 days
    "192311001": "PPPPPPPP",      # 100 %
    "192311002": "PPAAAPPP",      # 3 consecutive absences, 62.5 %
    "192311003": "PAPPAPPP",      # exactly 75 % -> NOT below 75
    "192311004": "AAPAPAPA",      # 37.5 %
    "192311005": "PPPPPPPA",      # 87.5 %
    "192311006": "PPPPPAAA",      # 62.5 %, absent on the last 3 days
}
EXTRA = {                                                # damaged / duplicate lines added to some days
    "2026-10-02": ["192311099,2026-10-02,X"],                 # wrong status letter
    "2026-10-04": ["192311003,2026-10-04"],                   # missing field
    "2026-10-05": ["192311002,2026-13-05,A"],                 # impossible date
    "2026-10-06": ["abc,2026-10-06,P", ""],                   # bad register number, blank line
    "2026-10-07": ["192311001,2026-10-07,P"],                 # duplicate record
}


def build(folder):
    os.makedirs(folder, exist_ok=True)
    for i, day in enumerate(DAYS):
        lines = [f"{s},{day},{PATTERN[s][i]}" for s in STUDENTS]
        lines[2:2] = EXTRA.get(day, [])[:1]
        lines += EXTRA.get(day, [])[1:]
        with open(os.path.join(folder, f"attendance_{day}.txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    build(os.path.join(ROOT, "Task2", "sample_data"))
    shutil.rmtree(os.path.join(ROOT, "Task5", "sample_data"), ignore_errors=True)
    shutil.copytree(os.path.join(ROOT, "Task2", "sample_data"), os.path.join(ROOT, "Task5", "sample_data"))
    print("Sample data written to Task2/sample_data and Task5/sample_data")
