#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
from PIL import Image, ImageTk
from datetime import datetime, timedelta

class GolfWaitlistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Torrey Pines Waitlist Automation")
        self.root.geometry("600x700")
        self.root.configure(bg='#f0f0f0')
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#f0f0f0', foreground='black', font=('Arial', 10))
        style.configure('TEntry', fieldbackground='white', foreground='black')
        style.configure('TButton', background='#4CAF50', foreground='white', font=('Arial', 12, 'bold'))
        style.configure('TCombobox', fieldbackground='white', foreground='black')
        
        # Create main canvas and scrollbar
        canvas = tk.Canvas(root, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_label = tk.Label(scrollable_frame, text="Torrey Pines Waitlist Automation", 
                              font=('Arial', 16, 'bold'), fg='black', bg='#f0f0f0')
        title_label.pack(pady=(20, 10))
        
        # Golf Settings Section
        golf_frame = tk.LabelFrame(scrollable_frame, text="Golf Settings", 
                                  font=('Arial', 12, 'bold'),
                                  fg='black', bg='#f0f0f0',
                                  padx=15, pady=15)
        golf_frame.pack(fill='x', pady=(0, 20))
        
        # Course selection
        tk.Label(golf_frame, text="Course:", font=('Arial', 10), fg='black', bg='#f0f0f0').pack(anchor='w')
        self.course_var = tk.StringVar(value="First Available")
        course_combo = ttk.Combobox(golf_frame, textvariable=self.course_var, 
                                   values=["South", "North", "First Available"],
                                   state="readonly", font=('Arial', 10))
        course_combo.pack(fill='x', pady=(0, 10))
        
        # Date selection
        tk.Label(golf_frame, text="Date:", font=('Arial', 10), fg='black', bg='#f0f0f0').pack(anchor='w')
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%m/%d/%Y")
        self.date_var = tk.StringVar(value=tomorrow)
        date_entry = tk.Entry(golf_frame, textvariable=self.date_var, font=('Arial', 10))
        date_entry.pack(fill='x', pady=(0, 10))
        
        # Time selection (fillable)
        tk.Label(golf_frame, text="Time:", font=('Arial', 10), fg='black', bg='#f0f0f0').pack(anchor='w')
        self.time_var = tk.StringVar(value="6:00 AM")
        time_entry = tk.Entry(golf_frame, textvariable=self.time_var, font=('Arial', 10))
        time_entry.pack(fill='x', pady=(0, 10))
        
        # Number of players
        tk.Label(golf_frame, text="Number of Players:", font=('Arial', 10), fg='black', bg='#f0f0f0').pack(anchor='w')
        self.players_var = tk.StringVar(value="1")
        players_combo = ttk.Combobox(golf_frame, textvariable=self.players_var,
                                   values=["1", "2", "3", "4"],
                                   state="readonly", font=('Arial', 10))
        players_combo.pack(fill='x', pady=(0, 10))
        
        # User Information Section
        user_frame = tk.LabelFrame(scrollable_frame, text="User Information", 
                                  font=('Arial', 12, 'bold'),
                                  fg='black', bg='#f0f0f0',
                                  padx=15, pady=15)
        user_frame.pack(fill='x', pady=(0, 20))
        
        # Use default checkbox
        self.use_default_var = tk.BooleanVar(value=False)
        self.default_checkbox = tk.Checkbutton(user_frame, 
                                             text="Use default information for 'John'", 
                                             variable=self.use_default_var,
                                             font=('Arial', 10), fg='black', bg='#f0f0f0',
                                             selectcolor='#4CAF50')
        self.default_checkbox.pack(anchor='w', pady=(0, 10))
        
        # Name
        tk.Label(user_frame, text="Name:", font=('Arial', 10), fg='black', bg='#f0f0f0').pack(anchor='w')
        self.name_var = tk.StringVar(value="John")
        self.name_entry = tk.Entry(user_frame, textvariable=self.name_var, font=('Arial', 10))
        self.name_entry.pack(fill='x', pady=(0, 10))
        
        # Email
        tk.Label(user_frame, text="Email:", font=('Arial', 10), fg='black', bg='#f0f0f0').pack(anchor='w')
        self.email_var = tk.StringVar(value="john@example.com")
        self.email_entry = tk.Entry(user_frame, textvariable=self.email_var, font=('Arial', 10))
        self.email_entry.pack(fill='x', pady=(0, 10))
        
        # Phone
        tk.Label(user_frame, text="Phone:", font=('Arial', 10), fg='black', bg='#f0f0f0').pack(anchor='w')
        self.phone_var = tk.StringVar(value="555-123-4567")
        self.phone_entry = tk.Entry(user_frame, textvariable=self.phone_var, font=('Arial', 10))
        self.phone_entry.pack(fill='x', pady=(0, 10))
        
        # Automation Options Section
        options_frame = tk.LabelFrame(scrollable_frame, text="Automation Options", 
                                     font=('Arial', 12, 'bold'),
                                     fg='black', bg='#f0f0f0',
                                     padx=15, pady=15)
        options_frame.pack(fill='x', pady=(0, 20))
        
        # Prevent sleep checkbox
        self.prevent_sleep_var = tk.BooleanVar(value=True)
        self.sleep_checkbox = tk.Checkbutton(options_frame, 
                                            text="Prevent computer sleep during automation", 
                                            variable=self.prevent_sleep_var,
                                            font=('Arial', 10), fg='black', bg='#f0f0f0',
                                            selectcolor='#4CAF50')
        self.sleep_checkbox.pack(anchor='w')
        
        # Summary frame
        summary_frame = tk.LabelFrame(scrollable_frame, text="Summary", 
                                     font=('Arial', 12, 'bold'),
                                     fg='black', bg='#f0f0f0',
                                     padx=15, pady=15)
        summary_frame.pack(fill='x', pady=(0, 20))
        
        self.summary_text = tk.Text(summary_frame, height=6, width=50, 
                                   font=('Arial', 9), fg='black', bg='white',
                                   wrap='word')
        self.summary_text.pack(fill='x')
        
        # Start button
        self.start_button = tk.Button(scrollable_frame, text="Start Waitlist Automation", 
                                     command=self.start_automation,
                                     font=('Arial', 14, 'bold'),
                                     fg='white', bg='#4CAF50',
                                     activebackground='#45a049',
                                     relief='raised', bd=3,
                                     width=25, height=2)
        self.start_button.pack(pady=20)
        
        # Status label
        self.status_label = tk.Label(scrollable_frame, text="Ready to start automation", 
                                    font=('Arial', 10), fg='black', bg='#f0f0f0')
        self.status_label.pack(pady=(10, 20))
        
        # Bind checkbox to toggle fields
        self.default_checkbox.config(command=self.toggle_fields)
        self.toggle_fields()
        
        # Update summary
        self.update_summary()
        
        # Bind events to update summary (simplified)
        course_combo.bind('<<ComboboxSelected>>', lambda e: self.update_summary())
        date_entry.bind('<KeyRelease>', lambda e: self.update_summary())
        time_entry.bind('<KeyRelease>', lambda e: self.update_summary())
        players_combo.bind('<<ComboboxSelected>>', lambda e: self.update_summary())
    
    def update_summary(self):
        """Update the summary text with current settings"""
        try:
            summary = f"""Golf Settings:
• Course: {self.course_var.get()}
• Date: {self.date_var.get()}
• Time: {self.time_var.get()}
• Players: {self.players_var.get()}

User: {self.name_var.get().title()}
Email: {self.email_var.get()}

The automation will attempt to join the waitlist for {self.course_var.get()} on {self.date_var.get()} at {self.time_var.get()} for {self.players_var.get()} player(s)."""
            
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(1.0, summary)
        except:
            pass  # Ignore errors during summary update
    
    def toggle_fields(self):
        """Enable/disable fields based on default checkbox"""
        if self.use_default_var.get():
            # Disable fields and set default values
            self.name_entry.config(state='disabled')
            self.email_entry.config(state='disabled')
            self.phone_entry.config(state='disabled')
            
            # Set default values
            self.name_var.set("John")
            self.email_var.set("john@example.com")
            self.phone_var.set("555-123-4567")
        else:
            # Enable fields
            self.name_entry.config(state='normal')
            self.email_entry.config(state='normal')
            self.phone_entry.config(state='normal')
        
        self.update_summary()
    
    def start_automation(self):
        """Start the automation process"""
        try:
            self.status_label.config(text="Starting automation...")
            self.start_button.config(state='disabled')
            self.root.update()
            
            # Get all settings
            course = self.course_var.get()
            date = self.date_var.get()
            time = self.time_var.get()
            players = self.players_var.get()
            
            name = self.name_var.get().title()  # Convert to Title Case
            email = self.email_var.get()
            phone = self.phone_var.get()
            
            # Show confirmation dialog
            confirm_text = f"""Confirm Automation Settings:

Golf Details:
• Course: {course}
• Date: {date}
• Time: {time}
• Players: {players}

User: {name}
Email: {email}

The automation will attempt to join the waitlist for {course} on {date} at {time} for {players} player(s).

Do you want to proceed?"""
            
            if not messagebox.askyesno("Confirm Automation", confirm_text):
                self.status_label.config(text="Automation cancelled")
                self.start_button.config(state='normal')
                return
            
            # Convert time to 24-hour format for the script
            try:
                # Parse time like "11:52 AM" to 24-hour format
                from datetime import datetime
                time_obj = datetime.strptime(time, "%I:%M %p")
                time_24hr = time_obj.strftime("%H:%M")
            except:
                # If parsing fails, try direct format
                time_24hr = time
            
            # Create a temporary script with the settings
            temp_script_content = f'''import datetime
import pytz
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# User information from GUI
user_info = {{
    "first_name": "{name.split()[0].lower() if name else 'john'}",
    "last_name": "{name.split()[-1].lower() if len(name.split()) > 1 else 'silvestro'}",
    "email": "{email}",
    "phone": "{phone}"
}}

# Course mapping
course_mapping = {{
    "South": "South",
    "North": "North", 
    "First Available": "First Avail."
}}

course = course_mapping.get("{course}", "First Avail.")
players = "{players}"

# Parse time
hour, minute = map(int, "{time_24hr}".split(":"))

def wait_until_target_time(target_hour, target_minute, timezone_str):
    tz = pytz.timezone(timezone_str)
    now = datetime.datetime.now(tz)
    target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    if now > target:
        target += datetime.timedelta(days=1)
    wait_seconds = (target - now).total_seconds()
    print(f"Waiting until {{target.strftime('%Y-%m-%d %H:%M:%S %Z')}} ({{int(wait_seconds)}} seconds)...")
    time.sleep(wait_seconds)

print(f"Starting automation for {{course}} at {{time_24hr}} with {{players}} players")
print(f"User: {{user_info['first_name']}} {{user_info['last_name']}}")

wait_until_target_time(hour, minute, "America/Los_Angeles")

# --- Selenium Section ---

def select_react_select_option(driver, input_id, option_text):
    input_elem = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.ID, input_id))
    )
    input_elem.click()
    option_xpath = f"//div[contains(@class, 'option') and text()='{{option_text}}']"
    option_elem = WebDriverWait(driver, 3).until(
        EC.visibility_of_element_located((By.XPATH, option_xpath))
    )
    option_elem.click()

chrome_options = Options()
# chrome_options.add_argument("--headless")  # Uncomment to run headless

driver = None
try:
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_script_timeout(30)

    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {{
        "latitude": 32.8986,
        "longitude": -117.2431,
        "accuracy": 100
    }})

    website_url = "https://waitwhile.com/locations/torreypinesgolf/welcome"
    driver.get(website_url)

    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # Keep refreshing until "Join waitlist" button is available
    max_attempts = 100  # Prevent infinite loop; adjust as needed
    attempt = 0
    while True:
        try:
            join_waitlist_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'wwpp-primary-button')]"))
            )
            join_waitlist_button.click()
            print("Successfully clicked the 'Join waitlist' button.")
            break  # Exit loop if successful
        except Exception:
            attempt += 1
            if attempt >= max_attempts:
                print("Max attempts reached. Exiting.")
                raise
            now_str = datetime.datetime.now().strftime('%H:%M:%S')
            print(f"[{{now_str}}] 'Join waitlist' button not available yet. Refreshing... (Attempt {{attempt}})")
            time.sleep(2)  # Wait 2 seconds before refreshing
            driver.refresh()
            
    # Fill out the form and select dropdowns
    try:
        first_name_input = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "form_firstName"))
        )
        first_name_input.clear()
        first_name_input.send_keys(user_info["first_name"])

        last_name_input = driver.find_element(By.ID, "form_lastName")
        last_name_input.clear()
        last_name_input.send_keys(user_info["last_name"])

        email_input = driver.find_element(By.ID, "form_email")
        email_input.clear()
        email_input.send_keys(user_info["email"])

        phone_input = driver.find_element(By.ID, "form_phone")
        phone_input.clear()
        phone_input.send_keys(user_info["phone"])

        print("Successfully filled out the form fields.")

        # Use your input for course and players
        select_react_select_option(driver, "react-select-2-input", course)
        print(f"Selected '{{course}}' in the course dropdown.")

        select_react_select_option(driver, "react-select-3-input", players)
        print(f"Selected '{{players}}' in the players dropdown.")

        # Click the "Join the line" button
        try:
            join_line_button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-cy='form-button']"))
            )
            join_line_button.click()
            print("Successfully clicked the 'Join the line' button.")
        except Exception as e:
            print(f"Failed to click 'Join the line' button: {{e}}")

        time.sleep(15)

    except Exception as e:
        print(f"Failed to fill out the form or select dropdowns: {{e}}")

except Exception as e:
    print(f"An error occurred: {{e}}")
finally:
    if driver:
        driver.quit()
'''
            
            # Write the temporary script
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(temp_script_content)
                temp_script_path = f.name
            
            # Prepare command - use the virtual environment python
            cmd = ["python", temp_script_path]
            
            if self.prevent_sleep_var.get():
                cmd = ["caffeinate", "-i"] + cmd
            
            # Run the automation in background
            process = subprocess.Popen(cmd, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     text=True,
                                     cwd=os.getcwd())  # Run in current directory
            
            self.status_label.config(text=f"Automation started for {course} at {time}!")
            
            # Don't wait for completion - let it run in background
            # The process will continue running even after GUI closes
            
            # Clean up temporary file after a delay
            def cleanup_temp_file():
                import time
                time.sleep(10)  # Wait 10 seconds
                try:
                    os.unlink(temp_script_path)
                except:
                    pass
            
            import threading
            cleanup_thread = threading.Thread(target=cleanup_temp_file)
            cleanup_thread.daemon = True
            cleanup_thread.start()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start automation: {str(e)}")
            self.status_label.config(text="Error occurred")
        finally:
            self.start_button.config(state='normal')

def main():
    root = tk.Tk()
    app = GolfWaitlistApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 