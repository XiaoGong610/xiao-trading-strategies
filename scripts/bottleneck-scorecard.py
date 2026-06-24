#!/usr/bin/env python3
"""Bottleneck scorecard — score supply-chain / hardware stocks by constraint severity.

Adapted from serenity-skill (github.com/muxuuu/serenity-skill).
Best for: semiconductors, AI infrastructure, power equipment, materials,
robotics, defense electronics, optical interconnect, advanced packaging.
NOT useful for: pure SaaS, financials, REITs, consumer brands, macro trades.

Usage:
  .venv/bin/python3 scripts/bottleneck-scorecard.py --template              # blank JSON
  .venv/bin/python3 scripts/bottleneck-scorecard.py scorecard.json          # JSON output
  .venv/bin/python3 scripts/bottleneck-scorecard.py scorecard.json --md     # Markdown output
  cat scorecard.json | .venv/bin/python3 scripts/bottleneck-scorecard.py -  # stdin
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, Tuple

# --- Scoring weights (sum = 100) ---
WEIGHTS = {
    "demand_inflection": 15,       # Is the demand wave real and accelerating?
    "chokepoint_severity": 15,     # How scarce and hard to replace is this layer?
    "evidence_quality": 15,        # How strong and verifiable is the evidence base?
    "supplier_concentration": 12,  # How few suppliers exist for this function?
    "expansion_difficulty": 12,    # How hard is it to add capacity?
    "valuation_disconnect": 11,    # Gap between market pricing and bottleneck value?
    "architecture_coupling": 10,   # How tightly coupled to the system change?
    "catalyst_timing": 10,         # How near-term are repricing events?
}

# --- Penalty factors (each point costs 2x) ---
PENALTY_KEYS = [
    "dilution_financing",       # Needs capital raises to fund the opportunity
    "governance",               # Related-party, management alignment issues
    "geopolitics",              # Export controls, sanctions exposure
    "liquidity",                # Thin trading, wide spreads
    "hype_risk",                # Story is social-media driven, not evidence-driven
    "accounting_quality",       # Receivables/inventory divergence, aggressive recognition
    "cyclicality",              # Exposed to cycle timing risk
    "alternative_design_risk",  # Customers could route around via architectural change
]

PENALTY_MULTIPLIER = 2.0

# --- Verdict thresholds ---
VERDICTS = [
    (85, "Top research priority"),
    (70, "High research priority"),
    (55, "Worth tracking"),
    (0,  "Early lead or low priority"),
]

TEMPLATE = {
    "ticker": "",
    "company": "",
    "market": "US",
    "value_chain_layer": "",
    "factors": {key: 0 for key in WEIGHTS},
    "penalties": {key: 0 for key in PENALTY_KEYS},
    "evidence": [
        {"claim": "", "source": "", "strength": "strong/medium/weak/needs-checking"}
    ],
    "what_could_weaken_view": ["", "", ""],
}


def _clamp_0_5(value: Any, label: str) -> float:
    try:
        n = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be a number 0-5") from None
    if n < 0 or n > 5:
        raise ValueError(f"{label} must be 0-5, got {n}")
    return n


def load_input(path: str) -> Dict[str, Any]:
    if path == "-":
        raw = sys.stdin.read()
    else:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit("Input must be a JSON object")
    return data


def score(data: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    factors = data.get("factors", {})
    penalties = data.get("penalties", {})

    # Score positive factors
    factor_details = {}
    factor_total = 0.0
    for key, weight in WEIGHTS.items():
        rating = _clamp_0_5(factors.get(key, 0), f"factors.{key}")
        points = rating / 5.0 * weight
        factor_details[key] = {"rating": rating, "weight": weight, "points": round(points, 2)}
        factor_total += points

    # Score penalties
    penalty_details = {}
    penalty_total = 0.0
    for key in PENALTY_KEYS:
        rating = _clamp_0_5(penalties.get(key, 0), f"penalties.{key}")
        points = rating * PENALTY_MULTIPLIER
        penalty_details[key] = {"rating": rating, "points": round(points, 2)}
        penalty_total += points

    final = max(0.0, min(100.0, factor_total - penalty_total))

    verdict = "Early lead or low priority"
    for threshold, label in VERDICTS:
        if final >= threshold:
            verdict = label
            break

    result = {
        "ticker": data.get("ticker", ""),
        "company": data.get("company", ""),
        "market": data.get("market", ""),
        "value_chain_layer": data.get("value_chain_layer", ""),
        "raw_factor_points": round(factor_total, 2),
        "penalty_points": round(penalty_total, 2),
        "final_score": round(final, 2),
        "verdict": verdict,
        "factor_details": factor_details,
        "penalty_details": penalty_details,
        "what_could_weaken_view": data.get("what_could_weaken_view", []),
        "evidence": data.get("evidence", []),
    }
    return result, verdict


def to_markdown(result: Dict[str, Any]) -> str:
    ticker = result.get("ticker") or "Unknown"
    company = f" ({result['company']})" if result.get("company") else ""
    layer = f"\nValue-chain layer: {result['value_chain_layer']}" if result.get("value_chain_layer") else ""

    lines = [
        f"### Bottleneck Scorecard: {ticker}{company}",
        "",
        f"Market: {result.get('market', 'US')}",
        f"Score: **{result['final_score']} / 100** — {result['verdict']}",
        f"Factor points: {result['raw_factor_points']} | Penalties: -{result['penalty_points']}",
        layer,
        "",
        "#### Factors",
        "| Factor | Rating | Weight | Points |",
        "|--------|-------:|-------:|-------:|",
    ]
    for key, d in result["factor_details"].items():
        name = key.replace("_", " ").title()
        lines.append(f"| {name} | {d['rating']:.0f} | {d['weight']} | {d['points']:.1f} |")

    # Only show non-zero penalties
    active_penalties = {k: d for k, d in result["penalty_details"].items() if d["rating"] > 0}
    if active_penalties:
        lines.extend(["", "#### Penalties", "| Penalty | Rating | Points |", "|---------|-------:|-------:|"])
        for key, d in active_penalties.items():
            name = key.replace("_", " ").title()
            lines.append(f"| {name} | {d['rating']:.0f} | -{d['points']:.1f} |")

    weakening = [str(w).strip() for w in result.get("what_could_weaken_view", []) if str(w).strip()]
    if weakening:
        lines.extend(["", "#### What Could Weaken the View"])
        for w in weakening:
            lines.append(f"- {w}")

    evidence = result.get("evidence", [])
    evidence_lines = []
    for ev in evidence:
        if isinstance(ev, dict):
            claim = ev.get("claim", "").strip()
            source = ev.get("source", "").strip()
            strength = ev.get("strength", "").strip()
            if claim:
                evidence_lines.append(f"- **[{strength}]** {claim}" + (f" — {source}" if source else ""))
    if evidence_lines:
        lines.extend(["", "#### Evidence"])
        lines.extend(evidence_lines)

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Score a supply-chain bottleneck thesis (0-100)")
    parser.add_argument("input", nargs="?", help="JSON scorecard file, or '-' for stdin")
    parser.add_argument("--template", action="store_true", help="Print blank JSON template")
    parser.add_argument("--md", action="store_true", help="Output markdown instead of JSON")
    args = parser.parse_args()

    if args.template:
        print(json.dumps(TEMPLATE, ensure_ascii=False, indent=2))
        return

    if not args.input:
        parser.error("input file required (or use --template)")

    data = load_input(args.input)
    result, _ = score(data)

    if args.md:
        print(to_markdown(result))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
