"""
CPU Architecture Utilities
Handle CPU-specific mappings (14900K: 8 P-cores + 16 E-cores)
"""

class CPUArchitecture:
    """CPU architecture helper for Intel 14900K"""
    
    @staticmethod
    def thread_to_core(thread_id):
        """
        Map thread ID to physical core ID
        
        14900K Layout:
        - P-cores (threads 0-15): cores 0,4,8,12,16,20,24,28 with HT
        - E-cores (threads 16-31): cores 32-47 without HT
        """
        if thread_id < 16:
            # P-cores with hyperthreading
            # Thread 0,1 -> Core 0; Thread 2,3 -> Core 4, etc.
            p_core_index = thread_id // 2
            return p_core_index * 4
        else:
            # E-cores without hyperthreading
            # Thread 16 -> Core 32; Thread 17 -> Core 33, etc.
            return 32 + (thread_id - 16)
