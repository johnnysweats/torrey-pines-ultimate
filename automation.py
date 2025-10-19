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
        print(f"Chrome started successfully. Version: {driver.capabilities['browserVersion']}")
        return driver
    except Exception as e:
        print(f"Failed to start Chrome: {e}")
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
    
    print("=" * 60)
    print("TORREY PINES WAITLIST AUTOMATION")
    print("=" * 60)
    print(f"Name: {first_name} {last_name}")
    print(f"Email: {email}")
    print(f"Phone: {phone}")
    print(f"Course: {course}")
    print(f"Players: {players}")
    print("=" * 60)
    
    driver = None
    
    try:
        print("\n[1/7] Setting up browser...")
        driver = setup_driver(headless=headless)
        
        # Override geolocation using Chrome DevTools Protocol
        driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "accuracy": 100
        })
        print(f"✓ Geolocation set to: {LATITUDE}, {LONGITUDE}")
        
        print(f"\n[2/7] Navigating to {WAITLIST_URL}...")
        
        # RETRY LOGIC - Keep trying until we find the Join waitlist button!
        join_button = None
        attempt = 0
        
        print(f"\n[3/7] Looking for 'Join waitlist' button (will retry up to {max_retries} times)...")
        
        while attempt < max_retries and not join_button:
            attempt += 1
            
            try:
                driver.get(WAITLIST_URL)
                time.sleep(3)
                
                current_url = driver.current_url
                print(f"\nAttempt {attempt}/{max_retries}")
                print(f"  URL: {current_url}")
                
                # Check if we're on the closed page
                if "/closed" in current_url:
                    print(f"  Status: Waitlist closed - will retry in {retry_delay} seconds...")
                    if attempt < max_retries:
                        time.sleep(retry_delay)
                        continue
                    else:
                        return {
                            'status': 'error',
                            'message': f'Waitlist remained closed after {max_retries} attempts over {max_retries * retry_delay} seconds.'
                        }
                
                # Look for the Join waitlist button
                wait = WebDriverWait(driver, 5)
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "button")))
                
                buttons = driver.find_elements(By.TAG_NAME, "button")
                print(f"  Found {len(buttons)} buttons")
                
                for btn in buttons:
                    btn_text = btn.text.lower()
                    if "join" in btn_text and "waitlist" in btn_text:
                        join_button = btn
                        print(f"  ✓ FOUND IT! Button text: '{btn.text}'")
                        break
                
                if not join_button:
                    print(f"  'Join waitlist' button not found yet")
                    if attempt < max_retries:
                        print(f"  Waiting {retry_delay} seconds before retry...")
                        time.sleep(retry_delay)
                    
            except Exception as e:
                print(f"  Error on attempt {attempt}: {e}")
                if attempt < max_retries:
                    print(f"  Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
        
        # After all retries, check if we found the button
        if not join_button:
            screenshot_path = f"screenshot_no_button_{int(time.time())}.png"
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved: {screenshot_path}")
            
            return {
                'status': 'error',
                'message': f'Join waitlist button not found after {max_retries} attempts ({max_retries * retry_delay / 60:.1f} minutes). Waitlist may still be closed.',
                'screenshot': screenshot_path
            }
        
        print("✓ Found button, clicking...")
        join_button.click()
        time.sleep(3)
        
        print(f"\n[4/7] Filling out form...")
        
        # Fill in first name
        first_name_field = wait.until(
            EC.presence_of_element_located((By.ID, "form_firstName"))
        )
        first_name_field.clear()
        first_name_field.send_keys(first_name)
        print(f"✓ Entered first name: {first_name}")
        
        # Fill in last name
        last_name_field = driver.find_element(By.ID, "form_lastName")
        last_name_field.clear()
        last_name_field.send_keys(last_name)
        print(f"✓ Entered last name: {last_name}")
        
        # Fill in phone
        phone_field = driver.find_element(By.ID, "form_phone")
        phone_field.clear()
        phone_field.send_keys(phone)
        print(f"✓ Entered phone: {phone}")
        
        # Fill in email
        email_field = driver.find_element(By.ID, "form_email")
        email_field.clear()
        email_field.send_keys(email)
        print(f"✓ Entered email: {email}")
        
        print(f"\n[5/7] Selecting course and players...")
        
        # Find all react-select containers
        react_selects = driver.find_elements(By.CSS_SELECTOR, ".css-1s2u09g-control, [class*='select__control']")
        
        if len(react_selects) >= 2:
            # First dropdown - likely Course
            print(f"  Selecting course: {course}")
            if fill_react_select(driver, react_selects[0], course):
                print(f"  ✓ Selected course: {course}")
            else:
                print(f"  ⚠ Could not select course")
            
            # Second dropdown - likely Players
            print(f"  Selecting players: {players}")
            if fill_react_select(driver, react_selects[1], str(players)):
                print(f"  ✓ Selected players: {players}")
            else:
                print(f"  ⚠ Could not select players")
        else:
            print(f"  ⚠ Warning: Found {len(react_selects)} dropdowns (expected 2)")
        
        print(f"\n[6/7] Looking for submit button...")
        
        # Take a screenshot before submitting
        screenshot_path = f"screenshot_before_submit_{int(time.time())}.png"
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved: {screenshot_path}")
        
        # Find submit button
        submit_button = None
        buttons = driver.find_elements(By.TAG_NAME, "button")
        
        for btn in buttons:
            btn_text = btn.text.lower()
            if "submit" in btn_text or "join" in btn_text or "add" in btn_text:
                submit_button = btn
                break
        
        if submit_button:
            print(f"✓ Found submit button: '{submit_button.text}'")
            
            print("\n[7/7] Submitting form...")
            submit_button.click()
            time.sleep(5)  # Wait for submission to complete
            
            # Take screenshot after submission
            screenshot_after = f"screenshot_after_submit_{int(time.time())}.png"
            driver.save_screenshot(screenshot_after)
            print(f"Screenshot saved: {screenshot_after}")
            
            # Check for success message or confirmation
            current_url = driver.current_url
            print(f"After submit URL: {current_url}")
            
            if not headless:
                print("\nBrowser will stay open for 10 seconds to see result...")
                time.sleep(10)
            
            return {
                'status': 'success',
                'message': f'Form filled successfully for {first_name} {last_name}',
                'screenshot': screenshot_path
            }
        else:
            return {
                'status': 'error',
                'message': 'Submit button not found'
            }
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        if driver and not headless:
            print("\nBrowser will stay open for 30 seconds for debugging...")
            time.sleep(30)
        
        return {
            'status': 'error',
            'message': str(e)
        }
    
    finally:
        if driver:
            print("\nClosing browser...")
            driver.quit()

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

