"""Model transport. Authentication stays with the locally installed Codex CLI."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import time


class ProviderError(RuntimeError):
    pass


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


class CodexProvider:
    """One fresh, structured inference per turn; conversation is supplied explicitly.

    No evaluation logic or course tools run inside Codex. The runner alone executes
    decisions against the simulator. Native CLI tool use is rejected and recorded.
    """

    def __init__(self, output_dir, model="gpt-6.1-sol", effort="medium", timeout=120):
        self.output_dir = Path(output_dir)
        self.model, self.effort, self.timeout = model, effort, timeout
        self.executable = shutil.which("codex")
        if not self.executable:
            raise ProviderError("Codex CLI was not found. Install it and run 'codex login', then retry.")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.workspace = self.output_dir / "model-workspace"
        self.workspace.mkdir(exist_ok=True)
        self.calls = {"agent": 0, "user": 0}
        self.version = subprocess.run([self.executable, "--version"], capture_output=True,
                                      text=True, encoding="utf-8", timeout=15).stdout.strip()

    def describe(self):
        return {
            "provider": "codex-cli", "cli_version": self.version,
            "model_version": self.model, "model_version_kind": "requested_model_alias",
            "immutable_backend_snapshot": None,
            "version_note": "The CLI does not expose an immutable backend model snapshot in its JSONL response.",
            "reasoning_effort": self.effort, "request_timeout_seconds": self.timeout,
            "transport": "fresh ephemeral CLI inference with explicit full conversation",
            "temperature": "not set; provider default", "user_config_loaded": False,
            "native_tools": "disabled where configurable; any observed native tool item fails the run"
        }

    def complete(self, role, prompt, schema_path):
        self.calls[role] += 1
        stem = self.output_dir / f"{role}-{self.calls[role]:03d}"
        schema_path = Path(schema_path)
        command = [self.executable, "exec", "--ignore-user-config", "--ephemeral",
                   "--skip-git-repo-check", "--sandbox", "read-only", "--model", self.model,
                   "--config", f'model_reasoning_effort="{self.effort}"',
                   "--config", 'web_search="disabled"', "--json", "--color", "never",
                   "--output-schema", str(schema_path.resolve()), "--cd", str(self.workspace.resolve())]
        for feature in ["shell_tool", "apps", "plugins", "browser_use", "computer_use",
                        "image_generation", "multi_agent", "multi_agent_v2", "sleep_tool",
                        "goals", "view_image", "shell_snapshot", "hooks", "skill_search",
                        "workspace_dependencies", "code_mode", "code_mode_only"]:
            command.extend(["--disable", feature])
        command.append("-")
        write_json(stem.with_suffix(".request.json"), {
            "role": role, "timestamp": utc_now(), "command": command,
            "prompt": prompt, "schema": json.loads(schema_path.read_text(encoding="utf-8"))
        })
        started = time.monotonic()
        try:
            result = subprocess.run(command, input=prompt, capture_output=True,
                                    text=True, encoding="utf-8", errors="replace", timeout=self.timeout)
            stdout, stderr = result.stdout, result.stderr
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or b""
            stderr = exc.stderr or b""
            if isinstance(stdout, bytes): stdout = stdout.decode("utf-8", errors="replace")
            if isinstance(stderr, bytes): stderr = stderr.decode("utf-8", errors="replace")
            stem.with_suffix(".events.jsonl").write_text(stdout, encoding="utf-8")
            stem.with_suffix(".stderr.txt").write_text(stderr, encoding="utf-8")
            raise ProviderError(f"{role} inference timed out after {self.timeout}s; partial output saved at {stem}") from exc
        stem.with_suffix(".events.jsonl").write_text(stdout, encoding="utf-8")
        stem.with_suffix(".stderr.txt").write_text(stderr, encoding="utf-8")
        if result.returncode:
            raise ProviderError(f"Codex exited {result.returncode}; inspect {stem.with_suffix('.stderr.txt')}")
        events, replies, usage = [], [], {}
        for line in stdout.splitlines():
            if not line.strip(): continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ProviderError(f"Unexpected non-JSON CLI output; preserved at {stem}") from exc
            events.append(event)
            item = event.get("item", {})
            if event.get("type", "").startswith("item."):
                if item.get("type") == "error":
                    raise ProviderError(f"CLI returned an error item: {item.get('message')}; raw events preserved at {stem}")
                if item.get("type") not in ("agent_message", "reasoning"):
                    raise ProviderError(f"Native CLI tool/item {item.get('type')} was used; run excluded, raw events preserved.")
                if event["type"] == "item.completed" and item.get("type") == "agent_message":
                    replies.append(item.get("text", ""))
            if event.get("type") in ("error", "turn.failed"):
                raise ProviderError(f"CLI inference failed: {event}")
            if event.get("type") == "turn.completed": usage = event.get("usage", {})
        if not replies:
            raise ProviderError(f"No model message returned; inspect {stem}")
        try:
            value = json.loads(replies[-1])
        except json.JSONDecodeError as exc:
            raise ProviderError(f"Model returned invalid structured JSON; inspect {stem}") from exc
        write_json(stem.with_suffix(".response.json"), value)
        return value, {"role": role, "request_prefix": stem.name, "events": events,
                       "usage": usage, "duration_seconds": time.monotonic() - started}
