# OpenHTF Starter

![Cover](cover.png)

A single OpenHTF procedure that showcases the core features you'll use in production tests.

## What This Shows

| Feature | Where |
|---------|-------|
| Plug (shared instrument) | `DutPlug` class, used by `power_on` and `measure_voltage` |
| Logger output | `test.logger.info(...)` in `power_on` |
| Operator button prompt | `confirm_led_on` (`text_input=False`) |
| Operator text input + string measurement | `check_led_color` |
| Numeric measurement with limits | `measure_voltage` (`in_range(4.8, 5.2)`) |
| Attachment | `test.attach("voltage_samples.csv", ...)` |
| Test-start prompt for serial number | `user_input.prompt_for_test_start()` |

## Get Started

1. Sign up for a free TofuPilot account at [tofupilot.app](https://www.tofupilot.app/auth/signup).
2. Open the **New Procedure** flow in the dashboard and clone this template.
3. Follow the dashboard's instructions to set up a station and run the procedure.

When deployed via TofuPilot, runs are captured automatically — no output callback or station server is needed. The TofuPilot dashboard provides the operator UI.

For deeper guides, see the [TofuPilot docs](https://www.tofupilot.com/docs/openhtf).

## Structure

```
.
├── main.py          # OpenHTF test definition
├── pyproject.toml   # Python dependencies
└── README.md
```
