from datetime import datetime, timedelta

from M2 import calculate_utilization  #import the function to be tested


def test_Power_ON():
    base = datetime(2026,7,1,10,0,0)  # Base time for the samples  # noqa: DTZ001

    # Create a list of samples with timestamps, robot modes, and active times
    samples = [(base + timedelta(seconds=i), 7, i * 0.5) for i in range(30)]  # 30 samples, mode 7 (ON), active time increasing by 0.5 seconds
    result = calculate_utilization(samples)
    assert result.powered_on_time == 29.0  # Total time from first to last sample (29 seconds)
    assert result.active_time == 14.5  # Active time from first to last sample
    assert result.idle_time == 14.5  # Idle time is powered_on_time - active_time
    assert result.utilization == (14.5 / 29.0) * 100  # Utilization percentage

def test_Power_OFF():
    base = datetime(2026,7,1,10,0,0)  # Base time for the samples  # noqa: DTZ001

    # Create a list of samples with timestamps, robot modes, and active times
    samples = [(base + timedelta(seconds=i), 3, 5) for i in range(30)]  # 30 samples, mode 3 (OFF), active time 5 seconds
    result = calculate_utilization(samples)
    assert result.powered_on_time == 0.0  # Total time from first to last sample (0 seconds)
    assert result.active_time == 0.0   # Active time from first to last sample
    assert result.idle_time == 0.0  # Idle time is powered_on_time - active_time = 0
    assert result.utilization is None  # Utilization percentage
def test_return_value():

    # Create a list of samples with timestamps, robot modes, and active times
    samples = []  # 3Empty list of samples
    result = calculate_utilization(samples)

    assert result.powered_on_time == 0.0  # Total time from first to last sample (0 seconds)
    assert result.active_time == 0.0   # Active time from first to last sample
    assert result.idle_time == 0.0  # Idle time is powered_on_time - active_time = 0
    assert result.utilization is None  # Utilization percentage should be None for empty samples

def test_Mixed_Scenario():
    base = datetime(2026,7,1,10,0,0)  # Base time for the samples  # noqa: DTZ001

    # Create a list of samples with timestamps, robot modes, and active times
    samples = ([ (base + timedelta(seconds=i), 4, i * 0.5) for i in range(10)]
    + [(base + timedelta(seconds=i), 7, i * 0.5) for i in range(10, 20)] 
    + [(base + timedelta(seconds=i), 3, 9.5) for i in range(20, 30)]) # Mixed modes: 4 (IDLE) for 10 seconds, 7 (ON) for 10 seconds, 3 (OFF) fpr 10 seconds

    result = calculate_utilization(samples)
    assert result.powered_on_time == 20.0  # Total time from first to last sample (20 seconds)
    assert result.active_time == 9.5  # Active time from first to last sample
    assert result.idle_time == 10.5  # Idle time is powered_on_time - active_time = 9.5
    assert result.utilization == (9.5 / 20.0) * 100  # Utilization percentage
