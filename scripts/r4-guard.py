#!/usr/bin/env python3
"""round4 live guard (TN10). Every 5 s:
- free disk < 10.0 GB -> storm RATE_MAX=0 (supervisor also has /tmp/tps-storm.diskguard=10.0)
- free disk < 9.3 GB  -> vprog runner rate 0 (/tmp/gd-rate) and SIGTERM the ttloop pids given in argv (exact pids)
- n0 mempool > 95,000 -> RATE_MAX=0 at once (kaspad panics at 100k)
Logs to logs/round4/guard.jsonl and major actions to logs/storm/ramp.log."""
import json, shutil, sys, time, os, subprocess, asyncio, websockets
D = "/workspace/tn10-break-test-2026-09-25"; L = f"{D}/logs/round4/guard.jsonl"; R = f"{D}/logs/storm/ramp.log"
TT = [int(x) for x in sys.argv[1:]]
def log(o):
    o = {"t": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **o}; open(L, "a").write(json.dumps(o) + "\n")
def ramp(s): open(R, "a").write(time.strftime("%Y-%m-%dT%H:%M:%S%z") + " R4-GUARD " + s + "\n")
async def mp():
    try:
        async with websockets.connect("ws://127.0.0.1:18210", open_timeout=3) as ws:
            await ws.send(json.dumps({"id": 1, "method": "getInfo", "params": {}})); r = json.loads(await asyncio.wait_for(ws.recv(), 5))
            return int(r["params"]["mempoolSize"])
    except Exception: return -1
def set_rmax(v):
    a = open("/tmp/tps-storm.limits").read().split(); a[3] = str(v); open("/tmp/tps-storm.limits", "w").write(" ".join(a))
storm_cut = vp_cut = False
while True:
    d = shutil.disk_usage("/").free / 2**30; m = asyncio.run(mp())
    if m > 95000: set_rmax(0); ramp(f"mempool {m} > 95k -> RATE_MAX=0"); log({"ev": "mp-brake", "mp": m})
    if d < 10.0 and not storm_cut:
        set_rmax(0); storm_cut = True; ramp(f"disk {d:.2f}G < 10.0 -> storm RATE_MAX=0"); log({"ev": "storm-cut", "disk": round(d, 2), "mp": m})
    if d < 9.3 and not vp_cut:
        open("/tmp/gd-rate", "w").write("0")
        for p in TT:
            try: os.kill(p, 15)
            except Exception: pass
        vp_cut = True; ramp(f"disk {d:.2f}G < 9.3 -> gd-rate 0 + SIGTERM ttloop {TT}"); log({"ev": "vprog-cut", "disk": round(d, 2)})
    log({"disk": round(d, 3), "mp": m})
    time.sleep(5)
