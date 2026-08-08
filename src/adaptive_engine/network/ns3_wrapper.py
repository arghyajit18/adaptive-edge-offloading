import asyncio
import json
import shlex
from pathlib import Path
from typing import AsyncIterator, Dict
from adaptive_engine.config import settings


class Ns3Wrapper:
    """Spawns the ns‑3 binary and yields parsed metric dicts line‑by‑line."""
    def __init__(self, binary: Path | None = None, tick_ms: int | None = None):
        self.binary = binary or Path(settings.ns3.binary_path)
        self.tick_ms = tick_ms or settings.ns3.tick_ms
        self._proc: asyncio.subprocess.Process | None = None

    async def start(self) -> None:
        cmd = f"{self.binary} --tickMs={self.tick_ms}"
        self._proc = await asyncio.create_subprocess_exec(
            *shlex.split(cmd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        asyncio.create_task(self._log_stderr())

    async def _log_stderr(self) -> None:
        assert self._proc and self._proc.stderr
        async for line in self._proc.stderr:
            print(f"[ns3‑stderr] {line.decode().rstrip()}")

    async def metrics(self) -> AsyncIterator[Dict]:
        assert self._proc and self._proc.stdout
        async for raw in self._proc.stdout:
            line = raw.decode().strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue

    async def stop(self) -> None:
        if self._proc and self._proc.returncode is None:
            self._proc.terminate()
            await self._proc.wait()
