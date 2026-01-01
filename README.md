market-state-detector is a lightweight, open-source monitoring tool that identifies high-uncertainty market states based on observable price behavior.

The logic is intentionally simple and could be executed manually. The value comes from automation, consistency, and reduced human error, not from complexity or prediction.

The tool answers one question only:
Is the market currently in a shock / uncertainty regime where acting is usually a bad idea?
It does not generate buy/sell signals, does not support day trading, and does not attempt to predict market direction.

This project is:
	•	a market state / regime monitor
	•	a decision-hygiene tool
	•	comparable to alerting in distributed systems
	•	designed for slow, deliberate use (e.g. daily checks)

This project is not:
	•	a trading bot
	•	a signal generator
	•	an alpha strategy
	•	a performance claim
