"""
Torrey Pines Waitlist Automation
Fills out and submits the waitlist form
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time
import logging
import traceback

# Set up logging
logger = logging.getLogger(__name__)

# Torrey Pines coordinates (using the exact coordinates from working script)
LATITUDE = 32.8986
LONGITUDE = -117.2431
WAITLIST_URL = "https://waitwhile.com/locations/torreypinesgolf/welcome"  # OLD WORKING URL!

# Map course names from form to website format (OLD WORKING METHOD uses "First Avail." not "1st Available")
COURSE_MAP = {
    "North": "North",
    "South": "South", 
    "1st Available": "First Avail."  # Website expects "First Avail." format
}

def setup_driver(headless=False):
    """Setup Chrome driver with geolocation"""
    chrome_options = Options()
    
    # Set geolocation
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.geolocation": 1,
        "profile.default_content_settings.geolocation": 1,
    })
    
    # Set Chrome binary location for Docker/Linux
    import os
    if os.path.exists('/usr/bin/google-chrome'):
        chrome_options.binary_location = '/usr/bin/google-chrome'
    
    if headless:
        # Headless mode for cloud/production
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument("--remote-debugging-port=9222")
    else:
        # Start maximized so we can see everything (for local testing)
        chrome_options.add_argument("--start-maximized")
    
    # Suppress DevTools logging
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    try:
        # Use Selenium's built-in driver manager
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.selenium_manager import SeleniumManager
        
        driver = webdriver.Chrome(options=chrome_options)
        logger.info(f"✅ Chrome started successfully. Version: {driver.capabilities.get('browserVersion', 'Unknown')}")
        logger.info(f"ChromeDriver version: {driver.capabilities.get('chrome', {}).get('chromedriverVersion', 'Unknown')}")
        return driver
    except Exception as e:
        error_msg = f"❌ Failed to start Chrome: {e}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise

def select_react_select_option(driver, input_id, option_text):
    """
    Fill in a react-select dropdown using the OLD WORKING METHOD
    This matches the exact approach from waitlist.py that worked!
    """
    try:
        logger.info(f"    Selecting '{option_text}' in dropdown with ID: {input_id}")
        
        # Click the input field to open dropdown (OLD WORKING METHOD)
        input_elem = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.ID, input_id))
        )
        input_elem.click()
        logger.info(f"    ✅ Clicked input field {input_id}")
        time.sleep(0.5)
        
        # Find and click the option using XPath (OLD WORKING METHOD)
        option_xpath = f"//div[contains(@class, 'option') and text()='{option_text}']"
        option_elem = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.XPATH, option_xpath))
        )
        option_elem.click()
        logger.info(f"    ✅ Clicked option: '{option_text}'")
        time.sleep(0.5)
        
        return True
        
    except Exception as e:
        logger.error(f"    ❌ Error selecting react-select option: {e}\n{traceback.format_exc()}")
        return False

def run_waitlist_automation(first_name, last_name, email, phone, course, players, headless=False, max_retries=60, retry_delay=5):
    """
    Run the Torrey Pines waitlist automation
    
    Args:
        first_name: User's first name
        last_name: User's last name
        email: User's email
        phone: User's phone number
        course: Course selection (North, South, 1st Available)
        players: Number of players (1-4)
        headless: Run in headless mode (True for production)
        max_retries: Maximum number of times to check for waitlist button (default 60)
        retry_delay: Seconds to wait between retries (default 5)
    
    Returns:
        dict: Result with status and message
    """
    
    logger.info("=" * 60)
    logger.info("TORREY PINES WAITLIST AUTOMATION")
    logger.info("=" * 60)
    logger.info(f"Name: {first_name} {last_name}")
    logger.info(f"Email: {email}")
    logger.info(f"Phone: {phone}")
    logger.info(f"Course: {course}")
    logger.info(f"Players: {players}")
    logger.info(f"Headless: {headless}")
    logger.info(f"Max retries: {max_retries}, Retry delay: {retry_delay}s")
    logger.info("=" * 60)
    
    driver = None
    
    try:
        logger.info("\n[1/7] Setting up browser...")
        driver = setup_driver(headless=headless)
        
        # Override geolocation using Chrome DevTools Protocol
        try:
            driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
                "latitude": LATITUDE,
                "longitude": LONGITUDE,
                "accuracy": 100
            })
            logger.info(f"✅ Geolocation set to: {LATITUDE}, {LONGITUDE}")
        except Exception as geo_error:
            logger.warning(f"⚠️ Failed to set geolocation: {geo_error} - continuing anyway")
        
        logger.info(f"\n[2/7] Navigating to {WAITLIST_URL}...")
        driver.get(WAITLIST_URL)
        
        # Wait for page to load (OLD WORKING METHOD)
        wait = WebDriverWait(driver, 3)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        logger.info("✅ Page loaded")
        
        # RETRY LOGIC - Keep refreshing until we find the Join waitlist button! (OLD WORKING METHOD)
        logger.info(f"\n[3/7] Looking for 'Join waitlist' button (will retry up to {max_retries} times, {retry_delay}s between attempts)...")
        join_button = None
        attempt = 0
        
        while attempt < max_retries and not join_button:
            attempt += 1
            
            try:
                # Use the EXACT selector from the working script (OLD WORKING METHOD)
                join_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'wwpp-primary-button')]"))
                )
                logger.info(f"  ✅ FOUND IT on attempt {attempt}! Clicking 'Join waitlist' button...")
                join_button.click()
                logger.info("✅ Successfully clicked the 'Join waitlist' button.")
                break  # Exit loop if successful
                
            except Exception as e:
                if attempt >= max_retries:
                    error_msg = f"Max attempts ({max_retries}) reached. Join waitlist button not found."
                    logger.error(f"  ❌ {error_msg}")
                    raise Exception(error_msg)
                
                now_str = datetime.now().strftime('%H:%M:%S')
                logger.info(f"  [{now_str}] 'Join waitlist' button not available yet. Refreshing... (Attempt {attempt})")
                time.sleep(retry_delay)  # Wait before refreshing
                driver.refresh()  # Refresh instead of navigate (OLD WORKING METHOD)
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))  # Wait for page to reload
        
        # If we get here, the button was found and clicked successfully
        time.sleep(2)  # Give form time to load
        
        logger.info(f"\n[4/7] Filling out form...")
        
        try:
            # Fill in first name
            first_name_field = wait.until(
                EC.element_to_be_clickable((By.ID, "form_firstName"))
            )
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView(true);", first_name_field)
            time.sleep(0.3)
            first_name_field.clear()
            time.sleep(0.2)
            first_name_field.send_keys(first_name)
            time.sleep(0.3)
            # Verify it was entered
            entered_value = first_name_field.get_attribute('value')
            if entered_value == first_name:
                logger.info(f"✅ Entered first name: {first_name}")
            else:
                logger.warning(f"⚠️ First name may not have been entered correctly. Expected: {first_name}, Got: {entered_value}")
        except Exception as e:
            error_msg = f"Failed to fill first name: {e}"
            logger.error(f"❌ {error_msg}")
            return {'status': 'error', 'message': error_msg}
        
        try:
            # Fill in last name
            last_name_field = wait.until(
                EC.element_to_be_clickable((By.ID, "form_lastName"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", last_name_field)
            time.sleep(0.3)
            last_name_field.clear()
            time.sleep(0.2)
            last_name_field.send_keys(last_name)
            time.sleep(0.3)
            entered_value = last_name_field.get_attribute('value')
            if entered_value == last_name:
                logger.info(f"✅ Entered last name: {last_name}")
            else:
                logger.warning(f"⚠️ Last name may not have been entered correctly. Expected: {last_name}, Got: {entered_value}")
        except Exception as e:
            error_msg = f"Failed to fill last name: {e}"
            logger.error(f"❌ {error_msg}")
            return {'status': 'error', 'message': error_msg}
        
        try:
            # Fill in phone
            phone_field = wait.until(
                EC.element_to_be_clickable((By.ID, "form_phone"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", phone_field)
            time.sleep(0.3)
            phone_field.clear()
            time.sleep(0.2)
            phone_field.send_keys(phone)
            time.sleep(0.3)
            entered_value = phone_field.get_attribute('value')
            if phone in entered_value or entered_value.replace('-', '').replace('(', '').replace(')', '').replace(' ', '') == phone.replace('-', '').replace('(', '').replace(')', '').replace(' ', ''):
                logger.info(f"✅ Entered phone: {phone}")
            else:
                logger.warning(f"⚠️ Phone may not have been entered correctly. Expected: {phone}, Got: {entered_value}")
        except Exception as e:
            error_msg = f"Failed to fill phone: {e}"
            logger.error(f"❌ {error_msg}")
            return {'status': 'error', 'message': error_msg}
        
        try:
            # Fill in email
            email_field = wait.until(
                EC.element_to_be_clickable((By.ID, "form_email"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", email_field)
            time.sleep(0.3)
            email_field.clear()
            time.sleep(0.2)
            email_field.send_keys(email)
            time.sleep(0.3)
            entered_value = email_field.get_attribute('value')
            if entered_value == email:
                logger.info(f"✅ Entered email: {email}")
            else:
                logger.warning(f"⚠️ Email may not have been entered correctly. Expected: {email}, Got: {entered_value}")
        except Exception as e:
            error_msg = f"Failed to fill email: {e}"
            logger.error(f"❌ {error_msg}")
            return {'status': 'error', 'message': error_msg}
        
        logger.info(f"\n[5/7] Selecting course and players using OLD WORKING METHOD...")
        
        # Map course name to website format
        website_course = COURSE_MAP.get(course, course)
        logger.info(f"  Course from form: '{course}' -> Website format: '{website_course}'")
        
        # Use the EXACT method from the working script (OLD WORKING METHOD)
        # Course dropdown - use the mapped course name
        logger.info(f"  Selecting course: {website_course}")
        if select_react_select_option(driver, "react-select-2-input", website_course):
            logger.info(f"  ✅ Selected '{website_course}' in the course dropdown.")
        else:
            error_msg = f'Failed to select course: {website_course}'
            logger.error(f"  ❌ {error_msg}")
            return {'status': 'error', 'message': error_msg}
        
        # Players dropdown
        logger.info(f"  Selecting players: {players}")
        if select_react_select_option(driver, "react-select-3-input", str(players)):
            logger.info(f"  ✅ Selected '{players}' in the players dropdown.")
        else:
            error_msg = f'Failed to select players: {players}'
            logger.error(f"  ❌ {error_msg}")
            return {'status': 'error', 'message': error_msg}
        
        logger.info(f"\n[6/7] Looking for 'Join the line' button using OLD WORKING METHOD...")
        
        # Use the EXACT selector from the working script (OLD WORKING METHOD)
        try:
            join_line_button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-cy='form-button']"))
            )
            logger.info(f"✅ Found 'Join the line' button")
            submit_button = join_line_button
        except Exception as e:
            error_msg = f"Failed to find 'Join the line' button: {e}"
            logger.error(f"❌ {error_msg}")
            return {'status': 'error', 'message': error_msg}
        
        try:
            logger.info("\n[7/7] Clicking 'Join the line' button (OLD WORKING METHOD)...")
            join_line_button.click()
            logger.info("✅ Successfully clicked the 'Join the line' button.")
            
            # OLD WORKING METHOD: Just wait 15 seconds like the original script
            logger.info("Waiting 15 seconds for submission to process (OLD WORKING METHOD)...")
            time.sleep(15)
            
            # Check final state
            current_url = driver.current_url
            logger.info(f"Final URL after submission: {current_url}")
            
            success_msg = f'Form submitted successfully for {first_name} {last_name}. Final URL: {current_url}'
            logger.info(f"✅ {success_msg}")
            
            return {
                'status': 'success',
                'message': success_msg
            }
                
        except Exception as submit_error:
            error_msg = f"Failed to click 'Join the line' button: {submit_error}"
            logger.error(f"❌ {error_msg}\n{traceback.format_exc()}")
            return {'status': 'error', 'message': error_msg}
        
    except Exception as e:
        error_msg = f"❌ CRITICAL ERROR in automation: {e}"
        error_trace = traceback.format_exc()
        logger.error(f"\n{error_msg}\n{error_trace}")
        
        return {
            'status': 'error',
            'message': f'Automation failed: {str(e)}'
        }
    
    finally:
        if driver:
            try:
                logger.info("\n🔒 Closing browser...")
                driver.quit()
                logger.info("✅ Browser closed successfully")
            except Exception as quit_error:
                logger.error(f"❌ Error closing browser: {quit_error}")

if __name__ == "__main__":
    # Test with sample data
    print("Testing Torrey Pines Waitlist Automation")
    print("(Browser will be visible for testing)")
    
    result = run_waitlist_automation(
        first_name="John",
        last_name="Test",
        email="john.test@example.com",
        phone="555-123-4567",
        course="North",
        players="2",
        headless=False  # Set to True for production
    )
    
    print("\n" + "=" * 60)
    print("RESULT:")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print("=" * 60)

