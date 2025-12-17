"""
System Data Collector
Centralized data fetching for all system stats
"""
import psutil
import subprocess

class SystemData:
    """Static methods for collecting system data"""
    
    # Store previous network counters for speed calculation
    _prev_net_counters = None
    _prev_net_time = None
    
    @staticmethod
    def get_all():
        """Collect all system data at once"""
        return {
            'cpu_percents': SystemData.get_cpu_percents(),
            'cpu_freqs': SystemData.get_cpu_frequencies(),
            'cpu_temps': SystemData.get_cpu_temperatures(),
            'cpu_package_temp': SystemData.get_cpu_package_temp(),
            'gpu_stats': SystemData.get_gpu_stats(),
            'cuda_available': SystemData.get_cuda_status(),
            'memory_stats': SystemData.get_memory_stats(),
            'disk_io': SystemData.get_disk_io(),
            'disk_usage': SystemData.get_disk_usage('/home'),
            'network_stats': SystemData.get_network_stats('eno1')
        }
    
    @staticmethod
    def get_cpu_percents():
        """Get per-CPU usage percentages"""
        return psutil.cpu_percent(percpu=True, interval=None)
    
    @staticmethod
    def get_cpu_frequencies():
        """Get CPU frequencies from /proc/cpuinfo"""
        freqs = []
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'cpu MHz' in line:
                        freqs.append(float(line.split(':')[1].strip()))
        except:
            pass
        return freqs
    
    @staticmethod
    def get_cpu_temperatures():
        """Get per-core temperatures from sensors"""
        temps = {}
        try:
            result = subprocess.run(['sensors'], capture_output=True, text=True, timeout=2)
            for line in result.stdout.split('\n'):
                if 'Core' in line and 'Â°C' in line:
                    parts = line.split(':')
                    core_num = int(parts[0].replace('Core', '').strip())
                    temp_str = parts[1].split('Â°C')[0].strip().replace('+', '')
                    temps[int(core_num)] = float(temp_str)
        except:
            pass
        return temps
    
    @staticmethod
    def get_cpu_package_temp():
        """Get overall CPU package temperature"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                return int(f.read().strip()) / 1000
        except:
            return None
    
    @staticmethod
    def get_gpu_stats():
        """Get GPU temperature, power, and memory from nvidia-smi"""
        stats = {'temp': None, 'power_draw': None, 'power_limit': None, 
                 'mem_used': None, 'mem_total': None}
        try:
            # Temperature
            result = subprocess.run(['nvidia-smi', '--query-gpu=temperature.gpu', 
                                   '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                stats['temp'] = int(result.stdout.strip())
            
            # Power
            result = subprocess.run(['nvidia-smi', '--query-gpu=power.draw,power.limit', 
                                   '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                parts = result.stdout.strip().split(',')
                stats['power_draw'] = float(parts[0].strip())
                stats['power_limit'] = float(parts[1].strip())
            
            # Memory
            result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total', 
                                   '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                parts = result.stdout.strip().split(',')
                stats['mem_used'] = int(parts[0].strip())
                stats['mem_total'] = int(parts[1].strip())
        except:
            pass
        return stats
    
    @staticmethod
    def get_cuda_status():
        """Check if CUDA is available"""
        try:
            import ctypes
            cudart = ctypes.CDLL('libcudart.so')
            count = ctypes.c_int()
            result = cudart.cudaGetDeviceCount(ctypes.byref(count))
            return result == 0 and count.value > 0
        except:
            return False
    
    @staticmethod
    def get_memory_stats():
        """Get memory usage statistics"""
        try:
            mem = psutil.virtual_memory()
            return {
                'total': mem.total,
                'used': mem.used,
                'available': mem.available,
                'percent': mem.percent
            }
        except:
            return {}
    
    @staticmethod
    def get_disk_io():
        """Get disk I/O statistics"""
        try:
            disk_io = psutil.disk_io_counters()
            # Convert to MB/s (psutil gives bytes)
            return {
                'read_mb': disk_io.read_bytes / (1024**2),
                'write_mb': disk_io.write_bytes / (1024**2)
            }
        except:
            return {}
    
    @staticmethod
    def get_disk_usage(path='/home'):
        """Get disk usage for a path"""
        try:
            usage = psutil.disk_usage(path)
            return {
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent
            }
        except:
            return {}
    
    @staticmethod
    def get_network_stats(interface='eno1'):
        """Get network speed statistics"""
        import time
        
        try:
            # Get current counters
            net_io = psutil.net_io_counters(pernic=True)
            if interface not in net_io:
                # Try to find first active interface
                for iface in net_io.keys():
                    if iface != 'lo':  # Skip loopback
                        interface = iface
                        break
            
            if interface not in net_io:
                return {}
            
            current = net_io[interface]
            current_time = time.time()
            
            # Calculate speed if we have previous data
            if SystemData._prev_net_counters and SystemData._prev_net_time:
                time_delta = current_time - SystemData._prev_net_time
                
                if time_delta > 0:
                    bytes_sent_delta = current.bytes_sent - SystemData._prev_net_counters.bytes_sent
                    bytes_recv_delta = current.bytes_recv - SystemData._prev_net_counters.bytes_recv
                    
                    # Convert to KB/s
                    upload_kbs = (bytes_sent_delta / time_delta) / 1024
                    download_kbs = (bytes_recv_delta / time_delta) / 1024
                    
                    # Store current for next calculation
                    SystemData._prev_net_counters = current
                    SystemData._prev_net_time = current_time
                    
                    return {
                        'upload_kbs': upload_kbs,
                        'download_kbs': download_kbs,
                        'interface': interface
                    }
            
            # First run - store counters
            SystemData._prev_net_counters = current
            SystemData._prev_net_time = current_time
            return {'upload_kbs': 0, 'download_kbs': 0, 'interface': interface}
            
        except:
            return {}
