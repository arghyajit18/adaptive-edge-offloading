import asyncio
import json
import sys
import textwrap
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))
from adaptive_engine.network.ns3_wrapper import Ns3Wrapper


MOCK_NS3 = textwrap.dedent("""\
    #!/usr/bin/env python3
    import json, time, sys
    for i in range(2):
        print(json.dumps({"bandwidth_mbps": 100 + i, "rtt_ms": 5, "loss": 0.01, "sinr_db": 20}))
        sys.stdout.flush()
        time.sleep(0.01)
""")


class _FakeStdout:
    def __init__(self, lines):
        self._lines = [l.encode() + b"\n" for l in lines]

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._lines:
            raise StopAsyncIteration
        return self._lines.pop(0)


class _FakeProc:
    def __init__(self):
        # Two fake JSON metric lines, as ns-3 would print them on stdout
        lines = [
            json.dumps({"bandwidth_mbps": 100 + i, "rtt_ms": 5, "loss": 0.01, "sinr_db": 20})
            for i in range(2)
        ]
        self.stdout = _FakeStdout(lines)
        self.stderr = _FakeStdout([])
        self.returncode = None          # wrapper.stop() checks this

    async def wait(self):
        return 0

    def terminate(self):
        pass


@pytest.mark.asyncio
async def test_wrapper_parses_json_lines():
    # Create wrapper *without* launching a real subprocess
    wrapper = Ns3Wrapper(tick_ms=10)      # binary argument is ignored
    # Inject our fake process directly
    wrapper._proc = _FakeProc()

    # Use a normal async‑for loop – works reliably on Windows
    metrics = []
    async for m in wrapper.metrics():
        metrics.append(m)
        if len(metrics) == 2:
            break

    await wrapper.stop()   # harmless – just checks returncode

    assert len(metrics) == 2
    assert metrics[0]["bandwidth_mbps"] == 100
    assert metrics[1]["bandwidth_mbps"] == 101
