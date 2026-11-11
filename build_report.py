"""Build the two PDFs for the portal (max 2 files, 10 MB each).

    python run_all.py
    python build_report.py --github https://github.com/<you>/CSA08-1911260095-Assignment4

PDF 1 = report (diagnoses, designs, pseudocode, failure tables, comparisons).
PDF 2 = source code, sample input files, output files and error logs.
"""
import argparse
import ast
import datetime
import os
import platform
import re
import textwrap

import matplotlib
import reportlab
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, Preformatted, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

import make_figures

ROOT = os.path.dirname(os.path.abspath(__file__))
parser = argparse.ArgumentParser()
parser.add_argument("--github", default="https://github.com/<your-username>/CSA08-1911260095-Assignment4")
parser.add_argument("--name", default="Dharshidha S")
parser.add_argument("--reg", default="1911260095")
parser.add_argument("--date", default=datetime.date.today().strftime("%d %B %Y"))
args = parser.parse_args()
PYVER = platform.python_version()

fdir = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")
for nm, fn in (("DV", "DejaVuSans.ttf"), ("DV-B", "DejaVuSans-Bold.ttf"), ("DV-I", "DejaVuSans-Oblique.ttf"),
               ("DVM", "DejaVuSansMono.ttf"), ("DVM-B", "DejaVuSansMono-Bold.ttf")):
    pdfmetrics.registerFont(TTFont(nm, os.path.join(fdir, fn)))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-B")
pdfmetrics.registerFontFamily("DVM", normal="DVM", bold="DVM-B", italic="DVM", boldItalic="DVM-B")

BODY = ParagraphStyle("body", fontName="DV", fontSize=8.8, leading=12.2, spaceAfter=4)
H1 = ParagraphStyle("h1", fontName="DV-B", fontSize=14, leading=18, spaceBefore=4, spaceAfter=6, textColor=colors.HexColor("#1f3b63"))
H2 = ParagraphStyle("h2", fontName="DV-B", fontSize=10.2, leading=13, spaceBefore=8, spaceAfter=3, textColor=colors.HexColor("#2c5d8f"))
CAP = ParagraphStyle("cap", fontName="DV-I", fontSize=7.8, leading=10, alignment=TA_CENTER, spaceAfter=6)
MONO = ParagraphStyle("mono", fontName="DVM", fontSize=6.6, leading=7.9, backColor=colors.HexColor("#f4f4f4"), borderPadding=3, spaceAfter=6)
TITLE = ParagraphStyle("title", fontName="DV-B", fontSize=22, leading=28, alignment=TA_CENTER, spaceAfter=10, textColor=colors.HexColor("#1f3b63"))
CENTER = ParagraphStyle("center", parent=BODY, alignment=TA_CENTER, fontSize=10.5, leading=15)
M = "<font name='DVM'>%s</font>"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def P(t, style=BODY):
    return Paragraph(t, style)


def bullets(items):
    return [Paragraph("•&nbsp;&nbsp;" + t, ParagraphStyle("b", parent=BODY, leftIndent=12, firstLineIndent=-9, spaceAfter=2)) for t in items]


def code(text, width=118):
    lines = []
    for ln in text.rstrip("\n").split("\n"):
        lines += textwrap.wrap(ln, width, subsequent_indent="      ", replace_whitespace=False, drop_whitespace=False) or [""]
    return Preformatted("\n".join(lines), MONO)


