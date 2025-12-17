"""
CPU Graph Widget
Reusable CPU usage graph component
"""
import cairo

class CPUGraph:
    """CPU usage graph widget"""
    
    def __init__(self, cpu_num, max_points=50):
        self.cpu_num = cpu_num
        self.max_points = max_points
        self.data_points = [0] * max_points
    
    def update(self, cpu_percent):
        """Add new data point"""
        self.data_points.append(cpu_percent)
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)
    
    def draw(self, widget, cr):
        """Draw the graph on Cairo context"""
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        
        # Background
        cr.set_source_rgba(0, 0, 0, 0.3)
        cr.rectangle(0, 0, width, height)
        cr.fill()
        
        if len(self.data_points) < 2:
            return
        
        x_step = width / (self.max_points - 1)
        
        # Draw line
        cr.set_source_rgb(1.0, 0.64, 0.0)  # Orange
        cr.set_line_width(1.0)
        for i, value in enumerate(self.data_points):
            x = i * x_step
            y = height - (value / 100.0 * height)
            if i == 0:
                cr.move_to(x, y)
            else:
                cr.line_to(x, y)
        cr.stroke()
        
        # Fill under line
        cr.set_source_rgba(1.0, 0.64, 0.0, 0.2)
        for i, value in enumerate(self.data_points):
            x = i * x_step
            y = height - (value / 100.0 * height)
            if i == 0:
                cr.move_to(x, height)
                cr.line_to(x, y)
            else:
                cr.line_to(x, y)
        cr.line_to(width, height)
        cr.close_path()
        cr.fill()
