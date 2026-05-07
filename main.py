"""OpenHTF starter procedure for TofuPilot."""

import csv
import io
import math
import random
import time

import openhtf as htf
from openhtf import PhaseResult
from openhtf.core.measurements import Dimension
from openhtf.plugs import BasePlug, user_input
from openhtf.util import units


class DutPlug(BasePlug):
    """Mock device under test. Replace with your real instrument driver."""

    def __init__(self):
        self._powered = False

    def power_on(self):
        self._powered = True

    def read_voltage(self) -> float:
        if not self._powered:
            return 0.0
        ripple = 0.03 * math.sin(2 * math.pi * 5.0 * time.time())
        noise = random.gauss(0.0, 0.005)
        return 5.01 + ripple + noise

    def tearDown(self):
        self._powered = False


@htf.plug(dut=DutPlug)
def power_on(test, dut):
    """Turn on the DUT."""
    test.logger.info("Powering on the DUT")
    dut.power_on()


@htf.plug(prompt=user_input.UserInput)
def confirm_led_on(test, prompt):
    """Operator confirms the LED is lit; type `skip` to skip the rest of the test."""
    response = prompt.prompt(
        message="Is the LED on? Click OK to continue, or type `skip` to skip.",
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
    """Operator types the LED color."""
    test.measurements.led_color = prompt.prompt(
        message="Enter the LED color:", text_input=True,
    )


@htf.measures(
    htf.Measurement("supply_voltage")
    .in_range(4.8, 5.2, marginal_minimum=4.95, marginal_maximum=5.05)
    .with_units("V")
)
@htf.plug(dut=DutPlug)
def measure_voltage(test, dut):
    """Read steady-state voltage from the DUT."""
    test.measurements.supply_voltage = dut.read_voltage()


@htf.measures(
    htf.Measurement("voltage_vs_time")
    .with_dimensions(Dimension(description="Time", unit=units.SECOND))
    .with_units("V")
)
@htf.plug(dut=DutPlug)
def sweep_voltage(test, dut):
    """Sample voltage over one second and stream the curve to TofuPilot."""
    samples = []
    start = time.time()
    for _ in range(50):
        t = time.time() - start
        v = dut.read_voltage()
        test.measurements.voltage_vs_time[t] = v
        samples.append((t, v))
        time.sleep(0.02)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["t_s", "voltage_v"])
    writer.writerows(samples)
    test.attach("voltage_sweep.csv", buf.getvalue().encode(), mimetype="text/csv")


def main():
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
    main()
