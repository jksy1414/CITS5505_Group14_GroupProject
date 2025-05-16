from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# ❌ Fake credentials
email = "nonexistentuser@example.com"
password = "WrongPassword123"

# Launch browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    # Step 1: Open login page
    driver.get("http://127.0.0.1:5000/login")

    # Step 2: Fill in incorrect login info
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)

    # Step 3: Small delay before clicking login
    time.sleep(2)

    # Step 4: Click submit
    driver.find_element(By.NAME, "submit").click()
    time.sleep(3)  # wait for error message

    # Step 5: Assert login failed
    assert "login" in driver.current_url.lower()
    assert "incorrect" in driver.page_source.lower() or "invalid" in driver.page_source.lower()

    print("✅ Login failure correctly handled. Test passed.")

except Exception as e:
    print(f"❌ Login failure test failed: {e}")

finally:
    time.sleep(5)
    driver.quit()
