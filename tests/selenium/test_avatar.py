from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

print("🚀 Launching browser...")
time.sleep(3)

# Load test credentials
with open("tests/selenium/test_files/last_test_account.txt", "r") as f:
    username, email, password = f.readline().strip().split(",")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    print("🔑 Logging in...")
    driver.get("http://127.0.0.1:5000/login")
    time.sleep(3)

    driver.find_element(By.NAME, "email").send_keys(email)
    time.sleep(3)

    driver.find_element(By.NAME, "password").send_keys(password)
    time.sleep(3)

    driver.find_element(By.NAME, "submit").click()
    WebDriverWait(driver, 10).until(EC.url_contains("account"))
    print("✅ Logged in!")
    time.sleep(3)

    print("👤 Navigating to profile page...")
    driver.get("http://127.0.0.1:5000/account")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "account-tabs")))
    time.sleep(3)

    print("🧭 Clicking 'Profile' tab...")
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Profile']"))
    ).click()
    print("📸 Switched to Profile tab")
    time.sleep(3)

    # Upload avatar
    image_path = os.path.abspath("tests/test_files/Stitch.jpg")
    print(f"📤 Uploading new avatar: {image_path}")
    time.sleep(3)

    file_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "avatarInput"))
    )
    file_input.send_keys(image_path)
    print("✅ Avatar file sent")
    time.sleep(3)

    # Wait for avatar to appear
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "profile-avatar"))
    )
    print("✅ Avatar upload triggered successfully!")
    time.sleep(3)

except Exception as e:
    print(f"❌ Test failed: {repr(e)}")
    print("📍 Current URL:", driver.current_url)
    print("📄 Page content preview:", driver.page_source[:500])
    time.sleep(3)

finally:
    print("🛑 Closing browser...")
    time.sleep(3)
    driver.quit()
