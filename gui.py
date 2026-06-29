import customtkinter as ctk
import threading
import sys
import os

# Import our pipeline orchestrator
import main as pipeline

# Set appearance mode and color theme
ctk.set_appearance_mode("Dark")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class TextRedirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, str):
        self.widget.insert(ctk.END, str)
        self.widget.see(ctk.END)
        
    def flush(self):
        pass

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("F1 Content Pipeline")
        self.geometry("600x650")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # Title Label
        self.title_label = ctk.CTkLabel(self, text="F1 POST-RACE PIPELINE", font=ctk.CTkFont(family="Inter", size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Input Frame
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(1, weight=1)

        # Year Input
        self.year_label = ctk.CTkLabel(self.input_frame, text="Season Year:")
        self.year_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.year_entry = ctk.CTkEntry(self.input_frame, placeholder_text="e.g. 2024")
        self.year_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.year_entry.insert(0, "2024")

        # Round Input
        self.round_label = ctk.CTkLabel(self.input_frame, text="Round Num:")
        self.round_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.round_entry = ctk.CTkEntry(self.input_frame, placeholder_text="e.g. 1")
        self.round_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Session Input
        self.session_label = ctk.CTkLabel(self.input_frame, text="Session:")
        self.session_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.session_entry = ctk.CTkOptionMenu(self.input_frame, values=["Race (R)", "Qualifying (Q)", "Sprint (S)", "Sprint Shootout (SS)"])
        self.session_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # Run Button
        self.run_button = ctk.CTkButton(self, text="Generate Graphics", height=40, font=ctk.CTkFont(size=16, weight="bold"), command=self.start_pipeline)
        self.run_button.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

        # Logs Label
        self.logs_label = ctk.CTkLabel(self, text="Execution Logs:", font=ctk.CTkFont(size=14, weight="bold"))
        self.logs_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")

        # Text Box for output
        self.log_textbox = ctk.CTkTextbox(self, state="normal", wrap="word", font=ctk.CTkFont(family="Consolas", size=12))
        self.log_textbox.grid(row=4, column=0, padx=20, pady=(5, 20), sticky="nsew")

        # Open Output Folder Button
        self.open_output_btn = ctk.CTkButton(self, text="Open Output Folder", fg_color="transparent", border_width=1, command=self.open_output_folder)
        self.open_output_btn.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # Redirect stdout
        sys.stdout = TextRedirector(self.log_textbox)
        sys.stderr = TextRedirector(self.log_textbox)

        self.current_output_dir = "output"

    def open_output_folder(self):
        if not os.path.exists(self.current_output_dir):
            os.makedirs(self.current_output_dir)
        os.startfile(os.path.abspath(self.current_output_dir))

    def start_pipeline(self):
        year_str = self.year_entry.get().strip()
        round_str = self.round_entry.get().strip()
        session_val = self.session_entry.get()
        
        if not year_str or not round_str:
            print("Error: Please fill in Year and Round number.")
            return
            
        try:
            year = int(year_str)
            round_num = int(round_str)
        except ValueError:
            print("Error: Year and Round must be numbers.")
            return
            
        # Parse session type
        session_type = "R"
        if "Qualifying" in session_val: session_type = "Q"
        elif "Sprint Shootout" in session_val: session_type = "SS"
        elif "Sprint" in session_val: session_type = "S"

        self.current_output_dir = f"output/round_{round_num}"

        # Disable button while running
        self.run_button.configure(state="disabled", text="Running...")
        self.log_textbox.delete("0.0", ctk.END)
        
        # Run in a background thread to prevent UI freezing
        thread = threading.Thread(target=self.run_pipeline_thread, args=(year, round_num, session_type))
        thread.start()

    def run_pipeline_thread(self, year, round_num, session_type):
        try:
            pipeline.run_pipeline(year, round_num, session_type)
        except Exception as e:
            print(f"\n[Error] Pipeline failed: {e}")
        finally:
            # Re-enable button via main thread
            self.after(0, self.reset_button)

    def reset_button(self):
        self.run_button.configure(state="normal", text="Generate Graphics")

if __name__ == "__main__":
    app = App()
    app.mainloop()
