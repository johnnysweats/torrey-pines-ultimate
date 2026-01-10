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
        
        # Use the EXACT method from the working script (OLD WORKING METHOD)
        # Course dropdown
        logger.info(f"  Selecting course: {course}")
        if select_react_select_option(driver, "react-select-2-input", course):
            logger.info(f"  ✅ Selected '{course}' in the course dropdown.")
        else:
            error_msg = f'Failed to select course: {course}'
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
            logger.info("\n[7/7] Submitting form...")
            
            # Check if button is enabled/clickable before submitting
            if not submit_button.is_enabled():
                error_msg = "Submit button is disabled - form may be invalid"
                logger.error(f"❌ {error_msg}")
                return {'status': 'error', 'message': error_msg}
            
            # Take screenshot before submit for debugging
            try:
                import os
                screenshot_dir = "/tmp" if headless else "."
                if os.path.exists(screenshot_dir):
                    screenshot_path = os.path.join(screenshot_dir, f"before_submit_{int(time.time())}.png")
                    driver.save_screenshot(screenshot_path)
                    logger.info(f"📸 Screenshot before submit: {screenshot_path}")
            except Exception as screenshot_error:
                logger.debug(f"Could not save pre-submit screenshot: {screenshot_error}")
            
            # Get the URL before clicking
            url_before = driver.current_url
            logger.info(f"URL before submit: {url_before}")
            
            # Scroll button into view if needed
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                time.sleep(0.5)
            except:
                pass
            
            # Click the submit button
            logger.info(f"Clicking submit button: '{submit_button.text}'")
            submit_button.click()
            logger.info("✅ Submit button clicked")
            
            # Wait for form submission to process - check for URL change, success message, or form disappearance
            logger.info("Waiting for submission to complete...")
            success_found = False
            max_wait_time = 15  # Wait up to 15 seconds for confirmation
            check_interval = 1
            waited = 0
            
            while waited < max_wait_time and not success_found:
                time.sleep(check_interval)
                waited += check_interval
                
                try:
                    current_url = driver.current_url
                    page_source = driver.page_source.lower()
                    
                    logger.info(f"  Check {waited}s: URL={current_url[:100]}...")
                    
                    # Check for URL change (indicates navigation after submission)
                    if current_url != url_before:
                        logger.info(f"✅ URL changed after submission: {current_url}")
                        success_found = True
                        break
                    
                    # Check for success indicators in page content
                    success_indicators = [
                        "you've joined",
                        "you have joined",
                        "you are on the waitlist",
                        "successfully added",
                        "confirmed",
                        "thank you",
                        "confirmation",
                        "you're in line",
                        "waitlist position"
                    ]
                    
                    for indicator in success_indicators:
                        if indicator in page_source:
                            logger.info(f"✅ Found success indicator: '{indicator}'")
                            success_found = True
                            break
                    
                    # Check if form is gone (indicating successful submission)
                    try:
                        form_element = driver.find_element(By.ID, "form_firstName")
                        if not form_element.is_displayed():
                            logger.info("✅ Form is no longer visible - submission likely successful")
                            success_found = True
                            break
                    except:
                        # Form element not found - form might be gone = success!
                        logger.info("✅ Form element not found - submission likely successful")
                        success_found = True
                        break
                    
                    # Check for error messages
                    error_indicators = [
                        "error",
                        "failed",
                        "invalid",
                        "required",
                        "try again"
                    ]
                    
                    for indicator in error_indicators:
                        if indicator in page_source and "success" not in page_source:
                            # Look for actual error elements
                            try:
                                error_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='error'], [class*='Error'], [role='alert']")
                                if error_elements:
                                    error_text = error_elements[0].text
                                    error_msg = f"Error found on page after submission: {error_text[:200]}"
                                    logger.error(f"❌ {error_msg}")
                                    return {'status': 'error', 'message': error_msg}
                            except:
                                pass
                    
                except Exception as check_error:
                    logger.debug(f"Error during success check: {check_error}")
            
            # Final verification
            if success_found:
                current_url = driver.current_url
                logger.info(f"✅ Submission appears successful. Final URL: {current_url}")
                
                # Take final screenshot
                try:
                    screenshot_path = os.path.join(screenshot_dir, f"after_submit_{int(time.time())}.png")
                    driver.save_screenshot(screenshot_path)
                    logger.info(f"📸 Screenshot after submit: {screenshot_path}")
                except:
                    pass
                
                success_msg = f'Successfully joined waitlist for {first_name} {last_name}. Final URL: {current_url}'
                logger.info(f"✅ {success_msg}")
                
                return {
                    'status': 'success',
                    'message': success_msg
                }
            else:
                # Check what's actually on the page
                current_url = driver.current_url
                page_title = driver.title
                logger.warning(f"⚠️ No clear success confirmation after {max_wait_time} seconds")
                logger.warning(f"Final URL: {current_url}")
                logger.warning(f"Page title: {page_title}")
                
                # Take screenshot of final state
                try:
                    screenshot_path = os.path.join(screenshot_dir, f"no_confirmation_{int(time.time())}.png")
                    driver.save_screenshot(screenshot_path)
                    logger.warning(f"📸 Screenshot of uncertain state: {screenshot_path}")
                except:
                    pass
                
                error_msg = f'Submission attempted but no confirmation received after {max_wait_time} seconds. URL: {current_url}. Please check manually.'
                logger.error(f"❌ {error_msg}")
                return {'status': 'error', 'message': error_msg}
                
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

