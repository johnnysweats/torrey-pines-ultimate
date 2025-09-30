#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import threading
import datetime
import pytz

class GolfWaitlistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Torrey Pines Waitlist")
        self.root.geometry("500x600")
        self.root.configure(bg='#f0f0f0')
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🌲 Torrey Pines Waitlist", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # User Information Section
        user_frame = ttk.LabelFrame(main_frame, text="User Information", padding="10")
        user_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Is this John?
        self.is_john_var = tk.StringVar(value="Y")
        ttk.Label(user_frame, text="Is this you john?").grid(row=0, column=0, sticky=tk.W)
        john_frame = ttk.Frame(user_frame)
        john_frame.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        ttk.Radiobutton(john_frame, text="Yes", variable=self.is_john_var, 
                       value="Y", command=self.toggle_user_info).pack(side=tk.LEFT)
        ttk.Radiobutton(john_frame, text="No", variable=self.is_john_var, 
                       value="N", command=self.toggle_user_info).pack(side=tk.LEFT)
        
        # Custom user info (initially hidden)
        self.custom_frame = ttk.Frame(user_frame)
        self.custom_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(self.custom_frame, text="First Name:").grid(row=0, column=0, sticky=tk.W)
        self.first_name_var = tk.StringVar(value="")
        self.first_name_entry = ttk.Entry(self.custom_frame, textvariable=self.first_name_var)
        self.first_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        ttk.Label(self.custom_frame, text="Last Name:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.last_name_var = tk.StringVar(value="")
        self.last_name_entry = ttk.Entry(self.custom_frame, textvariable=self.last_name_var)
        self.last_name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(5, 0))
        
        ttk.Label(self.custom_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.email_var = tk.StringVar(value="")
        self.email_entry = ttk.Entry(self.custom_frame, textvariable=self.email_var)
        self.email_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(5, 0))
        
        ttk.Label(self.custom_frame, text="Phone:").grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        self.phone_var = tk.StringVar(value="")
        self.phone_entry = ttk.Entry(self.custom_frame, textvariable=self.phone_var)
        self.phone_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(5, 0))
        
        # Course Selection
        course_frame = ttk.LabelFrame(main_frame, text="Course Selection", padding="10")
        course_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.course_var = tk.StringVar(value="south")
        courses = [("South Course", "south"), ("North Course", "north"), ("First Available", "first avail.")]
        for i, (text, value) in enumerate(courses):
            ttk.Radiobutton(course_frame, text=text, variable=self.course_var, 
                           value=value).grid(row=i, column=0, sticky=tk.W)
        
        # Players
        players_frame = ttk.LabelFrame(main_frame, text="Number of Players", padding="10")
        players_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.players_var = tk.StringVar(value="1")
        players_frame_inner = ttk.Frame(players_frame)
        players_frame_inner.grid(row=0, column=0)
        for i in range(1, 5):
            ttk.Radiobutton(players_frame_inner, text=str(i), variable=self.players_var, 
                           value=str(i)).grid(row=0, column=i-1, padx=(0, 10))
        
        # Time Selection
        time_frame = ttk.LabelFrame(main_frame, text="Target Time (24-hour format)", padding="10")
        time_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.hour_var = tk.StringVar(value="03")
        self.minute_var = tk.StringVar(value="30")
        
        time_inner = ttk.Frame(time_frame)
        time_inner.grid(row=0, column=0)
        
        ttk.Label(time_inner, text="Hour:").grid(row=0, column=0, sticky=tk.W)
        hour_spin = ttk.Spinbox(time_inner, from_=0, to=23, width=5, textvariable=self.hour_var)
        hour_spin.grid(row=0, column=1, padx=(5, 10))
        
        ttk.Label(time_inner, text="Minute:").grid(row=0, column=2, sticky=tk.W)
        minute_spin = ttk.Spinbox(time_inner, from_=0, to=59, width=5, textvariable=self.minute_var)
        minute_spin.grid(row=0, column=3, padx=(5, 0))
        
        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.caffeinate_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Prevent computer sleep (caffeinate)", 
                       variable=self.caffeinate_var).grid(row=0, column=0, sticky=tk.W)
        
        # Status
        self.status_var = tk.StringVar(value="Ready to run")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                font=('Arial', 10))
        status_label.grid(row=6, column=0, columnspan=2, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(10, 0))
        
        self.run_button = ttk.Button(button_frame, text="🚀 Start Automation", 
                                    command=self.run_automation)
        self.run_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="❌ Exit", 
                  command=root.quit).pack(side=tk.LEFT)
        
        # Initialize
        self.toggle_user_info()
        
    def toggle_user_info(self):
        if self.is_john_var.get() == "Y":
            self.custom_frame.grid_remove()
        else:
            self.custom_frame.grid()
    
    def validate_inputs(self):
        if self.is_john_var.get() == "N":
            if not self.first_name_var.get().strip():
                messagebox.showerror("Error", "Please enter a first name")
                return False
            if not self.last_name_var.get().strip():
                messagebox.showerror("Error", "Please enter a last name")
                return False
            if not self.email_var.get().strip():
                messagebox.showerror("Error", "Please enter an email")
                return False
            if not self.phone_var.get().strip():
                messagebox.showerror("Error", "Please enter a phone number")
                return False
        
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter valid time (HH:MM)")
            return False
        
        return True
    
    def run_automation(self):
        if not self.validate_inputs():
            return
        
        self.run_button.config(state='disabled')
        self.status_var.set("Starting automation...")
        
        # Run in separate thread to keep GUI responsive
        thread = threading.Thread(target=self._run_script)
        thread.daemon = True
        thread.start()
    
    def _run_script(self):
        try:
            # Get script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Prepare command
            if self.caffeinate_var.get():
                cmd = f'cd "{script_dir}" && caffeinate -i bash -c \'source venv/bin/activate && python waitlist.py\''
            else:
                cmd = f'cd "{script_dir}" && source venv/bin/activate && python waitlist.py'
            
            # Create input for the script
            inputs = []
            
            # User info
            if self.is_john_var.get() == "Y":
                inputs.extend(["Y"])  # Is this john? Yes
            else:
                inputs.extend(["N"])  # Is this john? No
                inputs.extend([
                    self.first_name_var.get().strip(),
                    self.last_name_var.get().strip(),
                    self.email_var.get().strip(),
                    self.phone_var.get().strip()
                ])
            
            # Course and players
            inputs.extend([
                self.course_var.get(),
                self.players_var.get(),
                f"{self.hour_var.get()}:{self.minute_var.get()}"
            ])
            
            # Run the script
            process = subprocess.Popen(
                cmd, 
                shell=True, 
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send inputs
            input_str = "\n".join(inputs) + "\n"
            stdout, stderr = process.communicate(input=input_str)
            
            if process.returncode == 0:
                self.root.after(0, lambda: self.status_var.set("✅ Automation completed successfully!"))
                self.root.after(0, lambda: messagebox.showinfo("Success", "Automation completed successfully!"))
            else:
                self.root.after(0, lambda: self.status_var.set("❌ Error occurred during automation"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"Automation failed:\n{stderr}"))
                
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"❌ Error: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to start automation:\n{str(e)}"))
        
        finally:
            self.root.after(0, lambda: self.run_button.config(state='normal'))

def main():
    root = tk.Tk()
    app = GolfWaitlistApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 