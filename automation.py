def select_react_select_option(driver, input_id, option_text):
    """
    Fill in a react-select dropdown - FIXED VERSION
    
    Instead of trying to find and click option elements (which is fragile),
    we type the option text into the combobox input and press Enter.
    This is far more reliable, especially in headless mode.
    """
    try:
        logger.info(f"    Selecting '{option_text}' in dropdown with ID: {input_id}")

        # Click the input field to open dropdown
        input_elem = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, input_id))
        )
        robust_click(driver, input_elem)
        logger.info(f"    ✅ Clicked input field {input_id}")
        time.sleep(0.5)

        # Clear any existing value and type the option text
        input_elem.send_keys(Keys.CONTROL + "a")
        input_elem.send_keys(Keys.BACKSPACE)
        time.sleep(0.2)
        
        input_elem.send_keys(option_text)
        logger.info(f"    ✅ Typed '{option_text}' into input")
        time.sleep(0.5)

        # Press Enter to select the filtered option
        input_elem.send_keys(Keys.ENTER)
        logger.info(f"    ✅ Pressed Enter to confirm selection")
        time.sleep(0.5)

        return True

    except Exception as e:
        logger.error(f"    ❌ Error selecting react-select option: {e}\n{traceback.format_exc()}")
        
        # Fallback: try the old XPath method
        try:
            logger.info(f"    Trying fallback XPath method...")
            input_elem = driver.find_element(By.ID, input_id)
            robust_click(driver, input_elem)
            time.sleep(0.5)
            
            # Try multiple XPath patterns
            xpaths = [
                f"//div[contains(@class, 'option') and contains(text(), '{option_text}')]",
                f"//div[contains(@class, 'select__option') and contains(text(), '{option_text}')]",
                f"//div[contains(@class, 'option')][contains(., '{option_text}')]",
            ]
            
            for xpath in xpaths:
                try:
                    option_elem = WebDriverWait(driver, 2).until(
                        EC.visibility_of_element_located((By.XPATH, xpath))
                    )
                    robust_click(driver, option_elem)
                    logger.info(f"    ✅ Fallback worked with xpath: {xpath}")
                    time.sleep(0.5)
                    return True
                except:
                    continue
            
            return False
        except Exception as e2:
            logger.error(f"    ❌ Fallback also failed: {e2}")
            return False
