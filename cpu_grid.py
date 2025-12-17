"""
CPU Grid Section Component
4x8 grid showing per-thread CPU usage
"""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import psutil

from cpu_graph import CPUGraph
from cpu_arch import CPUArchitecture

class CPUGrid:
    """CPU thread monitoring grid (4x8)"""
    
    def __init__(self):
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(0)
        self.grid.set_column_spacing(0)
        self.grid.set_margin_start(10)
        self.grid.set_margin_end(10)
        self.grid.set_margin_top(10)
        self.grid.set_margin_bottom(10)
        
        self.cpu_graphs = []
        self.drawing_areas = []
        self.cpu_labels = []
        
        self._build_grid()
    
    def _build_grid(self):
        """Build the 4x8 CPU grid"""
        num_cpus = psutil.cpu_count()
        cpu_index = 0
        
        for row in range(8):
            for col in range(4):
                if cpu_index >= num_cpus:
                    break
                
                frame = Gtk.Frame()
                frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
                
                drawing_area = Gtk.DrawingArea()
                drawing_area.set_size_request(96, 54)  # 16:9 aspect ratio
                
                cpu_graph = CPUGraph(cpu_index)
                self.cpu_graphs.append(cpu_graph)
                self.drawing_areas.append(drawing_area)
                
                drawing_area.connect("draw", cpu_graph.draw)
                
                label = Gtk.Label(label=f"{cpu_index}")
                label.set_halign(Gtk.Align.START)
                label.set_valign(Gtk.Align.START)
                label.set_margin_start(3)
                label.set_margin_top(2)
                self.cpu_labels.append((label, cpu_index))
                
                overlay = Gtk.Overlay()
                overlay.add(drawing_area)
                overlay.add_overlay(label)
                frame.add(overlay)
                
                self.grid.attach(frame, col, row, 1, 1)
                cpu_index += 1
    
    def update(self, data):
        """Update CPU graphs and labels with new data"""
        cpu_percents = data.get('cpu_percents', [])
        cpu_freqs = data.get('cpu_freqs', [])
        cpu_temps = data.get('cpu_temps', {})
        
        # Update graphs
        for i, cpu_graph in enumerate(self.cpu_graphs):
            if i < len(cpu_percents):
                cpu_graph.update(cpu_percents[i])
                self.drawing_areas[i].queue_draw()
        
        # Update labels
        for label, cpu_idx in self.cpu_labels:
            parts = [str(cpu_idx)]
            
            if cpu_idx < len(cpu_freqs):
                freq_ghz = cpu_freqs[cpu_idx] / 1000
                parts.append(f"{freq_ghz:.2f}GHz")
            
            core_id = CPUArchitecture.thread_to_core(cpu_idx)
            if core_id in cpu_temps:
                parts.append(f"{cpu_temps[core_id]:.0f}°C")
            
            label.set_markup(f'<span size="small">{chr(10).join(parts)}</span>')
    
    @property
    def widget(self):
        """Get the GTK widget"""
        return self.grid
