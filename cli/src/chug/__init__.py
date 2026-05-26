# ABOUTME: Chug is an agent-first changelog management CLI for teams.
# ABOUTME: This package exposes the CLI and the core file-based changelog workflow.

__version__ = "0.1.3"

try:
    from ._build import __commit__
except ImportError:
    __commit__ = "unknown"
