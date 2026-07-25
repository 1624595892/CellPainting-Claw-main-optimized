from __future__ import annotations

import os
import re
import shlex
import subprocess
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class ExecutionResult:
    label: str
    command: list[str]
    cwd: Path | None
    log_path: Path | None
    returncode: int


class CommandExecutionError(RuntimeError):
    """Raised when a subprocess-backed pipeline step cannot complete successfully."""

    def __init__(
        self,
        *,
        label: str,
        command: list[str],
        cwd: Path | None,
        log_path: Path | None,
        returncode: int | None,
        output_tail: list[str] | None = None,
        reason: str | None = None,
    ) -> None:
        self.label = label
        self.command = list(command)
        self.cwd = cwd
        self.log_path = log_path
        self.returncode = returncode
        self.output_tail = list(output_tail or [])
        self.reason = reason
        super().__init__(self._build_message())

    def _build_message(self) -> str:
        lines = []
        if self.reason:
            lines.append(f"Step '{self.label}' could not start: {self.reason}")
        else:
            lines.append(f"Step '{self.label}' failed with exit code {self.returncode}.")
        lines.append(f"Command: {shlex.join(self.command)}")
        if self.cwd is not None:
            lines.append(f"CWD: {self.cwd}")
        if self.log_path is not None:
            lines.append(f"Log: {self.log_path}")
        if self.output_tail:
            lines.append('Output tail:')
            lines.extend(self.output_tail)
        return '\n'.join(lines)


def run_python_script(
    python_executable: str,
    script_path: Path,
    *,
    cwd: Path | None = None,
    extra_args: list[str] | None = None,
    log_dir: Path | None = None,
    label: str | None = None,
    env: dict[str, str] | None = None,
) -> ExecutionResult:
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    cmd = [python_executable, str(script_path)]
    if extra_args:
        cmd.extend(extra_args)
    return run_command(cmd, cwd=cwd, log_dir=log_dir, label=label or script_path.stem, env=env)


def run_command(
    command: list[str],
    *,
    cwd: Path | None = None,
    log_dir: Path | None = None,
    label: str | None = None,
    env: dict[str, str] | None = None,
) -> ExecutionResult:
    if not command:
        raise ValueError('Command must not be empty.')
    if cwd is not None and not cwd.exists():
        raise FileNotFoundError(f"Working directory not found: {cwd}")

    execution_label = label or Path(command[0]).stem or 'run'

    log_path = None
    log_handle = None
    if log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        safe_label = re.sub(r'[^A-Za-z0-9._-]+', '_', execution_label).strip('_') or 'run'
        log_path = log_dir / f'{timestamp}_{safe_label}.log'
        log_handle = log_path.open('w', encoding='utf-8')

    print(f"[cellpaint_pipeline] running: {shlex.join(command)}")
    if cwd is not None:
        print(f"[cellpaint_pipeline] cwd: {cwd}")
    if log_path is not None:
        print(f"[cellpaint_pipeline] log: {log_path}")

    output_tail: deque[str] = deque(maxlen=20)
    try:
        try:
            process = subprocess.Popen(
                command,
                cwd=str(cwd) if cwd else None,
                env=({**os.environ, **env} if env else None),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
        except OSError as exc:
            raise CommandExecutionError(
                label=execution_label,
                command=command,
                cwd=cwd,
                log_path=log_path,
                returncode=None,
                reason=str(exc),
            ) from exc

        assert process.stdout is not None
        for line in process.stdout:
            print(line, end='')
            output_tail.append(line.rstrip())
            if log_handle is not None:
                log_handle.write(line)
        returncode = process.wait()
    finally:
        if log_handle is not None:
            log_handle.close()

    result = ExecutionResult(
        label=execution_label,
        command=command,
        cwd=cwd,
        log_path=log_path,
        returncode=returncode,
    )
    if returncode != 0:
        raise CommandExecutionError(
            label=execution_label,
            command=command,
            cwd=cwd,
            log_path=log_path,
            returncode=returncode,
            output_tail=list(output_tail),
        )
    return result
