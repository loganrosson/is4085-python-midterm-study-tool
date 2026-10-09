#!/usr/bin/env python3
"""
IS 4085 - Python Midterm Study Tool
===================================
A single self-contained file. No installs needed (Python 3.8+).

    python IS_4085_Python_Midterm_Study_Tool.py          opens the window (GUI)
    python IS_4085_Python_Midterm_Study_Tool.py --cli    terminal version instead

What it does
  * Practice Exam 1 (27 q), Practice Exam 2 (35 q), 25 bonus questions, a mixed Super Test
  * WHEN YOU MISS A QUESTION it shows: what the code really printed, why the right answer is right,
    why YOUR answer isn't (hand-written notes for the tricky ones, otherwise worked out from the real run),
    the program narrated step by step in words, and why each other option is wrong
  * DEV MODE on any question (press F2): steps through the code line by line - which value goes into
    which parameter (and whether it is the same object as the caller's variable), the call stack,
    how every expression was worked out (with plain-English notes on and / or / not truthiness,
    % remainders, // floor division, int / float / str conversions), what changed, the history of every
    variable, and an optional "predict first" mode that hides each answer until you click Reveal
  * CHEAT SHEETS (press F3): int / float / str conversions, True / False logic (falsy values, zero,
    and / or / not), % and //, printing & formatting, strings & lists. Every result is computed live by
    Python, and a "Try it" box evaluates any expression you type
  * Concept tracking: each question is tagged with the skills it practices; practice one skill at a time,
    and the results screen shows your weak spots with a one-click drill
  * Colored code (like the practice exam) and a light / dark mode button
  * Playground: paste your own Python and step through it

Safety notes
  * Everything runs locally. The tool makes no network connections and writes no files.
  * Code it runs (the built-in questions, code you paste into the Playground, or an expression typed in
    the Try-it box) is limited: a 5-second / 2000-step cap, no open(), and imports restricted to a short
    list of harmless modules (random, math, string, datetime, collections, re, json...).
    This is a safety net, not a security sandbox, so only paste code you trust.
"""


import ast
import builtins
import contextlib
import inspect
import io
import keyword
import os
import random
import re
import sys
import textwrap
import time
import tokenize
import types
import warnings

try:  # keep Windows terminals from crashing on symbols / emoji
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


# ===========================================================================
# Question bank
# ===========================================================================
def code(s):
    return textwrap.dedent(s).strip("\n")


def Q(source, num, prompt, choices, answer, why, src=None, inputs=None, demo=False):
    """
    source  : "Exam 1", "Exam 2" or "Bonus"
    src     : the code for the question (None = concept question)
    inputs  : values the "user types" for input() calls
    demo    : True if the code is a demo I added (not on the quiz) - it is
              hidden while you answer and shown afterwards / in dev mode
    answer  : correct choice text (or list of texts if several are accepted)
    """
    return {"source": source, "num": num, "prompt": prompt, "choices": choices,
            "answer": answer if isinstance(answer, list) else [answer],
            "why": why, "code": src, "inputs": inputs or [], "demo": demo}


# ---------------------------------------------------------------------------
# PRACTICE EXAM 1
# ---------------------------------------------------------------------------
QUIZ1 = [
    Q("Exam 1", 1, "What will the following code print?",
      ["Name: {name}", "Error", '"Name: Bob"', "Name: name", "Name: Bob", "print(name)"],
      "Name: Bob",
      "The f in front of the string turns {name} into the variable's value. "
      "Quotes are never printed - they only mark where the string starts/ends.",
      code(r'''
        name = "Bob"
        print(f"Name: {name}")
      ''')),

    Q("Exam 1", 2, "Which line correctly uses a single-line comment?",
      ["// # comment", "-- This is a comment", "/* This is a comment */",
       '""" This is a comment """', "# This is a comment", "// Comment"],
      "# This is a comment",
      "Python comments start with #. // and /* */ are JavaScript/C, -- is SQL. "
      "Triple quotes create a string (a docstring), not a real comment.",
      code(r'''
        # This is a comment - Python skips this whole line
        x = 5  # a comment can also go at the end of a line
        print(x)
      '''), demo=True),

    Q("Exam 1", 3, "What is the output of this code?",
      ["Value = 100", "Value = value", '"Value = 100"', "100", "value", "Value = {value}"],
      "Value = 100",
      "The f-string swaps {value} for 100. Everything else in the string prints as-is.",
      code(r'''
        value = 100
        print(f"Value = {value}")
      ''')),

    Q("Exam 1", 4, "What does the following code do?",
      ["Raises an error", "Creates a comment block", "Does nothing", "Calls a function",
       "Executes the print command", "Prints Hello"],
      "Does nothing",
      "The line starts with #, so the whole thing is a comment. Python never runs it "
      "(in dev mode you'll see there are zero steps).",
      code(r'''
        # print("Hello")
      ''')),

    Q("Exam 1", 5, "Which line uses an f-string to combine a string and number?",
      ['print("Score: 90")', "print(f'Score:' {90})", "print(Score: 90)",
       'print("Score: " + 90)', 'print(f"Score: {90}")', "print('Score: {90}')"],
      'print(f"Score: {90}")',
      "You need BOTH the f prefix and the {} INSIDE the quotes. "
      '"Score: " + 90 crashes: you can\'t + a str and an int (the demo shows the error).',
      code(r'''
        print(f"Score: {90}")
        print("Score: " + 90)
      '''), demo=True),

    Q("Exam 1", 6, "What is the output of this code?",
      ["Cost: $\n25", "Error", "Cost: /n$25", "Cost: $25", "Cost:\n$25", "Cost:\\n$25"],
      "Cost:\n$25",
      r"\n inside a string is the NEWLINE character, so 'Cost:' and '$25' land on "
      "separate lines. (/n is just two normal characters.)",
      code(r'''
        print("Cost:\n$25")
      ''')),

    Q("Exam 1", 7, "What will this code output if the user enters 7.5?",
      ["0", "number", "Error", "7.5", "float", "7"],
      "7.5",
      "input() ALWAYS returns a string. Here it's never converted, so printing it "
      "just shows 7.5. (Dev mode shows number = '7.5' with type str.)",
      code(r'''
        number = input("Enter a number: ")
        print(number)
      '''), inputs=["7.5"]),

    Q("Exam 1", 8, "What is the output of this code?",
      ["11", "8", "10", "13", "16", "Error"],
      "11",
      "Order of operations (PEMDAS): 3 * 2 = 6 happens first, then 5 + 6 = 11.",
      code(r'''
        print(f"{5 + 3 * 2}")
      ''')),

    Q("Exam 1", 9, "Which code correctly displays this output: Amount: $75.00 ?",
      ['print(f"Amount: ${75.0:.2f}")', 'print("Amount: $" + str(75.00))',
       'print("Amount: ${:.2f}".format(75.0))', "All of the above",
       'print(f"Amount: $%.2f" % 75.0)', "None of the above"],
      "All of the above",
      "Canvas grades 'All of the above' correct: :.2f in an f-string, .format() and "
      "% formatting all give $75.00. HEADS UP: run the demo - str(75.00) actually "
      "gives '75.0' because str() drops trailing zeros. So the quiz key is a little "
      "off on that one option; know both facts for the exam.",
      code(r'''
        print(f"Amount: ${75.0:.2f}")
        print("Amount: $" + str(75.00))
        print("Amount: ${:.2f}".format(75.0))
        print(f"Amount: $%.2f" % 75.0)
      '''), demo=True),

    Q("Exam 1", 10, "What does the following code output?",
      ["False", "TypeError", '"3.14"', "KeywordError", "True", "3.14"],
      "False",
      "3.14 is a float, not an int, so isinstance(3.14, int) is False and the "
      "function returns False.",
      code(r'''
        def intChecker(num):
            if isinstance(num, int):
                return True
            else:
                return False

        print(intChecker(3.14))
      ''')),

    Q("Exam 1", 11, "What will the following code print if the user inputs the number 0?",
      ["Zero", "Prints value", "Error due to int conversion", "None", "Non-zero",
       "Always prints Non-zero"],
      "Zero",
      "int('0') converts fine. 0 is 'falsy' (treated as False), so `if value:` "
      "fails and the else runs. Falsy values: 0, 0.0, '', [], {}, None, False.",
      code(r'''
        value = int(input("Enter a number: "))
        if value:
            print("Non-zero")
        else:
            print("Zero")
      '''), inputs=["0"]),

    Q("Exam 1", 12, "Which statement is true about the code below?",
      ["`None` is treated as True", "Skips comparison", "Raises an exception",
       "`None` cannot be compared", 'Prints "Status available"', 'Always prints "No status"'],
      'Always prints "No status"',
      "status is set to None right before the check, so `status is None` is always True.",
      code(r'''
        status = None
        if status is None:
            print("No status")
        else:
            print("Status available")
      ''')),

    Q("Exam 1", 13, "What is the result of this code if the input is `false`?",
      ["Always prints Enabled", "Input ignored", "Case-sensitive error", "Error",
       "Enabled", "Disabled"],
      "Disabled",
      "'false'.lower() is 'false', which is not equal to 'true', so the else branch runs.",
      code(r'''
        flag = input("Enter a flag: ")
        if flag.lower() == "true":
            print("Enabled")
        else:
            print("Disabled")
      '''), inputs=["false"]),

    Q("Exam 1", 14, "What is the effect of the `pass` statement here?",
      ['Prints "Positive number" for all inputs', "Only prints on 0",
       "Does nothing for negative numbers", 'Always prints "Positive number"',
       "Skips the else block", "Always prints an error"],
      "Does nothing for negative numbers",
      "pass is a do-nothing placeholder. Negative -> nothing prints. 0 or positive "
      "-> 'Positive number'. In dev mode, try typing -5, then 0, then 8.",
      code(r'''
        x = int(input("Enter number: "))
        if x < 0:
            pass
        else:
            print("Positive number")
      '''), inputs=["-5"]),

    Q("Exam 1", 15, "What will this code do if the user inputs `-1.5`?",
      ["Non-negative", "0", "None is printed", "Negative", "Error due to float", "Syntax Error"],
      "Negative",
      "float('-1.5') is valid. -1.5 >= 0 is False, so the else prints 'Negative'.",
      code(r'''
        num = float(input("Enter a float: "))
        if num >= 0:
            print("Non-negative")
        else:
            print("Negative")
      '''), inputs=["-1.5"]),

    Q("Exam 1", 16, "What is printed by this code?",
      ["green", "Error", "yellow", "Missing color", "blue", "red"],
      "Missing color",
      "'yellow' is not in the list, so `not in` is True and the print runs.",
      code(r'''
        colors = ["red", "blue", "green"]
        if "yellow" not in colors:
            print("Missing color")
      ''')),

    Q("Exam 1", 17, "What does the following code output?",
      ["a", "a b c", "c", "b", "Nothing", "a b"],
      "a",
      "Prints 'a'. On 'b', break exits the loop BEFORE the print, so 'b' and 'c' never print.",
      code(r'''
        letters = ["a", "b", "c"]
        for l in letters:
            if l == "b":
                break
            print(l)
      ''')),

    Q("Exam 1", 18, "What is the output of this code?",
      ["Valid", "20", "Error", "Sam", "age", "name"],
      "Valid",
      "`in` on a dictionary checks the KEYS. 'name' is a key, and 20 > 18, so both sides are True.",
      code(r'''
        person = {"name": "Sam", "age": 20}
        if "name" in person and person["age"] > 18:
            print("Valid")
      ''')),

    Q("Exam 1", 19, "What will this code output?",
      ["2", "0", "2 4", "1 2 3 4", "1 3", "Error"],
      "2 4",
      "n % 2 is the remainder after dividing by 2. It's 0 for even numbers, so 2 and 4 print.",
      code(r'''
        nums = [1, 2, 3, 4]
        for n in nums:
            if n % 2 == 0:
                print(n)
      ''')),

    Q("Exam 1", 20, "What is the result of this code?",
      ["France", "None", "city", "Paris", "country", "Error"],
      "France",
      "'country' isn't a key yet, so it gets added with the value 'France', then printed.",
      code(r'''
        info = {"city": "Paris"}
        if "country" not in info:
            info["country"] = "France"
        print(info["country"])
      ''')),

    Q("Exam 1", 21, "What is the output? (** is the exponent operator: 2 ** 3 == 8)",
      ["['a1', 'b4', 'c9']", "[1, 4, 9]", "[('a', 1), ('b', 4), ('c', 9)]",
       "[('a', 1), ('b', 2), ('c', 3)]", "[('a', 2), ('b', 4), ('c', 6)]",
       "[('a', 'a'), ('b', 'b'), ('c', 'c')]"],
      "[('a', 1), ('b', 4), ('c', 9)]",
      "Looping over a dict gives you its KEYS. Each loop appends the tuple "
      "(key, value squared).",
      code(r'''
        data = {'a': 1, 'b': 2, 'c': 3}
        result = []
        for key in data:
            result.append((key, data[key] ** 2))
        print(result)
      ''')),

    Q("Exam 1", 22, "What will be the output of this code snippet?",
      ["Student: Bob | Score: 95.68", "Student: Bob | Score: 00095.68",
       "Student: Bob | Score: 095.86", "Student: Bob | Score: 095.68",
       "Student: Bob | Score: 95.678", "Student: Bob | Score: 095.6"],
      "Student: Bob | Score: 095.68",
      "%10s right-aligns 'Bob' in a 10-character space (Canvas hides those spaces). "
      "%06.2f means 2 decimal places (95.68) in a total width of 6, padded with "
      "zeros -> 095.68.",
      code(r'''
        name = "Bob"
        score = 95.678
        print("Student: %10s | Score: %06.2f" % (name, score))
      ''')),

    Q("Exam 1", 23, "What happens when you run this code?",
      ["Hex: 255, Integer: ff, Float: 3.14", "Hex: FF, Integer: 255, Float: 3.140000",
       "Hex: 255, Integer: 255, Float: 3.14", "Hex: ff, Integer: 255, Float: 3.140000",
       "Error due to mixing types", "Hex: 0xff, Integer: 255, Float: 3.140000"],
      "Hex: ff, Integer: 255, Float: 3.140000",
      "%x = lowercase hex with no 0x prefix (255 -> ff). %d = integer. "
      "%f = float with 6 decimal places by default.",
      code(r'''
        print("Hex: %x, Integer: %d, Float: %f" % (255, 255, 3.14))
      ''')),

    Q("Exam 1", 24, "What will the following code output?",
      ["Error", "12", "60", "30", "40", "24"],
      "40",
      "a=4, b keeps its default of 2, and c is overridden to 5. 4 * 2 * 5 = 40.",
      code(r'''
        def multiply(a, b=2, c=3):
            return a * b * c

        print(multiply(4, c=5))
      ''')),

    Q("Exam 1", 25, "What does this code print?",
      ["15", "Error", "(5, 10)", "(10,)", "10", "5"],
      "10",
      "*args packs every argument into a tuple: (5, 10, 15). Index 1 is the SECOND item -> 10.",
      code(r'''
        def f(*args):
            return args[1]

        print(f(5, 10, 15))
      ''')),

    Q("Exam 1", 26, "What is the effect of this import statement?\n    from random import randint as ri",
      ["Causes a syntax error", "Imports a module called randint",
       "Imports the randint function and renames it ri", "Imports randint and ri functions",
       "Creates an alias random as ri", "Imports the entire random module as ri"],
      "Imports the randint function and renames it ri",
      "`from MODULE import NAME as ALIAS` brings in ONE function under a new name. "
      "Notice in dev mode: ri exists, but `random` does not.",
      code(r'''
        from random import randint as ri
        roll = ri(1, 6)
        print(roll)
      '''), demo=True),

    Q("Exam 1", 27, "Which import will raise an error if the module nonexistent does not exist?",
      ["All of the above.", "from nonexistent import def(x)", "from nonexistent import *",
       "import nonexistent as None", "import nonexistent", "import nonexistent as ne"],
      "All of the above.",
      "They all fail. The normal-looking ones raise ModuleNotFoundError. "
      "'def(x)' and 'as None' are SyntaxErrors, because def and None are reserved words.",
      code(r'''
        tests = ["from nonexistent import def(x)",
                 "from nonexistent import *",
                 "import nonexistent as None",
                 "import nonexistent",
                 "import nonexistent as ne"]
        for stmt in tests:
            try:
                exec(stmt)
            except Exception as e:
                print(type(e).__name__, "<-", stmt)
      '''), demo=True),
]

