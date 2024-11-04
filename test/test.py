import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import random

@cocotb.test()
async def test_pid_controller(dut):
    # Initialize the clock
    clock = Clock(dut.clk, 10, units="ns")  # 10ns period = 100MHz clock
    cocotb.start_soon(clock.start())

    # Initialize values
    setpoint = 128
    feedback = 75
    dut.setpoint.value = setpoint
    dut.feedback.value = feedback
    dut.rst_n.value = 0

    # Reset the DUT
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1

    # Simulated system response
    for i in range(100):  # Run for 100 cycles
        await RisingEdge(dut.clk)

        # Update the feedback based on control signal (simple simulation of plant response)
        pid_output = dut.control_signal.value.integer

        # Adjust feedback value to simulate approach toward setpoint
        if feedback < pid_output:
            feedback += min(pid_output - feedback, 2)  # Slow increase
        elif feedback > pid_output:
            feedback -= min(feedback - pid_output, 2)  # Slow decrease

        # Apply the updated feedback to DUT
        dut.feedback.value = feedback

        # Monitor the output and log values
        control_signal = dut.control_signal.value.integer
        error = setpoint - feedback

        # Print for observation
        dut._log.info(f"Cycle {i}: Setpoint={setpoint}, Feedback={feedback}, "
                      f"Control Signal={control_signal}, Error={error}")

        # Assertion to check if the feedback stabilizes around setpoint
        if i > 90:  # Give some settling time
            assert abs(feedback - setpoint) <= 5, f"Feedback did not converge: {feedback}"

    # Final check if feedback is close enough to setpoint
    assert abs(feedback - setpoint) <= 2, "PID controller did not reach setpoint adequately"