def table(rows, widths=None, font=7.8):
    cell = ParagraphStyle("cell", fontName="DV", fontSize=font, leading=font + 2.6)
    head = ParagraphStyle("head", parent=cell, fontName="DV-B")
    rows = [[c if not isinstance(c, str) else Paragraph(c, head if i == 0 else cell) for c in row] for i, row in enumerate(rows)]
    t = Table(rows, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dce6f2")), ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                           ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]))
    return [t, Spacer(1, 6)]


def img(name, width_cm, caption):
    path = os.path.join(ROOT, "figures", name)
    w, h = PILImage.open(path).size
    return [KeepTogether([Image(path, width=width_cm * cm, height=width_cm * cm * h / w), P(caption, CAP)])]


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8", newline="") as f:
        return f.read().replace("\r\n", "\n")


def funcs(path, names):
    src = read(path)
    out = []
    for node in ast.parse(src).body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names:
            out.append(ast.get_source_segment(src, node))
    return "\n\n".join(out)


def lines_of(path, start, end):
    return "\n".join(read(path).split("\n")[start:end])


def page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("DV", 7.5)
    canvas.setFillColor(colors.grey)
    canvas.drawString(1.6 * cm, 1.0 * cm, f"Python Programming - Assignment 4 (CO4) - {args.name} - {args.reg}")
    canvas.drawRightString(A4[0] - 1.6 * cm, 1.0 * cm, f"Page {doc.page}")
    canvas.restoreState()


def cover(story, second=False):
    story += [Spacer(1, 3 * cm), P("PYTHON PROGRAMMING", TITLE),
              P("Assignment 4 - CO4", ParagraphStyle("t2", parent=TITLE, fontSize=16, leading=20)),
              P("Robust data processing with files, exceptions, modules and packages", ParagraphStyle("t3", parent=CENTER, fontName="DV-I")),
              Spacer(1, 1.2 * cm)]
    rows = [["Student name", esc(args.name)], ["Register number", esc(args.reg)], ["Course", "Python Programming (CSA08)"],
            ["GitHub repository", esc(args.github)], ["Python version", PYVER],
            ["Libraries", f"Programs: standard library only. Report tools: matplotlib {matplotlib.__version__}, reportlab {reportlab.Version}"],
            ["Document", "Source code, sample input files, output files and error logs" if second else "Report - diagnoses, designs, pseudocode, failure tables, comparisons"],
            ["Date", esc(args.date)]]
    rows = [[P("<b>%s</b>" % a), P(b)] for a, b in rows]
    t = Table(rows, colWidths=[4.2 * cm, 12.3 * cm])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef3fa"))]))
    story += [t, Spacer(1, 0.8 * cm)]
    if not second:
        story += [P("<b>Contents.</b> Task 1 File-processing design review (6) · Task 2 From requirement to file-processing design (8) · "
                    "Task 3 Error handling (9) · Task 4 File and exception forensics (7) · Task 5 One utility organised four ways (7) · "
                    "Task 6 College fest registration desk (13). Every number in the tables and every output block comes from the programs in the "
                    "repository (folders Task1 … Task6), run with Python " + PYVER + ".", CENTER),
                  P("Pseudocode uses one consistent convention: ALGORITHM / INPUT / OUTPUT / BEGIN … END, upper-case keywords, "
                    "<- for assignment, indentation for blocks.", ParagraphStyle("n", parent=CENTER, fontSize=8.5, textColor=colors.grey))]
    story.append(PageBreak())


def num(pattern, text, cast=float):
    return cast(re.search(pattern, text).group(1))


# ======================================================================= TASK 1
def task1(story):
    out = read("Task1/output.txt")
    mem = {k: (num(rf"{re.escape(k)}\s+time=([\d.]+)s", out), num(rf"{re.escape(k)}\s+time=[\d.]+s\s+peak memory=([\d.]+) MB", out))
           for k in ("f.read()", "f.readlines()", "line by line")}
    size = num(r"File size: ([\d.]+) MB", out)
    story += [P("Task 1 - File-Processing Design Review: Diagnose and Repair a Poor Script (K4 - Analyse, 6 marks)", H1),
              P("Task 1.1 - Diagnosis (2 marks)", H2),
              P("The original script was run (Task1/mess_bad.py) on a sample file with 8 records; it printed <b>Total 3850</b> and listed only "
                "4 students. The correct total of the 5 valid bills is <b>6250.75</b>, and 3 lines should have been reported as rejected. "
                "Nothing in the output told the office that anything was wrong."), code(lines_of("Task1/output.txt", 0, 8))]
    rows = [["#", "Deficiency", "What could go wrong in the hostel office"],
            ["1", "Hard-coded path <font name='DVM'>C:\\\\Users\\\\Office\\\\Desktop\\\\mess_oct.txt</font>",
             "The script works only on one computer and one folder. On any other PC, or when the file is moved or renamed, it crashes with FileNotFoundError; "
             "the file name cannot be chosen per month or per hostel, and the script cannot be tested on a sample file."],
            ["2", "File never closed (no close() or with)", "The handle stays open until the program ends or the garbage collector runs; on Windows the file stays locked, "
             "so the clerk cannot save or move mess_oct.txt (or Excel reports it as in use); many open handles can exhaust the operating-system limit."],
            ["3", "<font name='DVM'>f.read()</font> loads the whole file, then <font name='DVM'>split</font> builds a second copy as a list",
             f"Memory grows with the file: measured {mem['f.read()'][1]:.2f} MB for a {size:.2f} MB file against {mem['line by line'][1]:.2f} MB line by line. "
             "A year of bills for the whole college, or a log file of several GB, could exhaust memory."],
            ["4", "Bare <font name='DVM'>except: pass</font>", "Hides every error, including mistakes in the program itself (a mistyped name, IndexError), and even "
             "Ctrl+C (KeyboardInterrupt). A wrong total is printed as if everything were fine."],
            ["5", "<font name='DVM'>int()</font> on amounts such as 1250.50", "<font name='DVM'>int('1250.50')</font> raises ValueError, which the bare except hides, so the bill "
             "is silently left out of the total (Anitha's 1250.50 and Esha's 1100.25 vanished). Converting to float would instead give rounding errors "
             "in money; <font name='DVM'>Decimal</font> is exact."],
            ["6", "Report built with repeated <font name='DVM'>+</font> on a string", "Each + may copy the whole growing string; in the worst case the time is O(n²) "
             "for n lines. CPython sometimes optimises this, but it is not guaranteed. A list joined once (or writing line by line) is O(n)."],
            ["7", "Last empty line of the file", "<font name='DVM'>split('\\n')</font> returns a final '' whose <font name='DVM'>parts[2]</font> raises IndexError. The bare except "
             "swallows it, so this harmless case and a genuinely damaged line look identical."],
            ["8", "No record of rejected lines", "Charan ('abc'), Divya (missing amount) and Farook (-50) disappeared without a trace. The office cannot tell which "
             "students were not billed or which lines to correct; the total is wrong with no indication."],
            ["9", "Other weaknesses: no encoding given; no check for negative amounts; spaces around fields",
             "The default encoding differs between computers (Tamil names can be garbled); a negative bill is added without question "
             "(Farook -50 was accepted by the original script); names containing commas split wrongly."]]
    story += table(rows, [0.7 * cm, 5.6 * cm, 10.3 * cm], font=7.4)
    story += [P("Task 1.2 - Repaired design (3 marks)", H2),
              P("The repaired script (Task1/mess_fixed.py) uses a function with the file name as parameter, a <font name='DVM'>with</font> statement, "
                "line-by-line reading, only specific exceptions (<font name='DVM'>InvalidOperation</font>, and <font name='DVM'>FileNotFoundError</font>/"
                "<font name='DVM'>PermissionError</font> in the caller) and a list of rejected lines with line number and reason.")]
    story.append(code(funcs("Task1/mess_fixed.py", {"total_mess_bills", "main"})))
    story += [P("Output on the same sample file:"), code(lines_of("Task1/output.txt", 8, 20))]
    defence = ("My version reads one line at a time, so memory stays at about one line (0.02 MB measured) instead of the whole text plus "
               "a list of 50,000 strings. The with statement closes the file even after an error. Amounts are Decimal, so paise are exact. "
               "Only specific errors are caught, and every rejected line is stored with its line number and reason, so no bill vanishes "
               "silently and the office can correct it. The file name is a parameter, so the function can be tested on any file.")
    assert len(defence.split()) <= 100, len(defence.split())
    story += [P("Task 1.3 - Design defence (1 mark, %d words)" % len(defence.split()), H2), P(defence)]
    story += [P("Alternative concept and complexity analysis", H2),
              P("<b>f.read() or f.readlines() instead of line-by-line iteration.</b> With <font name='DVM'>f.read()</font> the whole text is one string that is then split; "
                "with <font name='DVM'>f.readlines()</font> the file becomes a list of 50,000 line strings; both are processed afterwards with the same loop. "
                "Measured on a generated 50,000-line file (1% damaged lines):")]
    story += table([["Method", "Time", "Peak memory", "Memory in Big-O"],
                    ["f.read() + split", f"{mem['f.read()'][0] * 1000:.1f} ms", f"{mem['f.read()'][1]:.2f} MB", "O(file size): text plus the list of pieces"],
                    ["f.readlines()", f"{mem['f.readlines()'][0] * 1000:.1f} ms", f"{mem['f.readlines()'][1]:.2f} MB", "O(file size): list of all lines"],
                    ["for line in f", f"{mem['line by line'][0] * 1000:.1f} ms", f"{mem['line by line'][1]:.2f} MB", "O(longest line): one line at a time"]],
                   [3.6 * cm, 2.4 * cm, 3 * cm, 7.6 * cm])
    story += [P("All three read each of the n = 50,000 lines once, so the time is O(n) in every case, and the measured times are almost the same. "
                f"The memory differs: reading everything needs O(file size) ({mem['f.read()'][1] / mem['line by line'][1]:.0f} times more here), iterating needs O(length of one line). "
                "For a 1.6 MB file all three are acceptable; for a file of several GB only line-by-line iteration works. The repaired function "
                f"(which also validates every line and stores the rejects) took about {num(r'repaired function.*?: ([\d.]+)s', out) * 1000:.0f} ms.")]
    story.append(PageBreak())


# ======================================================================= TASK 2
def task2(story):
    out = read("Task2/output.txt")
    story += [P("Task 2 - From Requirement to File-Processing Design: Biometric Attendance Files (K3 - Apply, 8 marks)", H1),
              P("Task 2.1 - Model the data (2 marks)", H2)]
    story += bullets([
        "<b>Input:</b> one text file per day, <font name='DVM'>attendance_YYYY-MM-DD.txt</font>; each line <font name='DVM'>register_number,date,status</font>, for example "
        "<font name='DVM'>192311001,2026-10-08,P</font>. A line is valid if it has 3 fields, a 9-digit register number, a real date (YYYY-MM-DD) and status P or A; "
        "a second line for the same student and date is also rejected as a duplicate.",
        "<b>Data structures:</b> dictionary <font name='DVM'>counts</font> (register number → [present, absent]) for the totals; a set <font name='DVM'>seen</font> of "
        "(register number, date) pairs for duplicate detection; a list <font name='DVM'>damaged</font> of (file name, line number, text, reason) tuples; "
        "a list <font name='DVM'>below</font> of (register number, percentage).",
        "<b>Output 1 - attendance_summary.csv:</b> header <font name='DVM'>register_number,present,absent,percentage</font> and one row per student, sorted by register number; "
        "also <b>below_75.txt</b>: one line <font name='DVM'>192311002 62.5%</font> for every student whose percentage is below 75 (exactly 75.0 is not below).",
        "<b>Output 2 - damaged_lines.log:</b> one line per rejected line: <font name='DVM'>file name:line number: reason | 'original text'</font>."])
    story += [P("Task 2.2 - File operations (2 marks)", H2)]
    story += table([["Operation", "Choice", "Reason"],
                    ["List the daily files", "<font name='DVM'>pathlib.Path(folder).glob('attendance_*.txt')</font>, sorted", "finds exactly the month's files in a repeatable order (os.listdir gives names only, in arbitrary order)"],
                    ["Open input", "mode <font name='DVM'>'r'</font>, <font name='DVM'>encoding='utf-8'</font>, inside <font name='DVM'>with</font>", "text file, read only; the encoding is explicit so the result does not depend on the computer; closed even after an error"],
                    ["Read", "iterate: <font name='DVM'>for line in f</font>", "one line in memory at a time (a month of files may be large); read() would load everything and readline() needs a manual loop"],
                    ["Write the CSV and below_75.txt", "mode <font name='DVM'>'w'</font>, utf-8, <font name='DVM'>csv.writer</font> with <font name='DVM'>newline=''</font>", "each run must produce a fresh report, so an old report is replaced"],
                    ["Write damaged_lines.log", "mode <font name='DVM'>'w'</font> here (one log per monthly run); <font name='DVM'>'a'</font> if one log must collect several runs", "'w' keeps this month's log clean; append would mix months"],
                    ["Write", "<font name='DVM'>f.write(text + newline)</font> / <font name='DVM'>writer.writerow</font>", "explicit newline after every record"]],
                   [3.7 * cm, 6.2 * cm, 6.7 * cm], font=7.4)
    story += [P("Task 2.3 - Pseudocode (3 marks)", H2)]
    story.append(code("""ALGORITHM ProcessMonth
INPUT : folder - the directory that holds the daily files
OUTPUT: attendance_summary.csv, below_75.txt, damaged_lines.log
BEGIN
    counts  <- empty dictionary            // reg -> [present, absent]
    seen    <- empty set                   // (reg, date) pairs already counted
    damaged <- empty list
    files   <- sorted list of files in folder that match "attendance_*.txt"      // pathlib
    FOR EACH file IN files DO
        TRY
            OPEN file FOR reading (utf-8)
            lineNo <- 0
            FOR EACH line IN file DO
                lineNo <- lineNo + 1
                TRY
                    (reg, date, status) <- CheckLine(line)      // raises error if the line is damaged
                    IF (reg, date) IS IN seen THEN RAISE error "duplicate"
                ON ERROR (reason):
                    APPEND (file.name, lineNo, line, reason) TO damaged
                    CONTINUE with next line
                END TRY
                ADD (reg, date) TO seen
                IF reg IS NOT IN counts THEN counts[reg] <- [0, 0]
                IF status = "P" THEN counts[reg][0] <- counts[reg][0] + 1  ELSE counts[reg][1] <- counts[reg][1] + 1
            END FOR
            CLOSE file
        ON ERROR (cannot open / read / decode):
            APPEND (file.name, 0, "", reason) TO damaged
        END TRY
    END FOR
    OPEN attendance_summary.csv FOR writing;  WRITE header
    below <- empty list
    FOR EACH reg IN sorted keys of counts DO
        pct <- 100 * counts[reg][0] / (counts[reg][0] + counts[reg][1])
        WRITE row (reg, present, absent, pct to 1 decimal)
        IF pct < 75 THEN APPEND (reg, pct) TO below
    END FOR
    WRITE every item of below TO below_75.txt;  WRITE every item of damaged TO damaged_lines.log
END

FUNCTION CheckLine(line)
    fields <- split line at commas, strip each field
    IF line is empty THEN error "empty line"
    IF number of fields <> 3 THEN error "expected 3 fields"
    IF reg is not 9 digits THEN error "invalid register number"
    IF date is not a valid YYYY-MM-DD date THEN error "invalid date"
    IF status NOT IN {"P", "A"} THEN error "invalid status"
    RETURN (reg, date, status)"""))
    story += [P("Implementation (Task2/attendance_monthly.py) - output on the 8 sample daily files:", BODY), code(lines_of("Task2/output.txt", 0, 21))]
    story += [P("Task 2.4 - Trace (1 mark)", H2),
              P("File <font name='DVM'>attendance_2026-10-08.txt</font> with 4 lines, one damaged. Start: counts = {}, seen = {}, damaged = [].")]
    story += table([["lineNo", "Line", "CheckLine result", "Action", "counts after the line"],
                    ["1", "192311001,2026-10-08,P", "valid ('192311001','2026-10-08','P')", "add to seen; present + 1", "{001: [1, 0]}"],
                    ["2", "192311002,2026-10-08,A", "valid", "add to seen; absent + 1", "{001: [1, 0], 002: [0, 1]}"],
                    ["3", "192311003,2026-10-08", "error: expected 3 fields, found 2", "append (file, 3, line, reason) to damaged; CONTINUE", "unchanged"],
                    ["4", "192311001,2026-10-09,P", "valid; (001, 2026-10-09) not in seen", "present + 1 for 001", "{001: [2, 0], 002: [0, 1]}"]],
                   [1.2 * cm, 3.8 * cm, 4 * cm, 4.4 * cm, 3.2 * cm], font=7.2)
    story += [P("The program output for this file (lines 'Trace file' above) is <font name='DVM'>counts : {'192311001': [2, 0], '192311002': [0, 1]}</font> and "
                "<font name='DVM'>damaged: [('attendance_2026-10-08.txt', 3, '192311003,2026-10-08', 'expected 3 fields, found 2')]</font>, "
                "exactly as traced. Student 001 therefore has 2 of 2 = 100%, student 002 has 0 of 1 = 0%.")]
    story += [P("Alternative concept and complexity analysis", H2),
              P("<b>Re-read all daily files for every student.</b> For each of the s students open every one of the f files and scan every one of the l lines "
                "(function <font name='DVM'>percentages_reread</font>), keeping only that student's lines. The result is identical (checked by the program), "
                "but the time is <b>O(s·f·l)</b>, against <b>O(f·l)</b> for one pass with the dictionary. Space: both keep O(s) counters, and both read line by line "
                "(O(1) per line); the one-pass method also keeps the <font name='DVM'>seen</font> set, O(f·l) in the worst case.")]
    rows = re.findall(r"s=\s*(\d+) students.*?l=\s*(\d+) lines/file: one pass=([\d.]+)s\s+re-read per student=([\d.]+)s\s+ratio=(\d+)x", out)
    story += table([["Students s", "Files f", "Lines per file l", "One pass", "Re-read per student", "Ratio"]] +
                   [[a, "30", b, f"{float(c):.4f} s", f"{float(d):.4f} s", f"{e}×"] for a, b, c, d, e in rows], [2.4 * cm, 2 * cm, 3 * cm, 2.8 * cm, 3.6 * cm, 2.4 * cm])
    story += img("task2_timing.png", 10, "Fig. 1 - The re-read method grows with s·s·f (here l = s), the one-pass method with s·f.")
    story += [P(f"The ratio is close to s ({', '.join(r[4] for r in rows)} for s = {', '.join(r[0] for r in rows)}), as the O(s·f·l) versus O(f·l) comparison predicts. With 3,000 students it would "
                "already be thousands of times slower.")]
    story.append(PageBreak())


# ======================================================================= TASK 3
def task3(story):
    story += [P("Task 3 - Design the Error Handling: Exceptions in the Attendance Processor (K4 - Analyse, 9 marks)", H1),
              P("Task 3.1 - Identify the failures (3 marks)", H2),
              P("Every failure below was triggered on purpose by Task3/processor.py; the 'raised' column is what Python actually reported.")]
    story += table([["Failure", "Cause", "Built-in exception (observed)", "Where it is handled"],
                    ["Missing folder", "folder name wrong or folder deleted", "FileNotFoundError (<font name='DVM'>os.listdir</font>)", "at the start of the month run: report and stop that run"],
                    ["Missing file", "daily file absent", "FileNotFoundError (<font name='DVM'>open</font>)", "per file: log it, continue with the next file"],
                    ["Permission denied / path is a folder", "no read permission; a folder given as a file", "PermissionError (Windows) or IsADirectoryError (Linux, macOS); both are OSError", "per file: log, continue"],
                    ["Wrong encoding", "file saved in another encoding", "UnicodeDecodeError (a ValueError)", "per file: log, continue"],
                    ["Damaged line - wrong number of fields", "missing field", "ValueError on unpacking, IndexError on <font name='DVM'>parts[2]</font>; here InvalidRecord", "per line: log with line number, continue"],
                    ["Damaged line - bad value", "status or number not valid", "ValueError (<font name='DVM'>int('P')</font>, bad date); here InvalidRecord", "per line"],
                    ["Empty file", "no lines", "none while reading, but ZeroDivisionError when the percentage is computed", "check the total before dividing"],
                    ["Other I/O problems", "disk or network error", "OSError", "per file: log, continue"]],
                   [3.4 * cm, 3.5 * cm, 5.4 * cm, 4.3 * cm], font=7.2)
    story += [code(lines_of("Task3/output.txt", 0, 10), 118)]
    story += [P("Task 3.2 - Custom exception (2 marks)", H2),
              P(f"{M % 'class InvalidRecord(Exception)'} describes one damaged line. It is <b>raised</b> in {M % 'parse_line()'}, the only place that knows the format "
                f"(wrong number of fields, bad date, bad status). It is <b>handled</b> in the loop of {M % 'process_file()'} (and in {M % 'summarise()'}), the only place that "
                "knows what to do with a bad line: record the line number and message and go on to the next line. It is not caught in <font name='DVM'>parse_line</font> "
                "(it cannot decide what to do) or in the main program (one bad line must not stop a file). A dedicated class lets the handler catch damaged lines "
                "only, so other errors (a real bug) are not hidden.")]
    story.append(code(funcs("Task3/processor.py", {"InvalidRecord", "parse_line"})))
    story += [P("Task 3.3 - The complete try statement (3 marks)", H2)]
    story.append(code(funcs("Task3/processor.py", {"process_file"})))
    story += bullets([
        "<b>try</b> contains the reading loop; <b>except FileNotFoundError / PermissionError</b> around <font name='DVM'>open</font> and <b>except UnicodeDecodeError</b> around the reading: "
        "each named exception gets its own message; no other exception is caught.",
        "<b>else</b> (attached to the inner try) runs only when <font name='DVM'>parse_line</font> raised nothing, so the counting code is not protected by the "
        "<font name='DVM'>except InvalidRecord</font> and cannot hide its own errors.",
        "<b>finally</b> closes the file whatever happened (normal end, damaged lines, decoding error).",
        "<b>raise … from …</b>: the low-level error is turned into a clear message for the caller while the original is kept as <font name='DVM'>__cause__</font> "
        "(the output shows 'caused by FileNotFoundError(2, …)' and 'caused by UnicodeDecodeError(…)'); an invalid date becomes InvalidRecord <i>from</i> the ValueError of "
        "<font name='DVM'>strptime</font>."])
    story += [code(lines_of("Task3/output.txt", 10, 19))]
    story += [P("Task 3.4 - Misuse experiment (1 mark)", H2),
              P("In a copy of the processor the specific except clauses were replaced by <font name='DVM'>except Exception: pass</font>, and the line "
                "<font name='DVM'>present += 1</font> was mistyped as <font name='DVM'>presnt += 1</font>."), code(lines_of("Task3/output.txt", 20, 25)),
              P("<b>Why the error is hidden.</b> The mistyped name raises <font name='DVM'>NameError</font>, which is a subclass of <font name='DVM'>Exception</font>, so "
                "<font name='DVM'>except Exception</font> catches it; <font name='DVM'>pass</font> then discards it and the loop continues. The program never crashes and prints "
                "a plausible answer (0 present) that is simply wrong. Without the blanket except, Python stops at once and names the mistake. Specific exceptions "
                "catch only the failures that were expected; blanket handlers also swallow bugs.")]
    story += [P("Complete the Code (Task3/complete_the_code.py)", H2),
              P("TODO 1 raises <font name='DVM'>InvalidRecord</font> for the wrong number of fields or a status other than P or A and otherwise returns <font name='DVM'>tuple(parts)</font>. "
                "TODO 2 opens the file with <font name='DVM'>with</font>, parses each line inside <font name='DVM'>try/except InvalidRecord</font>, counts P and A and records "
                "<font name='DVM'>(line number, message)</font>. The rest of the program is unchanged. Output (identical to the expected output); the second line comes from "
                "calling <font name='DVM'>summarise()</font> with a file name that does not exist: <font name='DVM'>FileNotFoundError</font> is handled inside the function and "
                "reported as an error entry."),
              code(funcs("Task3/complete_the_code.py", {"parse_line", "summarise"})), code(read("Task3/complete_output.txt"))]
    story += [P("Alternative concept and complexity analysis", H2),
              P("<b>Look before you leap (LBYL).</b> Instead of raising and catching InvalidRecord, check each line with <font name='DVM'>if</font> statements "
                "(<font name='DVM'>if len(parts) != 3 or parts[2] not in ('P','A'): count it as bad</font>) before using it. The program "
                "Task3/lbyl_vs_eafp.py counts good and bad lines for 200,000 lines in both styles (identical results) and measures the cost per line:")]
    rows = re.findall(r"([\d.]+)%\s+(\d+) ns\s+(\d+) ns\s+([\d.]+)x", read("Task3/lbyl_output.txt"))
    story += table([["Bad lines", "EAFP (raise/catch)", "LBYL (if)", "EAFP / LBYL"]] + [[f"{a}%", f"{b} ns", f"{c} ns", f"{d}×"] for a, b, c, d in rows],
                   [3 * cm, 4 * cm, 4 * cm, 3 * cm])
    story += img("task3_timing.png", 10, "Fig. 2 - Cost per line in the two styles.")
    story += [P("<b>Analysis.</b> Both styles do O(1) work per line, so the time for n lines is O(n) and the space O(1) extra. A <font name='DVM'>try</font> block costs almost nothing when "
                "no exception is raised (modern Python), so with <b>rare bad lines</b> (0 to 1%) the two styles are equal within measurement noise and EAFP gives shorter code that "
                "cannot be fooled by a case the checks forgot. Raising and catching an exception costs several times more than a failed <font name='DVM'>if</font>, so when "
                "<b>bad lines are common</b> (50% to 100%) LBYL is 2 to 3 times faster per line. LBYL also has a weakness for files: checking that a file exists "
                "and then opening it leaves a gap in which the file can disappear, which EAFP avoids. For attendance files, where bad lines are rare, EAFP is the better choice.")]
    story.append(PageBreak())


# ======================================================================= TASK 4
def task4(story):
    out = read("Task4/output.txt")
    story += [P("Task 4 - File and Exception Forensics (K4 - Analyse, 7 marks)", H1), P("Task 4.1 - Locate the defects (2 marks)", H2)]
    story += bullets([
        "<b>Earlier days are lost:</b> <font name='DVM'>open('returns.log', 'w')</font> truncates (empties) the file every time <font name='DVM'>save_returns</font> is called, so each "
        "day starts with an empty log and only the last day survives. Mode <font name='DVM'>'a'</font> is needed.",
        "<b>Books are joined together:</b> <font name='DVM'>log.write(b)</font> writes the text without a line break, so 'Networks' and 'Databases' become <font name='DVM'>NetworksDatabases</font>. "
        "write() does not add a newline (unlike print()).",
        "<b>When write() fails</b> (for example an item that is not a string, a full disk): the exception leaves the function before <font name='DVM'>log.close()</font>, so the file is never "
        "explicitly closed; buffered text may not be saved, the file stays open (and locked on Windows) until Python's garbage collector releases it. A <font name='DVM'>with</font> statement "
        "or <font name='DVM'>try/finally</font> is needed.",
        "<b>Further defects:</b> <font name='DVM'>open(day_file).read()</font> never closes the day file (Python even raises a ResourceWarning); only FileNotFoundError is handled, so a "
        "PermissionError, a decoding error or a TypeError ends the program with no message saved; the message 'missing' is only printed, does not say which file, and is not "
        "recorded; <font name='DVM'>split('\\n')</font> leaves an empty last item."])
    story += [P("Task 4.2 - Evidence (2 marks)", H2),
              P("Task4/test_library.py creates three day files, runs the <b>original</b> <font name='DVM'>process()</font> for each day and prints the log; it then forces a write failure and "
                "checks the open files, and finally runs the repaired program on the same days."), code(lines_of("Task4/output.txt", 0, 14))]
    story += [P("Task 4.3 - Repaired program (2 marks)", H2), code(funcs("Task4/library_fixed.py", {"save_returns", "log_error", "process"}))]
    story += [P("Output of the repaired program for the three days plus a missing file and a file with bad encoding (all days are kept, each book on its own line, the two problems are "
                "recorded with time, file name and cause, and the program keeps going):"), code(lines_of("Task4/output.txt", 14, 36))]
    story += [P("Task 4.4 - Rules that prevent recurrence (1 mark)", H2)]
    story += bullets(["<b>Rule 1 - always open files with <font name='DVM'>with</font></b> (or try/finally), so that closing never depends on the code running to the end.",
                      "<b>Rule 2 - choose the mode deliberately and write complete records:</b> 'a' for a log that accumulates, 'w' only when the old content must be replaced, and "
                      "always add the newline after each record.",
                      "(Supporting rule) catch the specific exceptions you expect and write them, with file name and cause, to an error log."])
    story += [P("Alternative concept and complexity analysis", H2),
              P("<b>Manual open/close inside try/finally instead of with.</b> The function <font name='DVM'>save_returns_finally</font> opens the file before the try, writes inside the try and "
                "calls <font name='DVM'>close()</font> in the finally clause. Both versions do b writes for b books: time <b>O(b)</b> and extra space <b>O(1)</b>, so "
                "<b>the complexity does not change</b>; the measurement (20,000 calls) shows the same time within noise:"),
              code(lines_of("Task4/output.txt", 36, 40)),
              P("<b>How many files can remain open after an error?</b> Original program: <b>1</b> per failing call (the log), plus the day file that was never closed - closing then depends on "
                "garbage collection. Repaired with <b>with</b>: <b>0</b> (the output shows 0 inside the except block). Manual <b>try/finally</b>: <b>0</b> when open() is placed before the try and "
                "close() is in the finally (also shown: 0). Manual closing has two traps that the with statement does not: if open() is inside the try, the finally may "
                "call close() on a variable that was never assigned, and when several files are closed one after another in one finally, an error in the first close() leaves the "
                "remaining ones open (up to k − 1 of k files). <font name='DVM'>with a, b:</font> closes every file.")]
    story.append(PageBreak())


# ======================================================================= TASK 5
def task5(story):
    out = read("Task5/output.txt")
    base = "Task5/organisations_after"
    story += [P("Task 5 - The Same Utility Organised Four Ways (K5 - Evaluate, 7 marks)", H1), P("Task 5.1 - Four organisations (3 marks)", H2),
              P("The attendance processor has reading functions (<font name='DVM'>check_line, read_month</font>), statistics (<font name='DVM'>count_attendance, percentages, below_threshold</font>) and "
                "report writers (<font name='DVM'>write_summary, write_below, write_damaged</font>). Task5/build_organisations.py builds the four organisations from identical function "
                "bodies (so that only the organisation differs), runs each on the same sample data and compares the output files byte by byte (identical: True)."),
              ]
    story += table([["Organisation", "Files", "How it is used"],
                    ["(a) one script", "attendance.py", "all functions plus <font name='DVM'>run()</font> and the <font name='DVM'>if __name__ == '__main__':</font> block; "
                                                         "<font name='DVM'>python attendance.py data out</font>"],
                    ["(b) one module + main script", "attendance_lib.py, main.py", "functions in the module; main.py: <font name='DVM'>import attendance_lib as al</font> and calls <font name='DVM'>al.read_month(…)</font>"],
                    ["(c) three modules in one folder", "reader.py, stats.py, report.py, main.py", "main.py: <font name='DVM'>import reader, stats, report</font>"],
                    ["(d) package", "attendance/__init__.py, reader.py, stats.py, report.py; main.py", "main.py: <font name='DVM'>from attendance import reader, stats, report</font>"]],
                   [4.2 * cm, 5.4 * cm, 7 * cm], font=7.4)
    story += img("task5_package.png", 13.5, "Fig. 3 - Organisation (d): the package attendance/ with its sub-modules, and the three ways of importing from it.")
    story += [P("main.py of organisation (d) (the <font name='DVM'>if __name__ == '__main__':</font> test makes the file run as a program but lets it be imported without running):"),
              code(read(f"{base}/d_package/main.py"))]
    story += [P("Output of the four organisations (same result in each):"), code(lines_of("Task5/output.txt", 0, 6))]
    story += [P("Task 5.2 - Change the requirement (2 marks)", H2),
              P("New report: students absent for three consecutive recorded days. A function <font name='DVM'>absent_streaks</font> (statistics), a writer <font name='DVM'>write_streaks</font> "
                "(report) and two lines in <font name='DVM'>run()</font> (the main script) are added to each organisation. Result for the sample data:"),
              code(lines_of("Task5/output.txt", 7, 12)),
              code(funcs(f"{base}/d_package/attendance/stats.py", {"absent_streaks"}))]
    rows = re.findall(r"(\w+)\s+(\d+)\s+(\d+) \|\s+(\d+)\s+(\d+)\s+(.*)", out)
    story += table([["Organisation", "Files", "Lines", "Files changed", "Lines added", "Changed files"]] +
                   [[a, b, c, d, e, esc(f)] for a, b, c, d, e, f in rows], [3 * cm, 1.4 * cm, 1.4 * cm, 2.3 * cm, 2.2 * cm, 6.3 * cm], font=7.4)
    story += [P("The same 30 lines are added in every organisation (counted with <font name='DVM'>difflib</font>). The number of files touched is 1, 2, 3 and 3: in the single script "
                "everything is edited in one file, while the modular versions touch the statistics module, the report module and the main script, but "
                "<b>reader.py and the other untouched modules are not edited at all</b> (and so cannot be broken by the change).")]
    story += [P("Task 5.3 - Comparison (2 marks)", H2)]
    story += table([["Criterion", "(a) one script", "(b) one module + main", "(c) three modules", "(d) package"],
                    ["Readability", "good for 100 lines; the file grows and mixes three responsibilities", "functions separate from the control code", "one responsibility per file; short files", "same as (c), plus a named group (attendance.stats)"],
                    ["Reuse", "poor: importing it for one function also runs or loads everything (and needs the guard to avoid running)", "good: any program can <font name='DVM'>import attendance_lib</font>", "good: reuse only reader.py, for example", "best: one importable unit that can be installed or shared"],
                    ["Testing", "functions can be tested only by importing the whole script", "functions testable separately from main", "each module tested alone (stats needs no files)", "same as (c), tests can mirror the package layout"],
                    ["Naming conflicts", "one namespace: two functions of the same name overwrite each other", "one namespace inside the module", "short names such as <font name='DVM'>stats</font> or <font name='DVM'>report</font> can clash with other top-level modules or libraries", "names are qualified (attendance.stats) so they cannot clash with a top-level stats.py"]],
                   [2.4 * cm, 3.4 * cm, 3.4 * cm, 3.7 * cm, 3.7 * cm], font=7)
    story += [P("<b>The three import statements</b> (demonstrated in Task5/import_styles_demo.py):")]
    story += bullets([
        "<b>import attendance.stats</b> binds only the name <font name='DVM'>attendance</font>; a function is called with the full path, <font name='DVM'>attendance.stats.percentages(…)</font>. Clearest origin, longest to write; no clash is possible.",
        "<b>from attendance import stats</b> binds the name <font name='DVM'>stats</font> (the same module object); the call is <font name='DVM'>stats.percentages(…)</font>. A good balance, and the module name keeps the origin visible.",
        "<b>from attendance.stats import percentages</b> binds the name <font name='DVM'>percentages</font> directly (the same function object); the call is <font name='DVM'>percentages(…)</font>. "
        "Shortest, but the origin is hidden and the name can be overwritten by a local variable of the same name (shown in the demonstration) or clash with another import."]) + [code(read("Task5/import_output.txt"))]
    story += [P("Alternative concept and complexity analysis", H2),
              P("<b>All functions in one script instead of a package.</b> The solution is organisation (a): one file of about 100 lines, no packages, no import of project modules. "
                "Costs measured by Task5/build_organisations.py:"), code(lines_of("Task5/output.txt", 18, 22)),
              P("<b>Import cost.</b> Python executes a module's code only on the <i>first</i> import and stores the module object in <font name='DVM'>sys.modules</font>; every later "
                "<font name='DVM'>import</font> is a dictionary lookup (about %d ns), so the one-time cost does not repeat. The first import of the package takes about %.0f ms against %.0f ms for the "
                "single file; most of both is loading the standard-library modules (csv, datetime, pathlib), not the project's own code. The memory of the loaded package is under 1 MB "
                "(allocation measured with tracemalloc), the same order as the single script. So the time and memory cost of the package structure is a constant, small, one-time amount, "
                "independent of the size of the data (O(1) in the data size), and it is paid back by reuse." % (
                    num(r"cached in sys.modules\): (\d+) ns", out), num(r"first import of the package: ([\d.]+) ms", out),
                    num(r"one-file script as a module: ([\d.]+) ms", out)))]
    story += [P("<b>Effort to find and change a function.</b> In (a) the reader scans one file of ~100 lines (growing with every feature); in (b) 2 files; in (c) and (d) the name of the "
                "module tells which of 4 or 5 short files to open (the statistics function is in stats.py of about 35 lines). For this change the single script needed the fewest files "
                "(1), but the modular versions needed more files with the same number of added lines and left reader.py untouched. The advantage of the package grows with project "
                "size: in a 5,000-line project a single script would force every change through one huge file.")]
    story.append(PageBreak())


# ======================================================================= TASK 6
def task6(story):
    out = read("Task6/output.txt")
    story += [P("Task 6 - Design Challenge: College Fest Registration Desk (K5 - Evaluate, 13 marks)", H1),
              P("Stage 1 - Interpret the problem (2 marks)", H2),
              P("<b>Inputs:</b> five department files <font name='DVM'>registrations_cse.txt, _it, _ece, _mech, _civil</font>; every line "
                "<font name='DVM'>register_number,name,department,email,event1;event2;…</font>. <b>Outputs:</b> master list, one file per event, a summary report and an error log. "
                "<b>Rules and testable requirements:</b>")]
    story += table([["Req.", "Testable statement", "Test case"],
                    ["R1", "Every valid line of every existing file appears exactly once in <font name='DVM'>master_list.csv</font>", "9 valid lines → 9 rows"],
                    ["R2", "A register number already accepted is not added again; the repeat is logged as DUPLICATE (the first registration is kept)", "192311002 in the IT file"],
                    ["R3", "An e-mail with no @, more than one @, empty local or domain part, a space, a domain without an inner dot or with '..' is rejected and logged INVALID_EMAIL", "charan.r@mail; farook mail.com; kavi@@mail.com; omar@.com"],
                    ["R4", "A line with the wrong number of fields, a register number that is not 9 digits, an empty name/department or no event is logged DAMAGED with file name and line number", "Gita (3 fields); 'abc'; no event"],
                    ["R5", "For every event a file lists the register number and name of each participant, sorted", "events/dance.txt …"],
                    ["R6", "summary.txt gives lines read, accepted, duplicates, invalid e-mails, damaged lines, missing files, participants per department and per event", "summary.txt"],
                    ["R7", "A missing or unreadable department file never stops the run; it is logged MISSING_FILE / UNREADABLE_FILE", "registrations_civil.txt absent"],
                    ["R8", "Every error record has source file, line number, kind, reason and the original text", "errors.log"],
                    ["R9", "The program ends normally (no traceback) for every test input", "all cases below"],
                    ["R10", "Time grows linearly with the number of registrations (duplicate test in O(1) average)", "set versus list measurement"]],
                   [1.1 * cm, 10.2 * cm, 5.3 * cm], font=7.3)
    story += [P("Stage 2 - Processing flow (2 marks)", H2)]
    story += img("task6_flow.png", 16.4, "Fig. 4 - Flow from the five input files to the four kinds of output; validation, duplicate removal and error logging are marked.")
    story += [P("Stage 3 - Critical design decisions (2 marks)", H2)]
    story += bullets([
        "<b>Duplicates:</b> a <b>set</b> of register numbers already accepted. Testing <font name='DVM'>reg in seen</font> is O(1) on average, so n registrations cost O(n). The first registration "
        "is kept and the later one is logged, so nothing is lost silently and the committee can compare the two lines.",
        "<b>E-mail validation with string methods only:</b> reject if it contains a space or <font name='DVM'>count('@') != 1</font>; <font name='DVM'>split('@')</font> into local and domain; both "
        "non-empty; the domain must contain a '.', must not start or end with '.', and the address must not contain '..'. (A full RFC check is not needed for a fest list; this removes "
        "typical typing mistakes.)",
        "<b>Which exceptions are handled where:</b> <b>validators</b> raise the package's own exceptions <font name='DVM'>DamagedLine</font>, <font name='DVM'>InvalidEmail</font> (both subclasses of "
        "<font name='DVM'>RegistrationError</font>) and the pipeline raises <font name='DVM'>DuplicateRegistration</font>; <b>the line loop in pipeline.process</b> handles these three so that one bad line never stops "
        "the file; <b>the file level in pipeline.process</b> handles FileNotFoundError (missing department file), PermissionError and UnicodeDecodeError (unreadable file); "
        "<b>readers</b> handles nothing (it only yields lines), and <b>main</b> does not need to catch anything.",
        "<b>Encoding and files:</b> utf-8 everywhere, <font name='DVM'>with</font> for every file, read line by line, output files written once at the end in mode 'w', output folder created with "
        "<font name='DVM'>os.makedirs</font>."])
    story += [P("Stage 4 - The package (4 marks)", H2)]
    story += table([["Module", "Functions / classes", "Responsibility"],
                    ["fest/__init__.py", "<font name='DVM'>__all__</font>", "marks the folder as a package"],
                    ["fest/errors.py", "RegistrationError, DamagedLine, InvalidEmail, DuplicateRegistration", "the exceptions"],
                    ["fest/readers.py", "read_lines(path)", "yield (line number, text) for every non-empty line"],
                    ["fest/validators.py", "valid_email(email), parse_registration(line), Registration", "check one line; return a record or raise"],
                    ["fest/writers.py", "write_master, write_event_files, write_errors, write_summary", "all output files"],
                    ["fest/pipeline.py", "process(input_dir, output_dir)", "connects read → validate → de-duplicate → write; keeps counters"],
                    ["main.py", "-", "runs process() on the folders given on the command line"]],
                   [3.6 * cm, 7 * cm, 6 * cm], font=7.4)
    story.append(code("""ALGORITHM ReadLines(path)                                      // fest/readers.py
    OPEN path FOR reading (utf-8)                    // errors are NOT caught here; the caller decides
    lineNo <- 0
    FOR EACH line IN file DO
        lineNo <- lineNo + 1
        IF line is not blank THEN YIELD (lineNo, line without newline)
    CLOSE file

ALGORITHM ParseRegistration(line)                              // fest/validators.py
    fields <- split line at commas, strip each field
    IF number of fields <> 5 THEN RAISE DamagedLine
    (reg, name, dept, email, eventsText) <- fields
    IF reg is not 9 digits THEN RAISE DamagedLine
    IF name is empty OR dept is empty THEN RAISE DamagedLine
    events <- non-empty, stripped, capitalised pieces of eventsText split at ";"
    IF events is empty THEN RAISE DamagedLine
    IF NOT ValidEmail(email) THEN RAISE InvalidEmail
    RETURN Registration(reg, name, upper-case dept, lower-case email, events)

ALGORITHM Process(inputDir, outputDir)                         // fest/pipeline.py
    seen <- empty set;  accepted <- empty list;  errors <- empty list;  eventIndex <- empty dictionary
    FOR EACH dept IN [cse, it, ece, mech, civil] DO
        TRY
            FOR EACH (lineNo, text) IN ReadLines(inputDir/registrations_dept.txt) DO
                TRY
                    r <- ParseRegistration(text)
                    IF r.reg IS IN seen THEN RAISE DuplicateRegistration
                ON DuplicateRegistration / InvalidEmail / DamagedLine (reason):
                    APPEND (file, lineNo, kind, reason, text) TO errors;  CONTINUE
                ELSE
                    ADD r.reg TO seen;  APPEND r TO accepted
                    FOR EACH event IN r.events DO ADD (r.reg, r.name) TO eventIndex[event]
        ON FileNotFoundError: APPEND (file, 0, "MISSING_FILE", ...) TO errors
        ON PermissionError / UnicodeDecodeError: APPEND (file, 0, "UNREADABLE_FILE", ...) TO errors
    CREATE outputDir if needed
    WriteMaster(accepted sorted by reg);  WriteEventFiles(eventIndex);  WriteErrors(errors);  WriteSummary(counters)

ALGORITHM WriteEventFiles(folder, eventIndex)                  // fest/writers.py
    FOR EACH event, members IN eventIndex DO
        name <- event in lower case, non-letters/digits replaced by "_", plus ".txt"
        OPEN folder/name FOR writing
        FOR EACH (reg, name) IN sorted(members) DO WRITE reg + " " + name + newline"""))
    story += [P("Stage 5 - Implementation and demonstration (3 marks)", H2),
              P("Source code: Task6/fest/*.py and Task6/main.py (listed in the source-code PDF). Cases demonstrated (Task6/demo_all_cases.py and "
                "<font name='DVM'>python main.py</font>): (1) clean files, (2) a duplicate registration, (3) invalid e-mail addresses, (4) damaged lines, (5) a missing department "
                "file (registrations_civil.txt) - all in one run - and (6) an unreadable (wrong-encoding) file."),
              P("<b>Case 1 - clean files</b> (5 files, 6 registrations): no errors."), code(lines_of("Task6/output.txt", 0, 22)),
              P("<b>Cases 2 to 5 - all problems in one run.</b> Input files in Task6/input; output of <font name='DVM'>python main.py</font>: 9 accepted, 9 problems, and the program ends normally.")]
    story.append(code("accepted 9 registrations, logged 9 problems; outputs in output/\n\n--- output/errors.log\n" + read("Task6/output/errors.log")))
    story.append(code("--- output/master_list.csv\n" + read("Task6/output/master_list.csv") + "\n--- output/summary.txt\n" + read("Task6/output/summary.txt")))
    story += [code(lines_of("Task6/output.txt", 23, 48))]
    story += [P("Every requirement was met: R1 9 valid lines → 9 master rows; R2 192311002 duplicate logged; R3 four invalid addresses logged; R4 three damaged lines with file and line number; "
                "R5 event files (e.g. dance.txt above); R6 summary.txt; R7 civil file logged MISSING_FILE and the run continued; R8 every record has file, line, kind, reason and text; R9 no traceback. "
                "Note: when a file has invalid bytes, Python decodes the first block of the file at once, so such a file is logged as UNREADABLE_FILE and, for a small file, none of its lines is accepted; "
                "this is a deliberate, visible choice (the committee fixes the file) rather than a silent partial read.")]
    story += [P("Alternative concept and complexity analysis", H2),
              P("<b>Duplicate detection by searching a list of all earlier registrations.</b> Instead of <font name='DVM'>if reg in seen_set</font>, keep "
                "<font name='DVM'>seen_list</font> and test <font name='DVM'>if reg in seen_list</font> (a linear scan), appending accepted numbers. The i-th test scans up to i items, so n registrations "
                "cost 1 + 2 + … + n = n(n + 1)/2 comparisons: <b>O(n²)</b> time. The set needs one hash lookup per registration: <b>O(n)</b> time on average. Space: both store the accepted register "
                "numbers, <b>O(n)</b>; the set has a larger constant (hash table) than the list, which is the price for speed. Measured (results identical, asserted):")]
    rows = re.findall(r"\s*(\d+)\s+([\d.]+)s\s+([\d.]+)s\s+(\d+)x", out)
    story += table([["Registrations n", "Set", "List search", "Ratio"]] + [[f"{int(a):,}", f"{b} s", f"{c} s", f"{d}×"] for a, b, c, d in rows], [4 * cm, 3.5 * cm, 3.5 * cm, 3 * cm])
    story += img("task6_timing.png", 10, "Fig. 5 - The list search grows quadratically, the set linearly.")
    story += [P(f"The ratio rises with n (about {rows[0][3]}× at {int(rows[0][0]):,} and {rows[-1][3]}× at {int(rows[-1][0]):,}), as O(n²) versus O(n) predicts. For a college fest of a few thousand registrations both are acceptable, but "
                "the set costs no more to write and keeps the program fast if the data grows to the whole university.")]


# ======================================================================= PDFs
def build(path, story, title):
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=1.6 * cm, rightMargin=1.6 * cm, topMargin=1.5 * cm, bottomMargin=1.7 * cm, title=title, author=args.name)
    doc.build(story, onFirstPage=page_number, onLaterPages=page_number)


