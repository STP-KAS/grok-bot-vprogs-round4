#!/usr/bin/env python3
"""round4: load stats for a window from supervisor.jsonl, nettps (live + backfill), monitor.jsonl, guard.jsonl.
usage: r4-window-stats.py HH:MM:SS HH:MM:SS"""
import json, sys, statistics as st, glob
A, B = sys.argv[1], sys.argv[2]; D = "/workspace/tn10-break-test-2026-09-25/logs"
inw = lambda t: A <= t[11:19] <= B and t[:10] == "2026-09-26"
sup = [json.loads(l) for l in open(f"{D}/tps12h/supervisor.jsonl") if l.startswith('{"t": "2026-09-26')]
sup = [d for d in sup if "accepted_tps" in d and inw(d["t"])]
net = {}
for f in (f"{D}/round4/nettps-backfill.jsonl", f"{D}/tps12h/nettps.jsonl"):
    for l in open(f):
        try: d = json.loads(l)
        except Exception: continue
        if inw(d["t"]): net[d["t"][:19]] = d
net = list(net.values())
mon = [json.loads(l) for l in open(f"{D}/monitor.jsonl") if '"2026-09-26' in l[:30]]
mon = [d for d in mon if inw(d["t"])]
def s(x): x = sorted(x); return {"avg": round(sum(x) / len(x), 1), "median": round(st.median(x), 1), "p90": x[int(.9 * len(x))], "max": x[-1], "min": x[0], "n": len(x)} if x else None
out = {"window": [A, B],
       "accepted_tps_ours": s([d["accepted_tps"] for d in sup]),
       "net_tps": s([d["net_tps"] for d in net]),
       "blocks_per_10s": s([d["blocks"] for d in net]),
       "tx_per_block": s([d["tpb"] for d in net]),
       "mempool": s([d["nodes"]["n0"]["mempool"] for d in sup if d["nodes"].get("n0", {}).get("mempool") is not None]),
       "fees_tkas_storm": round(sup[-1]["fees_tkas"] - sup[0]["fees_tkas"], 1) if sup else None,
       "disk_free_gb": [sup[0]["disk_free_gb"], sup[-1]["disk_free_gb"]] if sup else None,
       "mem_avail_mb": s([d["mem_avail_mb"] for d in mon]),
       "load1": s([d["load1"] for d in mon]),
       "kaspad_cpu_pct": s([d["n0"]["cpu_pct"] for d in mon if d["n0"].get("cpu_pct") is not None]),
       "kaspad_rss_mb": s([d["n0"]["rss_mb"] for d in mon if d["n0"].get("rss_mb")])}
print(json.dumps(out, indent=1))
