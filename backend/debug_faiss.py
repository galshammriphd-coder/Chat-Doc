import sys
import os
import platform

print(f"Python Version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Executable: {sys.executable}")

try:
    import numpy
    print(f"NumPy Version: {numpy.__version__}")
    print(f"NumPy Location: {os.path.dirname(numpy.__file__)}")
except ImportError as e:
    print(f"Failed to import numpy: {e}")

try:
    import faiss
    print(f"FAISS Version: {faiss.__version__}")
    print(f"FAISS Location: {os.path.dirname(faiss.__file__)}")
except ImportError as e:
    print(f"Failed to import faiss: {e}")
    # Check for DLL load errors
    if os.name == 'nt':
        print("Checking for potential DLL issues...")
        import ctypes.util
        # Try to find a dependency that might be missing
