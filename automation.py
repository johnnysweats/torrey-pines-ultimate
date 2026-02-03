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
from selenium.webdriver.common.action_chains import ActionChains
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
        
        # Execute script to remove webdriver property (additional stealth)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info(f"✅ Chrome started successfully. Version: {driver.capabilities.get('browserVersion', 'Unknown')}")
        return driver
    except Exception as e:
        error_msg = f"❌ Failed to start Chrome: {e}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise

def js_click(driver, element):
    """
    Click an element using JavaScript - more reliable for React apps
    """
    driver.execute_script("arguments[0].click();", element)

def robust_click(driver, element):
    """
    Try multiple click methods to ensure the click registers
    """
    # First, scroll element into view
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.3)
    
    # Method 1: Try JavaScript click first (most reliable for React)
    try:
        driver.execute_script("arguments[0].click();", element)
        return True
    except Exception as e:
        logger.warning(f"JS click failed: {e}")
    
    # Method 2: Try ActionChains click
    try:
        ActionChains(driver).move_to_element(element).click().perform()
        return True
    except Exception as e:
        logger.warning(f"ActionChains click failed: {e}")
    
    # Method 3: Try native click as fallback
    try:
        element.click()
        return True
    except Exception as e:
        logger.warning(f"Native click failed: {e}")
    
    return False

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
        robust_click(driver, input_elem)
        logger.info(f"    ✅ Clicked input field {input_id}")
        time.sleep(0.5)
        
        # Find and click the option using XPath (OLD WORKING METHOD)
        option_xpath = f"//div[contains(@class, 'option') and text()='{option_text}']"
        option_elem = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.XPATH, option_xpath))
        )
        robust_click(driver, option_elem)
        logger.info(f"    ✅ Clicked option: '{option_text}'")
        time.sleep(0.5)
        
        return True
        
    except Exception as e:
        logger.error(f"    ❌ Error selecting react-select option: {e}\n{traceback.format_exc()}")
        return False

def check_button_enabled(driver, button):
    """Check if a button is actually enabled and clickable"""
    try:
        # Check disabled attribute
        disabled = button.get_attribute("disabled")
        if disabled:
            return False, "Button has disabled attribute"
        
        # Check aria-disabled
        aria_disabled = button.get_attribute("aria-disabled")
        if aria_disabled == "true":
            return False, "Button has aria-disabled=true"
        
        # Check if button has disabled class
        classes = button.get_attribute("class") or ""
        if "disabled" in classes.lower():
            return False, f"Button has disabled class: {classes}"
        
        # Check computed style for pointer-events
        pointer_events = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).pointerEvents;", button
        )
        if pointer_events == "none":
            return False, "Button has pointer-events: none"
        
        return True, "Button appears enabled"
    except Exception as e:
        return False, f"Error checking button state: {e}"

