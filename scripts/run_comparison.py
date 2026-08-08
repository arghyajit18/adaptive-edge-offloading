#!/usr/bin/env python3
import asyncio, csv, time
from pathlib import Path
from adaptive_engine.client.task_generator import TaskGenerator
from adaptive_engine.client.local_executor import LocalExecutor
from adaptive_engine.scheduler.always_local import AlwaysLocalScheduler
from adaptive_engine.scheduler.always_edge import AlwaysEdgeScheduler
from adaptive_engine.scheduler.greedy import GreedyScheduler
from adaptive_engine.scheduler.adaptive import AdaptiveScheduler
from adaptive_engine.network.link_monitor import LinkMonitor
from adaptive_engine.metrics.store import MetricsStore
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from adaptive_engine.metrics.models import Base
from adaptive_engine.config import settings
async def run_one_scheduler(name, scheduler, tasks, executor, link_monitor, store):
    rows = []
    for req in tasks:
        decision = await scheduler.schedule(req)
        if decision.value == "LOCAL":
            pred_lat, pred_en = executor.execute(req)
        else:
            metric = link_monitor.current() or {"bandwidth_mbps":120,"rtt_ms":2,"loss":0.001}
            bw, rtt, loss = metric"bandwidth_mbps", metric"rtt_ms", metric"loss"
            upload_ms = (req.input_size_bytes*8)/(bw1e6)1e3/max(1-loss,1e-3)
            edge_compute_ms = (req.compute_complexityreq.input_size_bytes)/1e101e3
            pred_lat = upload_ms + rtt + edge_compute_ms
            pred_en = (req.input_size_bytes/1e6)*5.0
        act_lat, act_en = executor.execute(req)
        deadline_met = act_lat <= req.deadline_ms
        rows.append({
            "task_id":req.task_id,
            "scheduler":name,
            "decision":decision.value,
            "pred_lat_ms":round(pred_lat,2),
            "pred_energy_mj":round(pred_en,2),
            "actual_lat_ms":round(act_lat,2),
            "actual_energy_mj":round(act_en,2),
            "deadline_met":deadline_met,
        })
        await asyncio.sleep(0.05)
    return rows
async def main():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
class StaticLinkMonitor:
    def current(self): return {"bandwidth_mbps":120,"rtt_ms":2,"loss":0.001}
link_monitor = StaticLinkMonitor()
store = MetricsStore(sessionmaker)
executor = LocalExecutor()
gen = TaskGenerator()
tasks = [next(gen) for _ in range(settings.comparison.num_tasks)]

schedulers = {
    "AlwaysLocal": AlwaysLocalScheduler(),
    "AlwaysEdge": AlwaysEdgeScheduler(),
    "Greedy": GreedyScheduler(link_monitor),
    "Adaptive": AdaptiveScheduler(link_monitor),
}

all_rows = []
for name, sched in schedulers.items():
    print(f"Running {name} …")
    all_rows.extend(await run_one_scheduler(name, sched, tasks, executor, link_monitor, store))

out_dir = Path("results")
out_dir.mkdir(exist_ok=True)
ts = time.strftime("%Y%m%d-%H%M%S")
csv_path = out_dir / f"comparison_{ts}.csv"
with csv_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
    writer.writeheader()
    writer.writerows(all_rows)
print(f"✅  Results written to {csv_path}")
if name == "main":
    asyncio.run(main())
