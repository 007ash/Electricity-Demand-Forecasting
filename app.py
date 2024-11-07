import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from model import ElectricityDemandForecast

class DemandForecastingFontEnd:

    def __init__(self, root):

        self.root = root
        self.root.title("Electricity Demand Forecast")
        self.root.state('zoomed')

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.root.geometry(f"{screen_width}x{screen_height}")
        self.root.configure(bg="#8FAADC")

        self.demand_forecast = ElectricityDemandForecast("DataSet.csv")
        self.demand_forecast.preprocess_data()
        self.demand_forecast.train_model()

        self.create_frames()
        self.create_left_frame_content()
        self.create_right_frame_content()

    def create_frames(self):

        self.frame_left = tk.Frame(self.root, bg="#5F85A3", bd=3, relief="ridge")
        self.frame_left.place(relx=0.05, rely=0.05, relwidth=0.4, relheight=0.4)

        self.frame_right = tk.Frame(self.root, bg="#5F85A3", bd=3, relief="ridge")
        self.frame_right.place(relx=0.55, rely=0.05, relwidth=0.4, relheight=0.4)

        self.graph_frame = tk.Frame(self.root, bg="#8FAADC")
        self.graph_frame.place(relx=0.05, rely=0.50, relwidth=0.9, relheight=0.5)

    def create_left_frame_content(self):

        tk.Label(self.frame_left, text="Start Date:", bg="#5F85A3",fg="white", font=("Arial", 15)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.start_date_entry = DateEntry(self.frame_left, width=15, date_pattern='yyyy-mm-dd',font=("Arial", 15))
        self.start_date_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.frame_left, text="Start Time (HH:MM):", font=("Arial", 15),bg="#5F85A3", fg="white").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.start_time_entry = tk.Entry(self.frame_left, width=10,font=("Arial", 15))
        self.start_time_entry.insert(0, "00:00")
        self.start_time_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.frame_left, text="End Date:", bg="#5F85A3", fg="white", font=("Arial", 15)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.end_date_entry = DateEntry(self.frame_left, width=15,hight=5, date_pattern='yyyy-mm-dd',font=("Arial", 15))
        self.end_date_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self.frame_left, text="End Time (HH:MM):",font=("Arial", 15), bg="#5F85A3", fg="white").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.end_time_entry = tk.Entry(self.frame_left, width=10,font=("Arial", 15))
        self.end_time_entry.insert(0, "23:59")
        self.end_time_entry.grid(row=3, column=1, padx=10, pady=5)

        display_button = tk.Button(
            self.frame_left, text="Display Values", bg="#4267B2", fg="white",
            font=("Arial", 15, "bold"), width=15, height=1, command=self.display_values)
        display_button.grid(row=4, column=0, columnspan=2, pady=20)

    def create_right_frame_content(self):

        self.text_area = tk.Text(self.frame_right, wrap="word", font=("Arial", 15))
        self.text_area.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(self.frame_right, orient="vertical", command=self.text_area.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_area.config(yscrollcommand=scrollbar.set)

    def display_values(self):

        start_date = self.start_date_entry.get()
        start_time = self.start_time_entry.get()
        end_date = self.end_date_entry.get()
        end_time = self.end_time_entry.get()
        start_datetime = f"{start_date} {start_time}"
        end_datetime = f"{end_date} {end_time}"

        try:
            result_df = self.demand_forecast.get_Value(start_datetime, end_datetime)
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, result_df.to_string(index=False))

            for widget in self.graph_frame.winfo_children():
                widget.destroy()

            fig, ax = plt.subplots(figsize=(8, 4))
            result_df['pred'].plot(figsize=(20, 5), color='Green', title='Future Predictions', ax=ax)
            ax.set_title("Electricity Future Predictions")
            ax.set_xlabel("Hour")
            ax.set_ylabel("Predicted Demand")
            ax.legend()

            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()
            canvas.get_tk_widget().pack(expand=True, fill='both')

        except Exception as e:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, f"Error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DemandForecastingFontEnd(root)
    root.mainloop()