import threading
import time
import pyperclip
from checker import check_email, is_email

class ClipboardMonitor:
    def __init__(self, on_detect_callback):
        self.running = False
        self.last_text = ""
        self.callback = on_detect_callback
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _monitor(self):
        while self.running:
            try:
                current = pyperclip.paste().strip()
                if current != self.last_text and is_email(current):
                    self.last_text = current
                    result = check_email(current)
                    self.callback(result)
            except Exception:
                pass
            time.sleep(1)