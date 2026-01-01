# Philosophy

## What this tool is about

This project is not about predicting markets.
It is not about finding better entries.
It is not about maximizing returns.

It is about **avoiding decisions when decisions are statistically worse**.

---

## Core idea

Markets move for two very different reasons:

1. **Information**
2. **Mechanics** (flows, hedging, rebalancing, noise)

During periods dominated by mechanics, price movements are loud,
but interpretation is poor.

This tool exists to detect exactly those periods.

---

## State-1

The detector classifies the market into a simple state:

- **ON**
  Price discovery is still ongoing.
  Movements are large, inconsistent, or unresolved.

- **OFF**
  The market has largely processed recent information.
  Price behavior is more stable and interpretable.

The state is not a signal.
It is a *context*.

---

## What the tool deliberately does NOT do

- No predictions
- No buy/sell recommendations
- No backtests
- No optimization
- No intraday signals
- No performance claims

Adding any of these would change the nature of the project.

---

## Design principles

- Deterministic logic over probabilistic models
- Explainability over complexity
- Daily data over intraday noise
- Stability over reactivity
- Fewer features over more knobs

If the output changes depending on when you run the tool,
the design is wrong.

---

## How it should be used

This tool is meant to be consulted *before* making a decision.

- **State = ON**
  → Avoid decisions. Wait.

- **State = OFF**
  → Decisions are allowed, not required.

The tool does not improve decisions.
It improves the *conditions* under which decisions are made.

---

## Final note

Good decisions made at bad times often look like bad decisions.

This project exists to reduce that category.
