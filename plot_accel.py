import time
from collections import deque

import matplotlib.pyplot as plt
import serial
from matplotlib.animation import FuncAnimation

PORT = "/dev/cu.usbmodem11203"
BAUD = 115200
WINDOW_SECONDS = 10

ser = serial.Serial(PORT, BAUD, timeout=0.05)

times = deque()
raw_values = deque()
filtered_values = deque()

fig, ax = plt.subplots()
raw_line, = ax.plot([], [], label="Raw X")
filtered_line, = ax.plot([], [], label="Filtered X")

ax.set_title("STM32 Accelerometer X")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Acceleration (mg)")
ax.legend()
ax.grid(True)


def update(_):
    while ser.in_waiting:
        line = ser.readline().decode("utf-8", errors="ignore").strip()

        try:
            time_ms, raw_x, filtered_x10 = map(int, line.split(","))
        except ValueError:
            continue

        t = time_ms / 1000.0
        times.append(t)
        raw_values.append(raw_x)
        filtered_values.append(filtered_x10 / 10.0)

        while times and t - times[0] > WINDOW_SECONDS:
            times.popleft()
            raw_values.popleft()
            filtered_values.popleft()

    if times:
        raw_line.set_data(times, raw_values)
        filtered_line.set_data(times, filtered_values)

        ax.set_xlim(max(0, times[-1] - WINDOW_SECONDS),
                    max(WINDOW_SECONDS, times[-1]))

        values = list(raw_values) + list(filtered_values)
        margin = max(10, (max(values) - min(values)) * 0.15)
        ax.set_ylim(min(values) - margin, max(values) + margin)

    return raw_line, filtered_line


ani = FuncAnimation(fig, update, interval=50, cache_frame_data=False)
plt.show()

ser.close()
