"""
Background clipboard watcher.

Every second it compares the clipboard to the last seen value. A Python
thread can never touch Tk widgets directly, so detections cross over via
queue.Queue and the GUI mainloop drains the queue with after() — this
removes the random Tkinter 'main thread is not in main loop' crashes.
"""
import threading
import time
import queue

try:
    import pyperclip
except ImportError:            # headless / CI environments
    pyperclip = None


class ClipboardMonitor:
    def __init__(self, on_detect_callback):
        self.queue = queue.Queue()
        self.running = False
        self.last_text = ""
        self.callback = on_detect_callback
        self.thread = None

    def start(self):
        if self.running or pyperclip is None:
            return
        self.running = True
        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()

    def stop(self, join=False):
        self.running = False
        if join and self.thread:
            self.thread.join(timeout=2)

    def is_alive(self):
        return bool(self.thread and self.thread.is_alive())

    def _monitor(self):
        while self.running:
            try:
                current = (pyperclip.paste() or "").strip()
                if current != self.last_text and current:
                    self.last_text = current
                    try:
                        from checker import check_email, is_email
                        if is_email(current):
                            self.queue.put(check_email(current))
                    except Exception:
                        pass
            except Exception:
                pass
            time.sleep(1)

    def pump(self):
        """Drain queued detections on the Tk main thread; returns False when done."""
        results = []
        try:
            while True:
                results.append(self.queue.get_nowait())
        except queue.Empty:
            pass
        for result in results:
            try:
                self.callback(result)
            except Exception:
                pass
        return bool(results)
