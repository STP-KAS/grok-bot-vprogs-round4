> **Experimental. We are just trying this.**
>
> Good intentions, shaky hands. STP does not know what he is doing. We test, we write down what we think we saw, and that is the whole product. A number here is not the truth. A chart is not the truth. Any other sentence that sounds sure of itself is not the truth either. Do not count any of it as a claim.
>
> [Disclaimer](DISCLAIMER.md)

> **Experimental only. Not a product.**
>
> Do not use wallet integrations on this GitHub. STP remains a clown. [DISCLAIMER.md](DISCLAIMER.md)

# grok-bot-vprogs round 4 — final (up to 09:20 CEST)

Report by Grok (acting for stp), 26 Sep 2026. All times are CEST (Europe/Brussels).
**Round 4 final report, with data up to 09:20 CEST on 26 Sep 2026.** At 09:17 the user changed the plan: storm until the faucet is empty, plus our own index-free tic-tac-toe and vprog runners. That work (the 11:52 stop removed, higher TPS/fee) is round 5: [STP-KAS/grok-bot-vprogs-round5](https://github.com/STP-KAS/grok-bot-vprogs-round5). The storm config was left unchanged until this report was pushed; round 5 records the switch time.

Next rounds: [round 5](https://github.com/STP-KAS/grok-bot-vprogs-round5), [round 6](https://github.com/STP-KAS/grok-bot-vprogs-round6), [round 7](https://github.com/STP-KAS/tn10-vprogs-round7-ideas), [round 8](https://github.com/STP-KAS/tn10-vprogs-round8-covenants). Previous rounds: [round 1](https://github.com/STP-KAS/grok-bot-vprogs-round1-public) (public clean copy), [round 2](https://github.com/STP-KAS/grok-bot-vprogs-round2), and [round 3](https://github.com/STP-KAS/grok-bot-vprogs-round3).

## Executive summary

Round 4 combined a Kaspa TN10 transaction storm, the `grok-deskfloor` vprog runner, and tic-tac-toe. The full-gusto windows measured high throughput but exposed two operational limits: TN10 periodic pruning/compaction can require more than 15 GB transient disk, and the mempool brake reacts too slowly when senders are already in flight. The node survived after an emergency stop, removal of the rebuildable `utxoindex`, and restart.

From 07:46 the storm ran as a **paced 6x-fee run** (P-tag fee 385,800 sompi/tx). Over 07:46:20–09:18:15 (1 h 32 min) it averaged **1,219 accepted tx/s** (1,255/s steady-state after 08:02, peak 1,378/s), about **6.7 M transactions**. Storm fees were **26,006 TKAS** (≈283 TKAS/min; the storm pools fell 78.9k→49.3k TKAS). Mempool max was **2,148** (average 318). Disk went 23.7→20.6 GB free (≈2.1 GB/h), RAM available never dropped below 5.4 GB, and **no guard fired** (552 pacer ticks, all unguarded). n0 stayed synced on the same pid for the whole run.

## What and how

- Testnet TN10 only, one node `n0`, no mainnet activity and no spending from the Grok Build wallet.
- Storm: `scripts/tps-supervisor.py` plus eight P2SH `rwstorm.mjs` workers and one 0.5-TKAS P2PK lane.
- The original full-gusto fee was 10x (P tag 643,000 sompi/tx, about 1,000 sompi/g). The paced run was restarted with `FEE_MULT_P=6.0` (P tag 385,800 sompi/tx).
- Supervisor safeguards: mempool taper/gate and hard brake; live disk guard; stale-worker-TPS fix; `STOP-FILE-PRESENT` logging; conditional `--utxoindex` on auto-restart.
- Standalone round-4 pacer: disk <12 GB, resume >15 GB, >3 GB/120 s drop latch for 10 minutes, mempool >80k with resume below 40k, n0 crash/RPC/sync latch, and the 11:52 stop.
- Measurements use `logs/tps12h/supervisor.jsonl`, `logs/storm/ramp.log`, `logs/monitor.jsonl`, `logs/round4/pacer.jsonl`, Kaspa processed-TPS lines, and the round-4 analysis scripts.

## Timeline (CEST, 26 Sep)

| time | event |
|---|---|
| 01:13–05:25 | 10x storm at about 1,000 tx/s; disk 17.9→9.7 GB; about 109,240 TKAS in fees |
| 05:25–06:30 | disk taper reduced the storm from 1,000 tx/s to zero |
| 06:31 | RECOVERY-1 fired with mempool 7; there was no recovery workload/data |
| 06:38–06:41 | round-4 cleanup and supervisor patch; W3 funded for vprog work |
| 06:43:44–06:55:44 | full gusto 1; 10 GB guard stopped the storm at 9.94 GB free |
| 07:02 | second cleanup recovered about 2.1 GB |
| 07:03:19 | TN10 periodic pruning-point move began |
| 07:04:52–07:07:36 | full gusto 2; guard stopped the storm after 2m44s |
| 07:07–07:10 | pruning/compaction grew consensus data about 75→89 GB; free space reached zero |
| 07:09–07:12 | n0 was halted; `utxoindex` (about 13 GB) was deleted; n0 restarted without it |
| 07:16 onward | full gusto 3, storm only, with 12 GB guard and 3 GB/120 s drop guard |
| 07:28 | mempool near-miss: 96,546 and 6,223 evictions; hard brake reaction was too slow |
| 07:34–07:46 | r4-pacer paced run at 10x (funds-bound, about 440 tx/s) |
| 07:46 | supervisor/pacer restarted at 6x fee; workers ramped to the paced rate |
| 07:52 | run shortened to 11:52; pacer recomputed (disk ≈1,360/s vs funds ≈1,400/s) |
| 08:00 | conservative blended fee 0.0043 TKAS/tx; RATE_MAX ≈1,257/s |
| 09:17 | user: run until the faucet is empty, add our own ttt and vprogs, remove 11:52 stop → **round 5** |
| 09:20 | round 4 report finalized |

## Results: full gusto 1 (06:43:44–06:55:44)

| metric | result |
|---|---:|
| accepted transaction rate | average 3,558/s; median 3,601/s; p90 4,733/s; peak 5,996/s |
| network processed TPS | average 5,001; median 5,062; peak 6,259 |
| blocks / 10 s | average 74; lower than nominal 100 under load |
| transactions / block | average 693; peak 827 |
| mempool | average 47.6k; max 72,600; zero evictions |
| storm fees | 17,222 TKAS |
| disk | 11.41→9.98 GB, about 7 GB/h; 10 GB guard stopped the storm |
| RAM / load / kaspad CPU | 6.0 GB average (5.6 GB minimum) / 25.6 / 196% |
| mempool drain | 54,294→<1k in 85 s after stop |

The vprog runner used 16 issuers at fixed 2,000 sompi/g (2x the storm fee): 37,963 moves in the full-gusto window, all executed; execution latency p50/p90/p99 was 8.1/14.4/21.5 s. Across the measured phases it submitted 85,891 moves, executed 81,587, and had zero impossible-debit results among 4,291 checked executions.

Tic-tac-toe (unpatched carriers) completed only 8 games in this full-gusto window and recorded 1,223 `GAME_FAIL` results. Fresh keys did not panic; fragmented-UTXO workers later did.

## Results: full gusto 2 (07:04:52–07:07:36)

| metric | result |
|---|---:|
| accepted transaction rate | average 2,334/s; peak 3,535/s |
| network processed TPS | average 3,698/s |
| mempool | max about 20k |
| storm fees | 2,595 TKAS |
| disk | 11.9→9.96 GB; pruning/compaction made the slope much worse |
| reason stopped | 10 GB guard after 2m44s |

The reduced rate was not a node-capacity result: the TN10 pruning-point move started at 07:03:19 and RocksDB was doing transient compaction work.

## Results: vprog and tic-tac-toe behavior

- `grok-deskfloor` at 2x storm fee ran 69,494 executed moves out of 73,184 issued in the overnight run, with execution p50 2.6 s, p90 3.4 s, p99 4.2 s, and zero bad executions among 3,675 checked. Issuers ran dry around 01:29.
- Under full load, the priority-fee runner reached roughly 100–130 moves/s briefly, then its fee estimate jumped to about 4,500 sompi/g and its 16 issuers ran nearly dry. The x2 runner managed only about 22–34 moves/s, with p50/p90/p99 execution latency 9.5/18.6/23 s.
- Tic-tac-toe at a 1k background storm completed 419 games (p50 14.1 s) but had 251 failures from UTXO reuse. During full storm it completed 5 games and had 1,322 failures; games resumed about 100 s after the storm stopped.
- A fee-floor proxy raising `getFeeEstimate` to 2,000 sompi/g did not change carrier fees. Carrier transactions price with `min_fee`, not the estimate. A release rebuild to add a fee knob did not fit the disk/RAM budget.
- Fragmented UTXOs caused the carrier assertion panic: all 8 workers in one round-3 run and all 4 `ttloop-f` workers in round 4 (funding UTXO about 0.149 TKAS below the 0.4-TKAS deposit).

## Results: full gusto 3 (07:16:07–07:33:41, storm only, no utxoindex)

| metric | 07:16:07–07:28:18 | whole window to 07:33:41 |
|---|---:|---:|
| accepted tx/s (ours) | avg 4,568; median 4,727; p90 5,745; **peak 7,652** | avg 3,942 |
| network processed TPS | avg 7,075; p90 8,184; peak 8,928 | avg 6,511; **peak 8,973** |
| blocks / 10 s | avg 90 | avg 94 |
| tx / block | avg 789; peak 855 | avg 705 |
| mempool | avg 38.3k; **max 96,546** | avg 40.5k |
| storm fees (10x) | 22,068 TKAS | 27,444 TKAS |
| disk free | 25.18→24.54 GB | 25.18→23.50 GB |
| RAM avail min / kaspad CPU avg | 7.25 GB / 281% | 6.68 GB / 245% |

This was the best throughput in round 4. n0 had just pruned, had no `utxoindex`, and had 25 GB free. It ended with the mempool near-miss (below) and the switch to the pacer.

## 07:10 disk emergency

The storm had already been stopped, but the TN10 pruning-point move and RocksDB compaction continued growing consensus storage at roughly 50 MB/s. Free space went from about 9.9 GB at 07:07:36 to 5.3 GB at 07:09:16 and then to zero. A graceful SIGINT hung inside pruning. n0 was frozen at about 44 MB free and then terminated; the rebuildable 13 GB `utxoindex` was deleted. n0 restarted without `--utxoindex`, caught up, and completed header/block and SMT pruning. Consensus data was not corrupted. Vprog and tic-tac-toe were left stopped because rebuilding the index would again require about 13 GB and roughly 18 minutes offline.

## 07:28 mempool near-miss

At 07:28:18 the mempool reached 96,546 and kaspad evicted 6,223 transactions. The brake had set `RATE_MAX=0`, but workers already had 6–9 seconds of in-flight work and continued offering 3–7k tx/s. A later 91,341 spike showed that stop/start gating at thousands of tx/s is unsafe. The paced run uses a much lower rate and an 80k brake; during the 6x restart the mempool remained in the low hundreds.

## Paced 6x run (07:46–09:18 CEST)

Setup: supervisor `FEE_MULT_P=6.0`, eight P workers plus the H lane, and `scripts/r4-pacer.py` pacing `RATE_MAX = min(disk_rate, fund_rate)` toward the 11:52 end. Config: 600 B/tx, 12.5 GB planning floor, 12 GB guard / 15 GB resume, mempool 80k/40k, >3 GB/120 s drop hold, and the n0 crash latch. Fee model: conservative blended 0.0043 TKAS/tx (P 0.003858, H 0.009744).

Data: `logs/tps12h/supervisor.jsonl` (1,848 samples, 3 s) and `logs/round4/pacer.jsonl` (552 ticks, 10 s).

| metric | 07:46:20–09:18:15 |
|---|---:|
| accepted tx/s | **avg 1,219**; steady state after 08:02 avg 1,255 (max 1,267); **peak 1,378** during the ramp |
| transactions | ≈6.7 M |
| P-tag fee | 385,800 sompi/tx (6x); H lane 974,400 sompi/tx |
| storm fee burn | **26,006 TKAS** (supervisor counter 2,674→28,680), ≈283 TKAS/min, ≈17k TKAS/h |
| storm pool | 78,900 → 49,308 TKAS |
| mempool | **max 2,148**, avg 318, far below the 80k brake and the 100k panic |
| disk free | 23.73 → 20.55 GB (≈2.1 GB/h; the 600 B/tx model was pessimistic) |
| RAM available | min 5.37 GB |
| guard events | **none**: no mempool brake, disk guard, drop hold, or n0 latch |
| n0 | pid 2341090 all run, synced, no `utxoindex` |
| binding limit | funds model (≈1,238/s at 09:18) below disk model (≈1,560/s) |

A steady paced rate at about 1.25k tx/s keeps the mempool in the hundreds. Stop/start gating at 4–7k tx/s swung it to 96k. For long runs, sustained TPS is limited by the fee budget and the disk slope, not by node capacity.

Note: the `nettps` logger (pid 2426338) died around 07:46, so network-wide processed TPS for the paced run is missing. The storm's accepted rate is the headline number here.

## Public explorer indexer stall

The public TN10 indexer (api-tn10.kaspa.org, apparently also kaspa.stream) froze network-wide at 2026-09-25 21:55:38 CEST, about 7 minutes into the round-1 PHASE1 overload, and was still frozen through round 4. Balances stay live because they come from kaspad; the transaction list does not. Mining rewards were verified to the sompi. Details: [STP-KAS/grok-bot-explorer-rewards-check](https://github.com/STP-KAS/grok-bot-explorer-rewards-check).

## Flaws and operational lessons

1. A 100k mempool assertion makes a high-rate brake inherently dangerous when workers have in-flight requests; the brake must act well below the cap and use a slower ramp.
2. Supervisor logs previously reported stale worker TPS after a worker stopped; stale lines are now ignored after 25 seconds.
3. A sticky global STOP file makes workers exit immediately while a supervisor respawns them. The supervisor now records the condition explicitly; operators must clear it only after checking the cause.
4. TN10 disk planning based only on steady-state bytes/transaction misses pruning-point compaction bursts. A 12 GB guard is not sufficient during a transient that needs more than 15 GB.
5. Rebuilding `utxoindex` is a substantial offline and disk event; it should not be attempted near the pruning-point window.
6. Vprog carrier fee selection is not estimator-aware, and carrier UTXO selection can panic on fragmented funds.
7. Pacing works: a rate spread from funds and disk ran 1.5 h with zero guard events. The 10x→6x fee change nearly tripled the affordable TPS (≈440→≈1,250/s).
8. Upstream vprogs/ttt runtimes depend on `utxoindex`. Losing it in the emergency ended vprog work, so round 5 uses our own index-free runners.
9. Single-point loggers (nettps) can die silently. The supervisor needs a liveness check for its side loggers.

## Ideas / next steps

- Keep sustained storm rate below the mempool reaction envelope; use a pacer that reserves both fee funds and transient disk, with a separate H-lane fee budget.
- Require a much larger free-space reserve before TN10 pruning-point moves, or stop cleanly before the expected window.
- Add a carrier `FeePolicy`/feerate parameter and return an ordinary insufficient-funds error instead of asserting on the first too-small UTXO.
- Add a preflight that measures the largest required carrier transaction, available UTXOs, and RAM/disk headroom before launching multi-worker vprog tests.
- Round 5: storm until the faucet is empty, plus index-free tic-tac-toe and vprog runners → [grok-bot-vprogs-round5](https://github.com/STP-KAS/grok-bot-vprogs-round5).

## Draft upstream issues (not filed)

These are drafts only; no upstream issue was filed:

- **U1 — vprogs carrier fee policy:** carrier transactions should accept a `FeePolicy`/target feerate (or an explicit configuration knob) instead of always using the relay-floor `min_fee`.
- **U2 — vprogs carrier UTXO selection:** choose a sufficiently large UTXO or combine inputs, and return an error rather than asserting when the first candidate is too small.
- **U3 — rusty-kaspa/TN10 disk documentation:** document pruning-window storage and transient space requirements, including the additional `--utxoindex` footprint.

Details and reproduction helpers are in `upstream-issues/README.md`, `scripts/`, and `patches/`.
