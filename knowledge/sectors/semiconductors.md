# Semiconductors — Sector Knowledge Base

## What Drives Semi Cycles

Semiconductors are the most cyclical sector in tech. Three forces drive the cycle:

1. **Inventory cycles** — customers double-order when supply is tight, then destock for 2-3 quarters. Watch inventory-to-revenue ratios at both the chipmaker and their customers.
2. **Capex waves** — foundries and equipment makers invest in lockstep. Overcapacity follows every boom. ASML/LRCX orders are a leading indicator.
3. **End-market demand** — PCs, smartphones, autos, industrial, and datacenter each have their own cycle. When they sync up (all recovering or all rolling over), moves are amplified.

The typical semi cycle is **3-4 years trough-to-trough**. AI spending is creating a secular overlay, but cycles still apply — they just hit different sub-sectors at different times.

## Sub-Sectors

| Sub-Sector | Key Names | What Matters |
|------------|-----------|--------------|
| **Logic / GPU** | NVDA, AMD, INTC | AI training/inference demand, datacenter mix, gaming attach rates |
| **Memory** | MU, SNDK, WDC | HBM demand, DRAM/NAND pricing, inventory days, supply discipline |
| **Foundry / Equipment** | ASML, LRCX, KLAC, AMAT, TSM | Wafer fab equipment (WFE) spending, utilization rates, order backlog |
| **Analog / Mixed-Signal** | TXN, ADI, MCHP, ON | Auto/industrial end-markets, inventory at distributors, pricing power |
| **Networking / Custom ASIC** | AVGO, MRVL, ALAB, CRDO | Custom silicon wins, optical interconnect upgrades, SerDes/retimer attach |
| **Optical / CPO** | COHR, LITE, FN, CIEN, AAOI, AXTI, MXL | 800G→1.6T modules, silicon photonics, CPO, InP substrates, optical DSP |
| **EDA / Design Tools** | SNPS, CDNS | "Toll booth" — every chip designed uses their software. Compounders. |

**Hierarchy of importance for current cycle (mid-2026):** GPU/HBM > Optical/CPO > Networking/Custom > Equipment > EDA (steady) > Analog recovery. Analog is last to inflect — still working through industrial destock.

**Optical sub-layer bottleneck:** Within optical, capital is rotating from finished modules (COHR, LITE) → upstream substrates (AXTI, Soitec) and CPO components (AAOI, Sivers). Small-cap, low-awareness substrate plays are the bottleneck within the bottleneck. See `knowledge/frameworks/ai-capital-flow.md` for the full optical sub-layer breakdown.

## Cycle Identification

Where are we? Check these signals:

| Signal | Early Cycle (Buy) | Mid Cycle (Hold) | Late Cycle (Trim) |
|--------|-------------------|-------------------|-------------------|
| Inventory days | Declining from peak, below 100 | Normal (80-100) | Rising, >110 |
| Book-to-bill | Crossing above 1.0 | Stable >1.0 | Declining toward 1.0 |
| Gross margins | Troughing, starting to recover | Expanding | Near peak or contracting |
| Capex announcements | Modest, focused | Accelerating | Massive, "we must build" |
| ASP trends | Stabilizing | Rising | Topping out |
| Sentiment | "Semis are dead" | "This time is different" | "Semis can only go up" |

**Book-to-bill above 1.0 is the single best buy signal.** It means orders are outpacing shipments — supply tightening ahead.

## Key Metrics by Sub-Sector

| Metric | Where It Matters | Why |
|--------|-----------------|-----|
| Revenue growth (QoQ) | All | Semis are about rate of change, not absolute level |
| Gross margin | All, especially analog | Proxy for pricing power and utilization |
| Inventory days | MU, TXN, MCHP | Early warning of demand mismatch |
| HBM revenue mix | MU, SK Hynix | Margin accretion driver — HBM GMs are 2-3x conventional DRAM |
| WFE spending | ASML, LRCX, KLAC, AMAT | Forward indicator of industry capex — leads revenue by 6-12 months |
| Design wins ($ pipeline) | MRVL, AVGO, CRDO, ALAB | Revenue doesn't hit for 12-24 months, but the win is the inflection |
| Data center revenue % | NVDA, AMD, AVGO, MRVL | Higher DC mix = higher multiples, more secular growth credit |
| Capex intensity (capex/rev) | TSM, INTC, MU | >30% is aggressive — watch for overcapacity signals |

