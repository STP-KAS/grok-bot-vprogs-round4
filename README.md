# grok-bot-vprogs round 4 — INTERIM

Private report by Grok (acting for stp), 26 Sep 2026. All times are CEST (Europe/Brussels).
**This is an interim report. The final paced-run numbers will be added after the scheduled 11:52 CEST stop.**

Previous rounds: [round 1](https://github.com/STP-KAS/grok-bot-vprogs/tree/tn10-break-report) (branch `tn10-break-report`), [round 2](https://github.com/STP-KAS/grok-bot-vprogs-round2), and [round 3](https://github.com/STP-KAS/grok-bot-vprogs-round3).

## Executive summary

Round 4 combined a Kaspa TN10 transaction storm, the `grok-deskfloor` vprog runner, and tic-tac-toe. The full-gusto windows measured high throughput but exposed two operational limits: TN10 periodic pruning/compaction can require more than 15 GB transient disk, and the mempool brake reacts too slowly when senders are already in flight. The node survived after an emergency stop, removal of the rebuildable `utxoindex`, and restart.

The storm is now in a **4-hour paced run to 11:52 CEST**, restarted at **6x minimum fee**. P-tag fee is 385,800 sompi/transaction (6 × the 64,300-sompi base used here). The pacer is currently conservatively fee-limited at about 1,257 accepted tx/s (disk model about 1,360/s), with a low mempool and n0 synced. Final burn and disk measurements are deliberately pending.

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
| 07:46 | 10x supervisor/pacer replaced; new 6x workers reached the disk-paced rate |
| 11:52 | scheduled stop; final numbers and conclusions will be appended then |

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

## 07:10 disk emergency

The storm had already been stopped, but the TN10 pruning-point move and RocksDB compaction continued growing consensus storage at roughly 50 MB/s. Free space went from about 9.9 GB at 07:07:36 to 5.3 GB at 07:09:16 and then to zero. A graceful SIGINT hung inside pruning. n0 was frozen at about 44 MB free and then terminated; the rebuildable 13 GB `utxoindex` was deleted. n0 restarted without `--utxoindex`, caught up, and completed header/block and SMT pruning. Consensus data was not corrupted. Vprog and tic-tac-toe were left stopped because rebuilding the index would again require about 13 GB and roughly 18 minutes offline.

## 07:28 mempool near-miss

At 07:28:18 the mempool reached 96,546 and kaspad evicted 6,223 transactions. The brake had set `RATE_MAX=0`, but workers already had 6–9 seconds of in-flight work and continued offering 3–7k tx/s. A later 91,341 spike showed that stop/start gating at thousands of tx/s is unsafe. The paced run uses a much lower rate and an 80k brake; during the 6x restart the mempool remained in the low hundreds.

## Interim paced run (6x; final after 11:52)

At restart, the live state was approximately 79k TKAS in the storm state files and 23.7 GB free. The pacer configuration uses 600 bytes/transaction, a 12.5 GB planning floor, a 12 GB hard guard, a 15 GB resume threshold, and a conservative blended `FEE_TKAS_PER_TX=0.0043`. The exact 6x P-tag fee remains 0.003858 TKAS (385,800 sompi); the blend accounts for the H lane (0.009744 TKAS base fee).

Observed after ramp-up:

| metric | interim observation |
|---|---:|
| P-tag fee | 385,800 sompi/tx |
| H-lane fee sample | 974,400 sompi/tx base lane fee at 6x |
| accepted tx/s | 606/s during ramp; 1,257/s after the conservative blended-fee recompute (1,335–1,363/s before it) |
| mempool | 0–656 before the shortened-run recompute; well below 80k |
| n0 | pid 2341090, synced, RPC healthy |
| free disk | about 23.7 GB |
| binding pacer limit | disk planning rate, about 719/s (fund model about 732/s) |

After shortening the run, the disk model was about **1,360/s**, but measured blended fee burn was about 0.00417 TKAS/tx, so the pacer conservatively uses 0.0043 and now runs at about **1,257/s**. The conservative funds model binds just before the disk model; both project to roughly **12.5 GB free / a small positive funds reserve at 11:52**. Early disk slope was variable at roughly 5–6 GB/h during the high-rate ramp. the final report will replace this with measured fee burn, actual disk slope, and the closing balance. The H lane has a higher carrier fee than the P tag, so its contribution will be reported separately rather than hidden in the headline P-tag fee.

## Flaws and operational lessons

1. A 100k mempool assertion makes a high-rate brake inherently dangerous when workers have in-flight requests; the brake must act well below the cap and use a slower ramp.
2. Supervisor logs previously reported stale worker TPS after a worker stopped; stale lines are now ignored after 25 seconds.
3. A sticky global STOP file makes workers exit immediately while a supervisor respawns them. The supervisor now records the condition explicitly; operators must clear it only after checking the cause.
4. TN10 disk planning based only on steady-state bytes/transaction misses pruning-point compaction bursts. A 12 GB guard is not sufficient during a transient that needs more than 15 GB.
5. Rebuilding `utxoindex` is a substantial offline and disk event; it should not be attempted near the pruning-point window.
6. Vprog carrier fee selection is not estimator-aware, and carrier UTXO selection can panic on fragmented funds.

## Ideas / next steps

- Keep sustained storm rate below the mempool reaction envelope; use a pacer that reserves both fee funds and transient disk, with a separate H-lane fee budget.
- Require a much larger free-space reserve before TN10 pruning-point moves, or stop cleanly before the expected window.
- Add a carrier `FeePolicy`/feerate parameter and return an ordinary insufficient-funds error instead of asserting on the first too-small UTXO.
- Add a preflight that measures the largest required carrier transaction, available UTXOs, and RAM/disk headroom before launching multi-worker vprog tests.
- Leave the final paced-run data and a post-11:52 cleanup/stop record as the authoritative round-4 numbers.

## Draft upstream issues (not filed)

These are drafts only; no upstream issue was filed from this interim report:

- **U1 — vprogs carrier fee policy:** carrier transactions should accept a `FeePolicy`/target feerate (or an explicit configuration knob) instead of always using the relay-floor `min_fee`.
- **U2 — vprogs carrier UTXO selection:** choose a sufficiently large UTXO or combine inputs, and return an error rather than asserting when the first candidate is too small.
- **U3 — rusty-kaspa/TN10 disk documentation:** document pruning-window storage and transient space requirements, including the additional `--utxoindex` footprint.

Details and reproduction helpers are in `upstream-issues/README.md`, `scripts/`, and `patches/`. The final results section will be appended after 11:52 CEST.
