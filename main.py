import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def _refocus_activity():
    try:
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        activity = PythonActivity.mActivity
        Intent = autoclass("android.content.Intent")
        intent = Intent(activity, activity.getClass())
        intent.addFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT | Intent.FLAG_ACTIVITY_NEW_TASK)
        activity.startActivity(intent)
    except:
        pass

if __name__ == "__main__":
    _refocus_activity()
    from findmycar.app import FindMyCarApp
    FindMyCarApp().run()
