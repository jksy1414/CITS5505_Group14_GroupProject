from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# New password generated
NEW_PASSWORD = "Test#1234"

print("🚀 Launching browser...")

# Load test account credentials
with open("tests/selenium/test_files/last_test_account.txt", "r") as f:
    username, email, old_password = f.readline().strip().split(",")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    # Step 1: Log in with old password
    print("🔑 Logging in...")
    driver.get("http://127.0.0.1:5000/login")
    time.sleep(2)
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(old_password)
    driver.find_element(By.NAME, "submit").click()
    WebDriverWait(driver, 10).until(EC.url_contains("account"))
    print("✅ Logged in!")
    time.sleep(3)

    # Step 2: Switch to Settings tab
    print("⚙️ Navigating to Settings tab...")
    driver.get("http://127.0.0.1:5000/account")
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Settings']"))
    ).click()
    time.sleep(2)

    # Step 3: Fill password fields
    print("✍️ Filling in password form...")
    driver.find_element(By.NAME, "current_password").send_keys(old_password)
    driver.find_element(By.NAME, "new_password").send_keys(NEW_PASSWORD)
    driver.find_element(By.NAME, "confirm_password").send_keys(NEW_PASSWORD)
    time.sleep(1)

    driver.find_element(By.XPATH, "//button[contains(text(), 'Change Password')]").click()
    print("🔁 Password change submitted.")
    time.sleep(3)

    # Step 4: Log out
    print("🚪 Logging out...")
    driver.find_element(By.CLASS_NAME, "logout").click()
    WebDriverWait(driver, 10).until(EC.url_contains("login"))
    print("✅ Logged out.")

    # Step 5: Log in with new password
    print("🔐 Re-logging in with new password...")
    driver.find_element(By.NAME, "email").send_keys(email)
    time.sleep(3)
    driver.find_element(By.NAME, "password").send_keys(NEW_PASSWORD)
    driver.find_element(By.NAME, "submit").click()

    WebDriverWait(driver, 10).until(EC.url_contains("account"))
    print("🎉 Successfully logged in with new password!")

    # Step 6: Update file with new password
    with open("tests/test_files/last_test_account.txt", "w") as f:
        f.write(f"{username},{email},{NEW_PASSWORD}")
    print("📝 Password updated in last_test_account.txt")

except Exception as e:
    print("❌ Test failed:", e)
    print("📍 Current URL:", driver.current_url)
    print("📄 Page content preview:\n", driver.page_source[:500])

finally:
    time.sleep(5)
    driver.quit()
