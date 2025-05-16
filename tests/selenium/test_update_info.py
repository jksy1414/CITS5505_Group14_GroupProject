from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

print("🚀 Launching browser...")

# Load test account credentials
with open("tests/selenium/test_files/last_test_account.txt", "r") as f:
    username, email, password = f.readline().strip().split(",")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    print("🔑 Logging in...")
    driver.get("http://127.0.0.1:5000/login")
    time.sleep(2)
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "submit").click()
    WebDriverWait(driver, 10).until(EC.url_contains("account"))
    print("✅ Logged in!")
    time.sleep(3)

    print("👤 Going to /account and switching to 'Profile' tab...")
    driver.get("http://127.0.0.1:5000/account")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "account-tabs")))
    time.sleep(3)

    # Click Profile tab
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Profile']"))
    ).click()
    time.sleep(3)

    # Click "Edit Profile"
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Edit Profile')]"))
    ).click()
    time.sleep(3)

    # Fill out form
    dob = driver.find_element(By.NAME, "dob")
    height = driver.find_element(By.NAME, "height")
    weight = driver.find_element(By.NAME, "weight")

    driver.execute_script("arguments[0].value = arguments[1];", dob, "1999-12-31")
    height.clear()
    height.send_keys("180")
    weight.clear()
    weight.send_keys("70")
    time.sleep(3)

    # Submit
    driver.find_element(By.XPATH, "//button[contains(text(), 'Save Changes')]").click()
    print("💾 Profile updated")
    time.sleep(3)

    print("✅ Test complete")

except Exception as e:
    print("❌ Test failed:", e)
    print("📍 Current URL:", driver.current_url)
    print("📄 Preview:\n", driver.page_source[:500])

finally:
    time.sleep(5)
    driver.quit()
