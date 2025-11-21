import shutil
import os

def clear_pycache():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pycache_dir = os.path.join(base_dir, "__pycache__")
    if os.path.exists(pycache_dir):
        shutil.rmtree(pycache_dir)
        print("pycache cleared successfully.")
    else:
        print("pycache directory not found.")
        print(pycache_dir)

clear_pycache()