# ---------------------------------------------------------------------------
# PRACTICE EXAM 2
# ---------------------------------------------------------------------------
QUIZ2 = [
    Q("Exam 2", 1, "What is printed when we execute the following code?",
      ["5 3 x+y=8", "5 5 x+y=10", "Error", "2 5 x+y=7", "3 3 x+y=6", "2 3 x+y=5"],
      "5 5 x+y=10",
      "x, y = 2, 3 sets x=2 and y=3. In x = y = x + y the right side is computed ONCE "
      "(2+3 = 5), then that 5 goes into BOTH x and y. f\"{x+y=}\" is the "
      "'debug' f-string: it prints the expression text, an =, then the value -> x+y=10.",
      code(r'''
        x, y = 2, 3
        x = y = x + y
        print(x, y, f"{x+y=}")
      ''')),

    Q("Exam 2", 2, "Choose the only line that does not raise a syntax/name error.",
      ['print("x =", x)', 'x = 1; print(f"{x}")', 'print(f"{val=}")', 'print("done");',
       "# just a comment", "3x = 4"],
      ['x = 1; print(f"{x}")', 'print("done");', "# just a comment"],
      "The intended answer is x = 1; print(f\"{x}\"), because x gets defined before "
      "it's used. print(\"x =\", x) and f\"{val=}\" are NameErrors (the variable doesn't "
      "exist), and 3x = 4 is a SyntaxError (names can't start with a digit). The demo "
      "shows that 'print(\"done\");' and the comment ALSO don't raise errors (a "
      "trailing ; is legal). So this tool accepts all three, but expect the first on the exam.",
      code(r'''
        lines = ['print("x =", x)', 'x = 1; print(f"{x}")', 'print(f"{val=}")',
                 'print("done");', '# just a comment', '3x = 4']
        for line in lines:
            try:
                exec(line, {})
                print("   OK ->", line)
            except Exception as e:
                print("  ", type(e).__name__, "->", line)
      '''), demo=True),

    Q("Exam 2", 3, "User types 8. Output?",
      ["64", "16", "None", "88", '"16"', "Error"],
      "88",
      "input() returns the STRING '8'. A string * 2 repeats it, so the result is '88'. "
      "To get 16 you'd need int(val) * 2.",
      code(r'''
        val = input()
        print(val*2)
      '''), inputs=["8"]),

    Q("Exam 2", 4, "Output?",
      ['Hello\nWorld"!', "Hello World!", 'Hello\\nWorld"!', "None", "Error", 'Hello "World!'],
      'Hello\nWorld"!',
      r'\n is a newline, so World moves to the next line. \" is an escaped quote: a real " '
      "character inside the string that doesn't end it.",
      code(r'''
        print("Hello\nWorld\"!")
      ''')),

    Q("Exam 2", 5, "User types 12.0. What prints?",
      ["13.0", "Error", "12.1", "121", "13", "12"],
      "13",
      "'12.0' -> float -> 12.0 -> int(12.0) -> 12 -> +1 -> 13 (an int, so no .0). "
      "Note: int('12.0') straight from the string WOULD be a ValueError. Going through "
      "float first avoids that.",
      code(r'''
        n = input()
        n = float(n)
        print(int(n)+1)
      '''), inputs=["12.0"]),

    Q("Exam 2", 6, "Exact layout printed by:",
      ['Line1\\n\n\nLine2"OK"', 'Line1\n\\nLine2"OK"', 'Line1\\nLine2"OK"', "Error",
       'Line1\\n\nLine2"OK"', "Line1\\nLine2OK"],
      'Line1\\n\nLine2"OK"',
      r'"\\" is an escaped BACKSLASH, so "Line1\\n" prints the characters Line1\n '
      r"(a backslash and an n, NOT a newline). print() then adds its own newline, so "
      r'Line2"OK" goes on the next line. \" prints a quote.',
      code(r'''
        print("Line1\\n")
        print("Line2\"OK\"")
      ''')),

    Q("Exam 2", 7, "Output?",
      ["None", "True", "One", "Error", "Both/None", "False"],
      "One",
      "x=0 is falsy and y=5 is truthy. (x or y) -> 5 (truthy). (x and y) -> 0, so "
      "not 0 -> True. Truthy and True -> the if runs -> 'One'. The elif is never checked.",
      code(r'''
        x, y = 0, 5
        if (x or y) and not (x and y):
            print("One")
        elif x == 0:
            print("Both/None")
      ''')),

    Q("Exam 2", 8, "Which branch is executed?",
      ["Nothing", "90", "Hit", "Miss", "0", "Error"],
      "Hit",
      "n < 10 is False, but (n >= 10 and n % 5 == 0) is True and True -> True. "
      "False or True -> True -> 'Hit'.",
      code(r'''
        n = 90
        if n < 10 or (n >= 10 and n % 5 == 0):
            print("Hit")
        else:
            print("Miss")
      ''')),

    Q("Exam 2", 9, "Which expression is True?",
      ['"Bob" == "bob" or 0', "0 and 1", "(3 < 5) and (8 >= 8)", "5 > 7 or 2 > 3 and 0",
       "4 < 4 and 1", "not (6 <= 6)"],
      "(3 < 5) and (8 >= 8)",
      "3 < 5 is True and 8 >= 8 is True (>= includes equal). The others: 'Bob' != 'bob' "
      "(case matters) so it gives 0. '0 and 1' gives 0. 'and' runs before 'or', so "
      "False or (False and 0) -> False. 4 < 4 is False. 6 <= 6 is True, so not -> False.",
      code(r'''
        print("Bob" == "bob" or 0)
        print(0 and 1)
        print((3 < 5) and (8 >= 8))
        print(5 > 7 or 2 > 3 and 0)
        print(4 < 4 and 1)
        print(not (6 <= 6))
      '''), demo=True),

    Q("Exam 2", 10, "Output?",
      ["B", "Nothing", "Error", "A", "C", "A B"],
      "A",
      "12 > 0, so you go inside. 12 >= 12 is True -> 'A'. Once one branch of an "
      "if/elif runs, the rest are skipped, so 'B' never prints even though 12 > 10. "
      "The else belongs to the OUTER if.",
      code(r'''
        x = 12
        if x > 0:
            if x >= 12:
                print('A')
            elif x > 10:
                print('B')
        else:
            print('C')
      ''')),

    Q("Exam 2", 11, "Output?",
      ["Nothing", "T", "0", "False", "True", "Error"],
      "Nothing",
      "flag is True, so `pass` runs, and it does nothing. The else (with the 'T') "
      "never runs.",
      code(r'''
        flag = True
        if flag:
            pass
        else:
            if not flag:
                print('T')
      ''')),

    Q("Exam 2", 12, "Output?",
      ["Error", "Has", "Empty", "Nothing", "False", "None"],
      "Empty",
      "x != None -> False. not x -> not None -> True (None is falsy). False or True -> True -> 'Empty'.",
      code(r'''
        x = None
        if x != None or not x:
            print("Empty")
        else:
            print("Has")
      ''')),

    Q("Exam 2", 13, "Output?",
      ["[1, 2, 3]", "[1, 9, 3]", "[[1,9,3]]", "Error", "None", "[9, 2, 3]"],
      "[1, 9, 3]",
      "b = [a, a] holds two REFERENCES to the SAME list a, not copies. b[0][1] = 9 "
      "changes a, so b[1] (also a) shows [1, 9, 3]. In dev mode, watch `a` change "
      "even though the line only mentions b!",
      code(r'''
        a = [1, 2, 3]
        b = [a, a]
        b[0][1] = 9
        print(b[1])
      ''')),

    Q("Exam 2", 14, "Output?",
      ["[10, 20, 30]", "[10, 30, 30, 30]", "[10, -10, 30, -10]", "[10, 10, 30, 10]",
       "Error", "[10, 20, 30, 10]"],
      "[10, 10, 30, 10]",
      "nums[1] = 30 - 20 = 10, giving [10, 10, 30]. Then append(nums[1]) adds 10 -> [10, 10, 30, 10].",
      code(r'''
        nums = [10, 20, 30]
        nums[1] = nums[2] - nums[1]
        nums.append(nums[1])
        print(nums)
      ''')),

    Q("Exam 2", 15, "Output?",
      ["3 4", "Error", "13", "34", "3  4", "1 3"],
      ["3 4", "3  4"],
      "del data[1] removes the value 1 -> [0, 2, 3]. data[-1] is the last item, 3. "
      "insert(1, 3) puts 3 at index 1 -> [0, 3, 2, 3]. data[1] = 3, len = 4. "
      "(Canvas lists '3 4' twice.)",
      code(r'''
        data = [0, 1, 2, 3]
        del data[1]
        data.insert(1, data[-1])
        print(data[1], len(data))
      ''')),

    Q("Exam 2", 16, "Which of the following about Python dictionaries is true?",
      ["Keys must always be integers", "Keys can be lists", "Keys must be unique",
       "Duplicate keys are allowed", "Values must be unique"],
      "Keys must be unique",
      "Each key appears once. Assigning to an existing key REPLACES its value. "
      "Keys can be str/int/tuple (unchangeable types), but not lists. Values can repeat.",
      code(r'''
        d = {"a": 1, "a": 2}
        print(d)
        d[(1, 2)] = "tuple key works"
        print(d)
        try:
            d[[1, 2]] = "list key?"
        except TypeError as e:
            print("TypeError:", e)
      '''), demo=True),

    Q("Exam 2", 17, "Output?",
      ["False 2", "True 2", "False 5", "False 3", "True 5", "True 3"],
      "False 5",
      "m starts as {'x':1}. Add y=2, delete x -> {'y': 2}. Then y = 2 + 3 = 5. "
      "'x' in m -> False.",
      code(r'''
        m = {"x":1}
        m["y"] = 2
        del m["x"]
        m["y"] = m["y"] + 3
        print("x" in m, m["y"])
      ''')),

    Q("Exam 2", 18, "Output?",
      ["{'a':3, 'b':3}", "{'a':1, 'b':3}", "Error", "{'a':1, 'b':1}", "{'a':3}", "{'a':2, 'b':3}"],
      "{'a':3, 'b':3}",
      "b = a + 2 = 3. Then a = b = 3. Both are 3.",
      code(r'''
        d = {"a":1}
        d["b"] = d["a"] + 2
        d["a"] = d["b"]
        print(d)
      ''')),

    Q("Exam 2", 19, "Which statement is true about range(5)?",
      ["Produces 6 values", "Produces [1,2,3,4,5]", "Always returns a list",
       "Produces [0,1,2,3,4]", "Cannot be iterated", "Includes both start and end"],
      "Produces [0,1,2,3,4]",
      "range starts at 0 by default and STOPS BEFORE the end number. It's a range "
      "object (not a list), but you can loop over it or convert it with list().",
      code(r'''
        r = range(5)
        print(r, list(r), len(r))
        print(list(range(2, 10, 3)))
      '''), demo=True),

    Q("Exam 2", 20, "Which statement about break is correct?",
      ["Ends all loops at once", "Execution jumps to the last line of the program.",
       "The outer loop restarts from 0.", "Both loops continue normally.",
       "Ends only the innermost loop", "The break is ignored in nested loops."],
      "Ends only the innermost loop",
      "break exits ONLY the loop it's directly inside. The outer loop keeps going "
      "with its next value.",
      code(r'''
        for i in range(3):
            for j in range(3):
                if j == 1:
                    break
                print("i =", i, "j =", j)
      '''), demo=True),

    Q("Exam 2", 21, "Output?",
      ["1\n3", "Nothing", "Error", "1 3", "1 2 3", "2"],
      "1\n3",
      "range(1,4) is 1, 2, 3. For 2 (even), continue skips the append. So out = [1, 3], "
      "and each print puts its number on its own line.",
      code(r'''
        out = []
        for i in range(1,4):
            if i % 2 == 0:
                continue
            out.append(i)
        for v in out:
            print(v)
      ''')),

    Q("Exam 2", 22, "If a function has no return statement:",
      ["It returns an empty string.", "It raises an error.", "It stops program execution.",
       "It returns None.", "It loops infinitely.", "It returns 0."],
      "It returns None.",
      "Every function returns SOMETHING. With no return statement it returns None.",
      code(r'''
        def say_hi():
            print("hi")

        result = say_hi()
        print(result)
      '''), demo=True),

    Q("Exam 2", 23, "Which is correct about function definitions?",
      ["Functions must have parameters.", "Functions must be defined before use.",
       "Functions cannot call other functions.", "Function names must include parentheses.",
       "Function names must be uppercase.", "Functions cannot return values."],
      "Functions must be defined before use.",
      "Python runs top to bottom. A def line must run before you can call the "
      "function. The demo calls it too early and gets a NameError.",
      code(r'''
        try:
            greet()
        except NameError as e:
            print("NameError:", e)

        def greet():
            print("hello!")

        greet()
      '''), demo=True),

    Q("Exam 2", 24, "Output?",
      ["Hi!\nHi", "Error", "Hi!\nHi!", "!Hi\nHi", "None", "Hi\nHi!"],
      "Hi!\nHi",
      "Inside shout(), text starts out pointing at the same 'Hi'. text = text + '!' "
      "makes a NEW string and only changes the LOCAL name text. msg outside is "
      "untouched (strings can't be changed in place). So it prints Hi! then Hi.",
      code(r'''
        msg = "Hi"
        def shout(text):
            text = text + "!"
            print(text)
        shout(msg)
        print(msg)
      ''')),

    Q("Exam 2", 25, "Output?",
      ["Error", "False", "Hello\nTrue", "True", "Nothing", "Hello\nFalse"],
      "Hello\nTrue",
      "Calling hello() prints Hello. It has no return statement, so it returns None, "
      "and x = None. x == None -> True.",
      code(r'''
        def hello():
            print("Hello")
        x = hello()
        print(x == None)
      ''')),

    Q("Exam 2", 26, "%pip install emoji (in Colab) does what?",
      ["Installs the emoji package.", "Removes the emoji package.", "Runs a Python print command.",
       "Updates Python interpreter.", "Converts code to emojis.", "Is invalid Python syntax."],
      "Installs the emoji package.",
      "In Colab/Jupyter, a line starting with % is a 'magic' command. %pip install X "
      "installs package X so you can import it. In a terminal you'd run: pip install emoji",
      code(r'''
        # %pip install emoji   <- only works in Colab/Jupyter
        try:
            import emoji
            print("emoji IS installed on this computer")
        except ImportError:
            print("emoji is NOT installed here - %pip install emoji would fix that")
      '''), demo=True),

    Q("Exam 2", 27, "Output?",
      ["Random 4-6", "None", "5", "0", "1", "Error"],
      "5",
      "randint(a, b) includes BOTH ends. randint(5, 5) can only ever give 5. "
      "`import random as R` loads the whole module under the short name R.",
      code(r'''
        import random as R
        lo = hi = 5
        print(R.randint(lo, hi))
      ''')),

    Q("Exam 2", 28, "Output?",
      [":fire:", "Error", "\U0001F525", "Nothing", "fire", '":fire:"'],
      "\U0001F525",
      "emojize() turns emoji codes like :fire: into the real emoji character.",
      code(r'''
        from emoji import emojize
        print(emojize(":fire:"))
      ''')),

    Q("Exam 2", 29, "Which is true about string slicing s[1:4]?",
      ["Always returns an empty string.", "Always returns 4 characters.",
       "Includes characters at positions 1,2,3.", "Excludes index 1.",
       "Includes positions 1 through 4.", "Raises error if string is shorter."],
      "Includes characters at positions 1,2,3.",
      "In a slice, the START is included and the STOP is excluded. Slices never "
      "raise an error. If the string is short, you just get less back.",
      code(r'''
        s = "abcdef"
        print(s[1:4])
        print("hi"[1:4])
      '''), demo=True),

    Q("Exam 2", 30, 'To change "test" into "best", which approach works?',
      ["Replace using .upper().", "Change variable type.",
       'Modify string directly with word[0]="b".', "Convert to list, change, join back.",
       "Use dictionary mapping.", "Impossible."],
      "Convert to list, change, join back.",
      "Strings are IMMUTABLE (word[0] = 'b' raises TypeError). A list CAN be "
      "changed, so: list(word) -> change -> ''.join(...).",
      code(r'''
        word = "test"
        try:
            word[0] = "b"
        except TypeError as e:
            print("TypeError:", e)
        letters = list(word)
        letters[0] = "b"
        word = "".join(letters)
        print(word)
      '''), demo=True),

    Q("Exam 2", 31, "Output?",
      ["None", "h3ll0", "h3llo", "Error", "hello", "3hll0"],
      "h3ll0",
      "list('hello') -> ['h','e','l','l','o']. Index 1 becomes '3' and index 4 "
      "becomes '0'. Then join -> 'h3ll0'.",
      code(r'''
        word = "hello"
        L = list(word)
        L[1] = "3"
        L[4] = "0"
        print("".join(L))
      ''')),

    Q("Exam 2", 32, "Output?",
      ["cxyz", "Error", "bcxyz", "ABCX", "bcdx", "bcxy"],
      "bcxy",
      ".lower() gives 'abcxyz'. [1:5] takes indexes 1, 2, 3, 4 -> 'bcxy'.",
      code(r'''
        txt = "abcXYZ"
        print(txt.lower()[1:5])
      ''')),

    Q("Exam 2", 33, "Which is true about lists vs strings?",
      ["Strings are mutable, lists are immutable.", "Both disallow slicing.",
       "Both must contain numbers.", "Both are mutable.",
       "Lists are mutable, strings are immutable.", "Neither can be indexed."],
      "Lists are mutable, strings are immutable.",
      "Mutable = can be changed in place. You can do lst[0] = 'x', but s[0] = 'x' is a "
      "TypeError. Both can be indexed and sliced.",
      code(r'''
        lst = ["c", "a", "t"]
        lst[0] = "b"
        print(lst)
        s = "cat"
        print(s[0], s[1:])
        s[0] = "b"
      '''), demo=True),

    Q("Exam 2", 34, "Which formatting token is for floating-point?",
      ["%c", "%d", "%s", "%f", "%x", "None"],
      "%f",
      "%f = float, %d = integer, %s = string, %x = hex, %c = character.",
      code(r'''
        print("%f | %.2f | %d | %s | %x | %c" % (2.5, 2.5, 2.5, 2.5, 255, 65))
      '''), demo=True),

    Q("Exam 2", 35, "from random import randint as dice   means:",
      ["All random functions are renamed dice.", "Error.", "dice is a list of random numbers.",
       "dice becomes a dictionary of functions.", "The whole random module is loaded as dice.",
       "Only the function randint is imported, using alias dice."],
      "Only the function randint is imported, using alias dice.",
      "from ... import ... brings in just that one function. `as dice` gives it a new "
      "name. The name `random` itself is NOT available (the demo shows the NameError).",
      code(r'''
        from random import randint as dice
        print(dice(1, 6))
        print(random)
      '''), demo=True),
]

# ---------------------------------------------------------------------------
# BONUS QUESTIONS (written to stretch the same topics a bit further)
# ---------------------------------------------------------------------------
BONUS = [
    Q("Bonus", 1, "Output? (the | marks show exactly where spaces go)",
      ["   tea|3.50   |", "tea   |   3.50|", "tea|3.50|", "   tea|3.5    |", "tea   |3.50   |", "Error"],
      "   tea|3.50   |",
      "Format spec = [align][width][.precision][type]. :>6 right-aligns in 6 characters. "
      ":<7.2f means left-aligned, 7 wide, 2 decimals.",
      code(r'''
        item = "tea"
        price = 3.5
        print(f"{item:>6}|{price:<7.2f}|")
      ''')),

    Q("Bonus", 2, "Output?",
      ["3 2 -4", "3 2 -3", "3.4 2 -3.4", "3 2 3", "4 2 -4", "3 3 -4"],
      "3 2 -4",
      "// is FLOOR division: it rounds DOWN toward negative infinity. 17/5 = 3.4 -> 3, "
      "and -17/5 = -3.4 -> -4 (not -3!). % gives the remainder: 17 % 5 = 2. "
      "Note: -a // 5 means (-a) // 5.",
      code(r'''
        a = 17
        print(a // 5, a % 5, -a // 5)
      ''')),

    Q("Bonus", 3, "Output?",
      ["6", "7", "6.5", "3 3", "ValueError (crash)", "3.53.5"],
      "ValueError (crash)",
      "int(float('3.5')) is fine -> 3. But int('3.5') crashes: int() can't read a "
      "string that has a decimal point. Dev mode shows exactly which part fails.",
      code(r'''
        s = "3.5"
        print(int(float(s)) + int(s))
      ''')),

    Q("Bonus", 4, "Output?",
      ["hi 0 0", "True False False", "hi hi 0", "0 0 hi", "True 0 False", "hi False 0"],
      "hi 0 0",
      "and / or return one of the actual VALUES, not just True/False. "
      "`a or b` gives the first truthy value (or the last one). "
      "`a and b` gives the first falsy value (or the last one). "
      "0 or 'hi' -> 'hi'. 0 and 'hi' -> 0. 'hi' and 0 -> 0.",
      code(r'''
        a = 0
        b = "hi"
        print(a or b, a and b, b and a)
      ''')),

    Q("Bonus", 5, "Output?",
      ["True False True", "True True True", "True False False", "False False True",
       "Error", "True True False"],
      "True False True",
      "Comparisons can chain: 1 < x < 10 means (1 < x) and (x < 10) -> True. "
      "10 > x > 6 -> 5 > 6 is False. x == 5 == 5.0 -> True (int 5 equals float 5.0).",
      code(r'''
        x = 5
        print(1 < x < 10, 10 > x > 6, x == 5 == 5.0)
      ''')),

    Q("Bonus", 6, "Output?",
      ["['hell0', ' w0rld']", "['hell0', 'w0rld']", "['Hell0', ' W0rld']", "hell0, w0rld",
       "['  hell0', ' w0rld  ']", "Error"],
      "['hell0', ' w0rld']",
      "Methods chain left to right: strip() removes the outer spaces, lower() lowercases, "
      "replace('o','0') swaps EVERY o, and split(',') cuts at the comma. The space after "
      "the comma stays with ' w0rld'.",
      code(r'''
        s = "  Hello, World  "
        print(s.strip().lower().replace("o", "0").split(","))
      ''')),

    Q("Bonus", 7, "Output?",
      ["hon pto no", "hon pyh no", "hon pto on", "on pto no", "hon ptn no", "Error"],
      "hon pto no",
      "word[-3:] = the last 3 characters -> 'hon'. word[::2] = every 2nd character "
      "from the start -> p,t,o. word[::-1] reverses it -> 'nohtyp', then [:2] -> 'no'.",
      code(r'''
        word = "python"
        print(word[-3:], word[::2], word[::-1][:2])
      ''')),

    Q("Bonus", 8, "Output?",
      ["[1, 2, 3, 4] 4 4", "[1, 2, 3] 4 4", "[1, 2, 3, 4, 5] 5 5", "[1, 2, 3, 4] 4 5",
       "[1, 2, 3, 4, 5] 4 4", "[1, 2, 3] 3 3"],
      "[1, 2, 3, 4] 4 4",
      "b = a makes b ANOTHER NAME for the same list. c = a[:] makes a COPY. So "
      "b.append(4) changes a too, and c.append(5) only changes the copy. "
      "c was [1,2,3] -> [1,2,3,5], so its length is 4.",
      code(r'''
        a = [1, 2, 3]
        b = a
        c = a[:]
        b.append(4)
        c.append(5)
        print(a, len(b), len(c))
      ''')),

    Q("Bonus", 9, "Output?",
      ["None [1, 2, 3] ['a', 'b', 'c']", "[1, 2, 3] [1, 2, 3] abc",
       "[1, 2, 3] [3, 1, 2] ['a', 'b', 'c']", "None [3, 1, 2] abc",
       "None [1, 2, 3] abc", "Error"],
      "None [1, 2, 3] ['a', 'b', 'c']",
      "list.sort() sorts IN PLACE and returns None (a classic trap). sorted() returns "
      "a NEW list, and sorted() on a string gives a list of its characters.",
      code(r'''
        nums = [3, 1, 2]
        result = nums.sort()
        print(result, nums, sorted("cab"))
      ''')),

    Q("Bonus", 10, "Output?",
      ["no evens", "even found", "Nothing", "even found\nno evens", "Error", "3 5 7"],
      "no evens",
      "A for loop can have an else. The else runs only if the loop finished WITHOUT "
      "hitting break. No number is even, so break never runs, and the else prints.",
      code(r'''
        for n in [3, 5, 7]:
            if n % 2 == 0:
                print("even found")
                break
        else:
            print("no evens")
      ''')),

    Q("Bonus", 11, "Output?",
      ["5 12", "5 15", "4 12", "5 10", "3 3", "Infinite loop"],
      "5 12",
      "i is increased BEFORE the continue, so the loop always moves forward. When "
      "i == 3, continue skips the add. total = 1 + 2 + 4 + 5 = 12, and the loop "
      "stops when i is 5.",
      code(r'''
        i = 0
        total = 0
        while i < 5:
            i += 1
            if i == 3:
                continue
            total += i
        print(i, total)
      ''')),

    Q("Bonus", 12, "Output?",
      ["1 0 2 0 2 1", "0 0 1 0 1 1 2 0 2 1 2 2", "1 0 2 0", "Nothing", "0 1 0 2 1 2", "1 0 2 1"],
      "1 0 2 0 2 1",
      "break only stops the INNER loop. i=0: j=0 equals i, so break right away "
      "(nothing printed). i=1: prints 1 0, then breaks at j=1. i=2: prints 2 0 and 2 1, "
      "then breaks at j=2. end=' ' keeps everything on one line.",
      code(r'''
        for i in range(3):
            for j in range(3):
                if j == i:
                    break
                print(i, j, end=" ")
        print()
      ''')),

    Q("Bonus", 13, "Output?",
      ["0 10 None", "10 10 None", "0 10 Error", "0 None None", "None 10 None", "KeyError"],
      "0 10 None",
      "dict.get(key, default) never crashes. If the key exists you get its value "
      "(even 0), otherwise the default. With no default given, a missing key gives None.",
      code(r'''
        stock = {"apple": 3, "pear": 0}
        print(stock.get("pear", 10), stock.get("kiwi", 10), stock.get("kiwi"))
      ''')),

    Q("Bonus", 14, "Output?",
      ["{'a': 3, 'b': 1, 'c': 1}", "{'a': 1, 'b': 1, 'c': 1}", "{'a': 3}", "['a', 'b', 'c']",
       "KeyError", "{'a': 2, 'b': 0, 'c': 0}"],
      "{'a': 3, 'b': 1, 'c': 1}",
      "The classic counting pattern. counts.get(w, 0) gives the current count, or 0 "
      "if w isn't a key yet, then you add 1. Step through it in dev mode to watch the dict grow.",
      code(r'''
        words = ["a", "b", "a", "c", "a"]
        counts = {}
        for w in words:
            counts[w] = counts.get(w, 0) + 1
        print(counts)
      ''')),

    Q("Bonus", 15, "Output?",
      ["10 20", "20 20", "10 10", "20 10", "Error", "None 20"],
      "10 20",
      "Assigning x inside a function creates a NEW LOCAL x. The global x stays 10. "
      "Dev mode shows both: the local x inside change() and the global x.",
      code(r'''
        x = 10
        def change():
            x = 20
            return x
        y = change()
        print(x, y)
      ''')),

    Q("Bonus", 16, "Output? (tricky!)",
      ["[1, 2]", "[2]", "[1]", "Error", "None", "[[1], 2]"],
      "[1, 2]",
      "A default value is created ONCE, when def runs, not on every call. So both "
      "calls share the SAME list. That's why a list makes a dangerous default. "
      "The safe way is: def add(item, bucket=None): if bucket is None: bucket = []",
      code(r'''
        def add(item, bucket=[]):
            bucket.append(item)
            return bucket
        add(1)
        print(add(2))
      ''')),

    Q("Bonus", 17, "Output?",
      ["8\nNone", "8\n8", "8", "None", "Error", "4\nNone"],
      "8\nNone",
      "print() SHOWS a value. return SENDS one back. double() prints 8 but returns "
      "nothing, so result is None.",
      code(r'''
        def double(n):
            print(n * 2)
        result = double(4)
        print(result)
      ''')),

    Q("Bonus", 18, "Output?",
      ["2 ['x', 'y']", "4 ['x', 'y']", "2 [3, 4]", "4 {'x': 3, 'y': 4}",
       "2 {'x': 3, 'y': 4}", "Error"],
      "2 ['x', 'y']",
      "*args collects POSITIONAL arguments into a tuple (1, 2). **kwargs collects "
      "NAMED arguments into a dict {'x': 3, 'y': 4}. list() of a dict gives its keys.",
      code(r'''
        def info(*args, **kwargs):
            print(len(args), list(kwargs))
        info(1, 2, x=3, y=4)
      ''')),

    Q("Bonus", 19, "Output?",
      ["Hi, Ann?", "Hi, Ann!", "Ann, Hi?", "?, Ann!", "Hi, Ann", "Error"],
      "Hi, Ann?",
      "Keyword arguments let you skip ahead. greeting keeps its default 'Hi', and "
      "punct is set to '?'.",
      code(r'''
        def greet(name, greeting="Hi", punct="!"):
            return f"{greeting}, {name}{punct}"
        print(greet("Ann", punct="?"))
      ''')),

    Q("Bonus", 20, "Output?",
      ["bat", "cat", "TypeError (crash)", "b", "bcat", "Nothing"],
      "TypeError (crash)",
      "Strings are immutable, so you can't assign to s[0]. The program crashes "
      "before print runs. The fix: s = 'b' + s[1:]",
      code(r'''
        s = "cat"
        s[0] = "b"
        print(s)
      ''')),

    Q("Bonus", 21, "Output? (| marks show where spaces go)",
      ["  3.1|42  |[1, 2]", "3.1|42|[1, 2]", "3.14159|  42|[1, 2]", "  3.1|  42|[1, 2]",
       "3.1  |42  |[1, 2]", "Error"],
      "  3.1|42  |[1, 2]",
      "%5.1f = 1 decimal place, 5 wide, right-aligned -> '  3.1'. %-4d: the - means "
      "LEFT-align, 4 wide -> '42  '. %s works on anything (it uses str()).",
      code(r'''
        print("%5.1f|%-4d|%s" % (3.14159, 42, [1, 2]))
      ''')),

    Q("Bonus", 22, "Output?",
      ["1 Al 30\n2 Bo 25", "0 Al 30\n1 Bo 25", "1 Al 30\n2 Bo 25\n3 Cy None", "Error",
       "1 ('Al', 30)\n2 ('Bo', 25)", "1 Al 30\n2 Bo 25\n3 Cy"],
      "1 Al 30\n2 Bo 25",
      "zip() pairs items up and STOPS at the shortest list, so Cy is dropped. "
      "enumerate(..., start=1) adds a counter starting at 1. (n, a) unpacks each pair.",
      code(r'''
        names = ["Al", "Bo", "Cy"]
        ages = [30, 25]
        for i, (n, a) in enumerate(zip(names, ages), start=1):
            print(i, n, a)
      ''')),

    Q("Bonus", 23, "Output?",
      ["[1, 4, 16, 25]", "[9, 36]", "[1, 2, 4, 5]", "[1, 4, 9, 16, 25, 36]", "[1, 16, 25]", "Error"],
      "[1, 4, 16, 25]",
      "A list comprehension is a loop in one line: [EXPRESSION for ITEM in LIST if "
      "CONDITION]. It keeps n only when n % 3 != 0 (that drops 3 and 6), then squares it.",
      code(r'''
        nums = [1, 2, 3, 4, 5, 6]
        print([n * n for n in nums if n % 3 != 0])
      ''')),

    Q("Bonus", 24, "The user just presses Enter (types nothing). What is the LAST line printed?",
      ["Empty: str", "Yes: ", "Empty: NoneType", "Error", "Yes: None", "Empty: bool"],
      "Empty: str",
      "Pressing Enter gives an EMPTY STRING '', not None. '' is falsy, so the else runs, "
      "and its type is still str.",
      code(r'''
        answer = input("Continue? ")
        if answer:
            print("Yes:", answer)
        else:
            print("Empty:", type(answer).__name__)
      '''), inputs=[""]),

    Q("Bonus", 25, "Output?",
      ["[1, 10, 7]", "[10, 7, 1]", "[1, 10, 7, 4]", "[4, 10, 7]", "Error", "[1, 10, 4, 7]"],
      "[1, 10, 7]",
      "range(10, 0, -3) counts DOWN by 3: 10, 7, 4, 1. remove(4) deletes the VALUE 4. "
      "pop() removes and returns the LAST item (1). insert(0, 1) puts it at the front.",
      code(r'''
        r = list(range(10, 0, -3))
        r.remove(4)
        r.insert(0, r.pop())
        print(r)
      ''')),
]

ALL_SETS = {"1": ("Practice Exam 1", QUIZ1), "2": ("Practice Exam 2", QUIZ2), "3": ("Bonus", BONUS)}


# ===========================================================================
# Terminal helpers
# ===========================================================================
if os.name == "nt":
    os.system("")  # turns on ANSI colors in Windows terminals
USE_COLOR = bool(sys.stdout) and sys.stdout.isatty() and "NO_COLOR" not in os.environ


