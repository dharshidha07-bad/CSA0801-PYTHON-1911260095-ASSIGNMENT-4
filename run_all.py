"""Run every program of Assignment 4 and save its output next to the source file."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROGRAMS = [
    (".", "make_sample_data.py", None),
    ("Task1", "mess_fixed.py", "output.txt"),
    ("Task2", "attendance_monthly.py", "output.txt"),
    ("Task3", "complete_the_code.py", "complete_output.txt"),
    ("Task3", "processor.py", "output.txt"),
    ("Task3", "lbyl_vs_eafp.py", "lbyl_output.txt"),
    ("Task4", "test_library.py", "output.txt"),
    ("Task5", "build_organisations.py", "output.txt"),
    ("Task5", "import_styles_demo.py", "import_output.txt"),
    ("Task6", "demo_all_cases.py", "output.txt"),
]
for folder, script, out in PROGRAMS:
    print(f"Running {folder}/{script} ...", flush=True)
    res = subprocess.run([sys.executable, script], cwd=os.path.join(ROOT, folder), capture_output=True, text=True)
    if out:
        with open(os.path.join(ROOT, folder, out), "w", encoding="utf-8") as f:
            f.write(res.stdout)
    if res.returncode != 0:
        print(res.stderr)
        sys.exit(f"{folder}/{script} failed")
# Task 6 main program (default folders)
res = subprocess.run([sys.executable, "main.py"], cwd=os.path.join(ROOT, "Task6"), capture_output=True, text=True)
print(res.stdout.strip())
print("All programs ran successfully. Now run:  python build_report.py --github <your repository URL>")
