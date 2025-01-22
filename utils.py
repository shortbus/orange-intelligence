from PyQt6.QtCore import QProcess
import os
import subprocess
import subprocess
def get_current_process_id():
    # Get current process ID
    return os.getpid()

def cmd_v():
    applescript = '''
    tell application "System Events"
        keystroke "v" using {command down}
    end tell
    '''
    return subprocess.run(["osascript", "-e", applescript])

def cmd_c():
    applescript = '''
    tell application "System Events"
        keystroke "c" using {command down}
    end tell
    '''
    return subprocess.run(["osascript", "-e", applescript])


def put_app_in_focus(process_id):
    script = f"""tell application "System Events"
        set frontmost of (first process whose unix id is {process_id}) to true
    end tell"""
    return QProcess.startDetached("/usr/bin/osascript", ["-e", script])


def put_this_app_in_focus():
    this_proceess_id = get_current_process_id()
    print(put_app_in_focus(this_proceess_id))
