"""Prompt templates for the LangGraph agent nodes."""

GRAPH_READER_SYSTEM = """You are a software architecture analyst.
Given a summary of module connectivity from a Python project knowledge graph,
identify the top suspicious areas that might contain bugs, focusing on
middleware and filtering components."""

GRAPH_READER_USER = """Knowledge graph top nodes by connectivity:
{top_nodes}

Which modules or classes should we investigate first for a None-handling bug
in allowed_domains filtering? Reply with a ranked list of 3 module names."""

OBSIDIAN_READER_SYSTEM = """You are a code investigation assistant.
Given Obsidian documentation pages about a Python codebase,
extract the most relevant context about the suspected bug area."""

OBSIDIAN_READER_USER = """Obsidian index:
{index_content}

Hot nodes page:
{hot_content}

What is the most likely bug location and what files should we read?
Reply with: file path, class name, method name, and reason."""

TARGETED_CODE_READER_SYSTEM = """You are a Python bug detective.
Analyze the provided source code snippets and identify the exact bug."""

TARGETED_CODE_READER_USER = """Source code from suspect files:
{code_content}

Previous investigation context:
{obsidian_context}

Identify the exact bug: what is wrong, which line, and why does it fail?"""

BUG_IDENTIFIER_SYSTEM = """You are a precise bug reporter.
Given a code analysis, produce a structured bug report."""

BUG_IDENTIFIER_USER = """Code analysis:
{analysis}

Produce a bug report with:
1. File path
2. Class and method
3. Root cause (one sentence)
4. Failing scenario (input that triggers the bug)
5. Severity"""

FIXER_SYSTEM = """You are a Python developer producing minimal, correct bug fixes.
Output ONLY the corrected code for the specific method, no explanation."""

FIXER_USER = """Bug report:
{bug_report}

Original code:
{target_code}

Provide the corrected method body only, as a Python code block."""
