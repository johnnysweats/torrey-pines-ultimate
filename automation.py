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
    """Setup Chrome driver - EXACTLY like the old working script"""
    chrome_options = Options()
    
    # OLD WORKING SCRIPT: headless is commented out, but we need it for cloud
    # So we'll make headless as stealthy as possible
    if headless:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Stealth options to avoid detection
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Set Chrome binary location for Docker/Linux
    import os
    if os.path.exists('/usr/bin/google-chrome'):
        chrome_options.binary_location = '/usr/bin/google-chrome'
    
    try:
        # OLD WORKING SCRIPT uses: webdriver.Chrome(options=chrome_options)
        # But in Docker we might need Service, so try both
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except:
            # Fallback for Docker environments
            from selenium.webdriver.chrome.service import Service
            driver = webdriver.Chrome(service=Service(), options=chrome_options)
        
        # OLD WORKING SCRIPT sets: driver.set_script_timeout(30)
        driver.set_script_timeout(30)
        
        logger.info(f"✅ Chrome started successfully. Version: {driver.capabilities.get('browserVersion', 'Unknown')}")
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
        
        # OLD WORKING SCRIPT: Keep refreshing until "Join waitlist" button is available
        # max_attempts = 100, wait 2 seconds between refreshes
        logger.info(f"\n[3/7] Looking for 'Join waitlist' button (EXACT OLD WORKING METHOD)...")
        max_attempts = max_retries if max_retries < 100 else 100  # Cap at 100 like old script
        attempt = 0
        
        while True:  # OLD WORKING SCRIPT uses infinite loop with break
            try:
                join_waitlist_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'wwpp-primary-button')]"))
                )
                join_waitlist_button.click()
                logger.info("✅ Successfully clicked the 'Join waitlist' button.")
                break  # Exit loop if successful (OLD WORKING METHOD)
            except Exception as e:
                attempt += 1
                if attempt >= max_attempts:
                    error_msg = "Max attempts reached. Exiting."
                    logger.error(f"  ❌ {error_msg}")
                    raise Exception(error_msg)
                now_str = datetime.now().strftime('%H:%M:%S')
                logger.info(f"  [{now_str}] 'Join waitlist' button not available yet. Refreshing... (Attempt {attempt})")
                time.sleep(2)  # OLD WORKING SCRIPT uses 2 seconds, not retry_delay
                driver.refresh()  # OLD WORKING METHOD: refresh not navigate
        
        # OLD WORKING SCRIPT: Fill out the form and select dropdowns
        logger.info(f"\n[4/7] Filling out form (EXACT OLD WORKING METHOD)...")
        
        try:
            # OLD WORKING SCRIPT: Uses WebDriverWait(driver, 3).until(EC.presence_of_element_located)
            first_name_input = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.ID, "form_firstName"))
            )
            first_name_input.clear()
            first_name_input.send_keys(first_name)
            logger.info(f"✅ Entered first name: {first_name}")

            last_name_input = driver.find_element(By.ID, "form_lastName")
            last_name_input.clear()
            last_name_input.send_keys(last_name)
            logger.info(f"✅ Entered last name: {last_name}")

            email_input = driver.find_element(By.ID, "form_email")
            email_input.clear()
            email_input.send_keys(email)
            logger.info(f"✅ Entered email: {email}")

            phone_input = driver.find_element(By.ID, "form_phone")
            phone_input.clear()
            phone_input.send_keys(phone)
            logger.info(f"✅ Entered phone: {phone}")

            logger.info("✅ Successfully filled out the form fields.")
        except Exception as e:
            error_msg = f"Failed to fill out the form: {e}"
            logger.error(f"❌ {error_msg}\n{traceback.format_exc()}")
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

