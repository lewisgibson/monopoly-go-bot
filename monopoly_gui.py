import tkinter as tk
from threading import Thread, Event
import queue
import monopoly_bot

class MonopolyGUI:
    def __init__(self, master):
        self.master = master
        self.bot_thread = None
        self.bot_stop_event = Event()
        self.queue = queue.Queue()

        self.master.title("Monopoly Bot Control")
        self.start_button = tk.Button(master, text="Start", command=self.start_bot)
        self.start_button.pack()

        self.stop_button = tk.Button(master, text="Stop", command=self.stop_bot)
        self.stop_button.pack()

        self.status_display = tk.Text(master, height=10, width=50)
        self.status_display.pack()

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_bot(self):
        if self.bot_thread is None or not self.bot_thread.is_alive():
            self.bot_stop_event.clear()
            self.bot_thread = Thread(target=self.run_bot)
            self.bot_thread.start()

    def stop_bot(self):
        self.bot_stop_event.set()

    def run_bot(self):
        self.monopoly_bot = monopoly_bot.Monopoly(delay=0.1, stop_event=self.bot_stop_event, queue=self.queue)
        while not self.bot_stop_event.is_set():
            try:
                message = self.queue.get_nowait()
                self.status_display.insert(tk.END, message)
            except queue.Empty:
                continue

    def on_closing(self):
        self.stop_bot()
        if self.bot_thread is not None:
            self.bot_thread.join()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    gui = MonopolyGUI(root)
    root.mainloop()
