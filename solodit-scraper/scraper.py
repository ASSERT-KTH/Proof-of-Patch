import json
import logging
from datetime import date
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
#from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import urllib.parse
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

# Setting up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def construct_url(impact, pagination=1, search_term=""):
    # Define the base URL
    base_url = "https://solodit.cyfrin.io/"

    # Prepare parameters
    params = {
        "i": ",".join(impact),  # Join the impacts into a comma-separated string
        "p": pagination,        # Pagination value
        "pc": "",               # Empty 'pc' parameter
        "r": "all",             # Default value for 'r'
        "s": search_term        # Search term
    }

    # Encode the parameters and construct the url
    encoded_params = urllib.parse.urlencode(params)
    full_url = f"{base_url}?{encoded_params}"

    return full_url

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

def search_solodit(driver, search_term, page):
    try:
        # Wait for and interact with the search input
        url = construct_url(["HIGH", "MEDIUM"], pagination=page, search_term=search_term)
        driver.get(url)

        # Find all the link elements
        link_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'loaded-findings')]//button[contains(@class, 'border-b')]//a"))
        )
        
        # Extract ALL 'href' attributes into a NEW list of STRINGS
        urls_to_visit = []
        for element in link_elements:
            href = element.get_attribute("href")
            if href: # Ensure we got a URL
                urls_to_visit.append(href)

        logging.info(f"Found {len(urls_to_visit)} URLs to process")
        return urls_to_visit

    except TimeoutException:
        logging.info(f"Error: Could not find or interact with the search elements within 20 seconds.")
        return False
    except Exception as e:
        logging.error(f"An unknown error occurred: {e}")
    
def find_codeblock_or_text_or_link_after_poc(driver):
    # Match any heading level with id='poc' or 'proof-of-concept'
    siblings = driver.find_elements(
        By.XPATH, "//*[self::h1 or self::h2 or self::h3 or self::h4 or self::h5 or self::h6][@id='poc' or @id='proof-of-concept']/following-sibling::*"
    )

    if not siblings:
            logging.info("PoC section found, but it has no content.")
            return False

    # Search for a code-block under the poc-heading
    result = []
    for sibling in siblings:
        tag = sibling.tag_name.lower()
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            break  # Stop at next heading
        if tag == "milkdown-code-block":
            logging.info(f"Found a codeblock in the PoC section")
            if "code" not in result:
                result.append("code")
        if sibling.find_elements(By.TAG_NAME, 'a'):
            logging.info("Found a link in the PoC section.")
            if "link" not in result:
                result.append("link")
        if tag in {"p", "ul"}:
            logging.info("Found text in the PoC section")
            if "text" not in result:
                result.append("text")

    if result:
        return result
    
    logging.info(f"Did not find a codeblock in the PoC section")
    return False

def find_PoC(driver, url):
    # Look for PoC headers with a following code-block before the next header
    logging.info("Starting to look for a PoC section")
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[self::h1 or self::h2 or self::h3 or self::h4 or self::h5 or self::h6][@id='poc' or @id='proof-of-concept']")
            )
        )
        print("Found PoC header, now checking for code block before next heading")
        return find_codeblock_or_text_or_link_after_poc(driver)
    except TimeoutException:
        logging.warning("PoC header not found within timeout.")
        return False
    except Exception as e:
        logging.error(f"An unknown error occurred: {e}")
        return False

def find_date_authors_bounty_impact(driver):
    logging.info("Starting to look for rarity, quality, bounty, and impact")
    results = {}
    try:
        impact = driver.find_element(By.XPATH, "//span[text()='HIGH' or text()='MED']")
        results['impact'] = impact.text

        publication_date = driver.find_element(By.XPATH, "//*[contains(@class, 'text-smn') and contains(@class, 'text-start') and contains(@class, 'text-gray-500')]/span[1]")
        results['publication_date'] = publication_date.text.removesuffix(" -")

        client_source_link = driver.find_element(By.XPATH, "//a[@class='text-gray-800 underline']")
        results['client_source_link'] = client_source_link.get_attribute('href')

        authors = driver.find_element(By.XPATH, "//*[contains(@class, 'text-start') and contains(@class, 'text-sm') and contains(@class, 'text-gray-800') and starts-with(normalize-space(.), 'Author(s)')]")
        author_string = authors.text.removeprefix("Author(s): ")
        results['authors'] = author_string
        if author_string.endswith(" more"):
            parts = author_string.split(" and ")
            list_part = parts[0]
            summary_part = parts[1]
            explicit_count = len(list_part.split(","))
            number_str = summary_part.replace(" more", "").strip()
            more_count = int(number_str)
            nr_authors = explicit_count + more_count
        else:
            nr_authors = len(author_string.split(","))
        results['n_authors'] = nr_authors

        results['total_bounty'] = 0
        try:
            bounty = driver.find_element(By.XPATH, "//span[contains(text(), 'USDC')]")
            results['total_bounty'] = bounty.text
        except NoSuchElementException:
            logging.info("No bounty was listed on this page. Continuing.")
            pass

        webpage_text = get_audit_content(driver)
        results['audit_content'] = webpage_text

    except Exception as e:
        logging.error(f"An unknown error occurred: {e}")
        return False
    return results

def get_audit_content(driver):
    """Extracts text content using BeautifulSoup."""
    try:
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
        return f"Error fetching the audit content: {e}" 
    
def main():
    # Setup the driver and login
    driver = setup_driver()
    login(driver)
    disregarded_urls = []
    #, "price oracle manipulation", "logic error", "lack of input validation", "reentrancy", "unchecked external calls", "flash loan", "integer overflow", "integer underflow", "insecure randomness", "denial of service (DoS)"
    categories = ["access control", "price oracle manipulation", "logic error", "lack of input validation", "reentrancy", 
                  "unchecked external calls", "flash loan", "integer overflow", "integer underflow", "insecure randomness", 
                  "denial of service (DoS)"]
    results = {}

    # For every OWASP top 10 category, find audits with PoC segments with included code-blocks
    for category in categories:
        urls = []
        pagination = 1
        logging.info(f"Looking at the category: {category}")
        while True:
            search_results = search_solodit(driver, category, pagination)
            if not search_results:
                break
            urls.extend(search_results)
            #if pagination == 1: # FOR DEMO
                #break # FOR DEMO
            pagination += 1
        if len(urls) == 0:
            logging.error("No search results found")
            return
        for url in urls:
            PoC_finding = find_PoC(driver, url)
            if PoC_finding:
                extra_parameters = find_date_authors_bounty_impact(driver)
                if extra_parameters:
                    if url in results:
                        results[url]['vulnerabilities'].append(category)
                    else:
                        results[url] = {'scrapping_date': date.today().isoformat(),
                                        'poc_content_types': PoC_finding,
                                        'vulnerabilities': [category],
                                        **extra_parameters}
                else:
                    disregarded_urls.append(url)
            else:
                disregarded_urls.append(url)

    # Create a .json file with the links to the audits found
    with open("results.json", "w") as f:
        f.write(json.dumps(results, indent=4))
    
    # Create a .json file with the disregarded links
    with open("disregarded_links.json", "w") as f:
        f.write(json.dumps(disregarded_urls, indent=4))

if __name__ == "__main__":
    main()