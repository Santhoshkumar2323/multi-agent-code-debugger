# Multi-Agent Code Debugger (Experimental)

What this project is

This is an experimental multi-agent system for debugging Python code, designed to test whether role-specialized agents can outperform a single LLM call when debugging real execution failures.

What problem it explores

LLMs often:

hallucinate fixes

break imports

return non-runnable code

claim success without execution

This project explores a stricter question:

Can agents be forced to earn correctness through execution and validation?

System architecture

1. Analyzer Agent

Reads the buggy Python code

Produces a structured bug report:

syntax issues

logic issues

runtime issues

severity

Output format is strictly enforced (plain text, fixed schema)

Purpose: isolate what is wrong, not how to fix it.

2. Fixer Agent

Receives the bug analysis + original code

Produces only runnable Python code

Purpose: propose a concrete fix, not commentary.

3. Execution Layer (non-LLM)

Executes the proposed fix in a persistent Python environment

Distinguishes between:

syntax errors

runtime errors

logic errors that still execute

4. Validator Agent

Compares:

original code

fixed code

execution result

Returns strict JSON only, including:

VALID / INVALID judgment

remaining issues

confidence level

Orchestration logic

A central Coordinator enforces the workflow:

Analyze the buggy code

Generate a fix

Run the fix

Validate the outcome

Retry (bounded) if execution or validation fails

The system succeeds only if:

the code runs

the validator confirms correctness

structure is preserved

Memory & traceability

Every step is recorded in a structured memory log:

agent name

phase

status

summary

execution artifacts

timestamps

This allows full inspection of how the system reasoned and failed.

User interface

A Streamlit app provides:

paste-in buggy code

example failure modes (syntax / logic / runtime)

step-by-step visibility into:

analysis

fixed code

execution output

validation report

full agent history

The UI is a debugging microscope, not a black box

What this system does NOT do

No guarantee of correctness beyond validation logic

This is a controlled experiment, not a dev-tool product.

LLM usage

LLMs are used only for:

analysis

fix generation

validation reasoning

They are never trusted without execution.

All correctness is earned via:

code execution

structural checks

explicit validation

Limitations:

Agents can still converge to wrong but runnable code

Validator confidence is heuristic

Complex multi-file bugs are out of scope

Status

Working experimental system.
Explores how agents fail, not just when they succeed.


