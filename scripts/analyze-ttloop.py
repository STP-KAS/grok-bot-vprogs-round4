#!/usr/bin/env python3
"""Summarize ttloop logs: games finished / timeouts / GAME_FAIL / panics, game_ms p50/p90, per time window.
usage: analyze-ttloop.py LOG [LOG..] [--from HH:MM:SS --to HH:MM:SS]"""
import re, sys, statistics as st
args = sys.argv[1:]; fr = to = None
if "--from" in args: i = args.index("--from"); fr = args[i + 1]; del args[i:i + 2]
if "--to" in args: i = args.index("--to"); to = args[i + 1]; del args[i:i + 2]
for f in args:
    fin = []; fail = to_n = pan = sub = 0; first = last = None
    for l in open(f, errors="ignore"):
        m = re.match(r"\d{4}-\d\d-\d\d (\d\d:\d\d:\d\d)", l); ts = m.group(1) if m else None
        if ts and ((fr and ts < fr) or (to and ts > to)): continue
        if "panicked" in l: pan += 1
        if not ts: continue
        if "GAME_FINISHED" in l: fin.append(int(re.search(r"game_ms=(\d+)", l).group(1))); first = first or ts; last = ts
        elif "GAME_TIMEOUT" in l: to_n += 1
        elif "GAME_FAIL" in l: fail += 1
        elif "GAME_SUBMITTED" in l: sub += 1
    q = lambda p: round(sorted(fin)[min(len(fin) - 1, int(p * len(fin)))] / 1000, 1) if fin else None
    print(f"{f}: submitted={sub} finished={len(fin)} fail={fail} timeout={to_n} panics={pan} game_p50_s={q(.5)} p90_s={q(.9)} first={first} last={last}")