def verify_submission_success(driver, original_url, timeout=10):
    """
    Verify that the form actually submitted successfully
    Returns (success: bool, message: str)
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        current_url = driver.current_url
        page_source = driver.page_source.lower()
        
        # Check for success indicators
        success_indicators = [
            "you're on the list" in page_source,
            "you are on the list" in page_source,
            "added to" in page_source and "waitlist" in page_source,
            "confirmation" in current_url,
            "success" in current_url,
            "thank" in page_source and "you" in page_source and "waitlist" in page_source,
            "/status" in current_url,  # Often redirects to status page after joining
        ]
        
        if any(success_indicators):
            return True, f"Success confirmed! URL: {current_url}"
        
        # Check for error indicators
        error_indicators = [
            "error" in page_source and "submit" in page_source,
            "failed" in page_source,
            "try again" in page_source,
            "something went wrong" in page_source,
        ]
        
        if any(error_indicators):
            return False, "Form submission failed - error message detected on page"
        
        # Check if URL changed (good sign)
        if current_url != original_url and "registration=waitlist" not in current_url:
            return True, f"URL changed to: {current_url}"
        
        time.sleep(0.5)
    
    # If we're still on the same page after timeout, submission likely failed
    final_url = driver.current_url
    if final_url == original_url or "registration=waitlist" in final_url:
        return False, f"Form did not submit - still on registration page: {final_url}"
    
    return True, f"Submission completed, final URL: {final_url}"

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
    logger.info("TORREY PINES WAITLIST AUTOMATION (FIXED VERSION)")
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
                
                # Use robust click instead of native click
                if robust_click(driver, join_waitlist_button):
                    logger.info("✅ Successfully clicked the 'Join waitlist' button.")
                    break  # Exit loop if successful (OLD WORKING METHOD)
                else:
                    raise Exception("All click methods failed")
                    
            except Exception as e:
                attempt += 1
                if attempt >= max_attempts:
                    # Save page source for debugging before failing
                    try:
                        import os
                        debug_dir = "/tmp" if headless else "."
                        page_source_file = os.path.join(debug_dir, f"debug_page_source_{int(time.time())}.html")
                        with open(page_source_file, 'w', encoding='utf-8') as f:
                            f.write(driver.page_source)
                        logger.error(f"  📄 Saved page source to {page_source_file} for debugging")
                        
                        # Log what buttons we actually found
                        try:
                            all_buttons = driver.find_elements(By.TAG_NAME, "button")
                            logger.error(f"  Found {len(all_buttons)} buttons on page:")
                            for i, btn in enumerate(all_buttons[:10]):  # First 10 buttons
                                try:
                                    logger.error(f"    Button {i+1}: text='{btn.text[:50]}', class='{btn.get_attribute('class')[:50]}'")
                                except:
                                    pass
                        except:
                            pass
                    except:
                        pass
                    
                    error_msg = "Max attempts reached. Exiting."
                    logger.error(f"  ❌ {error_msg}")
                    raise Exception(error_msg)
                now_str = datetime.now().strftime('%H:%M:%S')
                logger.info(f"  [{now_str}] 'Join waitlist' button not available yet. Refreshing... (Attempt {attempt})")
                time.sleep(2)  # OLD WORKING SCRIPT uses 2 seconds, not retry_delay
                driver.refresh()  # OLD WORKING METHOD: refresh not navigate
        
        # Wait for form to load after clicking join waitlist
        time.sleep(1)
        
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
        
        logger.info(f"\n[6/7] Looking for 'Join the line' button...")
        
        # Capture current URL before submission for comparison
        pre_submit_url = driver.current_url
        logger.info(f"  Pre-submit URL: {pre_submit_url}")
        
        # Use the EXACT selector from the working script (OLD WORKING METHOD)
        try:
            join_line_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-cy='form-button']"))
            )
            logger.info(f"✅ Found 'Join the line' button")
            
            # NEW: Check if button is actually enabled
            is_enabled, status_msg = check_button_enabled(driver, join_line_button)
            logger.info(f"  Button status: {status_msg}")
            
            if not is_enabled:
                # Check if waitlist is closed
                page_source = driver.page_source.lower()
                if "not available" in page_source or "closed" in page_source:
                    error_msg = "Waitlist is currently closed (button is disabled). The waitlist may not be open yet."
                    logger.error(f"❌ {error_msg}")
                    return {'status': 'error', 'message': error_msg}
                else:
                    logger.warning(f"⚠️ Button appears disabled but continuing anyway...")
            
        except Exception as e:
            error_msg = f"Failed to find 'Join the line' button: {e}"
            logger.error(f"❌ {error_msg}")
            return {'status': 'error', 'message': error_msg}
        
        try:
            logger.info("\n[7/7] Clicking 'Join the line' button (using robust click)...")
            
            # Scroll button into view first
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", join_line_button)
            time.sleep(0.5)
            
            # Try multiple click methods
            click_success = False
            
            # Method 1: JavaScript click (most reliable for React)
            logger.info("  Attempting JavaScript click...")
            try:
                driver.execute_script("arguments[0].click();", join_line_button)
                click_success = True
                logger.info("  ✅ JavaScript click executed")
            except Exception as e:
                logger.warning(f"  JS click error: {e}")
            
            # Method 2: If JS click didn't cause navigation, try dispatching click event
            time.sleep(1)
            if driver.current_url == pre_submit_url:
                logger.info("  URL unchanged, trying dispatchEvent click...")
                try:
                    driver.execute_script("""
                        var event = new MouseEvent('click', {
                            view: window,
                            bubbles: true,
                            cancelable: true
                        });
                        arguments[0].dispatchEvent(event);
                    """, join_line_button)
                    logger.info("  ✅ dispatchEvent click executed")
                except Exception as e:
                    logger.warning(f"  dispatchEvent click error: {e}")
            
            # Method 3: Try ActionChains as last resort
            time.sleep(1)
            if driver.current_url == pre_submit_url:
                logger.info("  URL still unchanged, trying ActionChains click...")
                try:
                    ActionChains(driver).move_to_element(join_line_button).click().perform()
                    logger.info("  ✅ ActionChains click executed")
                except Exception as e:
                    logger.warning(f"  ActionChains click error: {e}")
            
            # Wait and verify submission
            logger.info("  Waiting for submission to process...")
            time.sleep(3)
            
            # NEW: Actually verify the submission worked
            success, verify_msg = verify_submission_success(driver, pre_submit_url, timeout=12)
            
            if success:
                success_msg = f'Form submitted successfully for {first_name} {last_name}. {verify_msg}'
                logger.info(f"✅ {success_msg}")
                return {
                    'status': 'success',
                    'message': success_msg
                }
            else:
                # Save debug info
                try:
                    import os
                    debug_dir = "/tmp" if headless else "."
                    timestamp = int(time.time())
                    
                    # Save screenshot if possible
                    try:
                        screenshot_file = os.path.join(debug_dir, f"debug_screenshot_{timestamp}.png")
                        driver.save_screenshot(screenshot_file)
                        logger.error(f"  📸 Saved screenshot to {screenshot_file}")
                    except:
                        pass
                    
                    # Save page source
                    page_source_file = os.path.join(debug_dir, f"debug_page_source_{timestamp}.html")
                    with open(page_source_file, 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                    logger.error(f"  📄 Saved page source to {page_source_file}")
                except:
                    pass
                
                error_msg = f"Form submission failed: {verify_msg}"
                logger.error(f"❌ {error_msg}")
                return {'status': 'error', 'message': error_msg}
                
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
