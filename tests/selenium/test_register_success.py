from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import os

print("🚀 Launching browser...")

# Generate unique test data
unique_number = random.randint(1000, 9999)
username = f"testuser{unique_number}"
email = f"test{unique_number}@example.com"
password = "Test@1234"

# Launch browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    # Step 1: Go to homepage
    driver.get("http://127.0.0.1:5000/")
    print("📍 Opened homepage")
    time.sleep(2)

    # Step 2: Click "Sign Up"
    sign_up_button = driver.find_element(By.LINK_TEXT, "Sign Up")
    sign_up_button.click()
    print("📝 Navigated to registration form")
    time.sleep(2)

    # Step 3: Fill form
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "confirm_password").send_keys(password)
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "height").send_keys("170")
    driver.find_element(By.NAME, "weight").send_keys("65")
    dob_input = driver.find_element(By.NAME, "dob")
    driver.execute_script("arguments[0].value = '2000-01-01';", dob_input)
    print("✏️ Filled registration form")
    time.sleep(2)

    # Step 4: Submit
    driver.find_element(By.NAME, "submit").click()
    print("📤 Submitted form")
    time.sleep(3)

    # Step 5: Assert success
    assert "account" in driver.current_url or "Welcome" in driver.page_source
    print("✅ Registration successful")

    # Save account info to file
    file_path = os.path.abspath("tests/selenium/test_files/last_test_account.txt")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        f.write(f"{username},{email},{password}\n")
    print(f"📁 Account saved to: {file_path}")
    print(f"📧 Email: {email}\n👤 Username: {username}\n🔑 Password: {password}")

except Exception as e:
    print(f"❌ Test failed with exception: {e}")

finally:
    time.sleep(5)
    driver.quit()
