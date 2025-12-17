# GTK System Monitor

A lightweight system monitor for Linux written in Python and GTK3. It features a "Conky-style" dashboard with real-time CPU grids, historical graphs, and detailed system metrics.

<img width="400" alt="Screenshot from 2025-12-13 01-39-19" src="https://github.com/user-attachments/assets/a3bba17a-203f-4ad4-b855-0600537779f1" />

## Features

* **Real-time Monitoring:** Updates CPU, memory, and disk usage every second.
* **Visual Grid:** Displays individual CPU core load in a responsive grid.
* **Lightweight:** Built with `PyGObject` and `psutil` for minimal resource overhead.

## Dependencies

This project requires Python 3, GTK3, and the `psutil` library. You can install the system dependencies on Ubuntu/Debian based systems via `apt`.

sudo apt install python3-gi gir1.2-gtk-3.0 python3-psutil

# File Structure

gtk-system-monitor/
├── main.py
├── system_data.py
├── cpu_grid.py
├── cpu_graph.py
├── system_info.py
├── cpu_arch.py

## Usage
python3 main.py
