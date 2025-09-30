#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
import threading
import datetime

class SimpleGolfWaitlistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Torrey Pines Waitlist")
        self.root.geometry("450x550")
        self.root.resizable(False, False)
        
        # Configure grid weights
        root.grid_columnconfigure(0, weight=1)
        
        # Main container
        main_frame = tk.Frame(root, bg='#f5f5f5', padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky='nsew')
        
        # Title
        title_label = tk.Label(main_frame, text="🌲 Torrey Pines Waitlist", 
                              font=('Arial', 16, 'bold'), bg='#f5f5f5', fg='#222')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # User Information Section
        user_frame = tk.LabelFrame(main_frame, text="User Information", 
                                  bg='#f5f5f5', fg='#222', padx=10, pady=10)
        user_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        # Is this John?
        tk.Label(user_frame, text="Is this you john?", bg='#f5f5f5', fg='#222').grid(row=0, column=0, sticky='w')
        self.is_john_var = tk.StringVar(value="Y")
        john_frame = tk.Frame(user_frame, bg='#f5f5f5')
        john_frame.grid(row=1, column=0, sticky='w', pady=(5, 0))
        tk.Radiobutton(john_frame, text="Yes", variable=self.is_john_var, 
                      value="Y", command=self.toggle_user_info, bg='#f5f5f5', fg='#222', selectcolor='#e0e0e0', activebackground='#e0e0e0').pack(side='left')
        tk.Radiobutton(john_frame, text="No", variable=self.is_john_var, 
                      value="N", command=self.toggle_user_info, bg='#f5f5f5', fg='#222', selectcolor='#e0e0e0', activebackground='#e0e0e0').pack(side='left')
        
        # Custom user info (initially hidden)
        self.custom_frame = tk.Frame(user_frame, bg='#f5f5f5')
        self.custom_frame.grid(row=2, column=0, sticky='ew', pady=(10, 0))
        
        tk.Label(self.custom_frame, text="First Name:", bg='#f5f5f5', fg='#222').grid(row=0, column=0, sticky='w')
        self.first_name_var = tk.StringVar(value="")
        self.first_name_entry = tk.Entry(self.custom_frame, textvariable=self.first_name_var, bg='#fff', fg='#222', highlightbackground='#ccc', highlightcolor='#4CAF50', highlightthickness=1, relief='solid')
        self.first_name_entry.grid(row=0, column=1, sticky='ew', padx=(10, 0))
        
        tk.Label(self.custom_frame, text="Last Name:", bg='#f5f5f5', fg='#222').grid(row=1, column=0, sticky='w', pady=(5, 0))
        self.last_name_var = tk.StringVar(value="")
        self.last_name_entry = tk.Entry(self.custom_frame, textvariable=self.last_name_var, bg='#fff', fg='#222', highlightbackground='#ccc', highlightcolor='#4CAF50', highlightthickness=1, relief='solid')
        self.last_name_entry.grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=(5, 0))
        
        tk.Label(self.custom_frame, text="Email:", bg='#f5f5f5', fg='#222').grid(row=2, column=0, sticky='w', pady=(5, 0))
        self.email_var = tk.StringVar(value="")
        self.email_entry = tk.Entry(self.custom_frame, textvariable=self.email_var, bg='#fff', fg='#222', highlightbackground='#ccc', highlightcolor='#4CAF50', highlightthickness=1, relief='solid')
        self.email_entry.grid(row=2, column=1, sticky='ew', padx=(10, 0), pady=(5, 0))
        
        tk.Label(self.custom_frame, text="Phone:", bg='#f5f5f5', fg='#222').grid(row=3, column=0, sticky='w', pady=(5, 0))
        self.phone_var = tk.StringVar(value="")
        self.phone_entry = tk.Entry(self.custom_frame, textvariable=self.phone_var, bg='#fff', fg='#222', highlightbackground='#ccc', highlightcolor='#4CAF50', highlightthickness=1, relief='solid')
        self.phone_entry.grid(row=3, column=1, sticky='ew', padx=(10, 0), pady=(5, 0))
        
        # Course Selection
        course_frame = tk.LabelFrame(main_frame, text="Course Selection", 
                                   bg='#f5f5f5', fg='#222', padx=10, pady=10)
        course_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        self.course_var = tk.StringVar(value="south")
        courses = [("South Course", "south"), ("North Course", "north"), ("First Available", "first avail.")]
        for i, (text, value) in enumerate(courses):
            tk.Radiobutton(course_frame, text=text, variable=self.course_var, 
                          value=value, bg='#f5f5f5', fg='#222', selectcolor='#e0e0e0', activebackground='#e0e0e0').grid(row=i, column=0, sticky='w')
        
        # Players
        players_frame = tk.LabelFrame(main_frame, text="Number of Players", 
                                    bg='#f5f5f5', fg='#222', padx=10, pady=10)
        players_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        self.players_var = tk.StringVar(value="1")
        players_frame_inner = tk.Frame(players_frame, bg='#f5f5f5')
        players_frame_inner.grid(row=0, column=0)
        for i in range(1, 5):
            tk.Radiobutton(players_frame_inner, text=str(i), variable=self.players_var, 
                          value=str(i), bg='#f5f5f5', fg='#222', selectcolor='#e0e0e0', activebackground='#e0e0e0').grid(row=0, column=i-1, padx=(0, 10))
        
        # Time Selection
        time_frame = tk.LabelFrame(main_frame, text="Target Time (24-hour format)", 
                                 bg='#f5f5f5', fg='#222', padx=10, pady=10)
        time_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        self.hour_var = tk.StringVar(value="03")
        self.minute_var = tk.StringVar(value="30")
        
        time_inner = tk.Frame(time_frame, bg='#f5f5f5')
        time_inner.grid(row=0, column=0)
        
        tk.Label(time_inner, text="Hour:", bg='#f5f5f5', fg='#222').grid(row=0, column=0, sticky='w')
        hour_spin = tk.Spinbox(time_inner, from_=0, to=23, width=5, textvariable=self.hour_var, bg='#fff', fg='#222', highlightbackground='#ccc', highlightcolor='#4CAF50', highlightthickness=1, relief='solid')
        hour_spin.grid(row=0, column=1, padx=(5, 10))
        
        tk.Label(time_inner, text="Minute:", bg='#f5f5f5', fg='#222').grid(row=0, column=2, sticky='w')
        minute_spin = tk.Spinbox(time_inner, from_=0, to=59, width=5, textvariable=self.minute_var, bg='#fff', fg='#222', highlightbackground='#ccc', highlightcolor='#4CAF50', highlightthickness=1, relief='solid')
        minute_spin.grid(row=0, column=3, padx=(5, 0))
        
        # Options
        options_frame = tk.LabelFrame(main_frame, text="Options", 
                                    bg='#f5f5f5', fg='#222', padx=10, pady=10)
        options_frame.grid(row=5, column=0, columnspan=2, sticky='ew', pady=(0, 20))
        
        self.caffeinate_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Prevent computer sleep (caffeinate)", 
                      variable=self.caffeinate_var, bg='#f5f5f5', fg='#222', selectcolor='#e0e0e0', activebackground='#e0e0e0').grid(row=0, column=0, sticky='w')
        
        # Status
        self.status_var = tk.StringVar(value="Ready to run")
        status_label = tk.Label(main_frame, textvariable=self.status_var, 
                               font=('Arial', 10), bg='#f5f5f5', fg='#222')
        status_label.grid(row=6, column=0, columnspan=2, pady=(0, 10))
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#f5f5f5')
        button_frame.grid(row=7, column=0, columnspan=2, pady=(10, 0))
        
        self.run_button = tk.Button(button_frame, text="🚀 Start Automation", 
                                   command=self.run_automation, bg='#4CAF50', fg='white',
                                   font=('Arial', 10, 'bold'), relief='flat', padx=20, pady=5, activebackground='#388e3c', activeforeground='white')
        self.run_button.pack(side='left', padx=(0, 10))
        
        exit_button = tk.Button(button_frame, text="❌ Exit", 
                               command=root.quit, bg='#f44336', fg='white',
                               font=('Arial', 10, 'bold'), relief='flat', padx=20, pady=5, activebackground='#b71c1c', activeforeground='white')
        exit_button.pack(side='left')
        
        # Configure grid weights for custom frame
        self.custom_frame.grid_columnconfigure(1, weight=1)
        
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
    try:
        root = tk.Tk()
        app = SimpleGolfWaitlistApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 