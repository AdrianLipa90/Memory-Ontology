"""PNAML Continuity / selective durable episodic memory.

Research architecture: Adrian Lipa. Standalone candidate, not installed in NOEMA.
"""
from .core import (MemoryStore, MetricAccumulator, observe_aux_file,
                   normalize_event, MemoryErrorStatus)

__version__ = '0.1.0'
__all__ = ['MemoryStore', 'MetricAccumulator', 'observe_aux_file',
           'normalize_event', 'MemoryErrorStatus']
