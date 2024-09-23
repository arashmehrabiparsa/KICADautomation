import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
import threading
import queue

class DataVisualization:
    def __init__(self, master):
        self.master = master
        self.master.title("Channel Data Visualization")
        self.master.geometry("800x600")

        self.data_queue = queue.Queue()
        # Serial port initialization (this is where the serial connection is created)
        self.serial_port = serial.Serial('COM4', 115200)  # Adjust COM port as needed

        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.lines = [self.ax.plot([], [], label=f'Channel {i+1}')[0] for i in range(4)]
        self.ax.set_xlabel('Sample')
        self.ax.set_ylabel('Value')
        self.ax.set_title('Channel Data')
        self.ax.legend()

        self.data = [[] for _ in range(4)]
        self.max_samples = 100  # Limit how many samples to display

        self.start_button = ttk.Button(self.master, text="Start", command=self.start_plotting)
        self.start_button.pack()

        self.stop_button = ttk.Button(self.master, text="Stop", command=self.stop_plotting)
        self.stop_button.pack()

        self.plotting = False

    def read_serial_data(self):
        """ Continuously read from the serial port and add data to the queue """
        while self.plotting:
            try:
                line = self.serial_port.readline().decode().strip()
                values = list(map(int, line.split(',')))
                self.data_queue.put(values)
            except Exception as e:
                print(f"Error reading serial data: {e}")

    def update_plot(self):
        """ Update the plot with new data from the queue """
        while not self.data_queue.empty():
            values = self.data_queue.get()
            for i, value in enumerate(values):
                self.data[i].append(value)
                if len(self.data[i]) > self.max_samples:
                    self.data[i].pop(0)
                self.lines[i].set_data(range(len(self.data[i])), self.data[i])

        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

        if self.plotting:
            self.master.after(50, self.update_plot)  # Schedule the next update

    def start_plotting(self):
        """ Start reading data and updating the plot """
        self.plotting = True
        threading.Thread(target=self.read_serial_data, daemon=True).start()
        self.update_plot()

    def stop_plotting(self):
        """ Stop plotting """
        self.plotting = False

if __name__ == "__main__":
    root = tk.Tk()
    app = DataVisualization(root)
    root.mainloop()