def _c(code_):
    return lambda t: f"\033[{code_}m{t}\033[0m" if USE_COLOR else str(t)


BOLD, DIM, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN = (
    _c("1"), _c("2"), _c("31"), _c("32"), _c("33"), _c("34"), _c("35"), _c("36"))


def ask(prompt=""):
    try:
        return input(prompt)
    except EOFError:
        print()
        sys.exit(0)


def label(q):
    return f"{q['source']} Q{q['num']}"


def show_code(src, arrow_line=None):
    for n, line in enumerate(src.split("\n"), 1):
        if n == arrow_line:
            print(YELLOW(f" ->{n:>3} | {line}"))
        else:
            print(DIM(f"   {n:>3} | ") + line)


def show_output(text, indent="   "):
    """Print program output with a visible left edge so leading spaces show."""
    if text == "":
        print(indent + DIM("(nothing printed)"))
        return
    for line in text.rstrip("\n").split("\n"):
        print(indent + CYAN("|") + line)


# ===========================================================================
# Code runner + tracer (the engine behind dev mode)
# ===========================================================================
STEP_LIMIT = 2000
TIME_LIMIT = 5.0        # seconds a traced program may run
OUTPUT_LIMIT = 200_000  # characters a traced program may print

# Code run by this tool (the questions, and anything pasted into the Playground)
# may only import from this list. This is a safety net, not a real sandbox.
ALLOWED_MODULES = {"random", "math", "string", "datetime", "collections", "itertools",
                   "functools", "json", "re", "statistics", "decimal", "fractions",
                   "operator", "copy", "textwrap", "typing", "emoji", "enum", "dataclasses",
                   "calendar", "heapq", "bisect", "numbers", "array"}
_REAL_IMPORT = builtins.__import__


class StopTrace(BaseException):
    """Raised to stop a runaway program (BaseException so `except Exception` can't swallow it)."""


def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    root = name.split(".")[0]
    if level == 0 and root in ALLOWED_MODULES:
        return _REAL_IMPORT(name, globals, locals, fromlist, level)
    try:
        import importlib.util
        exists = level == 0 and importlib.util.find_spec(root) is not None
    except Exception:
        exists = False
    if exists:
        raise ImportError(f"'{root}' is blocked in this study tool (allowed: random, math, "
                          f"string, datetime, collections, itertools, re, json, ...)")
    raise ModuleNotFoundError(f"No module named '{name}'", name=name)


def _blocked(what):
    def blocked(*args, **kwargs):
        raise PermissionError(f"{what}() is disabled in this study tool")
    return blocked


def sandbox_builtins(fake_input):
    b = dict(vars(builtins))
    b["__import__"] = _safe_import
    b["input"] = fake_input
    for name in ("open", "breakpoint", "help", "exit", "quit"):
        b[name] = _blocked(name)
    return b


def make_fake_input(values):
    queue = list(values)

    def fake_input(prompt=""):
        value = queue.pop(0) if queue else ""
        print(f"{prompt}{value}")  # echo it like a real terminal would
        return value
    return fake_input


def ensure_emoji_module():
    try:
        import emoji  # noqa: F401
        return None
    except ImportError:
        stub = types.ModuleType("emoji")
        table = {":fire:": "\U0001F525", ":snake:": "\U0001F40D", ":thumbs_up:": "\U0001F44D",
                 ":red_heart:": "â¤ï¸", ":smile:": "\U0001F604"}

        def emojize(s, **kwargs):
            for k, v in table.items():
                s = s.replace(k, v)
            return s
        stub.emojize = emojize
        sys.modules["emoji"] = stub
        return ("note: the emoji package isn't installed, so a small stand-in is used. "
                "Run `pip install emoji` for the real one.")


def describe(v):
    """(display text, type name) for a value."""
    if isinstance(v, types.ModuleType):
        return f"<module {v.__name__}>", "module"
    if isinstance(v, (types.FunctionType, types.BuiltinFunctionType, types.MethodType)):
        return f"<function {getattr(v, '__name__', '?')}>", "function"
    if isinstance(v, type):
        return f"<class {v.__name__}>", "class"
    try:
        r = repr(v)
    except Exception:
        r = "<?>"
    if len(r) > 70:
        r = r[:67] + "..."
    return r, type(v).__name__


def snapshot(frame, is_module):
    src = frame.f_globals if is_module else frame.f_locals
    snap = {}
    for k, v in list(src.items()):
        if k.startswith("__") or (is_module and k == "input"):
            continue
        snap[k] = describe(v)
    return snap


# --- evaluating pieces of a line (without side effects) ---------------------
# Only calls that can't change anything are re-evaluated for the explanation.
# User-defined functions, print(), .append() etc. are never re-run.
SAFE_FUNCS = {"len", "int", "float", "str", "abs", "min", "max", "sum", "round", "sorted",
              "list", "tuple", "set", "dict", "bool", "repr", "ord", "chr", "isinstance",
              "type", "range", "reversed", "enumerate", "zip", "divmod", "pow"}
SAFE_METHODS = {"lower", "upper", "strip", "lstrip", "rstrip", "split", "replace", "join",
                "format", "title", "capitalize", "count", "find", "index", "startswith",
                "endswith", "get", "keys", "values", "items", "copy", "isdigit", "isalpha"}
OP_SYMBOLS = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.FloorDiv: "//",
              ast.Mod: "%", ast.Pow: "**"}


def make_env(frame):
    env = dict(frame.f_globals)
    env.update(frame.f_locals)
    return env


def is_safe(node, env):
    for n in ast.walk(node):
        if isinstance(n, (ast.Lambda, ast.NamedExpr, ast.Await, ast.Yield, ast.YieldFrom)):
            return False
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name):
                if f.id not in SAFE_FUNCS or isinstance(env.get(f.id), types.FunctionType):
                    return False
            elif isinstance(f, ast.Attribute):
                if f.attr not in SAFE_METHODS:
                    return False
            else:
                return False
    return True


def eval_node(node, env):
    e = ast.Expression(body=node)
    ast.fix_missing_locations(e)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return eval(compile(e, "<expr>", "eval"), dict(env))


_NOVAL = object()


def truthy_word(x):
    return "truthy" if x else "falsy"


def truth_tag(val):
    return "" if isinstance(val, bool) else f"   [{truthy_word(val)}]"


def _val(node, env):
    return eval_node(node, env) if is_safe(node, env) else _NOVAL


def explain_node(node, src, env, v):
    """A plain-English reason for how this piece of an expression got its value ('' if nothing to add)."""
    try:
        seg_of = lambda n: ast.get_source_segment(src, n) or "?"  # noqa: E731
        isnum = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)  # noqa: E731
        if isinstance(node, ast.BoolOp):
            is_and = isinstance(node.op, ast.And)
            word = "and" if is_and else "or"
            bits = []
            for idx, operand in enumerate(node.values):
                ov = _val(operand, env)
                if ov is _NOVAL:
                    return ""
                r = describe(ov)[0]
                decisive = (not ov) if is_and else bool(ov)
                if decisive:
                    rest = " (the rest is never checked)" if idx < len(node.values) - 1 else ""
                    bits.append(f"{seg_of(operand)} is {r} ({truthy_word(ov)}) -> `{word}` stops here and RETURNS it{rest}")
                    return "; ".join(bits)
                bits.append(f"{seg_of(operand)} is {r} ({truthy_word(ov)}) -> keep looking")
            bits.append(f"nothing decided early, so `{word}` RETURNS the last value")
            return "; ".join(bits)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            ov = _val(node.operand, env)
            if ov is _NOVAL:
                return ""
            return (f"`not` flips truthiness: {seg_of(node.operand)} is {describe(ov)[0]} ({truthy_word(ov)}), "
                    f"so not gives {v}")
        if isinstance(node, ast.Compare) and len(node.ops) > 1:
            return "a chained comparison: every link must be True (a < b < c means a < b AND b < c)"
        if isinstance(node, ast.BinOp):
            left, right = _val(node.left, env), _val(node.right, env)
            if left is _NOVAL or right is _NOVAL:
                return ""
            if isinstance(node.op, ast.Mod) and isnum(left) and isnum(right) and right != 0:
                note = f"% gives the REMAINDER:  {left} = {right} x {left // right} + {v}"
                return note + ("   (remainder 0: it divides evenly)" if v == 0 else "")
            if isinstance(node.op, ast.FloorDiv) and isnum(left) and isnum(right) and right != 0:
                return f"// divides, then rounds DOWN (toward negative infinity):  {left} / {right} = {left / right:g}  ->  {v}"
            if isinstance(node.op, ast.Div) and isnum(left) and isnum(right):
                return "/ ALWAYS gives a float" + (" (even int / int)" if isinstance(left, int) and isinstance(right, int) else "")
            if isinstance(node.op, ast.Mult) and ((isinstance(left, str) and isinstance(right, int))
                                                  or (isinstance(left, int) and isinstance(right, str))):
                return "str * int REPEATS the text (no math is done)"
            if isinstance(node.op, ast.Add) and isinstance(left, str) and isinstance(right, str):
                return "str + str JOINS the text (no math, even if it looks like digits)"
            return ""
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("int", "float", "str") \
                and len(node.args) == 1:
            a = _val(node.args[0], env)
            if a is _NOVAL:
                return ""
            note = f"{node.func.id}() converts a {type(a).__name__} ({describe(a)[0]}) into a {type(v).__name__}"
            if node.func.id == "int" and isinstance(a, float):
                note += ": it CUTS OFF the decimals (no rounding)"
            return note
        if isinstance(node, ast.Subscript):
            sl = node.slice
            if hasattr(ast, "Index") and isinstance(sl, getattr(ast, "Index")):
                sl = sl.value
            if isinstance(sl, ast.Slice):
                return "a slice includes the START index and stops just BEFORE the stop index"
    except Exception:
        return ""
    return ""


def condition_info(src_line, frame):
    """For if/elif/while lines: evaluate the condition (and its and/or parts)."""
    s = src_line.strip()
    expr = None
    for kw in ("if ", "elif ", "while "):
        if s.startswith(kw) and s.endswith(":"):
            expr = s[len(kw):-1].strip()
            break
    if not expr or "input(" in expr:
        return None
    try:
        tree = ast.parse(expr, mode="eval").body
    except SyntaxError:
        return None
    env = make_env(frame)
    if not is_safe(tree, env):
        return None

    parts = []
    try:
        if isinstance(tree, ast.BoolOp):
            is_and = isinstance(tree.op, ast.And)
            stopped = False
            for node in tree.values:
                seg = ast.get_source_segment(expr, node) or "?"
                if stopped:
                    parts.append((seg, None))
                    continue
                val = eval_node(node, env)
                parts.append((seg, describe(val)[0] + truth_tag(val)))
                if (is_and and not val) or (not is_and and val):
                    stopped = True
        elif isinstance(tree, ast.UnaryOp) and isinstance(tree.op, ast.Not):
            operand = eval_node(tree.operand, env)
            parts.append((ast.get_source_segment(expr, tree.operand) or "?", describe(operand)[0] + truth_tag(operand)))
        val = eval_node(tree, env)
    except Exception:
        return None
    return {"expr": expr, "parts": parts,
            "value": describe(val)[0], "truth": bool(val)}


