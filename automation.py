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
        logger.info(f"    Filling dropdown with value: '{value}'")
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView(true);", container_element)
        time.sleep(0.3)
        
        # Click the container to open dropdown
        container_element.click()
        logger.info(f"    Clicked dropdown container")
        time.sleep(1)  # Wait longer for dropdown to open
        
        # Type the value - try multiple selectors
        input_field = None
        selectors = [
            "input",
            "input[type='text']",
            ".css-1hwfws3 input",
            "[class*='input']"
        ]
        
        for selector in selectors:
            try:
                input_field = container_element.find_element(By.CSS_SELECTOR, selector)
                if input_field:
                    logger.info(f"    Found input field with selector: {selector}")
                    break
            except:
                continue
        
        if not input_field:
            # Try finding input in the document
            try:
                inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                for inp in inputs:
                    try:
                        if inp.is_displayed() and inp.is_enabled():
                            input_field = inp
                            logger.info(f"    Found visible input field in document")
                            break
                    except:
                        continue
            except:
                pass
        
        if not input_field:
            logger.error(f"    ❌ Could not find input field for dropdown")
            return False
        
        # Clear and type the value
        input_field.clear()
        time.sleep(0.2)
        input_field.send_keys(value)
        logger.info(f"    Typed '{value}' into input field")
        time.sleep(1)  # Wait for options to filter
        
        # Try to find and click the option, or press Enter
        try:
            # Look for the option in the dropdown
            options = driver.find_elements(By.CSS_SELECTOR, "[class*='option'], [id*='option']")
            for option in options:
                try:
                    if value.lower() in option.text.lower():
                        logger.info(f"    Found matching option: '{option.text}'")
                        option.click()
                        time.sleep(0.5)
                        logger.info(f"    ✅ Selected option by clicking")
                        return True
                except:
                    continue
        except:
            pass
        
        # Fallback: Press Enter
        input_field.send_keys(Keys.ENTER)
        time.sleep(0.5)
        logger.info(f"    ✅ Selected option by pressing Enter")
        
        # Verify selection was made
        time.sleep(0.5)
        try:
            # Check if the value appears in the container
            container_text = container_element.text.lower()
            if value.lower() in container_text:
                logger.info(f"    ✅ Verified selection: '{value}' appears in container")
                return True
            else:
                logger.warning(f"    ⚠️ Selection verification unclear. Container text: '{container_element.text[:100]}'")
                # Still return True as it might have worked
                return True
        except:
            logger.warning(f"    ⚠️ Could not verify selection, but assuming success")
            return True
        
    except Exception as e:
        logger.error(f"    ❌ Error filling react-select: {e}\n{traceback.format_exc()}")
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

