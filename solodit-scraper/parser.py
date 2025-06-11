import json
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def setup_driver():
    # Setup the selenium webdriver
    try:
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        logging.info("WebDriver setup successfully.")
        return driver
    except Exception as e:
        logging.error(f"Failed to set up WebDriver: {e}")
        return None
    
def login(driver):
    # Login to solodit to access the audits
    try:
        driver.get("https://solodit.xyz/auth?next=/login")
        wait = WebDriverWait(driver, 10)
        print("Login page opened, login to continue ...")
        input("Press ENTER to continue after you have logged in ...")
    except Exception as e:
        logging.error(f"Login failed: {e}")

def get_webpage_text_with_selenium(driver, url):
    """Navigates to a URL and extracts text content using BeautifulSoup."""
    try:
        driver.get(url)
        div = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-labelledby='details']//div[@role='textbox']"))
        )

        html_content = div.get_attribute('innerHTML')
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for code_block in soup.find_all("milkdown-code-block"):
            # Find all individual lines of code.
            lines_of_code = code_block.find_all("div", class_="cm-line")
            
            # Rebuild the code by joining the text of each line.
            reconstructed_code = "\n".join(line.get_text() for line in lines_of_code)
            
            # Replace the entire <milkdown-code-block> tag with our perfectly formatted text.
            code_block.replace_with(
                f"\n----new code block----\n{reconstructed_code}\n----end of code block ----\n"
            )

        # Remove any other general UI noise, like leftover buttons.
        for element in soup.find_all('button'):
            element.decompose()

        return soup.get_text(separator='\n', strip=True)

    except Exception as e:
        return f"Error fetching {url}: {e}"  

def main():
    # Setup the driver and login
    driver = setup_driver()
    login(driver)

    # Process URLs from JSON
    json_filename = 'mock.json'
    try:
        with open(json_filename, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        for category, items in json_data.items():
            print(f"\n--- Category: {category} ---")
            for item in items:
                if len(item) > 1:
                    url = item[1]
                    print(f"\n--- Extracting content from URL: {url} ---")
                    webpage_text = get_webpage_text_with_selenium(driver, url)
                    if webpage_text:
                        print("hello")
                else:
                    print("\n--- Skipping invalid item ---")
    
    except FileNotFoundError:
        print(f"Error: The file '{json_filename}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred during URL processing: {e}")

if __name__ == "__main__":
    main()