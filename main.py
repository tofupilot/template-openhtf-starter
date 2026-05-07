"""OpenHTF starter procedure for TofuPilot.

Showcases the most-used features in a single test:
  - Plug with shared state across phases
  - Logger output
  - Operator prompts (button + text input)
  - Numeric measurement with hard + marginal limits
  - String measurement with custom validator
  - Multi-dimensional measurement (voltage vs time -> chart in TofuPilot)
  - File attachment (CSV)
  - PhaseResult flow control (skip)

When deployed via TofuPilot, runs are captured automatically -- no
output callback or station server needed. The TofuPilot dashboard owns
the serial-number prompt and renders native `user_input.prompt(...)`
calls in the browser.
"""

import csv
import io
import time

import openhtf as htf
from openhtf import PhaseResult
from openhtf.plugs import BasePlug, user_input
from openhtf.util import units


class DutPlug(BasePlug):
    """Mock device under test. Replace with your real instrument driver."""

    def __init__(self):
        self._powered = False

    def power_on(self):
        self._powered = True

    def read_voltage(self) -> float:
        # Tiny ripple so the multi-dim chart isn't a flat line.
        ripple = 0.005 * ((time.time_ns() % 7) - 3)
        return 5.01 + ripple if self._powered else 0.0

    def tearDown(self):
        self._powered = False


@htf.plug(dut=DutPlug)
def power_on(test, dut):
    """Turn on the DUT."""
    test.logger.info("Powering on the DUT")
    dut.power_on()


@htf.plug(prompt=user_input.UserInput)
def confirm_led_on(test, prompt):
    """Operator confirms the LED is lit. Returns SKIP if the operator types `skip`."""
    response = prompt.prompt(
        message="Is the LED on? Click OK to continue, or type `skip` to skip the rest of the test.",
        text_input=True,
    )
    if (response or "").strip().lower() == "skip":
        test.logger.warning("Operator skipped: LED not visible")
        return PhaseResult.SKIP


@htf.measures(
    htf.Measurement("led_color").matches_regex(r"(?i)^(red|green|blue)$")
)
@htf.plug(prompt=user_input.UserInput)
def check_led_color(test, prompt):
    """Operator types the LED color (red, green, or blue)."""
    color = prompt.prompt(message="Enter the LED color:", text_input=True)
    test.measurements.led_color = color


# Hard limits 4.8..5.2; marginal limits 4.95..5.05 (warn but still pass).
@htf.measures(
    htf.Measurement("supply_voltage")
    .in_range(4.8, 5.2, marginal_minimum=4.95, marginal_maximum=5.05)
    .with_units("V")
)
@htf.plug(dut=DutPlug)
def measure_voltage(test, dut):
    """Read steady-state voltage from the DUT."""
    test.measurements.supply_voltage = dut.read_voltage()


# Multi-dim measurement: voltage vs time. TofuPilot plots this as a chart
# in the dashboard automatically.
@htf.measures(
    htf.Measurement("voltage_vs_time")
    .with_dimensions(units.SECOND)
    .with_units("V")
)
@htf.plug(dut=DutPlug)
def sweep_voltage(test, dut):
    """Sample voltage over a few seconds and stream it to TofuPilot."""
    samples = []
    for i in range(20):
        t = i * 0.1
        v = dut.read_voltage()
        test.measurements.voltage_vs_time[t] = v
        samples.append((t, v))
        time.sleep(0.02)

    # Same data attached as raw CSV for users who want the file too.
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["t_s", "voltage_v"])
    writer.writerows(samples)
    test.attach("voltage_sweep.csv", buf.getvalue().encode(), mimetype="text/csv")


def create_and_run_test():
    test = htf.Test(
        power_on,
        confirm_led_on,
        check_led_color,
        measure_voltage,
        sweep_voltage,
        procedure_id="FVT1",
    )
    test.execute()


if __name__ == "__main__":
    create_and_run_test()
