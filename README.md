# OpenHTF Starter

![Cover](cover.png)

A single OpenHTF procedure that showcases the core features you'll use in production tests.

## What This Shows

| Feature | Where |
|---------|-------|
| Plug (shared instrument with state across phases) | `DutPlug`, used by `power_on`, `measure_voltage`, `sweep_voltage` |
| Logger output | `test.logger.info(...)` in `power_on` |
| Operator prompt with text input + skip flow | `confirm_led_on` |
| String measurement with regex validator | `check_led_color` (`matches_regex(r"(?i)^(red\|green\|blue)$")`) |
| Numeric measurement with hard + marginal limits | `measure_voltage` (`in_range(4.8, 5.2, marginal_minimum=4.95, marginal_maximum=5.05)`) |
| Multi-dimensional measurement (chart in TofuPilot) | `sweep_voltage` (`voltage_vs_time` dimensioned by seconds) |
| File attachment | `sweep_voltage` attaches `voltage_sweep.csv` |
| PhaseResult flow control (skip rest of test) | `confirm_led_on` returns `PhaseResult.SKIP` |
| Framework-owned serial-number identification | bare `test.execute()` -- TofuPilot prompts the operator |

## Get Started

1. Sign up for a free TofuPilot account at [tofupilot.app](https://www.tofupilot.app/auth/signup).
2. Open the **New Procedure** flow in the dashboard and clone this template.
3. Follow the dashboard's instructions to set up a station and run the procedure.

When deployed via TofuPilot, runs are captured automatically -- no output callback or station server is needed. The TofuPilot dashboard provides the operator UI and renders multi-dim measurements as live charts.

For deeper guides, see the [TofuPilot docs](https://www.tofupilot.com/docs/openhtf).

## Structure

```
.
├── main.py          # OpenHTF test definition
├── pyproject.toml   # Python dependencies (uv)
├── uv.lock
└── README.md
```
