# CSA08-1911260095-Assignment4

**Name:** Dharshidha S  **Register number:** 1911260095
**Course:** Python Programming (CSA08) - Assignment 4 (CO4): files, exceptions, modules and packages

## Environment
- Python 3.12 (the programs use the standard library only)
- `requirements.txt`: matplotlib and reportlab (only to draw the graphs and build the PDF report)

## Folders, commands and results
| Task | Folder | Command (run inside the folder) | Result |
|---|---|---|---|
| 1 Diagnose and repair a script | `Task1` | `python mess_fixed.py` | original script printed 3850 and hid 3 bad lines and 2 bills with paise; repaired version gives 6250.75, lists 3 rejected lines; line-by-line reading uses 0.02 MB against 5.6 MB for `read()` |
| 2 Biometric attendance design | `Task2` | `python attendance_monthly.py` | summary CSV, students below 75% (62.5, 37.5, 62.5), 6 damaged lines logged with file and line number; re-reading per student is about s times slower |
| 3 Error handling | `Task3` | `python complete_the_code.py`, `python processor.py`, `python lbyl_vs_eafp.py` | expected output reproduced; misuse experiment hides a NameError; EAFP and LBYL equal when bad lines are rare |
| 4 File and exception forensics | `Task4` | `python test_library.py` | defects shown (log truncated, books glued, file not closed); repaired version keeps all days and writes errors.log |
| 5 Four organisations | `Task5` | `python build_organisations.py`, `python import_styles_demo.py` | four organisations give identical output; new report changes 1, 2, 3 and 3 files |
| 6 Fest registration package | `Task6` | `python main.py`, `python demo_all_cases.py` | 9 accepted, 1 duplicate, 4 invalid e-mails, 3 damaged lines, 1 missing file - run never stops |

Run everything and rebuild the PDF report:

    python run_all.py
    python build_report.py --github https://github.com/<your-username>/CSA08-1911260095-Assignment4

Sample inputs: `Task1/mess_oct.txt`, `Task2/sample_data/`, `Task5/sample_data/`, `Task6/input/`, `Task6/input_clean/`.
Outputs and logs: `output.txt` files, `Task2/out/`, `Task6/output/`, `Task5/out/`.
Put your own terminal screenshots of each run in a `screenshots/` folder inside each task folder.
