import datetime
import pytz
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# --- User Input Section ---

# Default user information
default_user = {
    "first_name": "john",
    "last_name": "silvestro", 
    "email": "silvestro.john@gmail.com",
    "phone": "2036101623"
}

# Ask if this is John
while True:
    is_john = input("Is this you john? (Y/N): ").strip().upper()
    if is_john in ["Y", "N"]:
        break
    else:
        print("Please enter Y or N.")

# Get user information
if is_john == "Y":
    user_info = default_user
    print("Using default information for John.")
else:
    print("Please enter your information:")
    user_info = {}
    
    user_info["first_name"] = input("First name: ").strip()
    user_info["last_name"] = input("Last name: ").strip()
    user_info["email"] = input("Email: ").strip()
    user_info["phone"] = input("Phone number: ").strip()

courses = {"south": "South", "north": "North", "first avail.": "First Avail."}
while True:
    print("Which course would you like to play? (south, north, first avail.)")
    course_input = input("Enter course: ").strip().lower()
    if course_input in courses:
        course = courses[course_input]
        break
    else:
        print("Invalid course. Please enter 'south', 'north', or 'first avail.'")

while True:
    players_input = input("How many players? (1, 2, 3, or 4): ").strip()
    if players_input in {"1", "2", "3", "4"}:
        players = players_input
        break
    else:
        print("Invalid number. Please enter 1, 2, 3, or 4.")

while True:
    time_input = input("What time would you like to run the script? (HH:MM or HHMM, 24-hour, California time): ").strip()
    try:
        # Remove colon if present
        time_input = time_input.replace(":", "")
        
        # Check if it's a 4-digit number
        if len(time_input) == 4 and time_input.isdigit():
            hour = int(time_input[:2])
            minute = int(time_input[2:])
        else:
            # Try original format with colon
            hour, minute = map(int, time_input.split(":"))
        
        if 0 <= hour < 24 and 0 <= minute < 60:
            break
        else:
            print("Invalid time. Please use HH:MM or HHMM in 24-hour format.")
    except Exception:
        print("Invalid format. Please use HH:MM or HHMM in 24-hour format.")

def wait_until_target_time(target_hour, target_minute, timezone_str):
    tz = pytz.timezone(timezone_str)
    now = datetime.datetime.now(tz)
    target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    if now > target:
        target += datetime.timedelta(days=1)
    wait_seconds = (target - now).total_seconds()
    print(f"Waiting until {target.strftime('%Y-%m-%d %H:%M:%S %Z')} ({int(wait_seconds)} seconds)...")
    time.sleep(wait_seconds)

wait_until_target_time(hour, minute, "America/Los_Angeles")

# --- Selenium Section ---

def select_react_select_option(driver, input_id, option_text):
    input_elem = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.ID, input_id))
    )
    input_elem.click()
    option_xpath = f"//div[contains(@class, 'option') and text()='{option_text}']"
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

    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
        "latitude": 32.8986,
        "longitude": -117.2431,
        "accuracy": 100
    })

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
            print(f"[{now_str}] 'Join waitlist' button not available yet. Refreshing... (Attempt {attempt})")
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
        print(f"Selected '{course}' in the course dropdown.")

        select_react_select_option(driver, "react-select-3-input", players)
        print(f"Selected '{players}' in the players dropdown.")

        # Click the "Join the line" button
        try:
            join_line_button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-cy='form-button']"))
            )
            join_line_button.click()
            print("Successfully clicked the 'Join the line' button.")
        except Exception as e:
            print(f"Failed to click 'Join the line' button: {e}")

        time.sleep(15)

    except Exception as e:
        print(f"Failed to fill out the form or select dropdowns: {e}")

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if driver:
        driver.quit()
