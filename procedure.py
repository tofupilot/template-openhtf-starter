"""Example OpenHTF test logic.

When deployed via TofuPilot the run is captured automatically — no
output callback is needed.
"""

import openhtf as htf

from openhtf.plugs import user_input


@htf.measures(htf.Measurement('hello_world_measurement'))
def hello_world(test):
    """A hello world test phase."""
    test.logger.info('Hello from TofuPilot!')
    test.measurements.hello_world_measurement = 'Hello from TofuPilot!'


def create_and_run_test():
    test = htf.Test(hello_world)
    test.execute(test_start=user_input.prompt_for_test_start())


if __name__ == '__main__':
    create_and_run_test()