def _post_order(n):
    """Inner expressions first. f-strings and comprehensions are shown as one piece
    (their insides use variables that only exist while they run)."""
    if not isinstance(n, (ast.JoinedStr, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
        for c in ast.iter_child_nodes(n):
            yield from _post_order(c)
    yield n


INTERESTING = (ast.BinOp, ast.BoolOp, ast.Compare, ast.UnaryOp, ast.Subscript, ast.Call,
               ast.JoinedStr, ast.IfExp, ast.ListComp)


def expression_evals(src_line, frame):
    """
    Work out the pieces of the line's expressions, innermost first, using the
    variable values from BEFORE the line runs. Returns [(text, value, is_error, explanation)].
    """
    s = src_line.strip()
    if not s or s.startswith("#") or "input(" in s:
        return None
    try:
        if s.startswith(("def ", "class ", "import ", "from ")):
            return None
        if s.startswith(("if ", "elif ", "while ")) and s.endswith(":"):
            kw = s.split(None, 1)[0]
            stmt = ast.parse(("if" if kw == "elif" else kw) + s[len(kw):] + " pass").body[0]
            roots = [stmt.test]
        elif s.endswith(":"):
            if not s.startswith("for "):
                return None
            stmt = ast.parse(s + " pass").body[0]
            roots = [stmt.iter]
        else:
            body = ast.parse(s).body
            if len(body) != 1:
                return None
            stmt = body[0]
            roots = []
            if isinstance(stmt, (ast.Assign, ast.Expr)):
                roots = [stmt.value]
            elif isinstance(stmt, ast.Return) and stmt.value is not None:
                roots = [stmt.value]
            elif isinstance(stmt, ast.AugAssign) and isinstance(stmt.target, ast.Name):
                roots = [ast.BinOp(left=ast.Name(id=stmt.target.id, ctx=ast.Load()),
                                   op=stmt.op, right=stmt.value)]
    except SyntaxError:
        return None
    if not roots:
        return None

    env = make_env(frame)
    out, seen = [], set()
    for root in roots:
        for node in _post_order(root):
            if not isinstance(node, INTERESTING):
                continue
            if isinstance(node, ast.Subscript) and not isinstance(node.ctx, ast.Load):
                continue
            if isinstance(node, ast.BinOp) and isinstance(root, ast.BinOp) and node is root \
                    and isinstance(stmt, ast.AugAssign):
                seg = f"{stmt.target.id} {OP_SYMBOLS.get(type(stmt.op), '?')} " \
                      f"{ast.get_source_segment(s, stmt.value)}"
            else:
                seg = ast.get_source_segment(s, node)
            if not seg or seg in seen or not is_safe(node, env):
                continue
            seen.add(seg)
            try:
                raw = eval_node(node, env)
                val = describe(raw)[0]
            except Exception as ex:
                out.append((seg, f"{type(ex).__name__}: {ex}  <- this is where it fails", True, ""))
                return out
            out.append((seg, val, False, explain_node(node, s, env, raw)))
    return out[:10] or None


def compute_stack(frame):
    names = []
    f = frame
    while f is not None:
        if f.f_code.co_filename == "<quiz>" and (f.f_code.co_name == "<module>" or not f.f_code.co_name.startswith("<")):
            names.append("main program" if f.f_code.co_name == "<module>" else f.f_code.co_name + "()")
        f = f.f_back
    names.reverse()
    return names


def compute_callargs(callee, lines, counters):
    """Which value went into which parameter, and where it came from (positional / keyword / default)."""
    caller = callee.f_back
    if caller is None or caller.f_code.co_filename != "<quiz>":
        return None
    code = callee.f_code
    name = code.co_name
    posparams = list(code.co_varnames[:code.co_argcount])
    params = list(code.co_varnames[:code.co_argcount + code.co_kwonlyargcount])
    idx = len(params)
    star = code.co_varnames[idx] if code.co_flags & 0x04 else None
    idx += 1 if star else 0
    kwstar = code.co_varnames[idx] if code.co_flags & 0x08 else None
    ln = caller.f_lineno
    src = lines[ln - 1].strip() if 0 < ln <= len(lines) else ""
    tree = None
    try:
        tree = ast.parse(src + " pass" if src.endswith(":") else src)
    except SyntaxError:
        pass
    calls = []
    if tree is not None:
        for n in ast.walk(tree):
            if isinstance(n, ast.Call):
                fn = n.func
                nm = fn.id if isinstance(fn, ast.Name) else fn.attr if isinstance(fn, ast.Attribute) else None
                if nm == name:
                    calls.append(n)
        calls.sort(key=lambda n: (n.lineno, n.col_offset))
    k = counters.get((ln, name), 0)
    counters[(ln, name)] = k + 1
    call = calls[k % len(calls)] if calls else None
    src_parsed = src + " pass" if src.endswith(":") else src
    defaults = set()
    fn_obj = caller.f_globals.get(name) or caller.f_locals.get(name)
    if isinstance(fn_obj, types.FunctionType):
        try:
            defaults = {p.name for p in inspect.signature(fn_obj).parameters.values()
                        if p.default is not inspect.Parameter.empty}
        except (TypeError, ValueError):
            pass
    passed, extra_pos, extra_kw = {}, [], []
    if call is not None:
        for i, a in enumerate(call.args):
            seg = ast.get_source_segment(src_parsed, a)
            if isinstance(a, ast.Starred):
                continue
            if i < len(posparams):
                passed[posparams[i]] = (seg, "positional argument", a)
            else:
                extra_pos.append(seg)
        for kw in call.keywords:
            seg = ast.get_source_segment(src_parsed, kw.value)
            if kw.arg is None:
                continue
            if kw.arg in params:
                passed[kw.arg] = (seg, f"keyword argument ({kw.arg}=...)", kw.value)
            else:
                extra_kw.append(f"{kw.arg}={seg}")
    loc = callee.f_locals
    rows = []
    for p in params:
        val = loc.get(p)
        seg, kind, node = passed.get(p, (None, "default value (you didn't pass it)" if p in defaults else "argument", None))
        same = None
        if isinstance(node, ast.Name):
            cv = caller.f_locals.get(node.id, caller.f_globals.get(node.id, _NOVAL))
            if cv is val:
                same = node.id
        rows.append({"param": p, "value": describe(val)[0], "type": type(val).__name__, "expr": seg,
                     "kind": kind, "same_as": same, "mutable": isinstance(val, (list, dict, set))})
    if star:
        rows.append({"param": "*" + star, "value": describe(loc.get(star))[0], "type": "tuple",
                     "expr": ", ".join(extra_pos) or None, "kind": "the extra positional arguments, packed into a tuple",
                     "same_as": None, "mutable": False})
    if kwstar:
        rows.append({"param": "**" + kwstar, "value": describe(loc.get(kwstar))[0], "type": "dict",
                     "expr": ", ".join(extra_kw) or None, "kind": "the extra keyword arguments, packed into a dict",
                     "same_as": None, "mutable": False})
    return {"func": name, "call": ast.get_source_segment(src_parsed, call) if call is not None else None, "rows": rows}


def trace_run(src, inputs=()):
    """Run code, recording every step. Returns (events, output, error_text, note)."""
    note = ensure_emoji_module() if "emojize" in src else None
    lines = src.split("\n")
    events, buf, frame_ids, counter = [], io.StringIO(), {}, [0]
    call_counts = {}
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            compiled = compile(src, "<quiz>", "exec")
    except SyntaxError as e:
        return [], "", f"SyntaxError: {e.msg} (line {e.lineno})", note

    def tracer(frame, event, arg):
        if frame.f_code.co_filename != "<quiz>":
            return None
        if frame.f_code.co_name in ("<listcomp>", "<dictcomp>", "<setcomp>", "<genexpr>"):
            return None  # treated as part of the line that contains it
        if event == "call":
            counter[0] += 1
            frame_ids[id(frame)] = counter[0]
        if len(events) > STEP_LIMIT:
            raise StopTrace(f"stopped after {STEP_LIMIT} steps (infinite loop?)")
        if time.monotonic() > deadline:
            raise StopTrace(f"stopped after {TIME_LIMIT:g} seconds (infinite loop?)")
        if buf.tell() > OUTPUT_LIMIT:
            raise StopTrace("stopped: the program printed too much")
        is_module = frame.f_code.co_name == "<module>"
        ev = {"kind": event, "line": frame.f_lineno, "func": frame.f_code.co_name,
              "fid": frame_ids.get(id(frame)), "module": is_module,
              "vars": snapshot(frame, is_module), "pos": buf.tell(), "extra": None,
              "cond": None, "evals": None, "stack": compute_stack(frame), "callargs": None}
        if event == "call" and not is_module:
            try:
                ev["callargs"] = compute_callargs(frame, lines, call_counts)
            except Exception:
                pass
        if event == "return":
            ev["extra"] = describe(arg)[0]
        elif event == "exception":
            ev["extra"] = f"{arg[0].__name__}: {arg[1]}"
        elif event == "line" and 0 < frame.f_lineno <= len(lines):
            try:
                ev["cond"] = condition_info(lines[frame.f_lineno - 1], frame)
                ev["evals"] = expression_evals(lines[frame.f_lineno - 1], frame)
            except Exception:
                pass
        events.append(ev)
        return tracer

    fake_input = make_fake_input(inputs)
    g = {"__name__": "__main__", "__builtins__": sandbox_builtins(fake_input), "input": fake_input}
    error = None
    old = sys.gettrace()
    deadline = time.monotonic() + TIME_LIMIT
    with contextlib.redirect_stdout(buf):
        sys.settrace(tracer)
        try:
            exec(compiled, g)
        except StopTrace as e:
            error = f"{e}"
        except (Exception, SystemExit, KeyboardInterrupt) as e:
            error = f"{type(e).__name__}: {e}"
        finally:
            sys.settrace(old)
            if note:  # remove the stand-in so it doesn't fool other questions
                sys.modules.pop("emoji", None)
    return events, buf.getvalue(), error, note


def diff_vars(before, after):
    out = []
    for k, (r, t) in after.items():
        if k not in before:
            out.append(f"{GREEN(k)} = {r}   {DIM('(new ' + t + ')')}")
        elif before[k] != (r, t):
            extra = f"   {DIM('(type ' + before[k][1] + ' -> ' + t + ')')}" if before[k][1] != t else ""
            out.append(f"{YELLOW(k)}: {before[k][0]}  ->  {r}{extra}")
    for k in before:
        if k not in after:
            out.append(f"{RED(k)} deleted")
    return out


def block_verdict(src_lines, header_line, next_event):
    """For an if/elif/while whose condition calls a function: did the block run?
    Decided by whether the next executed line is indented deeper than the header."""
    if not src_lines or header_line > len(src_lines):
        return ""
    header = src_lines[header_line - 1]
    if not (header.strip().startswith(("if ", "elif ", "while ")) and header.strip().endswith(":")):
        return ""
    if next_event["kind"] != "line" or next_event["line"] > len(src_lines):
        return ""

    def indent(s):
        return len(s) - len(s.lstrip())
    ran = indent(src_lines[next_event["line"] - 1]) > indent(header)
    return (GREEN(" -> condition was True, so the indented block runs") if ran
            else RED(" -> condition was False, so the indented block is skipped"))


def build_steps(events, output, error, src=None):
    """Turn raw trace events into human-readable steps."""
    src_lines = src.split("\n") if src else []
    steps, pending = [], {}
    module_vars = {}
    exc_frames = set()
    last_exc = None  # (text, event index) - to show a propagating error only once

    def where(e):
        return "main program" if e["module"] else f"{e['func']}()"

    def base(e):
        return {"line": e["line"], "func": e["func"], "fid": e["fid"], "stack": e["stack"]}

    for i, e in enumerate(events):
        if i in pending:
            steps.append(pending.pop(i))
        if e["module"]:
            module_vars = e["vars"]
        kind = e["kind"]

        if kind == "call":
            if e["module"]:
                continue
            args = ", ".join(f"{k}={v[0]}" for k, v in e["vars"].items())
            steps.append({**base(e),
                          "title": f"Calling {BOLD(e['func'] + '(' + args + ')')} - jumping INTO the function "
                                   + DIM("(the arrow sits on its def line)"),
                          "changes": [], "out": "", "vars": e["vars"], "globals": module_vars,
                          "cond": None, "evals": None, "callargs": e["callargs"]})

        elif kind == "line":
            exc_frames.discard(e["fid"])  # the frame kept running, so it handled any error
            j = next((k for k in range(i + 1, len(events)) if events[k]["fid"] == e["fid"]), None)
            after = events[j] if j is not None else e
            end = events[j]["pos"] if j is not None else len(output)
            deeper = i + 1 < len(events) and events[i + 1]["fid"] != e["fid"]
            if deeper:
                steps.append({**base(e),
                              "title": f"Line {e['line']} calls a function, so Python runs that function first...",
                              "changes": [], "out": "", "vars": e["vars"],
                              "globals": None if e["module"] else module_vars,
                              "cond": e["cond"], "evals": e["evals"]})
                if j is not None:
                    start = events[j - 1]["pos"]
                    pending[j] = {**base(e),
                                  "title": f"Back in {where(e)}: line {e['line']} finishes"
                                           + block_verdict(src_lines, e["line"], after),
                                  "changes": diff_vars(e["vars"], after["vars"]),
                                  "out": output[start:end], "vars": after["vars"],
                                  "globals": None if e["module"] else module_vars,
                                  "cond": None, "evals": None}
            else:
                title = (f"Running line {e['line']} ..." if after["kind"] == "exception"
                         else f"Ran line {e['line']}")
                steps.append({**base(e), "title": title,
                              "changes": diff_vars(e["vars"], after["vars"]),
                              "out": output[e["pos"]:end], "vars": after["vars"],
                              "globals": None if e["module"] else module_vars,
                              "cond": e["cond"], "evals": e["evals"]})

        elif kind == "exception":
            dup = (last_exc is not None and last_exc[0] == e["extra"] and
                   all(events[k]["kind"] in ("return", "exception")
                       for k in range(last_exc[1] + 1, i)))
            last_exc = (e["extra"], i)
            exc_frames.add(e["fid"])
            if not dup:
                steps.append({**base(e),
                              "title": RED(f"Line {e['line']} raised an error -> {e['extra']}"),
                              "changes": [], "out": "", "vars": e["vars"],
                              "globals": None if e["module"] else module_vars,
                              "cond": None, "evals": None})

        elif kind == "return" and not e["module"]:
            if e["fid"] in exc_frames:
                title = RED(f"{e['func']}() stops because of the error")
            else:
                title = f"{e['func']}() is done and RETURNS {BOLD(e['extra'])}"
            steps.append({**base(e), "title": title, "changes": [],
                          "out": "", "vars": e["vars"], "globals": module_vars,
                          "cond": None, "evals": None})
    return steps


# ===========================================================================
# Learning aids: explanations of right / wrong answers, concept tags, cheat sheets
# ===========================================================================
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def plain(s):
    return ANSI_RE.sub("", s)


def _norm(x):
    return re.sub(r"\s+", " ", str(x).strip().strip("'\"")).lower()


def narrate(src, steps):
    """The run of a program as plain-English sentences (one per meaningful step)."""
    lines = src.split("\n")
    out = []
    for s in steps:
        ln = s["line"]
        code_line = lines[ln - 1].strip() if 0 < ln <= len(lines) else ""
        title = plain(s["title"])
        if title.startswith("Calling "):
            ca = s.get("callargs")
            if ca and ca["rows"]:
                bits = [f"{r['param']} = {r['value']}" + (" (default)" if r["kind"].startswith("default") else "")
                        for r in ca["rows"]]
                out.append(f"Line {ln} calls {ca['func']}() - inside it the parameters are: " + ", ".join(bits))
            else:
                out.append(f"Line {ln} calls {s['func']}()")
        elif "calls a function, so Python runs that function first" in title:
            continue
        elif title.startswith("Back in"):
            ch = "; ".join(plain(c) for c in s["changes"])
            tail = f" -> {ch}" if ch else ""
            if s["out"]:
                tail += f" -> prints {s['out'].rstrip(chr(10))!r}"
            out.append(f"Back on line {ln}{tail}")
        elif "raised an error" in title:
            out.append(title)
        elif "RETURNS" in title:
            out.append(f"{s['func']}() finishes and hands back {title.split('RETURNS ', 1)[1]}")
        elif "stops because of the error" in title:
            out.append(title)
        else:
            parts = [f"Line {ln}  {code_line}"]
            c = s["cond"]
            if c:
                parts.append(f"the condition is {c['value']} -> the indented block "
                             + ("RUNS" if c["truth"] else "is SKIPPED"))
            if s["changes"]:
                parts.append("; ".join(plain(x) for x in s["changes"]))
            if s["out"]:
                parts.append(f"prints {s['out'].rstrip(chr(10))!r}")
            out.append("  ->  ".join(parts))
    return out


def diagnose(q, choice, steps, output, error):
    """Why is `choice` NOT the answer? Uses hand-written notes first, then the real run of the code."""
    if choice in q["answer"]:
        return "This is the right answer."
    trap = TRAPS.get((q["source"], q["num"]), {}).get(choice)
    if trap:
        return trap
    if q["demo"] or not q["code"]:
        return ""
    actual = output.rstrip("\n")
    last = actual.split("\n")[-1] if actual else ""
    answers = [_norm(a) for a in q["answer"]]
    err_kind = error.split(":")[0].lower() if error else ""
    is_output_q = _norm(actual) in answers or _norm(last) in answers
    is_error_q = bool(error) and any(err_kind and err_kind in a for a in answers)
    if not (is_output_q or is_error_q):
        return ""
    shown = last if (_norm(last) in answers and _norm(actual) not in answers) else actual
    cn = _norm(choice)
    claims_error = any(w in cn for w in ("error", "exception", "crash"))
    if claims_error and not error:
        return (f"The code does NOT crash. It runs to the end and prints {shown!r}." if shown
                else "The code does NOT crash; it simply prints nothing.")
    if error and not claims_error:
        return f"That output never appears: the program crashes with {error} before it can print it."
    if error and claims_error:
        return f"It does crash, but with {error}, not that."
    if cn in ("nothing", "none is printed", "does nothing") and actual:
        return f"The code does print something: {shown!r}."
    if re.search(r"\bprint\s*\(", choice) and "print(" not in actual:
        return "That is source code, not output. print() shows the VALUE, never the text of its own call."
    stripped = choice.strip()
    if len(stripped) > 1 and stripped[0] in "'\"" and stripped[-1] == stripped[0] \
            and _norm(stripped[1:-1]) == _norm(shown):
        return "Quotes only mark where a string starts and ends. print() never shows them."
    if re.search(r"\{\w+\}", choice):
        return ("Text inside { } is only a placeholder. The f in front of the string fills it with the variable's "
                "value, so the braces never appear in the output.")
    if cn.replace(" ", "") == _norm(shown).replace(" ", ""):
        return f"Same characters but not the exact output. Python printed {shown!r} - spaces and line breaks (\\n) count."
    try:
        if float(cn) == float(_norm(shown)):
            return f"Same number, different form. Python printed {shown!r}: the TYPE decides the format (an int never shows .0)."
    except ValueError:
        pass
    final = {}
    for s in steps:
        for name, (r, tp) in s["vars"].items():
            final[(s.get("fid"), name)] = r
    for s in steps:
        for name, (r, tp) in s["vars"].items():
            if _norm(r) == cn and len(cn) > 0:
                later = final.get((s.get("fid"), name))
                msg = f"`{name}` really is {r} after line {s['line']}"
                if later is not None and later != r:
                    msg += f", but it changes to {later} later"
                return msg + f". That's an in-between value, not what the program finally prints ({shown!r})."
        for ev in (s.get("evals") or []):
            seg, val = ev[0], ev[1]
            if _norm(val) == cn:
                return (f"That is what `{seg}` works out to on line {s['line']} - only one piece of the "
                        f"calculation. The final output is {shown!r}.")
    if re.fullmatch(r"-?\d+(\.\d+)?", cn) and not re.fullmatch(r"-?\d+(\.\d+)?", _norm(shown)):
        for s in steps:
            for name, (r, tp) in s["vars"].items():
                if tp == "str" and re.fullmatch(r"'-?\d+(\.\d+)?'", r):
                    return (f"`{name}` is the TEXT {r} (a str), not a number, so the program never does arithmetic "
                            f"with it. That is why a number like {choice} isn't produced.")
    return f"No line of this program produces that output. What it really prints is {shown!r}."


# --- hand-written "why NOT this option" notes for the questions people most often get tricked on -----------
TRAPS = {
    ("Exam 1", 7): {
        "7": "input() hands back TEXT and nothing converts it. print just shows the text as typed: 7.5. (int('7.5') would crash anyway.)",
        "float": "float is a TYPE name. print(number) prints the VALUE stored in number, not its type (type(number) would say str).",
        "number": "number is the VARIABLE'S NAME. print(number) with no quotes prints what is stored in it.",
        "Error": "No error: input() always works and returns a str, and printing a str is fine.",
        "0": "Nothing in the program produces 0. The user typed 7.5 and that text is printed back."},
    ("Exam 1", 8): {
        "16": "That is (5 + 3) * 2. Multiplication happens BEFORE addition: 3 * 2 = 6 first, then 5 + 6.",
        "13": "That would need 5 + 8. The 3 is multiplied by 2 first (6), then added to 5.",
        "8": "That is just 5 + 3. The * 2 still applies to the 3 before the addition.",
        "10": "That is 5 * 2. Only the 3 is multiplied by 2 - then 5 is added."},
    ("Exam 1", 11): {
        "Non-zero": "`if value:` asks whether the number is TRUTHY. 0 is falsy (like False, '', [], None), so the else runs.",
        "Always prints Non-zero": "Only non-zero numbers are truthy. 0 is falsy, so this input reaches the else branch.",
        "Error due to int conversion": "int('0') is perfectly valid. Only text that is not a whole number (like 'abc' or '7.5') fails.",
        "None": "One of the two print calls always runs, so something is printed.",
        "Prints value": "The program prints the words Zero or Non-zero, never the number itself."},
    ("Exam 1", 13): {
        "Enabled": "'false'.lower() is 'false', which is NOT equal to 'true', so the else runs.",
        "Error": "No error: .lower() works on any str and == compares two strings safely.",
        "Case-sensitive error": "Python doesn't raise an error for different capitalization. It just compares text, and .lower() makes it case-insensitive.",
        "Always prints Enabled": "Enabled only prints when the (lowercased) input equals 'true'.",
        "Input ignored": "The input IS used: it is lowercased and compared."},
    ("Exam 1", 14): {
        'Prints "Positive number" for all inputs': "If x < 0 the `pass` branch runs, and pass does nothing, so negative numbers print nothing.",
        'Always prints "Positive number"': "-5 < 0 is True, so the if branch (pass) runs and the else is skipped.",
        "Only prints on 0": "The else runs for every x that is NOT below 0: 0 and all positives.",
        "Skips the else block": "The else block is only skipped when x < 0 (the pass branch ran).",
        "Always prints an error": "pass is valid Python: it just does nothing."},
    ("Exam 1", 15): {
        "Error due to float": "float('-1.5') is valid: float() understands the minus sign and the decimal point.",
        "Non-negative": "-1.5 >= 0 is False, so the else branch (Negative) runs.",
        "0": "The program prints words, never the number.",
        "Syntax Error": "The code is valid. A SyntaxError would show before ANY line runs."},
    ("Exam 1", 17): {
        "a b c": "break leaves the loop the moment l == 'b', BEFORE print(l) runs for 'b'.",
        "a b": "When l is 'b' the if is True and break happens first, so 'b' is never printed.",
        "b": "'b' triggers the break, so it never reaches print."},
    ("Exam 1", 19): {
        "1 3": "n % 2 == 0 keeps EVEN numbers (remainder 0). 1 and 3 are odd (remainder 1).",
        "2": "4 is also even: 4 % 2 is 0, so it prints too.",
        "1 2 3 4": "The if filters: only numbers with n % 2 == 0 are printed.",
        "0": "The remainder is tested, not printed - the numbers 2 and 4 are what get printed."},
    ("Exam 1", 22): {
        "Student: Bob | Score: 95.68": "%06.2f means TOTAL width 6, padded with zeros: 095.68 (95.68 is only 5 characters).",
        "Student: Bob | Score: 00095.68": "Width 6 means 6 characters in total (095.68), not 8.",
        "Student: Bob | Score: 095.86": "Digits are rounded, never swapped: 95.678 rounds to 95.68.",
        "Student: Bob | Score: 95.678": ".2 asks for exactly TWO decimals, so 95.678 becomes 95.68.",
        "Student: Bob | Score: 095.6": ".2 means two decimal places, so it shows 95.68 and not 95.6."},
    ("Exam 1", 24): {
        "60": "That is 4 x 3 x 5. b keeps ITS default (2); 3 is c's default, which c=5 replaces.",
        "24": "That is 4 x 2 x 3: it ignores the keyword argument c=5, which replaces c's default of 3.",
        "30": "No arrangement of a=4, b=2 (default), c=5 gives 30.",
        "12": "That would use c's default (3) and ignore c=5."},
    ("Exam 1", 25): {
        "5": "args[0] is the FIRST item (5). args[1] is the second item, 10.",
        "15": "That is args[2], the third item.",
        "(5, 10)": "args[1] picks ONE item out of the tuple, not a slice of it.",
        "(10,)": "args[1] is the single value 10, not a one-item tuple."},
    ("Exam 2", 1): {
        "5 3 x+y=8": "x = y = x + y sets BOTH names to 5 (the right side is worked out once), so y is no longer 3.",
        "2 5 x+y=7": "x is reassigned too - x = y = ... gives the same value to both names.",
        "3 3 x+y=6": "The value stored is x + y evaluated ONCE with the OLD values: 2 + 3 = 5, not 3.",
        "2 3 x+y=5": "Those are the starting values. The line x = y = x + y runs BEFORE the print.",
        "Error": "x, y = 2, 3 and the chained assignment are valid; f\"{x+y=}\" is the legal 'debug' f-string."},
    ("Exam 2", 3): {
        "16": "That needs int(val) * 2. Here val is the TEXT '8', and text * 2 REPEATS it: '88'.",
        "64": "Nothing squares or multiplies 8 by itself here. val is text and * 2 repeats it.",
        "Error": "str * int is allowed in Python - it repeats the string.",
        '"16"': "That would be the number 16 in quotes. The text '8' repeated twice is 88.",
        "None": "print shows the value of val*2, which exists (88)."},
    ("Exam 2", 5): {
        "13.0": "int(n) turns 12.0 into the int 12 first. int + 1 is an int: 13, with no .0.",
        "12": "The + 1 is applied after int(n): 12 + 1 = 13.",
        "Error": "float('12.0') works, then int(12.0) works. (int('12.0') on the TEXT would fail - that is why float comes first.)",
        "121": "int(n) + 1 adds numbers (12 + 1). Joining text would need str() and +.",
        "12.1": "+ adds 1 (making 13); it doesn't put a '1' after a decimal point."},
    ("Exam 2", 7): {
        "Both/None": "The elif is only checked when the if condition is False. Here it was True, so the elif never ran.",
        "True": "The code prints the TEXT 'One'; it never prints the result of the condition.",
        "False": "The code prints text, not the condition's value. The condition was True, so 'One' printed.",
        "None": "Something is printed: the if branch ran.",
        "Error": "Using numbers with and/or/not is valid Python (0 is falsy, 5 is truthy)."},
    ("Exam 2", 8): {
        "Miss": "n < 10 is False, but the second part is True: 90 >= 10 and 90 % 5 == 0 (remainder 0). False OR True is True.",
        "90": "The program prints the text 'Hit' or 'Miss', never n.",
        "Nothing": "Either the if or the else prints, so something is always printed.",
        "0": "90 % 5 IS 0, but that is compared inside the condition and never printed."},
    ("Exam 2", 10): {
        "B": "Once `if x >= 12` is True its branch runs and the elif is skipped. Only ONE branch of an if/elif chain runs.",
        "A B": "Only one branch of if/elif runs. After A prints, the elif x > 10 is skipped.",
        "C": "The else belongs to the OUTER if (x > 0), which was True, so it is skipped.",
        "Nothing": "x >= 12 is True (12 is equal to 12), so 'A' prints."},
    ("Exam 2", 11): {
        "T": "flag is True, so `if flag:` runs `pass`. The else (the only place 'T' could print) never runs.",
        "True": "Nothing prints the value of flag; the only possible print is the string 'T'.",
        "False": "Nothing prints False. The code only has print('T') in a branch that is skipped."},
    ("Exam 2", 12): {
        "Has": "x != None is False, but `not x` is True (None is falsy). With `or`, ONE true side is enough.",
        "Nothing": "The condition is True, so print('Empty') runs.",
        "Error": "Comparing None with != and using not on None are both valid.",
        "False": "The code prints text, not the condition. The condition is True, so 'Empty' prints.",
        "None": "The print shows the string 'Empty', not the value of x."},
    ("Exam 2", 13): {
        "[1, 2, 3]": "b holds two references to the SAME list a. b[0][1] = 9 changes that shared list.",
        "[9, 2, 3]": "b[0][1] changes index 1 (the 2), not index 0.",
        "[[1,9,3]]": "print(b[1]) prints the inner list itself, not a list wrapped inside another list.",
        "Error": "Indexing a list inside a list (b[0][1]) is valid.",
        "None": "b[1] is the list a, which exists."},
    ("Exam 2", 14): {
        "[10, 20, 30, 10]": "nums[1] is reassigned FIRST (30 - 20 = 10), so the list is [10, 10, 30] before the append of 10.",
        "[10, 20, 30]": "The list is changed by the assignment and by append, so it isn't the original.",
        "[10, 30, 30, 30]": "nums[1] becomes 30 - 20 = 10, not 30; the appended value is also 10.",
        "[10, -10, 30, -10]": "nums[2] - nums[1] is 30 - 20 = +10, not negative.",
        "Error": "All indexes used exist, so nothing crashes."},
    ("Exam 2", 24): {
        "Hi!\nHi!": "text = text + '!' makes a NEW string and rebinds only the LOCAL name text. msg outside still points to 'Hi'.",
        "Hi\nHi!": "The prints happen in this order: shout() prints 'Hi!' first, then the main program prints msg ('Hi').",
        "!Hi\nHi": "The '!' is added to the END (text + '!'), not the front.",
        "Error": "Reassigning a parameter inside a function is allowed.",
        "None": "shout() prints the text; it returns None but the program prints msg, not the result."},
    ("Exam 2", 25): {
        "Hello\nFalse": "hello() has no return statement, so x is None. None == None is True.",
        "False": "x is None (hello() returns nothing), and None == None is True. Also 'Hello' prints first.",
        "True": "That is only the second line. hello() prints Hello first.",
        "Error": "Comparing None with == is valid.",
        "Nothing": "hello() prints Hello and then the comparison prints True."},
    ("Exam 2", 32): {
        "bcxyz": "[1:5] stops BEFORE index 5, so it has 4 characters: indexes 1, 2, 3, 4 -> b c x y.",
        "cxyz": "Slicing starts AT index 1 (b), not index 2.",
        "ABCX": ".lower() makes everything lowercase first, so no capitals remain.",
        "bcdx": "The letters come from 'abcxyz': indexes 1-4 are b, c, x, y.",
        "Error": "Chaining a method and a slice (txt.lower()[1:5]) is valid."},
    ("Bonus", 2): {
        "3 2 -3": "// FLOORS (rounds DOWN toward negative infinity): -17 / 5 = -3.4 -> -4, not -3.",
        "3.4 2 -3.4": "// always gives a whole-number floor, not the decimal result of /.",
        "4 2 -4": "17 // 5 is 3 (3.4 rounded DOWN), not 4.",
        "3 2 3": "-a // 5 means (-17) // 5, which is negative.",
        "3 3 -4": "17 % 5 is the remainder: 17 = 5 x 3 + 2, so 2, not 3."},
    ("Bonus", 3): {
        "6": "int('3.5') on the TEXT fails: int() can't read text with a decimal point (float first would work).",
        "7": "int(float('3.5')) is 3, and int('3.5') crashes before any addition happens.",
        "6.5": "int() would never give 3.5 - and the second int(s) crashes anyway.",
        "3 3": "print shows ONE value (the sum), and the second int(s) crashes first.",
        "3.53.5": "Both parts are wrapped in int(), so no text joining happens - and int(s) crashes."},
    ("Bonus", 4): {
        "True False False": "and/or return one of the actual VALUES, not just True/False: `0 or 'hi'` -> 'hi'.",
        "hi hi 0": "`a and b` with a = 0 stops at the first falsy value and RETURNS it: 0, not 'hi'.",
        "0 0 hi": "`a or b` returns the first TRUTHY value: 'hi' (0 is falsy).",
        "True 0 False": "or/and return values, not booleans, so the first result is 'hi'.",
        "hi False 0": "`0 and 'hi'` returns the falsy value itself (0), not the boolean False."},
    ("Bonus", 5): {
        "True True True": "10 > x > 6 means 10 > x AND x > 6. With x = 5, 5 > 6 is False.",
        "True False False": "x == 5 == 5.0 is True: 5 equals 5.0 (an int and a float can be equal).",
        "False False True": "1 < x < 10 means 1 < 5 AND 5 < 10: True.",
        "True True False": "10 > x > 6 is False and x == 5 == 5.0 is True - the last two are swapped.",
        "Error": "Chained comparisons like 1 < x < 10 are valid Python."},
    ("Bonus", 9): {
        "[1, 2, 3] [1, 2, 3] abc": "list.sort() sorts IN PLACE and returns None, so result is None. sorted('cab') returns a LIST of letters.",
        "[1, 2, 3] [3, 1, 2] ['a', 'b', 'c']": "result is None (sort() returns nothing) and nums IS changed to [1, 2, 3].",
        "None [3, 1, 2] abc": "nums.sort() changes nums in place, so it is [1, 2, 3] when printed.",
        "None [1, 2, 3] abc": "sorted('cab') gives a LIST ['a', 'b', 'c'], not the string abc.",
        "Error": "sort(), sorted() and printing a list are all valid."},
    ("Bonus", 11): {
        "5 15": "When i == 3, `continue` skips total += i, so 3 is never added: 1+2+4+5 = 12.",
        "4 12": "The loop ends when i reaches 5 (the last i += 1 makes it 5).",
        "5 10": "The sum is 1 + 2 + 4 + 5 = 12 (only 3 is skipped).",
        "3 3": "continue skips only the rest of that one pass; the loop keeps going.",
        "Infinite loop": "i += 1 runs BEFORE the continue, so i always moves forward and the loop ends."},
    ("Bonus", 13): {
        "10 10 None": "dict.get(key, default) returns the STORED value for a key that exists, even if it is 0. The default is only for missing keys.",
        "0 10 Error": "get() never raises an error for a missing key; it returns the default (or None).",
        "0 None None": "stock.get('kiwi', 10) returns the default you gave (10), not None.",
        "None 10 None": "'pear' exists with value 0, so get returns 0, not None.",
        "KeyError": "get() is the safe way to look up a key: it never raises KeyError."},
    ("Bonus", 15): {
        "20 20": "x = 20 inside change() creates a NEW LOCAL x. The global x is still 10.",
        "10 10": "y = change() receives the returned local x, which is 20.",
        "20 10": "The values are swapped: the global x stays 10 and y gets 20.",
        "Error": "Assigning to a name inside a function is allowed (it just makes a local variable).",
        "None 20": "The global x is 10, not None."},
    ("Bonus", 16): {
        "[2]": "The default list is created ONCE when def runs, so add(1) and add(2) share the SAME list, which holds [1, 2].",
        "[1]": "add(2) appends to the same shared list that already contains 1.",
        "[[1], 2]": "append(item) adds the number itself; it doesn't wrap earlier items in a list.",
        "Error": "A list default is legal - just risky.",
        "None": "add() returns bucket, so print shows the list."},
    ("Bonus", 17): {
        "8\n8": "double() prints 8 but returns nothing, so result is None (not 8).",
        "8": "There are TWO prints: one inside double() and one for result (None).",
        "None": "double() prints 8 first, then print(result) shows None.",
        "4\nNone": "double() prints n * 2 = 8, not n.",
        "Error": "A function with no return is fine; it returns None."},
    ("Bonus", 20): {
        "bat": "Strings are IMMUTABLE: s[0] = 'b' raises TypeError, so print never runs.",
        "cat": "The program crashes at s[0] = 'b' before print runs.",
        "b": "Assigning to a character of a string isn't allowed (TypeError).",
        "bcat": "Strings can't be changed in place at all - it crashes.",
        "Nothing": "It does something: it crashes with a TypeError."},
    ("Bonus", 24): {
        "Yes: ": "Pressing Enter gives '' (an EMPTY string), which is falsy, so the else runs.",
        "Empty: NoneType": "input() returns an empty STRING '', never None, so the type is str.",
        "Empty: bool": "The value is '' (a str). Being falsy doesn't change its type.",
        "Yes: None": "input() never returns None, and an empty string is falsy so the if fails.",
        "Error": "Empty input is fine: input() returns ''."},
}


# --- concept tags: which skills does a question practice? ------------------------------------------------
CONCEPTS = {
    "types": "Types: int / float / str",
    "logic": "Logic: and / or / not / truthiness",
    "mod": "% and // (remainder, division)",
    "fmt": "Printing & formatting",
    "strings": "Strings: slicing & methods",
    "lists": "Lists & dictionaries",
    "flow": "if / loops / break / continue",
    "funcs": "Functions & scope",
    "imports": "Imports & modules",
}
CONCEPT_SHORT = {"types": "Types (int / float / str)", "logic": "Logic (and / or / not)", "mod": "% and // math",
                 "fmt": "Printing & formatting", "strings": "Strings", "lists": "Lists & dicts",
                 "flow": "if / loops", "funcs": "Functions & scope", "imports": "Imports"}
CONCEPT_TAB = {"types": "types", "logic": "logic", "mod": "ops", "fmt": "fmt", "strings": "seq", "lists": "seq"}


def concept_tags(q):
    tags = set()
    src = q["code"] or ""
    text = (q["prompt"] + " " + " ".join(q["choices"])).lower()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        tree = None
    if tree is not None:
        for n in ast.walk(tree):
            if isinstance(n, ast.BinOp):
                if isinstance(n.op, ast.Mod):
                    tags.add("fmt" if isinstance(n.left, ast.Constant) and isinstance(n.left.value, str) else "mod")
                elif isinstance(n.op, ast.FloorDiv):
                    tags.add("mod")
            elif isinstance(n, ast.BoolOp):
                tags.add("logic")
            elif isinstance(n, ast.Compare) and len(n.ops) > 1:
                tags.add("logic")
            elif isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.Not):
                tags.add("logic")
            elif isinstance(n, ast.If):
                tags.add("flow")
                if isinstance(n.test, (ast.Name, ast.UnaryOp, ast.BoolOp)) or (
                        isinstance(n.test, ast.Compare) and any(isinstance(o, (ast.Is, ast.IsNot)) for o in n.test.ops)):
                    tags.add("logic")
            elif isinstance(n, (ast.For, ast.While, ast.Break, ast.Continue, ast.Pass)):
                tags.add("flow")
            elif isinstance(n, (ast.FunctionDef, ast.Return)):
                tags.add("funcs")
            elif isinstance(n, ast.JoinedStr):
                tags.add("fmt")
            elif isinstance(n, (ast.Import, ast.ImportFrom)):
                tags.add("imports")
            elif isinstance(n, ast.Call):
                f = n.func
                if isinstance(f, ast.Name) and f.id in ("int", "float", "str", "input", "isinstance", "type"):
                    tags.add("types")
                elif isinstance(f, ast.Name) and f.id == "range":
                    tags.add("flow")
                elif isinstance(f, ast.Attribute):
                    if f.attr in ("lower", "upper", "strip", "split", "join", "replace"):
                        tags.add("strings")
                    elif f.attr in ("append", "insert", "remove", "pop", "sort", "get"):
                        tags.add("lists")
                    elif f.attr == "format":
                        tags.add("fmt")
            elif isinstance(n, ast.Subscript):
                sl = n.slice
                if isinstance(sl, ast.Slice):
                    tags.add("strings")
                else:
                    tags.add("lists")
            elif isinstance(n, (ast.List, ast.Dict)):
                tags.add("lists")
            elif isinstance(n, ast.Constant) and isinstance(n.value, str) and ("\n" in n.value or "\\" in n.value):
                tags.add("fmt")
    if any(w in text for w in ("immutable", "slicing", "s[1:4]")):
        tags.add("strings")
    if "mutable" in text and "immutable" not in text:
        tags.add("lists")
    if "comment" in text or src.lstrip().startswith("#"):
        tags.add("fmt")
    if "int(" in text or "float" in text or " str" in text or "string" in text and "input" in text:
        tags.add("types")
    if "falsy" in text or "truthy" in text or "none" in text and "is none" in text:
        tags.add("logic")
    return [k for k in CONCEPTS if k in tags]


for _q in QUIZ1 + QUIZ2 + BONUS:
    _q["tags"] = concept_tags(_q)
ALL_QUESTIONS = QUIZ1 + QUIZ2 + BONUS


# --- cheat sheets: every "result" in the live tables is computed by Python itself ------------------------
def eval_expr(expr):
    """Evaluate ONE expression the way the study tool runs code.  -> (repr_text, type_name, error_text)"""
    expr = expr.strip()
    if not expr:
        return ("", "", "")
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        return ("", "", f"SyntaxError: {e.msg}")
    def has_seq(node):
        return any(isinstance(m, (ast.List, ast.Tuple, ast.JoinedStr)) or
                   (isinstance(m, ast.Constant) and isinstance(m.value, (str, bytes)))
                   or (isinstance(m, ast.Call) and isinstance(m.func, ast.Name) and m.func.id in ("str", "list", "range"))
                   for m in ast.walk(node))
    repeats = 0
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool) \
                and abs(n.value) >= 10 ** 7:
            return ("", "", "numbers that big aren't allowed here")
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mult) and (has_seq(n.left) or has_seq(n.right)):
            repeats += 1
            other = n.right if has_seq(n.left) else n.left
            if not (isinstance(other, ast.Constant) and isinstance(other.value, int) and 0 <= other.value <= 10000):
                return ("", "", "text/list repeats must use a plain number up to 10,000")
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Pow):
            if any(isinstance(m, ast.BinOp) and isinstance(m.op, ast.Pow) for m in ast.walk(n) if m is not n):
                return ("", "", "stacked ** isn't allowed here (it can freeze the computer)")
            if isinstance(n.right, ast.Constant) and isinstance(n.right.value, (int, float)) and abs(n.right.value) > 100:
                return ("", "", "exponents over 100 aren't allowed here")
    if repeats > 1:
        return ("", "", "only one text/list repeat per expression, please")
    events, out, err, _ = trace_run(f"_v = ({expr})")
    if err:
        return ("", "", err.split("\n")[0])
    snap = events[-1]["vars"].get("_v") if events else None
    if not snap:
        return ("", "", "no value")
    return (snap[0], snap[1], "")


