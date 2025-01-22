import subprocess
import sys
import time

import pyautogui
import pyperclip
from pynput import keyboard
from PyQt6.QtCore import QTimer, QCoreApplication, QPoint
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QMenu, QSystemTrayIcon

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt

from functions import get_available_functions
from utils import put_this_app_in_focus, put_app_in_focus, cmd_c, cmd_v


def get_focused_text():
    # Simulate Cmd+C to copy the current selection to the clipboard

    # pyperclip.copy('original text')

    # pyautogui.hotkey("command", "c")
    cmd_c()

    # Allow some time for the clipboard to update
    pyautogui.sleep(0.1)

    # Get clipboard content
    clipboard_content = pyperclip.paste()
    print(f"clipboard_content {clipboard_content}")
    return clipboard_content.strip()


class FloatingWindow(QWidget):
    def __init__(self, key_listener):
        super().__init__()
        self.key_listener: KeyListener = key_listener
        self.setWindowTitle("Floating Window")
        self.setGeometry(100, 100, 300, 200)
        self.previousFocusApp = ""

        layout = QVBoxLayout()

        # Add a label
        self.label = QLabel("This is a floating window.")
        layout.addWidget(self.label)

        # Add a scrollable list
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # Populate the list with sample items from a dictionary
        self.items_dict = get_available_functions()
        for key in self.items_dict.keys():
            item = QListWidgetItem(key)
            self.list_widget.addItem(item)

        # Set layout
        self.setLayout(layout)

        # Set focus to the list for navigation
        self.list_widget.setFocus()

    def keyPressEvent(self, event):
        # Handle arrow keys for list navigation
        if event.key() == Qt.Key.Key_Up:
            self.navigate_list(-1)  # Move up in the list
        elif event.key() == Qt.Key.Key_Down:
            self.navigate_list(1)  # Move down in the list
        elif event.key() == Qt.Key.Key_Return:  # Handle Enter key
            self.handle_enter_key()
        else:
            super().keyPressEvent(event)

    def navigate_list(self, direction):
        """Navigate through the list items using arrow keys."""
        current_row = self.list_widget.currentRow()
        new_row = current_row + direction

        # Ensure the new row is within valid bounds
        if 0 <= new_row < self.list_widget.count():
            self.list_widget.setCurrentRow(new_row)

    def processText(self, feature):
        print("prcessing the text")
        try:
            print(f"The focused text is {self.key_listener.focused_text}")
            processed_content = self.items_dict[feature](self.key_listener.focused_text)
            print(f"prcessing the text to {processed_content}")
            pyperclip.copy(processed_content)  # Update clipboard
            print("updated clipboard")
            print(put_app_in_focus(self.key_listener.focused_process_id))
            QTimer.singleShot(300, cmd_v)

            return processed_content

        except Exception as e:
            print(e)
            return f"Error: {e}"

    def handle_enter_key(self):
        """Close the window and trigger the processText function."""
        selected_item = self.list_widget.currentItem()
        if selected_item:  # Check if an item is selected
            self.processText(selected_item.text())  # Pass the text of the selected item to processText
        self.close()  # Close the window

    def closeEvent(self, event):
        # Hide the window instead of closing it to prevent application shutdown
        event.ignore()
        self.hide()
        # Update the key listener state when the window is hidden
        self.key_listener.window_open = False

    def hideEvent(self, event):
        # Ensure the key listener flag is updated when the window is hidden
        self.key_listener.window_open = False

    def showEvent(self, event):
        super().showEvent(event)
        # Ensure the window is focused when shown
        self.raise_()  # Raise the window to the top
        self.activateWindow()  # Make the window active (focused)
        self.key_listener.window_open = True
        self.move(QPoint(*pyautogui.position()))  # Move the window to the current mouse position
        put_this_app_in_focus()




class KeyListener:
    def __init__(self, app):
        self.app = app
        self.option_key = False
        self.last_time = 0
        self.window_open = False
        self.focused_process_id = 0
        self.focused_text = ""

    def get_focused_text(self):
        # Simulate Cmd+C to copy the current selection to the clipboard
        pyautogui.hotkey("command", "c")

        # Allow some time for the clipboard to update
        pyautogui.sleep(0.1)

        # Get clipboard content
        clipboard_content = pyperclip.paste()
        print(f"clipboard_content {clipboard_content}")
        self.focused_text = clipboard_content.strip()

    def return_app_in_focus(self):
        command = '''/usr/bin/osascript -e 'tell application "System Events"
	set frontApp to first application process whose frontmost is true
	return unix id of frontApp
end tell' '''
        res = subprocess.run(command, shell=True, stdin=sys.stdin, stdout=subprocess.PIPE, stderr=sys.stderr, text=True)
        print(res.stdout.strip())
        self.focused_process_id = res.stdout.strip()

    def on_press(self, key):
        try:
            # Check if the pressed key is the Option key (macOS Option key is Alt)
            if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                current_time = time.time()

                # If two presses are detected within 1 second, open the window
                if current_time - self.last_time < 0.8:
                    if not self.window_open:
                        time.sleep(0.3)
                        self.get_focused_text()
                        self.return_app_in_focus()
                        self.open_window()
                self.last_time = current_time
        except AttributeError as e:
            print(e)
            pass

    def open_window(self):
        self.window_open = True
        # Use QTimer.singleShot to schedule the window to be shown on the main thread
        QTimer.singleShot(0, self.app.floating_window.show)

    def on_release(self, key):
        # Stop listener if 'esc' key is pressed
        if key == keyboard.Key.esc:
            pass


class TrayIcon(QSystemTrayIcon):
    def __init__(self, app):
        super().__init__(QIcon("icon.png"), app)  # Set your icon file here
        self.app = app
        self.setToolTip("System Tray Application")

        # Create the menu with two actions
        menu = QMenu()

        # Action to open the floating window
        open_action = QAction("Open Floating Window", self)
        open_action.triggered.connect(self.open_floating_window)

        # Action to quit the application
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_app)

        # Add actions to the menu
        menu.addAction(open_action)
        menu.addAction(quit_action)

        # Set the menu to the tray icon
        self.setContextMenu(menu)

    def open_floating_window(self):
        # Show the floating window when the tray action is triggered
        if not self.app.floating_window.isVisible():
            self.app.floating_window.show()

    def quit_app(self):
        QCoreApplication.quit()


def main():
    app = QApplication(sys.argv)

    # Create the hidden main window (it won't be shown)
    main_window = QWidget()
    app.main_window = main_window

    # Create the key listener
    key_listener = KeyListener(app)
    app.key_listener = key_listener

    # Create the floating window, passing the key listener to it
    floating_window = FloatingWindow(key_listener)
    app.floating_window = floating_window

    # Create the system tray icon
    tray_icon = TrayIcon(app)
    tray_icon.show()

    # Create the key listener and start listening
    listener = keyboard.Listener(on_press=key_listener.on_press, on_release=key_listener.on_release)
    listener.start()

    # Run the event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