def build_report(path):
    story = []
    cover(story)
    for fn in (task1, task2, task3, task4, task5, task6):
        fn(story)
    build(path, story, "Python Programming - Assignment 4 (CO4) - Report")


def build_code(path):
    story = []
    cover(story, second=True)
    story += [P("How to run", H1),
              P("Repository folders: Task1 … Task6, one folder per task. From the repository root (Python " + PYVER + ", standard library only for the programs):"),
              code("python run_all.py                       # runs every program and saves the outputs\n"
                   "python build_report.py --github <URL>   # builds the two PDFs\n\n# or one task at a time, for example\n"
                   "cd Task3\npython complete_the_code.py\npython processor.py\n\n# Task 6\ncd Task6\npython main.py\npython demo_all_cases.py"),
              PageBreak()]
    sections = [
        ("Task 1 - source code, sample input file and output", ["Task1/mess_bad.py", "Task1/mess_fixed.py", "Task1/mess_oct.txt", "Task1/output.txt"]),
        ("Task 2 - source code, sample input files, output files and damaged-line log",
         ["Task2/attendance_monthly.py"] + [f"Task2/sample_data/attendance_2026-10-0{d}.txt" for d in range(1, 9)]
         + ["Task2/out/attendance_summary.csv", "Task2/out/below_75.txt", "Task2/out/damaged_lines.log", "Task2/output.txt"]),
        ("Task 3 - source code and outputs", ["Task3/complete_the_code.py", "Task3/complete_output.txt", "Task3/processor.py", "Task3/output.txt",
                                              "Task3/lbyl_vs_eafp.py", "Task3/lbyl_output.txt"]),
        ("Task 4 - source code and outputs", ["Task4/library_bad.py", "Task4/library_fixed.py", "Task4/test_library.py", "Task4/output.txt"]),
        ("Task 5 - the four organisations (after the change) and outputs",
         ["Task5/build_organisations.py", "Task5/organisations_after/a_one_script/attendance.py",
          "Task5/organisations_after/b_one_module/attendance_lib.py", "Task5/organisations_after/b_one_module/main.py",
          "Task5/organisations_after/c_three_modules/reader.py", "Task5/organisations_after/c_three_modules/stats.py",
          "Task5/organisations_after/c_three_modules/report.py", "Task5/organisations_after/c_three_modules/main.py",
          "Task5/organisations_after/d_package/attendance/__init__.py", "Task5/organisations_after/d_package/attendance/reader.py",
          "Task5/organisations_after/d_package/attendance/stats.py", "Task5/organisations_after/d_package/attendance/report.py",
          "Task5/organisations_after/d_package/main.py", "Task5/import_styles_demo.py", "Task5/output.txt", "Task5/import_output.txt",
          "Task5/out/after/d_package/absent_3_days.txt"]),
        ("Task 6 - package fest/, sample input files, output files and error log",
         ["Task6/main.py", "Task6/fest/__init__.py", "Task6/fest/errors.py", "Task6/fest/readers.py", "Task6/fest/validators.py",
          "Task6/fest/writers.py", "Task6/fest/pipeline.py", "Task6/demo_all_cases.py"]
         + [f"Task6/input/registrations_{d}.txt" for d in ("cse", "it", "ece", "mech")]
         + ["Task6/output/master_list.csv", "Task6/output/summary.txt", "Task6/output/errors.log", "Task6/output/events/dance.txt",
            "Task6/output/events/quiz.txt", "Task6/output.txt"])]
    for heading, files in sections:
        story += [P(heading, H1)]
        for rel in files:
            story += [P(esc(rel), H2), code(read(rel), 120)]
        story.append(PageBreak())
    build(path, story[:-1], "Python Programming - Assignment 4 (CO4) - Source code")


if __name__ == "__main__":
    make_figures.make_all()
    out = os.path.join(ROOT, "submission")
    os.makedirs(out, exist_ok=True)
    build_report(os.path.join(out, "File1_Report_Tasks1-6.pdf"))
    build_code(os.path.join(out, "File2_Source_Code_Inputs_Outputs.pdf"))
    for f in sorted(os.listdir(out)):
        print(f, round(os.path.getsize(os.path.join(out, f)) / 1024 / 1024, 2), "MB")