CHEAT_TABS = [
    {"key": "types", "title": "int / float / str", "blocks": [
        {"kind": "static", "heading": "The types you mix up", "cols": ["Type", "What it is", "Looks like", "type() says"],
         "widths": [9, 42, 22],
         "rows": [("int", "a whole number (no decimal point)", "7   -3   0", "int"),
                  ("float", "a number WITH a decimal point", "7.0   3.14   -0.5", "float"),
                  ("str", "text: anything in quotes, even digits", "'7'   \"hi\"   ''", "str"),
                  ("bool", "True or False", "True   False", "bool"),
                  ("input()", "ALWAYS returns a str (even if you type digits)", "'7.5'", "str")]},
        {"kind": "live", "heading": "Converting between types", "rows": [
            ("int('7')", "text of a whole number -> int"),
            ("int('7.5')", "ValueError: int() can't read text with a decimal point"),
            ("int(float('7.5'))", "go through float first, then cut the decimals"),
            ("int(7.5)", "int() CUTS OFF decimals, it doesn't round"),
            ("int(-7.5)", "cuts toward zero (not down)"),
            ("float('7')", "text -> float, so it gets a .0"),
            ("float(7)", "int -> float"),
            ("float('abc')", "ValueError: not a number"),
            ("str(7)", "number -> text"),
            ("str(7.0)", "keeps the .0"),
            ("str(75.00)", "str() drops trailing zeros (75.0, not 75.00)"),
            ("int(' 7 ')", "spaces around the digits are OK"),
            ("int('abc')", "ValueError: not a number")]},
        {"kind": "live", "heading": "Mixing types with operators", "rows": [
            ("7 + 7", "int + int adds"),
            ("'7' + '7'", "str + str JOINS text (no math)"),
            ("'7' * 3", "str * int REPEATS text"),
            ("'7' + 7", "TypeError: can't add str and int"),
            ("'Score: ' + 90", "TypeError: use f\"Score: {90}\" or str(90)"),
            ("7 / 2", "/ always gives a float"),
            ("6 / 3", "still a float: 2.0"),
            ("7 // 2", "// floors to a whole number"),
            ("7.0 // 2", "float // int gives a float"),
            ("5 + 2.0", "int + float gives a float"),
            ("2 ** 3", "** is exponent"),
            ("'5' == 5", "text never equals a number"),
            ("5 == 5.0", "int and float CAN be equal")]},
        {"kind": "static", "heading": "Which one do I need?", "cols": ["I have...", "I want...", "Use"],
         "widths": [34, 34],
         "rows": [("text of digits (from input())", "a whole number", "int(text)"),
                  ("text with a decimal point", "a decimal number", "float(text)"),
                  ("a number", "text to join with +", "str(n)  or an f-string"),
                  ("text and a number to print", "one line of output", "print(f\"Score: {n}\")")]}]},
    {"key": "logic", "title": "True / False logic", "blocks": [
        {"kind": "live", "heading": "FALSY values (count as False)", "rows": [
            ("bool(0)", "zero is falsy"), ("bool(0.0)", "float zero too"), ("bool('')", "the empty string"),
            ("bool([])", "empty list"), ("bool({})", "empty dict"), ("bool(None)", "None"), ("bool(False)", "False")]},
        {"kind": "live", "heading": "TRUTHY values (count as True) - the tricky ones", "rows": [
            ("bool(1)", "any non-zero number"), ("bool(-1)", "negative counts too"),
            ("bool(0.5)", "any non-zero float"), ("bool('0')", "text '0' is NOT empty -> truthy!"),
            ("bool('False')", "any non-empty text is truthy"), ("bool(' ')", "a space is not empty"),
            ("bool([0])", "a list with an item is truthy"), ("bool('a')", "non-empty text")]},
        {"kind": "live", "heading": "and / or / not return VALUES (not just True / False)", "rows": [
            ("0 or 5", "or -> the first TRUTHY value"), ("5 or 0", "5 is truthy, so it stops there"),
            ("0 or 0", "none truthy -> returns the LAST value"), ("5 or 7", "first truthy: 5"),
            ("0 and 5", "and -> the first FALSY value"), ("5 and 0", "5 truthy, keep going -> last value 0"),
            ("5 and 7", "none falsy -> returns the LAST value"), ("'' or 'hi'", "'' is falsy"),
            ("'hi' and 0", "'hi' truthy -> returns 0"), ("None or 0", "both falsy -> last one"),
            ("not 0", "not ALWAYS returns True or False"), ("not 5", "5 is truthy -> not 5 is False"),
            ("not ''", "empty text is falsy -> True"), ("0 == False", "0 equals False"),
            ("0 is False", "equal is not the same object"), ("(0 or 5) and not (0 and 5)", "5 and True -> True")]},
        {"kind": "static", "heading": "Rules to memorize", "cols": ["Expression", "What Python does"], "widths": [14],
         "rows": [("a or b", "returns a if a is truthy, otherwise b"),
                  ("a and b", "returns a if a is FALSY, otherwise b"),
                  ("not a", "always gives True or False (flips the truthiness)"),
                  ("order", "not first, then and, then or  (use parentheses!)"),
                  ("short-circuit", "or stops at the first truthy, and stops at the first falsy; the rest never runs")]},
        {"kind": "static", "heading": "Truth table", "cols": ["A", "B", "A and B", "A or B", "not A"],
         "widths": [8, 8, 11, 10],
         "rows": [("True", "True", "True", "True", "False"), ("True", "False", "False", "True", "False"),
                  ("False", "True", "False", "True", "True"), ("False", "False", "False", "False", "True")]},
        {"kind": "live", "heading": "Comparisons always give True / False", "rows": [
            ("1 < 5 < 10", "chained: 1 < 5 AND 5 < 10"), ("10 > 5 > 6", "10 > 5 AND 5 > 6 -> False"),
            ("'Bob' == 'bob'", "capital letters matter"), ("None == 0", "None is not zero"),
            ("None is None", "use `is` to test for None"), ("3 != 3.0", "3 and 3.0 are equal")]}]},
    {"key": "ops", "title": "% and // math", "blocks": [
        {"kind": "live", "heading": "% is the REMAINDER  (a = b x quotient + remainder)", "rows": [
            ("7 % 3", "7 = 3 x 2 + 1"), ("6 % 3", "remainder 0 -> divides evenly"),
            ("3 % 7", "smaller % bigger = the smaller number itself"), ("0 % 5", "zero"),
            ("10 % 10", "always 0 when equal"), ("-7 % 3", "result takes the sign of the RIGHT number"),
            ("7 % -3", "negative right side -> negative result"), ("7.5 % 2", "works with floats too"),
            ("8 % 2 == 0", "even number test: True"), ("7 % 2 == 0", "odd number: False"),
            ("7 % 2", "odd numbers leave remainder 1")]},
        {"kind": "live", "heading": "// is FLOOR division (rounds DOWN)", "rows": [
            ("7 // 2", "3.5 rounded down"), ("-7 // 2", "-3.5 rounded DOWN toward negative infinity: -4"),
            ("7.0 // 2", "float in, float out"), ("7 / 2", "/ is true division (a float)"),
            ("6 / 3", "/ is always a float"), ("divmod(7, 2)", "(quotient, remainder) together")]},
        {"kind": "live", "heading": "Order of operations", "rows": [
            ("5 + 3 * 2", "multiply first"), ("(5 + 3) * 2", "parentheses first"),
            ("2 ** 3", "exponent before * and +"), ("-2 ** 2", "** before the minus sign"),
            ("10 - 2 - 3", "left to right"), ("2 + 3 > 4 and 1", "math, then comparison, then and")]},
        {"kind": "static", "heading": "Handy patterns", "cols": ["Test", "Meaning"], "widths": [16],
         "rows": [("n % 2 == 0", "n is even"), ("n % 2 == 1", "n is odd"), ("n % k == 0", "n is divisible by k"),
                  ("n % 10", "the last digit of n"), ("n // 10", "n without its last digit")]}]},
    {"key": "fmt", "title": "Printing & formatting", "blocks": [
        {"kind": "live", "heading": "f-strings and format specs", "rows": [
            ("f'{3.14159:.2f}'", ".2f = 2 decimals"), ("f'{7:>5}'", ">5 = right-align in 5 characters"),
            ("f'{7:05}'", "05 = pad with zeros to width 5"), ("f'{1234567:,}'", ", = thousands separators"),
            ("f'{3+4=}'", "= prints the expression AND its value")]},
        {"kind": "live", "heading": "% formatting", "rows": [
            ("'%d' % 3.7", "%d = integer (cuts decimals)"), ("'%s' % 3.7", "%s = any value as text"),
            ("'%f' % 2.5", "%f = float, 6 decimals by default"), ("'%.2f' % 2.5", "%.2f = 2 decimals"),
            ("'%5.1f' % 3.14159", "width 5, 1 decimal, right-aligned"), ("'%-4d' % 42", "- = left-align"),
            ("'%x' % 255", "%x = lowercase hex, no 0x"), ("'%06.2f' % 95.678", "width 6, zero-padded")]},
        {"kind": "live", "heading": "Escapes (the REPR shows what is really inside)", "rows": [
            ("'Line1\\nLine2'", "\\n is ONE newline character"), ("'a\\tb'", "\\t is a tab"),
            ("'C:\\\\temp'", "\\\\ is ONE backslash"), ("'say \"hi\"'", "quotes inside the other kind of quotes"),
            ("'\\\\n'", "backslash + n: two characters, NOT a newline")]}]},
    {"key": "seq", "title": "Strings & lists", "blocks": [
        {"kind": "live", "heading": "Slicing  [start:stop:step]  (stop is NOT included)", "rows": [
            ("'abcdef'[1:4]", "indexes 1, 2, 3"), ("'abcdef'[:3]", "first 3"), ("'abcdef'[-2:]", "last 2"),
            ("'abcdef'[::-1]", "reversed"), ("'abcdef'[::2]", "every 2nd"), ("'abcdef'[0]", "first character"),
            ("len('abcdef')", "length"), ("'hi'[1:4]", "slices never crash; you just get less")]},
        {"kind": "live", "heading": "String methods RETURN a new string", "rows": [
            ("'Hello'.lower()", "all lowercase"), ("' hi '.strip()", "removes outer spaces"),
            ("'a,b'.split(',')", "text -> list"), ("'-'.join(['a', 'b'])", "list -> text"),
            ("'hello'.replace('l', 'L')", "replaces EVERY match"), ("'a' in 'cat'", "membership test")]},
        {"kind": "live", "heading": "Lists and dictionaries", "rows": [
            ("[3, 1, 2].sort()", "sort() sorts IN PLACE and returns None"), ("sorted([3, 1, 2])", "sorted() returns a NEW list"),
            ("sorted('cab')", "a list of characters"), ("list('abc')", "text -> list of letters"),
            ("[1, 2, 3][-1]", "last item"), ("[0] * 3", "repeat a list"), ("{'a': 1}.get('b')", "missing key -> None"),
            ("{'a': 1}.get('b', 9)", "missing key -> your default"), ("'x' in {'x': 1}", "in checks the KEYS")]},
        {"kind": "static", "heading": "Mutable vs immutable", "cols": ["Type", "Can change in place?"], "widths": [14],
         "rows": [("str", "NO: s[0] = 'b' is a TypeError (build a new string)"), ("int / float / tuple", "NO"),
                  ("list / dict", "YES: a.append(1) changes the list for EVERY name pointing to it"),
                  ("b = a", "b is another NAME for the same list"), ("b = a[:]", "b is a COPY")]}]},
]


def print_vars(snap, heading):
    print(BOLD(heading))
    if not snap:
        print("   " + DIM("(none)"))
    width = max((len(k) for k in snap), default=0)
    for k, (r, t) in snap.items():
        print(f"   {k:<{width}} = {r}   {DIM('(' + t + ')')}")


def print_step(src, steps, k):
    s = steps[k]
    place = "" if s["func"] == "<module>" else MAGENTA(f"   [inside {s['func']}()]")
    print("\n" + BOLD(BLUE(f"=== Step {k + 1} of {len(steps)} ===")) + place)
    show_code(src, s["line"])
    print("\n" + BOLD(">> ") + s["title"])
    c = s["cond"]
    if c:
        print(f"   Condition: {BOLD(c['expr'])}")
        for seg, val in c["parts"]:
            if val is None:
                print(f"      {seg}  ->  {DIM('skipped (short-circuit: answer already known)')}")
            else:
                print(f"      {seg}  ->  {val}")
        verdict = GREEN("True -> the indented block RUNS") if c["truth"] else RED("False -> the block is SKIPPED")
        shown = c["value"]
        note = "" if shown in ("True", "False") else DIM(f"  ({shown} counts as {c['truth']})")
        print(f"   Whole condition = {shown}{note}  ->  {verdict}")
    if s.get("evals"):
        print("   Worked out (inside first, using the values from before this line):")
        for seg, val, is_err, note in s["evals"]:
            print(f"      {seg}  ->  {RED(val) if is_err else val}")
            if note:
                print(DIM(f"          ({note})"))
    if s["changes"]:
        print("   Changed:")
        for ch in s["changes"]:
            print("      " + ch)
    if s["out"]:
        print("   Printed:")
        show_output(s["out"], indent="      ")
    print()
    heading = "Variables now:" if s["func"] == "<module>" else f"Local variables in {s['func']}():"
    print_vars(s["vars"], heading)
    if s.get("globals") is not None:
        print_vars(s["globals"], "Global (main program) variables:")


def walk_through(src, inputs, intro=None):
    """Interactive step-by-step view of some code."""
    events, output, error, note = trace_run(src, inputs)
    steps = build_steps(events, output, error, src)
    if intro:
        print(intro)
    if note:
        print(DIM(note))
    if not steps:
        print("\nThere are no steps: no line of this code actually runs" +
              (" (it's all comments)." if not error else "."))
    else:
        print(DIM("\nControls: [Enter] next step   b = back   a = show all remaining   q = stop"))
        k = 0
        while k < len(steps):
            print_step(src, steps, k)
            cmd = ask(DIM("\n[Enter]/b/a/q > ")).strip().lower()
            if cmd == "q":
                break
            if cmd == "b":
                k = max(0, k - 1)
            elif cmd == "a":
                for j in range(k + 1, len(steps)):
                    print_step(src, steps, j)
                break
            else:
                k += 1
    print("\n" + BOLD("=== Finished ==="))
    print(BOLD("Full output:"))
    show_output(output)
    if error:
        print(RED(f"   Program crashed with  {error}"))


# ===========================================================================
# Dev mode for one question
# ===========================================================================
def dev_question(q):
    print("\n" + "=" * 70)
    print(BOLD(f"DEV MODE - {label(q)}: ") + q["prompt"])
    if q["demo"]:
        print(DIM("(This is a concept question, so the code below is a demo that shows the idea.)"))
    print()
    show_code(q["code"])
    inputs = list(q["inputs"])
    uses_input = "input(" in q["code"]
    while True:
        if uses_input:
            shown = ", ".join(repr(v) for v in inputs) if inputs else "nothing"
            typed = ask(f"\nThis code calls input(). The quiz's value is {shown}.\n"
                        f"Press Enter to use it, or type your own (separate several with commas): ")
            if typed.strip():
                inputs = [v.strip() for v in typed.split(",")]
        walk_through(q["code"], inputs)
        print("\n" + BOLD("Correct answer: ") + GREEN(" / ".join(a.replace("\n", " | ") for a in q["answer"])))
        print(BOLD("Why: ") + q["why"])
        again = ask(DIM("\n[Enter] continue" + ("   r = run again with different input" if uses_input else "")
                        + " > ")).strip().lower()
        if again == "r" and uses_input:
            inputs = list(q["inputs"])
            continue
        break


# ===========================================================================
# Quiz mode
# ===========================================================================
LETTERS = "ABCDEFGH"


def fmt_choice(text, indent=6):
    return text.replace("\n", "\n" + " " * indent)


def yes(prompt, default=True):
    a = ask(prompt + (" [Y/n] " if default else " [y/N] ")).strip().lower()
    return default if not a else a.startswith("y")


def run_quiz(pool, title):
    if not pool:
        return
    shuffle_q = yes("Shuffle the question order?")
    shuffle_c = yes("Shuffle the answer letters too (so you can't memorize 'it was C')?")
    order = pool[:]
    if shuffle_q:
        random.shuffle(order)

    score, answered, missed = 0, 0, []
    for idx, q in enumerate(order, 1):
        choices = q["choices"][:]
        if shuffle_c:
            random.shuffle(choices)
        print("\n" + "=" * 70)
        print(BOLD(f"[{idx}/{len(order)}]  {title}  -  {label(q)}"))
        print(BOLD(q["prompt"]))
        if q["code"] and not q["demo"]:
            print()
            show_code(q["code"])
        if q["inputs"] and not q["demo"]:
            print(DIM("   (the user types: " + ", ".join(repr(v) for v in q["inputs"]) + ")"))
        print()
        for letter, ch in zip(LETTERS, choices):
            print(f"  {letter}) {fmt_choice(ch)}")
        correct_letters = [LETTERS[i] for i, ch in enumerate(choices) if ch in q["answer"]]

        while True:
            guess = ask("\nYour answer (letter, Enter = skip, q = quit): ").strip().upper()
            if guess in ("", "Q") or (len(guess) == 1 and guess in LETTERS[:len(choices)]):
                break
            print("Type one of: " + ", ".join(LETTERS[:len(choices)]))
        if guess == "Q":
            break
        if guess:
            answered += 1
            if guess in correct_letters:
                score += 1
                print(GREEN("Correct!"))
            else:
                missed.append(q)
                print(RED(f"Not quite. The answer is {'/'.join(correct_letters)}."))
        else:
            missed.append(q)
            print(f"Answer: {'/'.join(correct_letters)}")

        if q["code"]:
            events, output, error, note = trace_run(q["code"], q["inputs"])
            print(BOLD("\nWhen you actually run " + ("the demo code" if q["demo"] else "it") + ":"))
            if q["demo"]:
                show_code(q["code"])
                print()
            show_output(output)
            if error:
                print(RED(f"   -> crashes with {error}"))
        print(BOLD("\nWhy: ") + q["why"])
        if guess and guess not in correct_letters and q["code"]:
            why_not = diagnose(q, choices[LETTERS.index(guess)], build_steps(events, output, error, q["code"]),
                               output, error)
            if why_not:
                print(BOLD(f"Why {guess} isn't right: ") + why_not)

        cmd = ask(DIM("\n[Enter] next   d = step through it in DEV MODE   q = quit > ")).strip().lower()
        if cmd == "d":
            dev_question(q)
        elif cmd == "q":
            break

    print("\n" + "=" * 70)
    if answered:
        pct = round(100 * score / answered)
        print(BOLD(f"Score: {score} / {answered} answered  ({pct}%)"))
    if missed:
        print("Missed or skipped: " + ", ".join(label(q) for q in missed))
        if yes("Step through the ones you missed in dev mode now?", default=False):
            for q in missed:
                dev_question(q)
                if not yes("Next missed question?"):
                    break


def pick_bonus(n_max=len(BONUS)):
    a = ask(f"Mix in how many bonus questions? (0-{n_max}, Enter = 0): ").strip()
    try:
        n = max(0, min(n_max, int(a)))
    except ValueError:
        n = 0
    return random.sample(BONUS, n)


# ===========================================================================
# Menus
# ===========================================================================
def dev_menu():
    print("\nDEV MODE - which set?")
    for k, (name, qs) in ALL_SETS.items():
        print(f"  {k}) {name} ({len(qs)})")
    s = ask("> ").strip()
    if s not in ALL_SETS:
        return
    name, qs = ALL_SETS[s]
    while True:
        print(f"\n{BOLD(name)}")
        for q in qs:
            first = q["prompt"].split("\n")[0][:48]
            snippet = q["code"].split("\n")[0][:30] if q["code"] and not q["demo"] else "(concept)"
            print(f"  {q['num']:>2}) {first:<50} {DIM(snippet)}")
        pick = ask("\nQuestion number (q = back): ").strip().lower()
        if pick == "q" or not pick:
            return
        try:
            i = int(pick)
            q = next(x for x in qs if x["num"] == i)
        except (ValueError, StopIteration):
            continue
        while True:
            dev_question(q)
            nxt = ask(DIM("n = next question   l = back to list > ")).strip().lower()
            if nxt == "n":
                later = [x for x in qs if x["num"] > q["num"]]
                if not later:
                    break
                q = later[0]
            else:
                break


