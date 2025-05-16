from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 🔄 Load test account information (generated during registration)
with open("tests/selenium/test_files/last_test_account.txt", "r") as f:
    username, email, password = f.readline().strip().split(",")

print("🚀 Launching browser for login test...")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    # Step 1: Open login page
    driver.get("http://127.0.0.1:5000/login")
    print("📍 Opened login page")
    time.sleep(2)

    # Step 2: Enter email (used as username)
    driver.find_element(By.NAME, "email").send_keys(email)
    print(f"📧 Entered email (username): {email}")
    time.sleep(3)  # ⏳ Pause to visually confirm username input

    # Step 3: Enter password and submit
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "submit").click()
    print("🔐 Submitted login credentials")
    time.sleep(3)

    # Step 4: Wait until redirected to the account page
    WebDriverWait(driver, 10).until(EC.url_contains("/account"))
    print("✅ Login successful")

except Exception as e:
    print(f"❌ Login test failed: {e}")
    print("📍 Current URL:", driver.current_url)
    print("📄 Page content preview:", driver.page_source[:500])

finally:
    time.sleep(3)
    driver.quit()
