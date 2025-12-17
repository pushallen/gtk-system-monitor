"""
System Info Section Component
Displays system stats in tree-style ASCII layout (Conky-inspired)
"""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class SystemInfo:
    """System-wide stats in tree format"""
    
    def __init__(self):
        # Create box directly (no frame for borderless look)
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.widget.set_margin_start(10)
        self.widget.set_margin_end(10)
        self.widget.set_margin_top(5)
        self.widget.set_margin_bottom(10)
        
        # Single label with monospace font for tree structure
        self.tree_label = Gtk.Label()
        self.tree_label.set_halign(Gtk.Align.END)  # Right-align
        self.tree_label.set_justify(Gtk.Justification.RIGHT)
        self.tree_label.set_line_wrap(False)
        self.tree_label.set_selectable(False)
        
        self.widget.pack_start(self.tree_label, False, False, 0)
    
    def _format_line(self, value, label, branch):
        """Format a line with proper alignment
        value: right-aligned value (e.g., '67°C', '45.2%')
        label: the label (e.g., 'cpu', 'used')
        branch: the tree branch characters (e.g., '─┤   │   │')
        """
        return f"{value:>12}  {label:<3} {branch}"
    
    def update(self, data):
        """Update system info with tree structure"""
        cpu_temp = data.get('cpu_package_temp')
        gpu = data.get('gpu_stats', {})
        cuda = data.get('cuda_available', False)
        mem = data.get('memory_stats', {})
        disk_io = data.get('disk_io', {})
        disk_usage = data.get('disk_usage', {})
        net = data.get('network_stats', {})
        
        # Build tree structure
        lines = []
        
        # Header
        lines.append("                  ───────────┐")
        lines.append("                             │")
        lines.append("                    system ──┤")
        
        # Temperatures
        lines.append("               Temperatures ─┤   │")
        
        cpu_temp_str = f"{cpu_temp:.0f}°C " if cpu_temp else "N/A"
        lines.append(self._format_line(cpu_temp_str, "cpu", "─┤   │   │"))
        
        gpu_temp_str = f"{gpu.get('temp', 'N/A')}°C " if gpu.get('temp') else "N/A"
        lines.append(self._format_line(gpu_temp_str, "gpu", "─┘   │   │"))
        
        cuda_str = "yes" if cuda else "no"
        lines.append(self._format_line(cuda_str, "cuda", "─┤   │   │"))
        
        # GPU Power
        if gpu.get('power_draw') and gpu.get('power_limit'):
            power_str = f"{gpu['power_draw']:.0f}W/{gpu['power_limit']:.0f}W"
        else:
            power_str = "N/A"
        lines.append(f"{power_str:>8} power ─┘   │   │")
        
        # GPU Memory
        if gpu.get('mem_used') and gpu.get('mem_total'):
            gpu_mem_str = f"{gpu['mem_used']}M/{gpu['mem_total']}M"
        else:
            gpu_mem_str = "N/A"
        lines.append(self._format_line(gpu_mem_str, "vram", "─┤   │   │"))
        
        lines.append(" │   │   │")
        lines.append("     │   │")
        
        # Memory
        lines.append("                    Memory ──┤   │")
        if mem:
            mem_percent = mem.get('percent', 0)
            lines.append(self._format_line(f"{mem_percent:.1f}%", "used", "─┤   │   │"))
            
            mem_used_gb = mem.get('used', 0) / (1024**3)
            mem_total_gb = mem.get('total', 0) / (1024**3)
            lines.append(self._format_line(f"{mem_used_gb:.1f}G/{mem_total_gb:.1f}G ", "", "─┘   │   │"))
        else:
            lines.append(self._format_line("N/A", "", "─┘   │   │"))
        
        lines.append("                             │   │")
        
        # Disk
        lines.append("                Disk Usage ──┘   │")
        if disk_io:
            read_mb = disk_io.get('read_mb', 0)
            write_mb = disk_io.get('write_mb', 0)
            lines.append(self._format_line(f"{read_mb:.1f}M", " read", "─┤       │"))
            lines.append(self._format_line(f"{write_mb:.1f}M", "write", "─┤       │"))
        
        if disk_usage:
            used_gb = disk_usage.get('used', 0) / (1024**3)
            total_gb = disk_usage.get('total', 0) / (1024**3)
            percent = disk_usage.get('percent', 0)
            lines.append(self._format_line(f"{used_gb:.0f}G/{total_gb:.0f}G", "/home", "─┤       │"))
            lines.append(self._format_line(f"{percent:.1f}%  ", "", "─┘       │"))
        
        lines.append("                             │")
        
        # Network
        lines.append("                   Network ──┘")
        if net:
            down_kbs = net.get('download_kbs', 0)
            up_kbs = net.get('upload_kbs', 0)
            lines.append(self._format_line(f"{down_kbs:.1f} KB/s", "download", "─┤    "))
            lines.append(self._format_line(f"{up_kbs:.1f} KB/s  ", "upload", "─┘    "))
        else:
            lines.append(self._format_line("N/A", "", "─┘"))
        
        # Set the text with monospace markup (large size for readability)
        tree_text = '\n'.join(lines)
        self.tree_label.set_markup(f'<span font_desc="Ubuntu Mono 10">{tree_text}</span>')