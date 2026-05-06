"""OpenHTF starter procedure for TofuPilot.

Showcases the core features in a single test:
  - Plugs (shared instrument across phases)
  - Logger output
  - Operator prompts (button + text input)
  - Numeric measurement with limits
  - String measurement with validator
  - Attachments

When deployed via TofuPilot, runs are captured automatically — no
output callback or station server is needed. The TofuPilot dashboard
prompts the operator for the serial number and renders native
`user_input.prompt(...)` calls in the browser.
"""

import csv
import io

import openhtf as htf
from openhtf.plugs import BasePlug, user_input


class DutPlug(BasePlug):
    """Mock device under test. Replace with your real instrument driver."""

    def __init__(self):
        self._powered = False

    def power_on(self):
        self._powered = True

    def read_voltage(self) -> float:
        return 5.01 if self._powered else 0.0

    def tearDown(self):
        self._powered = False


@htf.plug(dut=DutPlug)
def power_on(test, dut):
    """Turn on the DUT."""
    test.logger.info("Powering on the DUT")
    dut.power_on()


@htf.plug(prompt=user_input.UserInput)
def confirm_led_on(test, prompt):
    """Operator confirms the LED is lit."""
    prompt.prompt(message="Is the LED on? Click OK to continue.", text_input=False)


@htf.measures(
    htf.Measurement("led_color").with_validator(
        lambda c: str(c).lower() in ("red", "green", "blue")
    )
)
@htf.plug(prompt=user_input.UserInput)
def check_led_color(test, prompt):
    """Operator types the LED color (red, green, or blue)."""
    color = prompt.prompt(message="Enter the LED color:", text_input=True)
    test.measurements.led_color = color


@htf.measures(htf.Measurement("supply_voltage").in_range(4.8, 5.2).with_units("V"))
@htf.plug(dut=DutPlug)
def measure_voltage(test, dut):
    """Read voltage from the DUT and attach the raw sample as CSV."""
    voltage = dut.read_voltage()
    test.measurements.supply_voltage = voltage

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["sample", "voltage_v"])
    writer.writerow([1, voltage])
    test.attach("voltage_samples.csv", buf.getvalue().encode(), mimetype="text/csv")


def create_and_run_test():
    test = htf.Test(
        power_on,
        confirm_led_on,
        check_led_color,
        measure_voltage,
        procedure_id="FVT1",
    )
    test.execute()


if __name__ == "__main__":
    create_and_run_test()
