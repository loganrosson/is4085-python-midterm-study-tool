# IS 4085 – Python Midterm Study Tool

An interactive study app for an intro Python course midterm, built as a single self-contained file (Python 3.8+, no installs).

## Features
- Two practice exams, bonus questions, and a mixed "Super Test"
- When you miss a question: the actual program output, why the right answer is right, why yours isn't, and a step-by-step narration of the code
- **Dev Mode (F2):** a line-by-line code stepper showing parameters, call stack, expression evaluation, variable history, and an optional "predict first" mode
- **Cheat sheets (F3):** type conversions, truthiness, `%` and `//`, formatting, strings & lists — all computed live, with a "Try it" box
- Skill tagging, weak-spot tracking, one-click drills, syntax highlighting, light/dark mode
- Playground for stepping through your own code
- GUI (Tkinter) or `--cli` terminal mode

## Run it
```bash
python IS4085_Python_Midterm_Study_Tool.py        # GUI
python IS4085_Python_Midterm_Study_Tool.py --cli  # terminal
```
Runs entirely locally — no network access, no files written.
