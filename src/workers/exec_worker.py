"""Execution Worker: Secure subprocess sandbox with AST/timeout guardrails."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass


@dataclass
class SandboxResult:
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool = False


# TODO: Milestone 4: Implement isolated subprocess runner with env scrubbing
# class ExecWorker:
#     def run_code(self, python_code: str, timeout_sec: float = 3.0) -> SandboxResult:
#         ...