def playground():
    print("\nPLAYGROUND - paste or type any Python code.")
    print("Finish with a line that says just  END")
    lines = []
    while True:
        line = ask()
        if line.strip() == "END":
            break
        lines.append(line)
    src = "\n".join(lines).strip("\n")
    if not src:
        return
    inputs = []
    if "input(" in src:
        typed = ask("Your code uses input(). What should the user type? (separate several with commas): ")
        inputs = [v.strip() for v in typed.split(",")] if typed else []
    walk_through(src, inputs)
    ask(DIM("\n[Enter] back to menu > "))


def main():
    random.seed()
    while True:
        print("\n" + "=" * 70)
        print(BOLD("   IS 4485  -  PYTHON MIDTERM STUDY TOOL"))
        print("=" * 70)
        print(f"  1) Practice Exam 1        ({len(QUIZ1)} questions)")
        print(f"  2) Practice Exam 2        ({len(QUIZ2)} questions)")
        print(f"  3) Bonus questions        ({len(BONUS)} harder ones)")
        print(f"  4) SUPER TEST             (everything mixed)")
        print(f"  5) DEV MODE               step through any question line by line")
        print(f"  6) PLAYGROUND             step through your own code")
        print(f"  q) Quit")
        c = ask("> ").strip().lower()
        if c == "1":
            run_quiz(QUIZ1 + pick_bonus(), "Exam 1")
        elif c == "2":
            run_quiz(QUIZ2 + pick_bonus(), "Exam 2")
        elif c == "3":
            run_quiz(BONUS, "Bonus")
        elif c == "4":
            pool = QUIZ1 + QUIZ2 + (BONUS if yes("Include the 25 bonus questions?") else [])
            a = ask(f"How many questions? (Enter = all {len(pool)}): ").strip()
            random.shuffle(pool)
            if a.isdigit() and 0 < int(a) < len(pool):
                pool = pool[:int(a)]
            run_quiz(pool, "SUPER TEST")
        elif c == "5":
            dev_menu()
        elif c == "6":
            playground()
        elif c == "q":
            print("Good luck on the midterm!")
            return


# ===========================================================================
# GUI (tkinter ships with Python; if it is missing the terminal version is used)
# ===========================================================================
try:
    import tkinter as tk
    from tkinter import font as tkfont
    from tkinter import messagebox, ttk
    HAVE_TK = True
except Exception:  # ImportError, or a broken Tcl install
    HAVE_TK = False

