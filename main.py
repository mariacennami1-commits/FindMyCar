import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from findmycar.app import FindMyCarApp
    FindMyCarApp().run()
