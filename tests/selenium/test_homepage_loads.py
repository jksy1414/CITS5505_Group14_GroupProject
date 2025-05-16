from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Launch the browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    # Open the homepage (make sure Flask is running)
    driver.get("http://127.0.0.1:5000/")

    # Assertion: Check if the title or key text is present
    assert "FitBug" in driver.title or "Welcome" in driver.page_source

    print("✅ Homepage loaded successfully. Test passed.")

except AssertionError:
    print("❌ Page title or content does not match expectations. Test failed.")

except Exception as e:
    print(f"❌ An exception occurred during the test: {e}")

finally:
    # Optional: wait for 2 seconds before closing the browser
    time.sleep(10)
    driver.quit()
