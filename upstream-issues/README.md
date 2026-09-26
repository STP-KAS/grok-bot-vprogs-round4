# Draft upstream issues (round 4). DRAFTS ONLY, NOT FILED.

## U1 (vprogs `l1/wallet`): carrier txs always pay the relay floor fee (`min_fee`), whatever the fee estimate says
`build::carrier::signed_carrier_transaction` prices every carrier (deposit / lane action / withdraw, used by
`app_kit::fund_and_submit` and so by vprog-tictactoe) with `min_fee(params, &probe)`. `Wallet::fee_policy()`
(estimate-based) only applies to activity/settlement builds. Under any flood above the floor, every tic-tac-toe step waits
until the flood stops. Round 4 measurement: 0 games finished during 12 min of storm at 1000 sompi/g, and games resumed about 100 s after the storm stopped.
Ask: accept a `FeePolicy` in `CarrierTxArgs` (TargetFeerate from the estimator, with an optional cap), or at least an env/config knob.
We verified that a wRPC proxy raising `getFeeEstimate` to 2000 sompi/g does not change carrier fees.

## U2 (vprogs `l1/wallet`): the carrier path takes `candidates.into_iter().next()` and then asserts (panics) when that UTXO is too small
`carrier.rs:62` `assert!(entry.amount > extra_value + fee, ...)`. The first UTXO is not the largest, and a worker
whose UTXOs have fragmented below the deposit panics the whole task. We saw this in round 3 (8/8 workers) and round 4
(ttloop-f, 4/4 workers at 06:58:56, `funding UTXO amount 14913800 too small for extra outputs 40000000`).
Ask: pick the largest UTXO (or combine inputs) and return an error instead of panicking.

## U3 (rusty-kaspa, TN10 ops): disk
At 10 BPS with full blocks, the pruning window (~42 h, 1.52M blocks in the DB) held 75 GB of consensus data plus 13 GB of utxoindex on our node,
growing about 2 GB/h at a 1k TPS storm and about 9 GB/h at about 3.5-5k TPS. There is no way to reclaim space before pruning catches up. Please document
the disk needed for a TN10 node under sustained load (and for `--utxoindex`).
