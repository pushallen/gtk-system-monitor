#!/usr/bin/env python3
"""
System Monitor - Main Entry Point
Conky-style system monitoring with GTK

Installation:
    sudo apt install python3-gi gir1.2-gtk-3.0 python3-psutil

Usage:
    /usr/bin/python3 main.py
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

from system_data import SystemData
from cpu_grid import CPUGrid
from system_info import SystemInfo

class SystemMonitor(Gtk.Window):
    """Main monitoring window"""
    
    def __init__(self):
        super().__init__(title="System Monitor")
        self.set_default_size(400, 800)
        self._setup_transparency()
        
        # Main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        # Initialize sections
        self.cpu_grid = CPUGrid()
        self.metrics = SystemInfo()  # Tree-style metrics
        
        # Pack into UI
        self.main_box.pack_start(self.cpu_grid.widget, False, False, 0)
        self.main_box.pack_start(self.metrics.widget, False, False, 0)
        
        self.add(self.main_box)
        self.apply_css()
        
        # Start update loop
        GLib.timeout_add_seconds(1, self._update)
    
    def _setup_transparency(self):
        """Enable window transparency"""
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        self.set_app_paintable(True)
    
    def _update(self):
        """Collect data and update all sections"""
        data = SystemData.get_all()
        
        self.cpu_grid.update(data)
        self.metrics.update(data)
        
        return True
    
    def apply_css(self):
        """Apply global styling"""
        css_provider = Gtk.CssProvider()
        css = b"""
        window {
            background-color: rgba(0, 0, 0, 0.7);
        }
        frame {
            border: .5px solid #FFFFFF;
            background-color: transparent;
        }
        box {
            background-color: transparent;
        }
        label {
            color: white;
            font-family: monospace;
            font-size: 12px;
        }
        """
        css_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

def main():
    win = SystemMonitor()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
