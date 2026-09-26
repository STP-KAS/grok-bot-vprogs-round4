// ROUND4-FUND-W3 (TN10 only): move ~PER TKAS from each stopped rwstorm P-worker state (P2SH tag wallets) to our own W3 fund wallet (vprog issuers + ttt workers).
// to the Grok Build receive address (RECEIVING only; we never spend from it). Each tx: N inputs -> 1 output (~100-1000 TKAS).
// Run ONLY while the storm fleet is halted (it edits state-rw-P*.json). usage: DRY=1 node fund-grokbuild.mjs
import { readFileSync, writeFileSync, appendFileSync } from "node:fs";
import { kaspa, connect, NET, sleep } from "./lib.mjs";
const D = "/workspace/tn10-break-test-2026-09-25", TO = "kaspatest:qzy736483sz0lafs7css4j0ssq0t4xelc58jdfhg9c6yncgul7r4snj0v7mxg";
const PER = BigInt(process.env.PER || 37500) * 100000000n, NIN = Number(process.env.NIN || 84), FEERATE = 1000n, DRY = process.env.DRY === "1";
const LOG = `${D}/logs/round4/fund-w3.jsonl`; const out = (o) => appendFileSync(LOG, JSON.stringify({ t: new Date().toISOString(), ...o }) + "\n");
const tagRedeem = (id) => "04" + Buffer.from(Uint32Array.of(id).buffer).toString("hex") + "7551";
const toSpk = kaspa.payToAddressScript(TO);
const rpc = DRY ? null : await connect("n0");
let totTx = 0, totAmt = 0n, totFee = 0n, fails = 0;
for (let k = 0; k < 8; k++) {
  const F = `${D}/state-rw-P${k}.json`; const S = JSON.parse(readFileSync(F, "utf8"));
  const all = []; for (const [id, us] of Object.entries(S)) for (const u of us) all.push({ id: +id, u });
  all.sort((a, b) => Number(BigInt(b.u[2]) - BigInt(a.u[2]))); // biggest first
  const take = []; let sum = 0n; for (const x of all) { if (sum >= PER) break; take.push(x); sum += BigInt(x.u[2]); }
  const used = new Set(); let wAmt = 0n, wTx = 0;
  for (let j = 0; j < take.length; j += NIN) {
    const grp = take.slice(j, j + NIN);
    const ents = grp.map(({ id, u }) => { const r = tagRedeem(id), spk = kaspa.payToScriptHashScript(r);
      return { address: kaspa.addressFromScriptPublicKey(spk, NET).toString(), outpoint: { transactionId: u[0], index: u[1] }, utxoEntry: { amount: BigInt(u[2]), scriptPublicKey: spk, blockDaaScore: 0n, isCoinbase: false }, _ss: "07" + r }; });
    const inSum = ents.reduce((s, e) => s + e.utxoEntry.amount, 0n);
    const mk = (fee) => { const tx = kaspa.createTransaction(ents.map(({ _ss, ...e }) => e), [{ address: TO, amount: inSum - fee }], 0n, null, 0); ents.forEach((e, i) => tx.inputs[i].signatureScript = e._ss); return tx; };
    if (grp.length !== NIN || !globalThis._fee) globalThis._fee = BigInt(kaspa.calculateTransactionMass(NET, mk(100000n))) * FEERATE; const fee = globalThis._fee, mass = fee / FEERATE; const tx = mk(fee);
    if (DRY) { if (j === 0) console.log(JSON.stringify({ w: `P${k}`, nin: grp.length, mass: String(mass), out_tkas: Number(inSum - fee) / 1e8, groups: Math.ceil(take.length / NIN), take_tkas: Number(sum) / 1e8 })); continue; }
    try { const r = await rpc.submitTransaction({ transaction: tx, allowOrphan: false }); grp.forEach((x) => used.add(x.u[0] + ":" + x.u[1]));
      wAmt += inSum - fee; wTx++; totFee += fee; out({ w: `P${k}`, txid: r.transactionId, nin: grp.length, amount: String(inSum - fee), fee: String(fee) });
    } catch (e) { fails++; out({ w: `P${k}`, err: String(e).replace(/[0-9a-f]{64}/g, "<h>").slice(0, 200) }); if (/full/.test(String(e))) { await sleep(2000); j -= NIN; } }
  }
  if (!DRY) { for (const id of Object.keys(S)) S[id] = S[id].filter((u) => !used.has(u[0] + ":" + u[1])); writeFileSync(F + ".fundtmp", JSON.stringify(S)); writeFileSync(F, JSON.stringify(S));
    totTx += wTx; totAmt += wAmt; console.log(JSON.stringify({ w: `P${k}`, txs: wTx, tkas: Number(wAmt) / 1e8, removed_utxos: used.size })); }
}
if (!DRY) { const s = { step: "total", txs: totTx, tkas: Number(totAmt) / 1e8, fee_tkas: Number(totFee) / 1e8, fails }; out(s); console.log(JSON.stringify(s)); }
process.exit(0);
