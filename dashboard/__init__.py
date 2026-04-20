"""
space-dashboard
~~~~~~~~~~~~~~~
Interaktywny dashboard astronomiczny z danymi na żywo.
"""

from .nasa_client import NASAClient
from .iss_client import ISSClient

__all__ = ["NASAClient", "ISSClient"]
__version__ = "1.0.0"
