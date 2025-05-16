from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

print("🚀 Launching browser...")

# Load test credentials
with open("tests/selenium/test_files/last_test_account.txt", "r") as f:
    username, email, password = f.readline().strip().split(",")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    # Step 1: Login
    print("🔑 Logging in...")
    driver.get("http://127.0.0.1:5000/login")
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "submit").click()
    WebDriverWait(driver, 5).until(EC.url_contains("account"))
    print("✅ Logged in as:", email)
    time.sleep(3)

    # Step 2: Go to analysis page
    driver.get("http://127.0.0.1:5000/analyze_full")
    print("📊 Navigated to analysis page")
    time.sleep(3)

    # Step 3: Upload CSV
    csv_path = os.path.abspath("tests/test_files/Testing.csv")
    print("📁 Uploading CSV:", csv_path)
    upload_input = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.NAME, "fitnessFile"))
    )
    upload_input.send_keys(csv_path)
    time.sleep(3)

    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]"))
    ).click()
    time.sleep(3)

    # Step 4: Select "Steps"
    WebDriverWait(driver, 10).until(EC.url_contains("step=columns"))
    print("🧮 Waiting for 'Steps' checkbox to appear...")
    checkbox = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='checkbox' and @value='Steps']"))
    )
    driver.execute_script("arguments[0].checked = true;", checkbox)
    print("✅ Selected column: Steps")
    time.sleep(3)

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".tab-section.active button[type='submit']"))
    ).click()
    time.sleep(3)

    # Step 5: Rename Headers
    WebDriverWait(driver, 10).until(EC.url_contains("step=rename"))
    print("✏️ Renaming headers...")
    time.sleep(3)

    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".tab-section.active button[type='submit']"))
    ).click()
    time.sleep(3)

    # Step 6: Chart rendering
    WebDriverWait(driver, 10).until(EC.url_contains("step=results"))
    print("📈 Opening chart area...")
    time.sleep(3)

    steps_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Steps']"))
    )
    steps_button.click()
    print("📌 Chart for 'Steps' rendered")
    time.sleep(3)

    # Step 7: Share
    share_now_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "share_now"))
    )
    share_now_button.click()
    print("📤 Chart shared")
    time.sleep(3)

    # Step 8: Confirm success
    WebDriverWait(driver, 5).until(EC.url_contains("/explore"))
    assert "Chart for Steps" in driver.page_source
    print("✅ Chart uploaded and shared successfully!")

except Exception as e:
    print("❌ Test failed:", repr(e))
    print("🧭 Current URL:", driver.current_url)
    print("🧾 Page content preview:\n", driver.page_source[:500])

finally:
    time.sleep(3)
    driver.quit()