## AI as Secular Overlay

AI spending is real and structural, but it doesn't eliminate cycles — it shifts them:

- **GPU (NVDA):** Training demand remains strong but growth rate decelerating. The question is whether inference offloads to custom ASICs (MRVL, AVGO) over time. NVDA's moat is CUDA ecosystem, not just hardware.
- **HBM (MU):** AI's killer app for memory. HBM demand growing 3-4x annually. MU is the biggest beneficiary because HBM carries 2-3x the gross margin of standard DRAM. But supply is catching up — monitor pricing quarterly.
- **Custom ASIC risk:** Google (TPU), Amazon (Trainium), Meta, and MSFT are all building custom inference chips. This is the biggest long-term threat to NVDA's inference TAM. Bullish for MRVL and AVGO as custom silicon design partners.
- **Optical interconnect:** Every GPU cluster needs massive bandwidth between chips. The 800G-to-1.6T upgrade cycle benefits ALAB, CRDO (retimers/SerDes), and COHR, LITE (optics). This is still early innings.

**The playbook:** GPU was Phase 1 (2023-24). Memory/HBM is Phase 2 (2025-26). Networking/interconnect is Phase 3 (2026-27). Power/cooling runs alongside. Position ahead of each phase, not after it re-rates.

## Trading Implications

| Scenario | Action | Tickers |
|----------|--------|---------|
| **Inventory trough confirmed** (book-to-bill >1.0, inventory days declining) | Buy aggressively — LEAPs or shares | SMH (broad), MU, MCHP, ON |
| **Earnings with high IV** (IV Rank >60) | Sell premium — CSPs at support | Works best on MU, AMD, MCHP (volatile reporters) |
| **AI capex acceleration** (hyperscaler capex guides up) | Buy networking/custom names | AVGO, MRVL, ALAB, CRDO |
| **Late cycle euphoria** (peak margins, massive capex, "this time is different") | Trim or hedge — buy puts on SMH | Reduce NVDA, AMD if at peak multiples |
| **Analog destock ending** (distributor inventory normalizing) | Start building analog positions | TXN, ADI, MCHP, ON — these are the best mean-reversion trades |

**Earnings playbook:** Semis are the highest-IV sector around earnings. If you have conviction, sell CSPs 2 weeks before earnings to capture IV expansion. If you don't, stay out — binary risk is real. MU and AMD routinely move 8-12% on earnings.

## Common Mistakes

1. **Buying at peak margins because P/E looks "cheap."** Semi P/Es compress at peak earnings because the market knows margins will fall. A stock at 12x peak earnings can become 25x trough earnings. Always use forward estimates through the cycle, not trailing.
2. **Ignoring inventory builds.** Rising inventory days while revenue decelerates = the cycle is turning. This signal killed MU holders in late 2022 and MCHP holders in 2023. Watch it every quarter.
3. **Treating AI demand as cycle-proof.** AI is a secular tailwind, not a suspension of physics. Even NVDA had a 65% drawdown in 2022. Datacenter spending is lumpy and subject to digestion periods.
4. **Chasing equipment stocks after WFE guidance raises.** By the time ASML guides up, the move is 60% done. Equipment stocks are leading indicators — buy them when WFE estimates are being cut, not raised.
5. **Conflating design wins with revenue.** A $1B custom ASIC design win (MRVL, AVGO) takes 18-24 months to hit revenue. The stock often re-rates on the win, then grinds sideways waiting for revenue. Don't overpay for optionality.