if HAVE_TK:
    t = sys.modules[__name__]  # the GUI code below refers to the engine as `t`
    # palette
    # Every value inside one palette must be unique: switching themes remaps old colors to new ones.
    LIGHT = dict(
        BG="#f4f5f7", CARD="#ffffff", LINE="#d0d5dd", TEXT="#101828", MUTED="#667085", HEAD="#1e3a8a",
        ACCENT="#2563eb", ACCENT_DK="#1d4ed8", GOOD="#15803d", GOOD_BG="#dcfce7", BAD="#b91c1c",
        BAD_BG="#fee2e2", SEL_BG="#dbeafe", CUR_BG="#fff3b0", CHG_BG="#e6f4ea",
        # code colors (modelled on the Colab / Jupyter look of the practice exam)
        SYN_KW="#008000", SYN_KWOP="#aa22ff", SYN_BUILTIN="#2e8b2e", SYN_STR="#ba2121",
        SYN_NUM="#2255dd", SYN_COMMENT="#408080", SYN_DEF="#0000ff",
        B1="#2f6fed", B2="#0d9488", B3="#ea7a12", B4="#7c3aed", B5="#16a34a", B6="#db2777",
    )
    DARK = dict(
        BG="#0d1117", CARD="#161b22", LINE="#30363d", TEXT="#e6edf3", MUTED="#8b949e", HEAD="#79b8ff",
        ACCENT="#388bfd", ACCENT_DK="#1f6feb", GOOD="#3fb950", GOOD_BG="#14301f", BAD="#f85149",
        BAD_BG="#3d1418", SEL_BG="#1c3358", CUR_BG="#4a4210", CHG_BG="#173824",
        SYN_KW="#7ee787", SYN_KWOP="#d2a8ff", SYN_BUILTIN="#56d364", SYN_STR="#ffa198",
        SYN_NUM="#79c0ff", SYN_COMMENT="#7d8590", SYN_DEF="#a5d6ff",
        B1="#2d6cdf", B2="#14a39a", B3="#d9730d", B4="#8957e5", B5="#2ea043", B6="#d12f7d",
    )
    PALETTES = {"light": LIGHT, "dark": DARK}
    CURRENT = {"name": "light"}


    def apply_palette(name):
        CURRENT["name"] = name
        globals().update(PALETTES[name])  # BG, CARD, TEXT, ... become module-level names


    def system_theme():
        """'dark' if Windows is set to dark app mode, else 'light'."""
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as k:
                return "light" if winreg.QueryValueEx(k, "AppsUseLightTheme")[0] else "dark"
        except Exception:
            return "light"


    apply_palette("light")

    F = {}  # shared fonts (resizing them resizes the whole app)


    def make_fonts(root):
        F["ui"] = tkfont.Font(root=root, family="Segoe UI", size=11)
        F["bold"] = tkfont.Font(root=root, family="Segoe UI", size=11, weight="bold")
        F["h1"] = tkfont.Font(root=root, family="Segoe UI", size=20, weight="bold")
        F["h2"] = tkfont.Font(root=root, family="Segoe UI", size=13, weight="bold")
        F["code"] = tkfont.Font(root=root, family="Consolas", size=12)
        F["codeb"] = tkfont.Font(root=root, family="Consolas", size=12, weight="bold")
        F["codei"] = tkfont.Font(root=root, family="Consolas", size=12, slant="italic")




    def shade(color, factor):
        h = color.lstrip("#")
        rgb = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
        return "#%02x%02x%02x" % tuple(max(0, min(255, int(c * factor))) for c in rgb)


    APP = {"root": None, "listeners": []}


    def row_height():
        return F["ui"].metrics("linespace") + 10


    def scale_trees(widget, ratio):
        """Keep table columns proportional when the text size changes."""
        if isinstance(widget, ttk.Treeview):
            for col in widget["columns"]:
                c = widget.column(col)
                widget.column(col, width=int(c["width"] * ratio), minwidth=int(c["minwidth"] * ratio))
        for child in widget.winfo_children():
            scale_trees(child, ratio)


    def resize_fonts(delta):
        old = abs(F["ui"].cget("size"))
        for f in F.values():
            f.configure(size=max(8, min(26, abs(f.cget("size")) + delta)))
        new = abs(F["ui"].cget("size"))
        root = APP["root"]
        if root is not None and new != old:
            ttk.Style(root).configure("Treeview", rowheight=row_height())  # taller rows for bigger text
            scale_trees(root, new / old)
        for fn in list(APP["listeners"]):
            fn()


    def make_tile(parent, title, subtitle, color_key, command):
        """A big colored button whose text WRAPS instead of being cut off at large text sizes."""
        col = globals()[color_key]
        tile = tk.Frame(parent, bg=col, cursor="hand2", padx=16, pady=12)
        top = tk.Label(tile, text=title, font=F["h2"], bg=col, fg="#fefefe", anchor="w", justify="left")
        sub = tk.Label(tile, text=subtitle, font=F["bold"], bg=col, fg="#fefefe", anchor="w", justify="left")
        top.pack(fill="x")
        sub.pack(fill="x")
        parts = (tile, top, sub)

        def paint(factor):
            c = globals()[color_key]
            c = c if factor == 1 else shade(c, factor)
            for w in parts:
                w.configure(bg=c)
        hover = lambda: 0.88 if CURRENT["name"] == "light" else 1.2  # noqa: E731
        for w in parts:
            w.bind("<Button-1>", lambda e: command())
            w.bind("<Enter>", lambda e: paint(hover()))
            w.bind("<Leave>", lambda e: paint(1))
        tile.bind("<Configure>", lambda e: (top.configure(wraplength=max(120, e.width - 40)),
                                            sub.configure(wraplength=max(120, e.width - 40))))
        return tile



    def style_app(root):
        st = ttk.Style(root)
        st.theme_use("clam")
        root.configure(bg=BG)
        hover = 0.86 if CURRENT["name"] == "light" else 1.18
        st.configure(".", background=BG, foreground=TEXT, font=F["ui"], bordercolor=LINE,
                     lightcolor=BG, darkcolor=BG, troughcolor=LINE, focuscolor=BG)
        st.configure("TFrame", background=BG)
        st.configure("Card.TFrame", background=CARD)
        st.configure("TLabel", background=BG, foreground=TEXT, font=F["ui"])
        st.configure("TButton", background=CARD, foreground=TEXT, font=F["ui"], padding=(12, 6),
                     bordercolor=LINE, lightcolor=CARD, darkcolor=CARD)
        st.map("TButton", background=[("active", SEL_BG), ("disabled", BG)],
               foreground=[("disabled", MUTED)])
        st.configure("Accent.TButton", background=ACCENT, foreground="#ffffff", font=F["bold"],
                     padding=(14, 8), bordercolor=ACCENT_DK, lightcolor=ACCENT, darkcolor=ACCENT)
        st.map("Accent.TButton", background=[("active", ACCENT_DK), ("disabled", MUTED)],
               foreground=[("disabled", "#ffffff")])
        for i in range(1, 7):
            col = globals()[f"B{i}"]
            st.configure(f"Big{i}.TButton", background=col, foreground="#ffffff", font=F["h2"],
                         padding=(18, 16), bordercolor=col, lightcolor=col, darkcolor=col)
            st.map(f"Big{i}.TButton", background=[("active", shade(col, hover))])
        st.configure("Treeview", font=F["ui"], rowheight=row_height(), background=CARD, fieldbackground=CARD,
                     foreground=TEXT, bordercolor=LINE)
        st.map("Treeview", background=[("selected", ACCENT)], foreground=[("selected", "#ffffff")])
        st.configure("Treeview.Heading", font=F["bold"], background=LINE, foreground=TEXT, relief="flat")
        st.map("Treeview.Heading", background=[("active", SEL_BG)])
        st.configure("TLabelframe", background=BG, bordercolor=LINE)
        st.configure("TLabelframe.Label", background=BG, font=F["bold"], foreground=MUTED)
        for name in ("TEntry", "TSpinbox"):
            st.configure(name, fieldbackground=CARD, foreground=TEXT, insertcolor=TEXT,
                         bordercolor=LINE, arrowcolor=TEXT, background=CARD)
        st.configure("TCheckbutton", background=BG, foreground=TEXT, indicatorbackground=CARD,
                     indicatorforeground=TEXT)
        st.map("TCheckbutton", background=[("active", BG)],
               indicatorbackground=[("selected", ACCENT), ("!selected", CARD)])
        st.configure("TScrollbar", background=LINE, troughcolor=BG, bordercolor=BG, arrowcolor=TEXT)
        st.map("TScrollbar", background=[("active", MUTED)])
        st.configure("TScale", background=ACCENT, troughcolor=LINE)
        st.configure("TSeparator", background=LINE)
        st.configure("TPanedwindow", background=BG)
        st.configure("Sash", background=LINE)
        st.configure("TNotebook", background=BG, bordercolor=LINE)
        st.configure("TNotebook.Tab", background=BG, foreground=MUTED, padding=(14, 6), font=F["bold"])
        st.map("TNotebook.Tab", background=[("selected", CARD)], foreground=[("selected", TEXT)])


    # --- coloring code (tokenize-based, so it matches Python's own idea of a keyword/string) ---
    BUILTIN_NAMES = {n for n in dir(builtins) if n[0].islower() and not keyword.iskeyword(n)}
    WORD_OPS = {"and", "or", "not", "in", "is"}
    STRING_TOKENS = {"STRING", "FSTRING_START", "FSTRING_MIDDLE", "FSTRING_END"}
    SYNTAX_TAGS = ("kw", "kwop", "builtin", "string", "number", "comment", "defname", "gutter")


    def code_tags(txt):
        txt.tag_configure("kw", foreground=SYN_KW, font=F["codeb"])
        txt.tag_configure("kwop", foreground=SYN_KWOP, font=F["codeb"])
        txt.tag_configure("builtin", foreground=SYN_BUILTIN)
        txt.tag_configure("string", foreground=SYN_STR)
        txt.tag_configure("number", foreground=SYN_NUM)
        txt.tag_configure("comment", foreground=SYN_COMMENT, font=F["codei"])
        txt.tag_configure("defname", foreground=SYN_DEF, font=F["codeb"])
        txt.tag_configure("gutter", foreground=MUTED)


    def highlight(txt, src, offset=0):
        """Color the code in `txt`. Line n of src is row n; `offset` = characters before the code
        on each row (the line-number gutter). Works on incomplete code too (colors what it can)."""
        for tag in SYNTAX_TAGS:
            txt.tag_remove(tag, "1.0", "end")
        if offset:
            for row in range(1, src.count("\n") + 2):
                txt.tag_add("gutter", f"{row}.0", f"{row}.{offset}")
        tokens = []
        try:
            for tok in tokenize.generate_tokens(io.StringIO(src).readline):
                tokens.append(tok)
        except (tokenize.TokenError, SyntaxError):
            pass  # unfinished code: keep what was read so far
        prev = ""
        for tok in tokens:
            text, (srow, scol), (erow, ecol) = tok.string, tok.start, tok.end
            kind = tokenize.tok_name.get(tok.type, "")
            tag = None
            if kind == "NAME":
                if prev in ("def", "class"):
                    tag = "defname"
                elif text in WORD_OPS:
                    tag = "kwop"
                elif keyword.iskeyword(text):
                    tag = "kw"
                elif text in BUILTIN_NAMES:
                    tag = "builtin"
                prev = text
            else:
                if kind in ("NL", "NEWLINE", "INDENT", "DEDENT", "COMMENT"):
                    pass
                else:
                    prev = ""
                if kind == "NUMBER":
                    tag = "number"
                elif kind in STRING_TOKENS:
                    tag = "string"
                elif kind == "COMMENT":
                    tag = "comment"
            if not tag:
                continue
            for row in range(srow, erow + 1):
                a = (scol if row == srow else 0) + offset
                if row == erow:
                    txt.tag_add(tag, f"{row}.{a}", f"{row}.{ecol + offset}")
                else:
                    txt.tag_add(tag, f"{row}.{a}", f"{row}.end")


    # --- switching theme: restyle ttk, then remap every color already painted on a widget ---
    COLOR_OPTIONS = ("bg", "fg", "background", "foreground", "highlightbackground", "highlightcolor",
                     "insertbackground", "selectbackground", "selectforeground", "activebackground",
                     "activeforeground", "troughcolor", "disabledforeground")


    def recolor(widget, mapping):
        try:
            keys = widget.keys()
        except Exception:
            keys = []
        for opt in COLOR_OPTIONS:
            if opt in keys:
                try:
                    cur = str(widget.cget(opt)).lower()
                    if cur in mapping:
                        widget.configure(**{opt: mapping[cur]})
                except tk.TclError:
                    pass
        if isinstance(widget, tk.Text):
            for tag in widget.tag_names():
                for opt in ("background", "foreground"):
                    try:
                        cur = str(widget.tag_cget(tag, opt)).lower()
                        if cur in mapping:
                            widget.tag_configure(tag, **{opt: mapping[cur]})
                    except tk.TclError:
                        pass
        if isinstance(widget, ttk.Treeview):
            try:
                cur = str(widget.tag_configure("chg", "background")).lower()
                if cur in mapping:
                    widget.tag_configure("chg", background=mapping[cur])
            except tk.TclError:
                pass
        if getattr(widget, "_theme_btn", False):
            widget.configure(text=theme_button_text())
        for child in widget.winfo_children():
            recolor(child, mapping)


    def theme_button_text():
        return "Light mode" if CURRENT["name"] == "dark" else "Dark mode"


    def set_theme(root, name):
        old, new = PALETTES[CURRENT["name"]], PALETTES[name]
        mapping = {old[k].lower(): new[k] for k in old}
        apply_palette(name)
        style_app(root)
        recolor(root, mapping)


    def ro_text(parent, height, font=None, bg=None, **kw):
        """Read-only Text widget with a scrollbar."""
        box = ttk.Frame(parent)
        kw.setdefault("wrap", "word")
        txt = tk.Text(box, height=height, font=font or F["ui"], bg=bg or CARD, fg=TEXT,
                      insertbackground=TEXT, relief="solid", bd=1, highlightthickness=0,
                      padx=8, pady=6, **kw)
        sb = ttk.Scrollbar(box, command=txt.yview)
        txt.configure(yscrollcommand=sb.set, state="disabled")
        sb.pack(side="right", fill="y")
        txt.pack(side="left", fill="both", expand=True)
        return box, txt


    def set_text(txt, content, tag=None):
        txt.configure(state="normal")
        txt.delete("1.0", "end")
        txt.insert("end", content, tag or ())
        txt.configure(state="disabled")


    class ScrollFrame(ttk.Frame):
        """A vertically scrollable area. Put content in .body"""

        def __init__(self, parent):
            super().__init__(parent)
            self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
            self.sb = ttk.Scrollbar(self, command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=self.sb.set)
            self.sb.pack(side="right", fill="y")
            self.canvas.pack(side="left", fill="both", expand=True)
            self.body = ttk.Frame(self.canvas, padding=(24, 12))
            self.win = self.canvas.create_window((0, 0), window=self.body, anchor="nw")
            self.body.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
            self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.win, width=e.width))

        def scroll(self, units):
            if self.body.winfo_reqheight() > self.canvas.winfo_height():
                self.canvas.yview_scroll(units, "units")


    def parse_inputs(raw):
        raw = raw.strip()
        return [v.strip() for v in raw.split(",")] if raw else []


    # ===========================================================================
    # DEV MODE WINDOW
    # ===========================================================================
    class DevWindow(tk.Toplevel):
        def __init__(self, app, heading, src, inputs, q=None):
            super().__init__(app.root)
            self.app, self.src, self.q = app, src, q
            self.inputs = list(inputs)
            self.uses_input = "input(" in src
            self.k = 0
            self.steps, self.output, self.error = [], "", None
            self.hist, self.fid_label, self.module_fid = {}, {}, None
            self.revealed = set()
            self._scale_lock = False
            self.playing = False
            self.predict = tk.BooleanVar(value=False)
            self.title("Dev Mode  -  " + heading)
            self.geometry("1360x880")
            self.minsize(1000, 680)
            self.configure(bg=BG)
            self._build(heading)
            for key, fn in (("<Right>", self.next), ("<space>", self.next), ("<Return>", self.next),
                            ("<Left>", self.prev), ("<BackSpace>", self.prev)):
                self.bind(key, lambda e, fn=fn: self._key(fn))
            self.bind("<Home>", lambda e: self._key(lambda: self.go(0)))
            self.bind("<End>", lambda e: self._key(lambda: self.go(len(self.steps) - 1)))
            self.bind("<Escape>", lambda e: self.destroy())
            self.bind("<F3>", lambda e: self.app.open_cheat(self.app.cheat_tab_for(self.q)))
            self.bind("<Control-equal>", lambda e: resize_fonts(1))
            self.bind("<Control-minus>", lambda e: resize_fonts(-1))
            self.predict.trace_add("write", self._on_predict)
            self.rerun()
            self.lift()
            self.focus_force()

        # --- layout ------------------------------------------------------------
        def _build(self, heading):
            top = ttk.Frame(self, padding=(14, 10, 14, 4))
            top.pack(fill="x")
            ttk.Label(top, text=heading, font=F["h2"], foreground=HEAD, wraplength=700,
                      justify="left").pack(side="left")
            self.app.theme_button(top).pack(side="right", padx=8)
            ttk.Button(top, text="A+", width=3, command=lambda: resize_fonts(1)).pack(side="right", padx=2)
            ttk.Button(top, text="A-", width=3, command=lambda: resize_fonts(-1)).pack(side="right", padx=2)
            ttk.Button(top, text="Cheat sheets  (F3)", style="Accent.TButton",
                       command=lambda: self.app.open_cheat(self.app.cheat_tab_for(self.q))).pack(side="right", padx=8)
            if self.q:
                ttk.Button(top, text="Show answer", command=self.show_answer).pack(side="right", padx=2)

            hint = ttk.Frame(self, padding=(14, 0, 14, 2))
            hint.pack(fill="x")
            ttk.Label(hint, text="Keys:  Right / Space = next step    Left = back    F3 = cheat sheets    Esc = close",
                      foreground=MUTED).pack(side="left")
            ttk.Checkbutton(hint, text="Predict first  (hide what each line does until I click Reveal)",
                            variable=self.predict, takefocus=False).pack(side="right")
            if self.uses_input:
                row = ttk.Frame(self, padding=(14, 2, 14, 6))
                row.pack(fill="x")
                ttk.Label(row, text="This code calls input().  The user types:").pack(side="left")
                self.entry = ttk.Entry(row, width=30, font=F["code"])
                self.entry.insert(0, ", ".join(self.inputs))
                self.entry.pack(side="left", padx=8)
                self.entry.bind("<Return>", lambda e: self.rerun_with_entry())
                ttk.Button(row, text="Run with this value", style="Accent.TButton",
                           command=self.rerun_with_entry).pack(side="left")
                ttk.Label(row, text="(several input() calls? separate with commas)",
                          foreground=MUTED).pack(side="left", padx=10)

            # bottom controls first so they never get squeezed out
            bar = ttk.Frame(self, padding=(14, 8))
            bar.pack(side="bottom", fill="x")
            self.btn_first = ttk.Button(bar, text="|<", width=4, command=lambda: self.go(0))
            self.btn_prev = ttk.Button(bar, text="<  Back", command=self.prev)
            self.btn_next = ttk.Button(bar, text="Next step  >", style="Accent.TButton", command=self.next)
            self.btn_last = ttk.Button(bar, text=">|", width=4, command=lambda: self.go(len(self.steps) - 1))
            self.btn_play = ttk.Button(bar, text="Auto-play", command=self.toggle_play)
            for b in (self.btn_first, self.btn_prev, self.btn_next, self.btn_last, self.btn_play):
                b.pack(side="left", padx=3)
            self.scale = ttk.Scale(bar, from_=0, to=1, orient="horizontal", command=self._on_scale)
            self.scale.pack(side="left", fill="x", expand=True, padx=14)
            self.counter = ttk.Label(bar, text="", font=F["bold"])
            self.counter.pack(side="left")

            main = ttk.PanedWindow(self, orient="horizontal")
            main.pack(fill="both", expand=True, padx=14, pady=4)

            left = ttk.Frame(main)
            main.add(left, weight=2)
            ttk.Label(left, text="CODE", foreground=MUTED, font=F["bold"]).pack(anchor="w")
            box, self.code = ro_text(left, 10, font=F["code"], wrap="none")
            self.code.configure(wrap="none")
            self.code.tag_configure("cur", background=CUR_BG)
            code_tags(self.code)
            box.pack(fill="both", expand=True)
            ttk.Label(left, text="PROGRAM OUTPUT SO FAR", foreground=MUTED, font=F["bold"]).pack(anchor="w", pady=(8, 0))
            obox, self.out = ro_text(left, 6, font=F["code"])
            self.out.tag_configure("err", foreground=BAD)
            obox.pack(fill="x")

            right = ttk.Frame(main)
            main.add(right, weight=3)
            self.title_lbl = tk.Label(right, text="", font=F["h2"], bg=BG, fg=TEXT, anchor="w", justify="left", wraplength=640)
            self.title_lbl.pack(fill="x")
            self.stack_lbl = tk.Label(right, text="", font=F["ui"], bg=BG, fg=MUTED, anchor="w", justify="left", wraplength=640)
            self.stack_lbl.pack(fill="x", pady=(0, 6))
            right.bind("<Configure>", lambda e: (self.title_lbl.configure(wraplength=max(300, e.width - 20)),
                                                 self.stack_lbl.configure(wraplength=max(300, e.width - 20))))
            ebox, self.explain = ro_text(right, 8)
            self.explain.tag_configure("h", font=F["bold"], spacing1=6)
            self.explain.tag_configure("code", font=F["code"])
            self.explain.tag_configure("ok", foreground=GOOD, font=F["bold"])
            self.explain.tag_configure("bad", foreground=BAD, font=F["bold"])
            self.explain.tag_configure("dim", foreground=MUTED)
            self.explain.tag_configure("note", foreground=SYN_COMMENT, lmargin1=40, lmargin2=60)
            ebox.pack(fill="both", expand=True)

            self.vnb = ttk.Notebook(right)
            self.vnb.pack(fill="both", expand=True, pady=(8, 0))
            vpage = ttk.Frame(self.vnb, padding=4)
            self.vnb.add(vpage, text="Variables")
            self.vars_frame = ttk.LabelFrame(vpage, text="Variables now", padding=4)
            self.vars_frame.pack(fill="both", expand=True)
            self.tree = self._make_tree(self.vars_frame)
            self.glob_frame = ttk.LabelFrame(vpage, text="Global (main program) variables", padding=4)
            self.glob_tree = self._make_tree(self.glob_frame, height=3)
            hpage = ttk.Frame(self.vnb, padding=4)
            self.vnb.add(hpage, text="History of each variable")
            hbox = ttk.Frame(hpage)
            hbox.pack(fill="both", expand=True)
            self.hist_tree = ttk.Treeview(hbox, columns=("var", "scope", "vals"), show="headings", height=5)
            for col, w, txt, stretch in (("var", 90, "Variable", False), ("scope", 130, "Where", False),
                                         ("vals", 360, "Its values so far (and the line that set each)", True)):
                self.hist_tree.heading(col, text=txt, anchor="w")
                self.hist_tree.column(col, width=w, minwidth=w if not stretch else 80, anchor="w", stretch=stretch)
            self.hist_tree.tag_configure("chg", background=CHG_BG)
            hs = ttk.Scrollbar(hbox, command=self.hist_tree.yview)
            self.hist_tree.configure(yscrollcommand=hs.set)
            hs.pack(side="right", fill="y")
            self.hist_tree.pack(side="left", fill="both", expand=True)

        def _make_tree(self, parent, height=4):
            tree = ttk.Treeview(parent, columns=("name", "value", "type", "set"), show="headings", height=height)
            for col, w, txt, stretch in (("name", 90, "Name", False), ("value", 200, "Value", True),
                                         ("type", 80, "Type", False), ("set", 100, "Last set", False)):
                tree.heading(col, text=txt, anchor="w")
                tree.column(col, width=w, minwidth=w if not stretch else 60, anchor="w", stretch=stretch)
            tree.tag_configure("chg", background=CHG_BG)
            tree.pack(fill="both", expand=True)
            return tree

        # --- running -----------------------------------------------------------
        def rerun_with_entry(self):
            self.inputs = parse_inputs(self.entry.get())
            self.rerun()

        def rerun(self):
            self.playing = False
            self.revealed = set()
            self.btn_play.configure(text="Auto-play")
            events, self.output, self.error, note = t.trace_run(self.src, self.inputs)
            self.steps = t.build_steps(events, self.output, self.error, self.src)
            self.cum = []
            acc = ""
            for s in self.steps:
                acc += s["out"]
                self.cum.append(acc)
            self._build_history()
            self.code.configure(state="normal")
            self.code.delete("1.0", "end")
            for n, line in enumerate(self.src.split("\n"), 1):
                self.code.insert("end", f"{n:>3} | {line}\n")
            highlight(self.code, self.src, 6)
            self.code.configure(state="disabled")
            n = len(self.steps)
            self.scale.configure(to=max(1, n - 1))
            self.k = 0
            if n == 0:
                self._render_empty()
            else:
                self.render()

        def _build_history(self):
            """For every variable: the list of (step index, value, type, what set it)."""
            self.hist, self.fid_label, self.module_fid = {}, {}, None
            prev, order = {}, []
            for idx, s in enumerate(self.steps):
                fid = s.get("fid")
                if fid not in self.fid_label:
                    self.fid_label[fid] = s["func"]
                    order.append(fid)
                if s["func"] == "<module>" and self.module_fid is None:
                    self.module_fid = fid
                is_call = t.plain(s["title"]).startswith("Calling ")
                for name, (r, tp) in s["vars"].items():
                    if prev.get((fid, name)) != (r, tp):
                        self.hist.setdefault((fid, name), []).append(
                            (idx, r, tp, "passed in" if is_call else f"line {s['line']}"))
                        prev[(fid, name)] = (r, tp)
            counts, seen = {}, {}
            for fid in order:
                counts[self.fid_label[fid]] = counts.get(self.fid_label[fid], 0) + 1
            for fid in order:
                fn = self.fid_label[fid]
                if fn == "<module>":
                    self.fid_label[fid] = "main program"
                elif counts[fn] > 1:
                    seen[fn] = seen.get(fn, 0) + 1
                    self.fid_label[fid] = f"{fn}() call {seen[fn]}"
                else:
                    self.fid_label[fid] = f"{fn}()"

        def _render_empty(self):
            self.title_lbl.configure(text="No steps - no line of this code actually runs", fg=MUTED)
            self.stack_lbl.configure(text="")
            msg = self.error or "(it is all comments, so Python does nothing)"
            set_text(self.explain, msg, "bad" if self.error else "dim")
            set_text(self.out, self.output or "(nothing printed)")
            self.counter.configure(text="0 / 0")
            for tr in (self.tree, self.glob_tree, self.hist_tree):
                tr.delete(*tr.get_children())

        # --- navigation --------------------------------------------------------
        def _key(self, fn):
            if isinstance(self.focus_get(), (tk.Entry, ttk.Entry)):
                return
            fn()

        def _on_predict(self, *_):
            self.focus_set()
            if self.steps:
                self.render()

        def go(self, k):
            if not self.steps:
                return
            self.k = max(0, min(len(self.steps) - 1, k))
            self.render()

        def next(self):
            if not self.steps:
                return
            if self.predict.get() and self.k not in self.revealed:
                self.revealed.add(self.k)  # first click = reveal what this line did
                self.render()
            elif self.k < len(self.steps) - 1:
                self.go(self.k + 1)
            else:
                self.playing = False
                self.btn_play.configure(text="Auto-play")

        def prev(self):
            self.go(self.k - 1)

        def _on_scale(self, v):
            if not self._scale_lock and self.steps:
                self.go(int(round(float(v))))

        def toggle_play(self):
            self.playing = not self.playing
            self.btn_play.configure(text="Pause" if self.playing else "Auto-play")
            if self.playing:
                if self.k >= len(self.steps) - 1:
                    self.go(0)
                self._tick()

        def _tick(self):
            if self.playing and self.winfo_exists():
                self.next()
                if self.playing:
                    self.after(1400 if self.predict.get() else 900, self._tick)

        # --- drawing -----------------------------------------------------------
        def _prev_vars(self, k):
            fid = self.steps[k].get("fid")
            for j in range(k - 1, -1, -1):
                if self.steps[j].get("fid") == fid:
                    return self.steps[j]["vars"]
            return {}

        def last_set(self, fid, name, k):
            best = ""
            for idx, r, tp, label in self.hist.get((fid, name), []):
                if idx > k:
                    break
                best = label
            return best

        def render(self):
            s, k, n = self.steps[self.k], self.k, len(self.steps)
            predicting = self.predict.get() and k not in self.revealed
            self._scale_lock = True
            self.scale.set(k)
            self._scale_lock = False
            self.counter.configure(text=f"Step {k + 1} / {n}")
            self.btn_next.configure(text="Reveal  >" if predicting else "Next step  >")
            self.btn_prev.state(["!disabled"] if k > 0 else ["disabled"])
            self.btn_first.state(["!disabled"] if k > 0 else ["disabled"])
            self.btn_next.state(["!disabled"] if (k < n - 1 or predicting) else ["disabled"])
            self.btn_last.state(["!disabled"] if k < n - 1 else ["disabled"])

            self.code.configure(state="normal")
            self.code.tag_remove("cur", "1.0", "end")
            self.code.tag_add("cur", f"{s['line']}.0", f"{s['line']}.0 lineend+1c")
            self.code.configure(state="disabled")
            self.code.see(f"{s['line']}.0")

            place = "" if s["func"] == "<module>" else f"   [inside {s['func']}()]"
            title = t.plain(s["title"])
            if predicting:
                self.title_lbl.configure(text=f"Step {k + 1}:  PREDICT - what will line {s['line']} do?{place}", fg=ACCENT)
            else:
                bad = "error" in title or "because of the error" in title
                self.title_lbl.configure(text=title + place, fg=BAD if bad else TEXT)
            stack = s.get("stack") or []
            self.stack_lbl.configure(text=("Call stack:   " + "   ->   ".join(stack)) if stack else "")

            ex = self.explain
            ex.configure(state="normal")
            ex.delete("1.0", "end")
            if predicting:
                ex.insert("end", "Your turn! Before you click Reveal, think:\n", "h")
                ex.insert("end", "  1. Which variables does this line use, and what are their values right now?\n"
                                 "  2. What will change, or what will print?\n"
                                 "  3. If it is an if / while: will the condition be True or False?\n\n")
                ex.insert("end", "The tables below show the values from BEFORE this line runs.", "dim")
            else:
                self._explain_step(ex, s)
            ex.configure(state="disabled")

            fid = s.get("fid")
            prev = None if predicting else {}
            if not predicting and k > 0 and self.steps[k - 1].get("fid") == fid:
                prev = self.steps[k - 1]["vars"]
            snap = self._prev_vars(k) if predicting else s["vars"]
            self._fill(self.tree, snap, prev, fid, k - 1 if predicting else k)
            self.vars_frame.configure(text="Variables now" if s["func"] == "<module>"
                                      else f"Local variables in {s['func']}()")
            if s.get("globals") is not None:
                self.glob_frame.pack(fill="both", expand=True, pady=(8, 0))
                self._fill(self.glob_tree, s["globals"], None, self.module_fid, k)
            else:
                self.glob_frame.pack_forget()
            self._fill_history(k - 1 if predicting else k)

            out = (self.cum[k - 1] if k > 0 else "") if predicting else self.cum[k]
            self.out.configure(state="normal")
            self.out.delete("1.0", "end")
            self.out.insert("end", out if out else "(nothing printed yet)")
            if k == n - 1 and self.error and not predicting:
                self.out.insert("end", f"\n[program crashed: {self.error}]", "err")
            self.out.configure(state="disabled")
            self.out.see("end")

        def _explain_step(self, ex, s):
            ca = s.get("callargs")
            if ca and ca["rows"]:
                ex.insert("end", "Values passed in", "h")
                ex.insert("end", (f"   by the call  {ca['call']}\n" if ca["call"] else "\n"), "code")
                for r in ca["rows"]:
                    where = f", from `{r['expr']}`" if r["expr"] and not r["kind"].startswith("default") else ""
                    ex.insert("end", f"    {r['param']}  <-  {r['value']}", "code")
                    ex.insert("end", f"     {r['kind']}{where}   [{r['type']}]\n", "dim")
                    if r["same_as"]:
                        tail = ("it is MUTABLE: changing it in here changes `%s` out there too!" % r["same_as"]
                                if r["mutable"] else
                                "numbers and strings can't change in place, so `%s` outside is safe" % r["same_as"])
                        ex.insert("end", f"        same object as `{r['same_as']}` - {tail}\n", "dim")
            c = s["cond"]
            if c:
                ex.insert("end", "Condition:  ", "h")
                ex.insert("end", c["expr"] + "\n", "code")
                for seg, val in c["parts"]:
                    if val is None:
                        ex.insert("end", f"    {seg}  ->  skipped (short-circuit: the answer was already known)\n", "dim")
                    else:
                        ex.insert("end", f"    {seg}  ->  {val}\n", "code")
                ok = c["truth"]
                shown = c["value"]
                extra = "" if shown in ("True", "False") else f"   ({shown} counts as {ok})"
                ex.insert("end", f"  Whole condition = {shown}{extra}  ->  ", "code")
                ex.insert("end", "True: the indented block RUNS\n" if ok else "False: the block is SKIPPED\n",
                          "ok" if ok else "bad")
            if s.get("evals"):
                ex.insert("end", "Worked out (inside first, using the values from before this line):\n", "h")
                for seg, val, is_err, note in s["evals"]:
                    ex.insert("end", f"    {seg}  ->  {val}\n", "bad" if is_err else "code")
                    if note:
                        ex.insert("end", f"-> {note}\n", "note")
            if s["changes"]:
                ex.insert("end", "Changed:\n", "h")
                for ch in s["changes"]:
                    ex.insert("end", "    " + ch + "\n", "code")
            if s["out"]:
                ex.insert("end", "This step printed:\n", "h")
                for ln in s["out"].rstrip("\n").split("\n"):
                    ex.insert("end", "    | " + ln + "\n", "code")
            if not (ca and ca["rows"]) and not (c or s.get("evals") or s["changes"] or s["out"]):
                ex.insert("end", "Nothing changes on this step.", "dim")

        def _fill(self, tree, snap, prev, fid, k):
            tree.delete(*tree.get_children())
            for name, (r, tp) in snap.items():
                changed = prev is not None and prev.get(name) != (r, tp)
                tree.insert("", "end", values=(name, r, tp, self.last_set(fid, name, k)),
                            tags=("chg",) if changed else ())

        def _fill_history(self, k):
            tree = self.hist_tree
            tree.delete(*tree.get_children())
            for (fid, name), entries in self.hist.items():
                shown = [(idx, r, label) for idx, r, tp, label in entries if idx <= k]
                if not shown:
                    continue
                text = "   ->   ".join(f"{r}  ({label})" for idx, r, label in shown)
                tree.insert("", "end", values=(name, self.fid_label.get(fid, ""), text),
                            tags=("chg",) if shown[-1][0] == k else ())

        def show_answer(self):
            q = self.q
            ans = "  /  ".join(a.replace("\n", " | ") for a in q["answer"])
            messagebox.showinfo("Answer", f"Correct answer:\n{ans}\n\nWhy:\n{q['why']}", parent=self)


    # ===========================================================================
    # CHEAT SHEETS (every result shown is computed live by Python)
    # ===========================================================================
    class CheatSheet(tk.Toplevel):
        TYPE_COLORS = {"int": "SYN_NUM", "float": "SYN_KWOP", "str": "SYN_STR", "bool": "SYN_KW",
                       "NoneType": "MUTED", "list": "SYN_BUILTIN", "dict": "SYN_BUILTIN", "tuple": "SYN_BUILTIN"}

        def __init__(self, app, tab=None):
            super().__init__(app.root)
            self.app = app
            self.cache = {}
            self.title("Cheat sheets  -  int / float / str, logic, % and more")
            self.geometry("1140x820")
            self.minsize(860, 560)
            self.configure(bg=BG)
            top = ttk.Frame(self, padding=(14, 10, 14, 4))
            top.pack(fill="x")
            ttk.Label(top, text="Cheat sheets", font=F["h2"], foreground=HEAD).pack(side="left")
            app.theme_button(top).pack(side="right", padx=8)
            ttk.Button(top, text="A+", width=3, command=lambda: resize_fonts(1)).pack(side="right", padx=2)
            ttk.Button(top, text="A-", width=3, command=lambda: resize_fonts(-1)).pack(side="right", padx=2)
            tk.Label(self, bg=BG, fg=MUTED, font=F["ui"], anchor="w", justify="left", wraplength=1000,
                     text="Every result in these tables was computed by Python just now, so it can't be wrong. "
                          "Colors show the TYPE: blue = int, purple = float, red = str, green = bool."
                     ).pack(fill="x", padx=14)
            bar = ttk.Frame(self, padding=(14, 8))
            bar.pack(side="bottom", fill="x")
            ttk.Label(bar, text="Try it:", font=F["bold"]).pack(side="left")
            self.entry = ttk.Entry(bar, font=F["code"], width=36)
            self.entry.pack(side="left", padx=8)
            self.entry.insert(0, "0 or 5")
            self.entry.bind("<Return>", lambda e: self.run_try())
            ttk.Button(bar, text="Evaluate", style="Accent.TButton", command=self.run_try).pack(side="left")
            self.result = tk.Label(bar, text="", font=F["code"], bg=BG, fg=MUTED, anchor="w", justify="left", wraplength=560)
            self.result.pack(side="left", padx=14, fill="x", expand=True)
            self.nb = ttk.Notebook(self)
            self.nb.pack(fill="both", expand=True, padx=14, pady=8)
            self.pages, self.order = {}, []
            for tab_def in t.CHEAT_TABS:
                box, txt = ro_text(self.nb, 20, font=F["ui"], wrap="word")
                self.nb.add(box, text=tab_def["title"])
                self.pages[tab_def["key"]] = txt
                self.order.append(tab_def["key"])
                txt.tag_configure("h", font=F["h2"], foreground=HEAD, spacing1=16, spacing3=4)
                txt.tag_configure("colhead", font=F["bold"], foreground=MUTED, underline=True)
                txt.tag_configure("code", font=F["code"])
                txt.tag_configure("note", font=F["ui"])
                txt.tag_configure("t_err", font=F["codeb"], foreground=BAD)
                txt.tag_configure("t_other", font=F["codeb"], foreground=TEXT)
                for ty, color in self.TYPE_COLORS.items():
                    txt.tag_configure("t_" + ty, font=F["codeb"], foreground=globals()[color])
            self.render_all()
            self.run_try()
            if tab:
                self.select_tab(tab)
            APP["listeners"].append(self.render_all)
            self.bind("<Destroy>", self._on_destroy)
            self.bind("<Escape>", lambda e: self.destroy())
            self.bind("<Control-equal>", lambda e: resize_fonts(1))
            self.bind("<Control-minus>", lambda e: resize_fonts(-1))
            self.lift()

        def _on_destroy(self, e):
            if e.widget is self and self.render_all in APP["listeners"]:
                APP["listeners"].remove(self.render_all)

        def select_tab(self, key):
            if key in self.order:
                self.nb.select(self.order.index(key))

        def render_all(self):
            for tab_def in t.CHEAT_TABS:
                self._fill(self.pages[tab_def["key"]], tab_def)

        def _eval(self, expr):
            if expr not in self.cache:
                self.cache[expr] = t.eval_expr(expr)
            return self.cache[expr]

        def _fill(self, txt, tab_def):
            cw = F["code"].measure("0")
            txt.configure(state="normal")
            txt.delete("1.0", "end")
            for bi, block in enumerate(tab_def["blocks"]):
                txt.insert("end", block["heading"] + "\n", "h")
                tabtag = f"tabs{bi}"
                if block["kind"] == "live":
                    rows = [(expr, note, self._eval(expr)) for expr, note in block["rows"]]
                    shown = [r[2][2].split(":")[0] if r[2][2] else r[2][0] for r in rows]
                    w1 = max(len(r[0]) for r in rows) + 3
                    w2 = min(30, max(len(x) for x in shown) + 3)
                    x1, x2, x3 = cw * w1, cw * (w1 + w2), cw * (w1 + w2 + 10)
                    txt.tag_configure(tabtag, tabs=(x1, x2, x3), lmargin1=8, lmargin2=x3 + 8)
                    txt.insert("end", "Expression\tResult\tType\tWhy\n", ("colhead", tabtag))
                    for (expr, note, (rep, ty, err)), cell in zip(rows, shown):
                        ctag = "t_err" if err else ("t_" + ty if ("t_" + ty) in txt.tag_names() else "t_other")
                        txt.insert("end", expr, ("code", tabtag))
                        txt.insert("end", "\t", tabtag)
                        txt.insert("end", cell if len(cell) <= 30 else cell[:27] + "...", (ctag, tabtag))
                        txt.insert("end", "\t", tabtag)
                        txt.insert("end", "error" if err else ty, (ctag, tabtag))
                        txt.insert("end", "\t", tabtag)
                        txt.insert("end", note + "\n", ("note", tabtag))
                else:
                    widths = block["widths"]
                    stops, acc = [], 0
                    for w in widths:
                        acc += w
                        stops.append(cw * acc)
                    txt.tag_configure(tabtag, tabs=tuple(stops), lmargin1=8, lmargin2=(stops[-1] if stops else 0) + 8)
                    txt.insert("end", "\t".join(block["cols"]) + "\n", ("colhead", tabtag))
                    for row in block["rows"]:
                        txt.insert("end", row[0], ("code", tabtag))
                        for cell in row[1:]:
                            txt.insert("end", "\t", tabtag)
                            txt.insert("end", cell, ("note", tabtag))
                        txt.insert("end", "\n", tabtag)
            txt.configure(state="disabled")

        def run_try(self):
            rep, ty, err = t.eval_expr(self.entry.get())
            if err:
                self.result.configure(text=err, fg=BAD)
            elif not rep and not ty:
                self.result.configure(text="type an expression, e.g.  0 or 5   or   '8' * 2   or   7 % 3", fg=MUTED)
            else:
                color = globals()[self.TYPE_COLORS[ty]] if ty in self.TYPE_COLORS else TEXT
                self.result.configure(text=f"{rep}      ({ty})", fg=color)


    # ===========================================================================
    # MAIN APP
    # ===========================================================================
    class App:
        def __init__(self):
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass
            self.root = tk.Tk()
            self.root.title("IS 4485 - Python Midterm Study Tool")
            self.root.geometry("1080x820")
            self.root.minsize(820, 640)
            self.root.report_callback_exception = self._report
            APP["root"] = self.root
            apply_palette(system_theme())  # start in whatever Windows is set to
            make_fonts(self.root)
            style_app(self.root)
            self.mode = "home"
            self.frame = None
            self.wrap_labels, self.card_labels, self.scroller = [], [], None
            self.cheat = None
            self.concept_stats = {}
            self.shuffle_q = tk.BooleanVar(value=True)
            self.shuffle_c = tk.BooleanVar(value=True)
            self.bonus_n = tk.IntVar(value=0)
            self.super_bonus = tk.BooleanVar(value=True)
            self.super_n = tk.IntVar(value=0)
            self.root.bind("<Key>", self._on_key)
            self.root.bind("<F2>", lambda e: self.open_dev())
            self.root.bind("<F3>", lambda e: self.open_cheat(self.cheat_tab_for(self.current_q())
                                                             if self.mode == "quiz" else None))
            self.root.bind_all("<MouseWheel>", self._wheel)
            self.root.bind_all("<Button-4>", lambda e: self._wheel(e, 1))
            self.root.bind_all("<Button-5>", lambda e: self._wheel(e, -1))
            self.root.bind("<Control-equal>", lambda e: resize_fonts(1))
            self.root.bind("<Control-minus>", lambda e: resize_fonts(-1))
            self.root.bind("<Configure>", self._on_resize)
            self.show_home()

        # --- helpers -----------------------------------------------------------
        def _report(self, exc, val, tb):
            """Show an unexpected error in a dialog instead of dying silently."""
            import traceback
            detail = "".join(traceback.format_exception(exc, val, tb))
            try:
                messagebox.showerror("Something went wrong",
                                     "The app hit an unexpected error but is still running.\n\n" + detail[-1500:])
            except Exception:
                pass

        def theme_button(self, parent):
            btn = ttk.Button(parent, text=theme_button_text(), command=self.toggle_theme)
            btn._theme_btn = True  # recolor() keeps its label ("Dark mode"/"Light mode") up to date
            return btn

        def toggle_theme(self):
            set_theme(self.root, "light" if CURRENT["name"] == "dark" else "dark")

        def clear(self):
            if self.frame is not None:
                self.frame.destroy()
            self.frame = ttk.Frame(self.root, padding=(24, 16))
            self.frame.pack(fill="both", expand=True)
            self.wrap_labels, self.card_labels, self.scroller = [], [], None

        def wlabel(self, parent, text, font=None, fg=None, bg=None, **kw):
            lbl = tk.Label(parent, text=text, font=font or F["ui"], fg=fg or TEXT, bg=bg or BG,
                           justify="left", anchor="w", **kw)
            self.wrap_labels.append(lbl)
            lbl.configure(wraplength=max(300, self.root.winfo_width() - 110))
            return lbl

        def _on_resize(self, e):
            if e.widget is self.root:
                for lbl in self.wrap_labels:
                    try:
                        lbl.configure(wraplength=max(300, e.width - 110))
                    except tk.TclError:
                        pass
                for lbl in self.card_labels:
                    try:
                        lbl.configure(wraplength=max(300, e.width - 190))
                    except tk.TclError:
                        pass

        def _typing(self):
            return isinstance(self.root.focus_get(), (tk.Text, tk.Entry, ttk.Entry, tk.Spinbox, ttk.Spinbox))

        def _on_key(self, e):
            if self.mode != "quiz" or self._typing():
                return
            ch = e.char.upper()
            if not self.answered and ch and ch in t.LETTERS[:len(self.cur_choices)]:
                self.select(t.LETTERS.index(ch))
            elif e.keysym in ("Return", "KP_Enter"):
                (self.next_q if self.answered else self.submit)()

        # --- home --------------------------------------------------------------
        def show_home(self):
            self.mode = "home"
            self.clear()
            self.frame.configure(padding=0)
            sf = ScrollFrame(self.frame)
            sf.pack(fill="both", expand=True)
            self.scroller = sf
            f = sf.body
            head = ttk.Frame(f)
            head.pack(fill="x")
            ttk.Label(head, text="IS 4485  -  Python Midterm Study Tool", font=F["h1"],
                      foreground=HEAD).pack(side="left")
            self.theme_button(head).pack(side="right")
            self.wlabel(f, "Take the exams.  F2 = Dev Mode (step through any code)    F3 = cheat sheets "
                           "(int / float / str, and / or, %).", fg=MUTED).pack(fill="x", pady=(2, 12))

            opts = ttk.LabelFrame(f, text="Quiz options", padding=10)
            opts.pack(fill="x")
            ttk.Checkbutton(opts, text="Shuffle question order", variable=self.shuffle_q).grid(row=0, column=0, sticky="w", padx=6)
            ttk.Checkbutton(opts, text="Shuffle answer letters", variable=self.shuffle_c).grid(row=0, column=1, sticky="w", padx=6)
            ttk.Label(opts, text="Mix bonus questions into Exam 1 / 2:").grid(row=0, column=2, padx=(20, 4))
            ttk.Spinbox(opts, from_=0, to=len(t.BONUS), width=4, textvariable=self.bonus_n).grid(row=0, column=3)
            ttk.Checkbutton(opts, text="Super Test includes bonus", variable=self.super_bonus).grid(row=1, column=0, sticky="w", padx=6, pady=(6, 0))
            ttk.Label(opts, text="Super Test: number of questions (0 = all):").grid(row=1, column=2, padx=(20, 4), pady=(6, 0))
            ttk.Spinbox(opts, from_=0, to=87, width=4, textvariable=self.super_n).grid(row=1, column=3, pady=(6, 0))

            grid = ttk.Frame(f)
            grid.pack(fill="x", pady=(14, 4))
            for c in range(3):
                grid.columnconfigure(c, weight=1, uniform="a")
            items = [
                (f"Practice Exam 1\n{len(t.QUIZ1)} questions", self.start_exam1),
                (f"Practice Exam 2\n{len(t.QUIZ2)} questions", self.start_exam2),
                (f"Bonus questions\n{len(t.BONUS)} harder ones", self.start_bonus),
                ("SUPER TEST\neverything mixed", self.start_super),
                ("Dev Mode browser\nstep through any question", self.show_browser),
                ("Playground\nstep through your own code", self.show_playground),
                ("Cheat Sheets\nint / float / str, logic, %, f-strings", self.open_cheat),
            ]
            for i, (txt, cmd) in enumerate(items):
                title, _, sub = txt.partition("\n")
                make_tile(grid, title, sub, f"B{i % 6 + 1}", cmd).grid(row=i // 3, column=i % 3, sticky="nsew", padx=6, pady=6)

            ttk.Label(f, text="PRACTICE BY CONCEPT  (drill the skills you mix up)", foreground=MUTED,
                      font=F["bold"]).pack(anchor="w", pady=(10, 0))
            cgrid = ttk.Frame(f)
            cgrid.pack(fill="x", pady=(2, 8))
            for c in range(3):
                cgrid.columnconfigure(c, weight=1, uniform="c")
            for i, key in enumerate(t.CONCEPTS):
                n = sum(1 for q in t.ALL_QUESTIONS if key in q["tags"])
                make_tile(cgrid, t.CONCEPT_SHORT[key], f"{n} questions", f"B{(i + 3) % 6 + 1}",
                          lambda k=key: self.start_concept(k)).grid(row=i // 3, column=i % 3, sticky="nsew", padx=6, pady=6)
            ttk.Label(f, text="Tips:  F2 = Dev Mode   |   F3 = cheat sheets   |   A-F = pick an answer   |   Enter = submit / next   |   Ctrl +/- = text size",
                      foreground=MUTED).pack(anchor="w")

        def _bonus_sample(self):
            try:
                n = max(0, min(len(t.BONUS), int(self.bonus_n.get())))
            except (tk.TclError, ValueError):
                n = 0
            return random.sample(t.BONUS, n)

        def start_exam1(self):
            self.start_quiz(t.QUIZ1 + self._bonus_sample(), "Exam 1")

        def start_exam2(self):
            self.start_quiz(t.QUIZ2 + self._bonus_sample(), "Exam 2")

        def start_bonus(self):
            self.start_quiz(list(t.BONUS), "Bonus")

        def start_super(self):
            pool = t.QUIZ1 + t.QUIZ2 + (t.BONUS if self.super_bonus.get() else [])
            random.shuffle(pool)
            try:
                n = int(self.super_n.get())
            except (tk.TclError, ValueError):
                n = 0
            if 0 < n < len(pool):
                pool = pool[:n]
            self.start_quiz(pool, "SUPER TEST")

        # --- quiz --------------------------------------------------------------
        def start_quiz(self, pool, title, shuffle_q=None):
            self.title_text = title
            self.order = pool[:]
            if self.shuffle_q.get() if shuffle_q is None else shuffle_q:
                random.shuffle(self.order)
            self.i, self.score, self.answered_count, self.missed = 0, 0, 0, []
            self.concept_stats = {}
            self.show_question()

        def start_concept(self, key):
            self.start_quiz([q for q in t.ALL_QUESTIONS if key in q["tags"]], t.CONCEPTS[key])

        def current_q(self):
            return self.order[self.i]

        def show_question(self):
            self.mode = "quiz"
            self.clear()
            q = self.current_q()
            self.answered = False
            self.selected = None
            choices = q["choices"][:]
            if self.shuffle_c.get():
                random.shuffle(choices)
            self.cur_choices = choices
            self.correct_idx = [i for i, c in enumerate(choices) if c in q["answer"]]
            self.frame.configure(padding=0)
            sf = ScrollFrame(self.frame)
            sf.pack(fill="both", expand=True)
            self.scroller = sf
            f = sf.body

            info = ttk.Frame(f)
            info.pack(fill="x")
            ttk.Label(info, text=f"Question {self.i + 1} of {len(self.order)}   |   {t.label(q)}",
                      font=F["bold"], foreground=HEAD).pack(side="left")
            self.score_lbl = ttk.Label(info, text=self._score_text(), foreground=MUTED, font=F["bold"])
            self.score_lbl.pack(side="right")
            bar = ttk.Frame(f)  # buttons get their own row so big text never squeezes them
            bar.pack(fill="x", pady=(6, 0))
            ttk.Button(bar, text="Dev Mode  (F2)", style="Accent.TButton", command=self.open_dev).pack(side="right")
            ttk.Button(bar, text="Cheat sheets  (F3)",
                       command=lambda: self.open_cheat(self.cheat_tab_for(self.current_q()))).pack(side="right", padx=8)
            ttk.Button(bar, text="Home", command=self.confirm_home).pack(side="right")
            self.theme_button(bar).pack(side="right", padx=8)
            if q.get("tags"):
                self.wlabel(f, "Skills practiced:  " + "   |   ".join(t.CONCEPTS[x] for x in q["tags"]),
                            fg=MUTED).pack(fill="x", pady=(6, 0))

            ttk.Separator(f).pack(fill="x", pady=8)
            self.wlabel(f, q["prompt"], font=F["h2"]).pack(fill="x", pady=(0, 8))

            self.code_holder = ttk.Frame(f)
            self.code_holder.pack(fill="x")
            if q["code"] and not q["demo"]:
                self._show_code("Code")
            elif q["demo"]:
                self.wlabel(self.code_holder, "(Concept question. A demo of the idea appears after you answer, "
                            "and Dev Mode can step through it any time.)", fg=MUTED).pack(fill="x")
            if q["inputs"] and not q["demo"]:
                self.wlabel(self.code_holder, "The user types: " + ", ".join(repr(v) for v in q["inputs"]),
                            fg=MUTED).pack(fill="x", pady=(4, 0))

            self.cards = []
            cf = ttk.Frame(f)
            cf.pack(fill="x", pady=10)
            for i, ch in enumerate(choices):
                card = tk.Frame(cf, bg=CARD, bd=1, relief="solid", cursor="hand2")
                card.pack(fill="x", pady=3)
                letter = tk.Label(card, text=t.LETTERS[i], font=F["h2"], bg=CARD, width=3, fg=ACCENT)
                letter.pack(side="left")
                body = tk.Label(card, text=ch, font=F["code"] if q["code"] else F["ui"], bg=CARD, fg=TEXT,
                                justify="left", anchor="w", wraplength=max(300, self.root.winfo_width() - 190))
                body.pack(side="left", fill="x", expand=True, pady=6)
                self.card_labels.append(body)
                for w in (card, letter, body):
                    w.bind("<Button-1>", lambda e, i=i: self.select(i))
                self.cards.append((card, letter, body))

            self.btn_row = ttk.Frame(f)
            self.btn_row.pack(fill="x", pady=4)
            self.submit_btn = ttk.Button(self.btn_row, text="Submit answer", style="Accent.TButton",
                                         command=self.submit, state="disabled")
            self.submit_btn.pack(side="left")
            ttk.Button(self.btn_row, text="Skip", command=self.skip).pack(side="left", padx=8)
            self.result_holder = ttk.Frame(f)
            self.result_holder.pack(fill="both", expand=True)

        def _score_text(self):
            return f"Score {self.score} / {self.answered_count}"

        def _show_code(self, heading):
            q = self.current_q()
            ttk.Label(self.code_holder, text=heading.upper(), foreground=MUTED, font=F["bold"]).pack(anchor="w")
            lines = q["code"].split("\n")
            txt = tk.Text(self.code_holder, height=min(len(lines), 14), font=F["code"], bg=CARD, fg=TEXT,
                          insertbackground=TEXT, relief="solid", bd=1, highlightthickness=0,
                          padx=8, pady=6, wrap="none")
            code_tags(txt)
            for n, line in enumerate(lines, 1):
                txt.insert("end", f"{n:>3} | {line}\n")
            highlight(txt, q["code"], 6)
            txt.configure(state="disabled")
            txt.pack(fill="x")

        def select(self, i):
            if self.answered:
                return
            self.selected = i
            for j, (card, letter, body) in enumerate(self.cards):
                col = SEL_BG if j == i else CARD
                for w in (card, letter, body):
                    w.configure(bg=col)
            self.submit_btn.configure(state="normal")

        def _color_cards(self):
            for j, (card, letter, body) in enumerate(self.cards):
                if j in self.correct_idx:
                    col = GOOD_BG
                elif j == self.selected:
                    col = BAD_BG
                else:
                    col = CARD
                for w in (card, letter, body):
                    w.configure(bg=col)
                    w.configure(cursor="arrow")

        def submit(self):
            if self.answered or self.selected is None:
                return
            self._finish_question(guess=self.selected)

        def skip(self):
            if not self.answered:
                self._finish_question(guess=None)

        def _section(self, parent, title):
            ttk.Label(parent, text=title, foreground=MUTED, font=F["bold"]).pack(anchor="w", pady=(12, 0))

        def _finish_question(self, guess):
            q = self.current_q()
            self.answered = True
            self.submit_btn.destroy()
            for w in self.btn_row.winfo_children():
                w.destroy()
            letters = "/".join(t.LETTERS[i] for i in self.correct_idx)
            correct = guess is not None and guess in self.correct_idx
            if guess is None:
                self.missed.append(q)
                msg, col = f"Skipped. The answer is {letters}.", MUTED
            else:
                self.answered_count += 1
                if correct:
                    self.score += 1
                    msg, col = "Correct!", GOOD
                else:
                    self.missed.append(q)
                    msg, col = f"Not quite. The answer is {letters}.", BAD
            for tag in q.get("tags", []):
                stat = self.concept_stats.setdefault(tag, [0, 0])
                stat[1] += 1
                stat[0] += 1 if correct else 0
            self.score_lbl.configure(text=self._score_text())
            self.selected = guess
            self._color_cards()

            last = self.i == len(self.order) - 1
            tk.Label(self.btn_row, text=msg, font=F["h2"], fg=col, bg=BG).pack(side="left", padx=(0, 16))
            ttk.Button(self.btn_row, text="See results" if last else "Next question  >",
                       style="Accent.TButton", command=self.next_q).pack(side="left")
            ttk.Button(self.btn_row, text="Step through it in Dev Mode", command=self.open_dev).pack(side="left", padx=8)
            tab = self.cheat_tab_for(q)
            if tab:
                ttk.Button(self.btn_row, text="Open the cheat sheet",
                           command=lambda: self.open_cheat(tab)).pack(side="left")

            rf = self.result_holder
            steps, output, error = [], "", None
            if q["code"]:
                if q["demo"]:
                    self._show_code("Demo code")
                events, output, error, note = t.trace_run(q["code"], q["inputs"])
                steps = t.build_steps(events, output, error, q["code"])
                self._section(rf, "WHEN YOU ACTUALLY RUN " + ("THE DEMO" if q["demo"] else "IT"))
                box, txt = ro_text(rf, min(8, max(2, output.count("\n") + 1 + bool(error))), font=F["code"])
                txt.tag_configure("err", foreground=BAD)
                txt.configure(state="normal")
                txt.insert("end", output if output else "(nothing printed)")
                if error:
                    txt.insert("end", f"\n-> crashes with {error}", "err")
                txt.configure(state="disabled")
                box.pack(fill="x")

            self._section(rf, "WHY THE RIGHT ANSWER IS RIGHT")
            self.wlabel(rf, q["why"]).pack(fill="x")

            if guess is not None and not correct:
                chosen = self.cur_choices[guess]
                reason = t.diagnose(q, chosen, steps, output, error) if q["code"] else ""
                self._section(rf, f"WHY YOUR ANSWER ({t.LETTERS[guess]}) ISN'T RIGHT")
                self.wlabel(rf, "You picked:  " + chosen.replace("\n", "  |  "),
                            font=F["code"] if q["code"] else F["ui"]).pack(fill="x")
                self.wlabel(rf, reason or "Compare it with the explanation above, then step through the code in Dev "
                                          "Mode to see exactly where this option goes wrong.").pack(fill="x", pady=(2, 0))

            if steps:
                lines = t.narrate(q["code"], steps)
                if lines:
                    self._section(rf, "WHAT THE CODE DOES, STEP BY STEP (IN WORDS)")
                    box, txt = ro_text(rf, min(len(lines) + 1, 12), font=F["ui"])
                    txt.configure(state="normal")
                    txt.insert("end", "\n".join(f"{n}.  {ln}" for n, ln in enumerate(lines, 1)))
                    txt.configure(state="disabled")
                    box.pack(fill="x")

            others = [(i, ch) for i, ch in enumerate(self.cur_choices) if i not in self.correct_idx and i != guess]
            reasons = [(i, ch, t.diagnose(q, ch, steps, output, error)) for i, ch in others]
            reasons = [r for r in reasons if r[2]]
            if reasons:
                holder = ttk.Frame(rf)
                state = {"open": False}
                btn = ttk.Button(rf, text="Show why the other wrong options are wrong")

                def toggle():
                    if state["open"]:
                        holder.pack_forget()
                        btn.configure(text="Show why the other wrong options are wrong")
                    else:
                        if not holder.winfo_children():
                            for i, ch, why in reasons:
                                self.wlabel(holder, f"{t.LETTERS[i]})  " + ch.replace("\n", "  |  "), font=F["bold"]).pack(fill="x", pady=(6, 0))
                                self.wlabel(holder, why, fg=MUTED).pack(fill="x")
                        holder.pack(fill="x", pady=4)
                        btn.configure(text="Hide the other options")
                    state["open"] = not state["open"]
                btn.configure(command=toggle)
                btn.pack(anchor="w", pady=(12, 0))

        def next_q(self):
            if not self.answered:
                return
            if self.i >= len(self.order) - 1:
                self.show_results()
            else:
                self.i += 1
                self.show_question()

        def confirm_home(self):
            if messagebox.askyesno("Leave quiz?", "Go back to the home screen? Your progress in this quiz will be lost."):
                self.show_home()

        def show_results(self):
            self.mode = "results"
            self.clear()
            f = self.frame
            top = ttk.Frame(f)
            top.pack(fill="x")
            ttk.Label(top, text="Results", font=F["h1"], foreground=HEAD).pack(side="left")
            self.theme_button(top).pack(side="right")
            if self.answered_count:
                pct = round(100 * self.score / self.answered_count)
                ttk.Label(f, text=f"{self.score} / {self.answered_count} answered correctly  ({pct}%)",
                          font=F["h2"]).pack(anchor="w", pady=6)
            weak = []
            if self.concept_stats:
                ttk.Label(f, text="BY SKILL  (the red ones are your weak spots)", foreground=MUTED,
                          font=F["bold"]).pack(anchor="w", pady=(6, 2))
                for key in t.CONCEPTS:
                    if key not in self.concept_stats:
                        continue
                    good, total = self.concept_stats[key]
                    low = good / total < 0.75
                    if low:
                        weak.append(key)
                    tk.Label(f, text=f"{good}/{total}   {t.CONCEPTS[key]}", font=F["ui"], bg=BG, anchor="w",
                             fg=GOOD if good == total else (BAD if low else TEXT)).pack(fill="x")
            ttk.Label(f, text="MISSED OR SKIPPED  (double-click to step through in Dev Mode)", foreground=MUTED,
                      font=F["bold"]).pack(anchor="w", pady=(12, 2))
            tree = ttk.Treeview(f, columns=("q", "prompt"), show="headings", height=8)
            tree.heading("q", text="Question")
            tree.heading("prompt", text="Prompt")
            tree.column("q", width=120, stretch=False)
            tree.column("prompt", width=700)
            for idx, q in enumerate(self.missed):
                tree.insert("", "end", iid=str(idx), values=(t.label(q), q["prompt"].split("\n")[0]))
            tree.pack(fill="both", expand=True)

            def dev_selected(_=None):
                sel = tree.selection()
                if sel:
                    self.open_dev_for(self.missed[int(sel[0])])
            tree.bind("<Double-1>", dev_selected)
            row = ttk.Frame(f)
            row.pack(fill="x", pady=12)
            ttk.Button(row, text="Dev Mode on selected", style="Accent.TButton", command=dev_selected).pack(side="left")
            if self.missed:
                ttk.Button(row, text="Retry missed questions",
                           command=lambda: self.start_quiz(self.missed[:], "Retry", shuffle_q=True)).pack(side="left", padx=8)
            if weak:
                ttk.Button(row, text="Practice my weak skills",
                           command=lambda: self.start_quiz([q for q in t.ALL_QUESTIONS if any(k in q["tags"] for k in weak)],
                                                           "Weak skills", shuffle_q=True)).pack(side="left")
            ttk.Button(row, text="Home", command=self.show_home).pack(side="right")

        def cheat_tab_for(self, q):
            for tag in (q or {}).get("tags", []):
                if tag in t.CONCEPT_TAB:
                    return t.CONCEPT_TAB[tag]
            return None

        def open_cheat(self, tab=None):
            if self.cheat is not None and self.cheat.winfo_exists():
                self.cheat.lift()
                self.cheat.focus_force()
                if tab:
                    self.cheat.select_tab(tab)
                return
            self.cheat = CheatSheet(self, tab)

        def _wheel(self, e, direction=None):
            sc = self.scroller
            if sc is None or not sc.winfo_exists():
                return
            w = self.root.winfo_containing(e.x_root, e.y_root)
            if w is None or isinstance(w, (tk.Text, ttk.Treeview, tk.Listbox, ttk.Combobox)) or not str(w).startswith(str(sc)):
                return
            sc.scroll(direction * -1 if direction else int(-e.delta / 120))

        # --- dev mode entry points ---------------------------------------------
        def open_dev(self):
            if self.mode == "quiz":
                self.open_dev_for(self.current_q())

        def open_dev_for(self, q):
            DevWindow(self, f"{t.label(q)}:  {q['prompt'].splitlines()[0]}", q["code"], q["inputs"], q)

        # --- dev mode browser --------------------------------------------------
        def show_browser(self):
            self.mode = "browser"
            self.clear()
            f = self.frame
            top = ttk.Frame(f)
            top.pack(fill="x")
            ttk.Label(top, text="Dev Mode browser", font=F["h1"], foreground=HEAD).pack(side="left")
            ttk.Button(top, text="Home", command=self.show_home).pack(side="right")
            ttk.Label(f, text="Double-click any question to step through its code line by line.",
                      foreground=MUTED).pack(anchor="w", pady=(2, 8))
            srow = ttk.Frame(f)
            srow.pack(fill="x")
            ttk.Label(srow, text="Filter:").pack(side="left")
            flt = tk.StringVar()
            ttk.Entry(srow, textvariable=flt, width=32, font=F["ui"]).pack(side="left", padx=6)
            tree = ttk.Treeview(f, columns=("q", "prompt", "code"), show="headings")
            for col, w, txt in (("q", 110, "Question"), ("prompt", 420, "Prompt"), ("code", 330, "First line of code")):
                tree.heading(col, text=txt)
                tree.column(col, width=w)
            sb = ttk.Scrollbar(f, command=tree.yview)
            tree.configure(yscrollcommand=sb.set)
            sb.pack(side="right", fill="y", pady=8)
            tree.pack(fill="both", expand=True, pady=8)
            allq = t.QUIZ1 + t.QUIZ2 + t.BONUS

            def fill(*_):
                tree.delete(*tree.get_children())
                needle = flt.get().lower()
                for idx, q in enumerate(allq):
                    first = q["code"].split("\n")[0] if q["code"] and not q["demo"] else "(concept - demo)"
                    row = (t.label(q), q["prompt"].split("\n")[0], first)
                    if needle in " ".join(row).lower() or needle in (q["code"] or "").lower():
                        tree.insert("", "end", iid=str(idx), values=row)
            flt.trace_add("write", fill)
            fill()

            def go(_=None):
                sel = tree.selection()
                if sel:
                    self.open_dev_for(allq[int(sel[0])])
            tree.bind("<Double-1>", go)
            tree.bind("<Return>", go)
            ttk.Button(f, text="Step through selected", style="Accent.TButton", command=go).pack(anchor="w")

        # --- playground --------------------------------------------------------
        def show_playground(self):
            self.mode = "playground"
            self.clear()
            f = self.frame
            top = ttk.Frame(f)
            top.pack(fill="x")
            ttk.Label(top, text="Playground", font=F["h1"], foreground=HEAD).pack(side="left")
            ttk.Button(top, text="Home", command=self.show_home).pack(side="right")
            ttk.Label(f, text="Paste or type any Python code, then step through it.", foreground=MUTED).pack(anchor="w", pady=(2, 8))
            box = ttk.Frame(f)
            box.pack(fill="both", expand=True)
            ed = tk.Text(box, font=F["code"], bg=CARD, fg=TEXT, insertbackground=TEXT, relief="solid", bd=1,
                         undo=True, padx=8, pady=6, wrap="none", highlightthickness=0)
            code_tags(ed)
            sb = ttk.Scrollbar(box, command=ed.yview)
            ed.configure(yscrollcommand=sb.set)
            sb.pack(side="right", fill="y")
            ed.pack(fill="both", expand=True)
            ed.insert("1.0", 'def is_even(n):\n    return n % 2 == 0\n\ntotal = 0\n'
                             'for i in range(1, 6):\n    if is_even(i) or i == 5:\n        total += i\n'
                             'print(f"total = {total}")\n')
            pending = []

            def recolor_editor(_=None):
                pending.clear()
                highlight(ed, ed.get("1.0", "end-1c"), 0)

            def schedule(_=None):
                if not pending:
                    pending.append(ed.after(120, recolor_editor))

            def on_tab(_):
                ed.insert("insert", "    ")
                return "break"

            def on_return(_):  # keep the indentation of the previous line (+4 after a colon)
                line = ed.get("insert linestart", "insert")
                indent = line[:len(line) - len(line.lstrip())]
                if line.rstrip().endswith(":"):
                    indent += "    "
                ed.insert("insert", "\n" + indent)
                ed.see("insert")
                schedule()
                return "break"
            ed.bind("<KeyRelease>", schedule)
            ed.bind("<Tab>", on_tab)
            ed.bind("<Return>", on_return)
            recolor_editor()
            row = ttk.Frame(f)
            row.pack(fill="x", pady=10)
            ttk.Label(row, text="If it uses input(), the user types:").pack(side="left")
            ent = ttk.Entry(row, width=24, font=F["code"])
            ent.pack(side="left", padx=8)

            def run():
                src = ed.get("1.0", "end").strip("\n")
                if not src.strip():
                    return
                DevWindow(self, "Playground", src, parse_inputs(ent.get()))
            ttk.Button(row, text="Step through this code", style="Accent.TButton", command=run).pack(side="left", padx=8)

        def run(self):
            self.root.mainloop()


# ===========================================================================
# Entry point
# ===========================================================================
def entry():
    if sys.version_info < (3, 8):
        print("This tool needs Python 3.8 or newer. You have " + sys.version.split()[0] + ".")
        return
    global USE_COLOR
    if "--cli" not in sys.argv and HAVE_TK:
        USE_COLOR = False  # the window doesn't want terminal color codes
        try:
            App().run()
            return
        except tk.TclError as e:
            USE_COLOR = bool(sys.stdout) and sys.stdout.isatty() and "NO_COLOR" not in os.environ
            print(f"The window could not open ({e}). Using the terminal version instead.")
    elif "--cli" not in sys.argv:
        print("tkinter isn't available in this Python, so the window can't open. "
              "Using the terminal version instead.")
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye!")


if __name__ == "__main__":
    entry()
