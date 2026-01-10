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
import time
import logging
import traceback

# Set up logging
logger = logging.getLogger(__name__)

# Torrey Pines coordinates
LATITUDE = 32.9045
LONGITUDE = -117.2454
WAITLIST_URL = "https://waitwhile.com/locations/torreypinesgolf"

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

def fill_react_select(driver, container_element, value):
    """Fill in a react-select dropdown"""
    try:
        # Click the container to open dropdown
        container_element.click()
        time.sleep(0.5)
        
        # Type the value
        input_field = container_element.find_element(By.CSS_SELECTOR, "input")
        input_field.send_keys(value)
        time.sleep(0.5)
        
        # Press Enter to select
        input_field.send_keys(Keys.ENTER)
        time.sleep(0.5)
        
        return True
    except Exception as e:
        print(f"Error filling react-select: {e}")
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
        
        # RETRY LOGIC - Keep trying until we find the Join waitlist button!
        join_button = None
        attempt = 0
        
        logger.info(f"\n[3/7] Looking for 'Join waitlist' button (will retry up to {max_retries} times, {retry_delay}s between attempts)...")
        
        while attempt < max_retries and not join_button:
            attempt += 1
            
            try:
                driver.get(WAITLIST_URL)
                time.sleep(3)
                
                current_url = driver.current_url
                logger.info(f"\n  Attempt {attempt}/{max_retries}")
                logger.info(f"  Current URL: {current_url}")
                
                # Check if we're on the closed page
                if "/closed" in current_url:
                    logger.warning(f"  ⚠️ Waitlist closed - will retry in {retry_delay} seconds...")
                    if attempt < max_retries:
                        time.sleep(retry_delay)
                        continue
                    else:
                        error_msg = f'Waitlist remained closed after {max_retries} attempts over {max_retries * retry_delay} seconds.'
                        logger.error(f"  ❌ {error_msg}")
                        return {
                            'status': 'error',
                            'message': error_msg
                        }
                
                # Look for the Join waitlist button
                wait = WebDriverWait(driver, 5)
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "button")))
                
                buttons = driver.find_elements(By.TAG_NAME, "button")
                logger.info(f"  Found {len(buttons)} buttons on page")
                
                for btn in buttons:
                    try:
                        btn_text = btn.text.lower()
                        if "join" in btn_text and "waitlist" in btn_text:
                            join_button = btn
                            logger.info(f"  ✅ FOUND IT! Button text: '{btn.text}'")
                            break
                    except Exception as btn_error:
                        logger.debug(f"  Could not read button text: {btn_error}")
                
                if not join_button:
                    logger.info(f"  'Join waitlist' button not found yet")
                    if attempt < max_retries:
                        logger.info(f"  Waiting {retry_delay} seconds before retry...")
                        time.sleep(retry_delay)
                    
            except Exception as e:
                logger.error(f"  ❌ Error on attempt {attempt}: {e}\n{traceback.format_exc()}")
                if attempt < max_retries:
                    logger.info(f"  Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise  # Re-raise on final attempt
        
        # After all retries, check if we found the button
        if not join_button:
            try:
                screenshot_path = f"screenshot_no_button_{int(time.time())}.png"
                driver.save_screenshot(screenshot_path)
                logger.error(f"❌ Screenshot saved: {screenshot_path}")
            except Exception as screenshot_error:
                logger.error(f"❌ Failed to save screenshot: {screenshot_error}")
            
            error_msg = f'Join waitlist button not found after {max_retries} attempts ({max_retries * retry_delay / 60:.1f} minutes). Waitlist may still be closed.'
            logger.error(f"❌ {error_msg}")
            return {
                'status': 'error',
                'message': error_msg
            }
        
        logger.info("✅ Found button, clicking...")
        try:
            join_button.click()
            time.sleep(3)
            logger.info("✅ Successfully clicked join waitlist button")
        except Exception as click_error:
            error_msg = f"Failed to click join waitlist button: {click_error}"
            logger.error(f"❌ {error_msg}")
            return {
                'status': 'error',
                'message': error_msg
            }
        
        logger.info(f"\n[4/7] Filling out form...")
        
        try:
            # Fill in first name
            first_name_field = wait.until(
                EC.presence_of_element_located((By.ID, "form_firstName"))
            )
            first_name_field.clear()
            first_name_field.send_keys(first_name)
            logger.info(f"✅ Entered first name: {first_name}")
        except Exception as e:
            error_msg = f"Failed to fill first name: {e}"
            logger.error(f"❌ {error_msg}")
            return {'status': 'error', 'message': error_msg}
        
        try:
            # Fill in last name
            last_name_field = driver.find_element(By.ID, "form_lastName")
            last_name_field.clear()
            last_name_field.send_keys(last_name)
            logger.info(f"✅ Entered last name: {last_name}")
        except Exception as e:
            error_msg = f"Failed to fill last name: {e}"
            logger.error(f"❌ {error_msg}")
            return {'status': 'error', 'message': error_msg}
        
        try:
            # Fill in phone
            phone_field = driver.find_element(By.ID, "form_phone")
            phone_field.clear()
            phone_field.send_keys(phone)
            logger.info(f"✅ Entered phone: {phone}")
        except Exception as e:
            error_msg = f"Failed to fill phone: {e}"
            logger.error(f"❌ {error_msg}")
            return {'status': 'error', 'message': error_msg}
        
        try:
            # Fill in email
            email_field = driver.find_element(By.ID, "form_email")
            email_field.clear()
            email_field.send_keys(email)
            logger.info(f"✅ Entered email: {email}")
        except Exception as e:
            error_msg = f"Failed to fill email: {e}"
            logger.error(f"❌ {error_msg}")
            return {'status': 'error', 'message': error_msg}
        
        logger.info(f"\n[5/7] Selecting course and players...")
        
        # Find all react-select containers
        try:
            react_selects = driver.find_elements(By.CSS_SELECTOR, ".css-1s2u09g-control, [class*='select__control']")
            logger.info(f"Found {len(react_selects)} react-select dropdowns")
        except Exception as e:
            error_msg = f"Failed to find dropdown containers: {e}"
            logger.error(f"❌ {error_msg}")
            return {'status': 'error', 'message': error_msg}
        
        if len(react_selects) >= 2:
            # First dropdown - likely Course
            logger.info(f"  Selecting course: {course}")
            if fill_react_select(driver, react_selects[0], course):
                logger.info(f"  ✅ Selected course: {course}")
            else:
                logger.warning(f"  ⚠️ Could not select course: {course}")
                return {'status': 'error', 'message': f'Failed to select course: {course}'}
            
            # Second dropdown - likely Players
            logger.info(f"  Selecting players: {players}")
            if fill_react_select(driver, react_selects[1], str(players)):
                logger.info(f"  ✅ Selected players: {players}")
            else:
                logger.warning(f"  ⚠️ Could not select players: {players}")
                return {'status': 'error', 'message': f'Failed to select players: {players}'}
        else:
            error_msg = f"Found {len(react_selects)} dropdowns (expected 2)"
            logger.error(f"  ❌ {error_msg}")
            return {'status': 'error', 'message': error_msg}
        
        logger.info(f"\n[6/7] Looking for submit button...")
        
        # Find submit button
        submit_button = None
        try:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            logger.info(f"Found {len(buttons)} buttons on form page")
            
            for btn in buttons:
                try:
                    btn_text = btn.text.lower()
                    if "submit" in btn_text or "join" in btn_text or "add" in btn_text:
                        submit_button = btn
                        logger.info(f"✅ Found submit button: '{btn.text}'")
                        break
                except Exception as btn_error:
                    logger.debug(f"Could not read button text: {btn_error}")
        except Exception as e:
            error_msg = f"Failed to find submit button: {e}"
            logger.error(f"❌ {error_msg}")
            return {'status': 'error', 'message': error_msg}
        
        if not submit_button:
            error_msg = 'Submit button not found on form'
            logger.error(f"❌ {error_msg}")
            return {'status': 'error', 'message': error_msg}
        
        try:
            logger.info("\n[7/7] Submitting form...")
            submit_button.click()
            time.sleep(5)  # Wait for submission to complete
            logger.info("✅ Form submitted, waiting for confirmation...")
            
            # Check for success message or confirmation
            current_url = driver.current_url
            logger.info(f"After submit URL: {current_url}")
            
            success_msg = f'Form submitted successfully for {first_name} {last_name} at {current_url}'
            logger.info(f"✅ {success_msg}")
            
            return {
                'status': 'success',
                'message': success_msg
            }
        except Exception as submit_error:
            error_msg = f"Failed to submit form: {submit_error}"
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

