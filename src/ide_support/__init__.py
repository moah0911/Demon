"""
IDE support for the Demon programming language.
"""

# Import components to make them available through the package
from .language_server_impl import DemonLanguageServer
from .code_completion import CodeCompleter
from .syntax_highlighter import SyntaxHighlighter
from .formatter import CodeFormatter
from .linter import CodeLinter