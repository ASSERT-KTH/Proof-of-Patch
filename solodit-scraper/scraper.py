import json
import logging
import re
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

# Setting up logging configuration with file output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()  # Also print to console
    ]
)

def load_existing_results():
    """Load existing results from file if it exists"""
    try:
        with open("results/results.json", "r", encoding="utf-8") as f:
            results = json.load(f)
            logging.info(f"Loaded {len(results)} existing results from results/results.json")
            return results
    except FileNotFoundError:
        logging.info("No existing results file found, starting fresh")
        return {}
    except json.JSONDecodeError:
        logging.warning("Existing results/results.json is corrupted, starting fresh")
        return {}

def save_results_incrementally(results, disregarded_urls, category=None):
    """Save results incrementally to avoid data loss"""
    try:
        # Ensure results directory exists
        import os
        os.makedirs("results", exist_ok=True)
        
        # Save main results
        with open("results/results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)
        
        # Save disregarded URLs
        with open("results/disregarded_links.json", "w", encoding="utf-8") as f:
            json.dump(disregarded_urls, f, indent=4)
        
        if category:
            logging.info(f"✓ Completed category '{category}': {len(results)} total results, {len(disregarded_urls)} disregarded URLs")
        else:
            logging.info(f"Saved {len(results)} results and {len(disregarded_urls)} disregarded URLs")
    except Exception as e:
        logging.error(f"Error saving results: {e}")

def save_progress(category, urls_found, urls_processed, urls_added, urls_disregarded):
    """Save progress information for debugging"""
    progress_data = {
        'category': category,
        'urls_found': urls_found,
        'urls_processed': urls_processed,
        'urls_added': urls_added,
        'urls_disregarded': urls_disregarded,
        'timestamp': date.today().isoformat()
    }
    
    try:
        import os
        os.makedirs("results", exist_ok=True)
        with open("results/progress.json", "w", encoding="utf-8") as f:
            json.dump(progress_data, f, indent=4)
        logging.info(f"Progress saved: {category} - Found: {urls_found}, Processed: {urls_processed}, Added: {urls_added}, Disregarded: {urls_disregarded}")
    except Exception as e:
        logging.error(f"Error saving progress: {e}")

def construct_url(impact, pagination=1, search_term=""):
    # Define the base URL
    base_url = "https://solodit.cyfrin.io/"
    #https://solodit.cyfrin.io/?i=HIGH%2CMEDIUM%2CLOW&p=20&s=access+control&rf=after

    # Prepare parameters
    params = {
        "i": ",".join(impact),  # Join the impacts into a comma-separated string
        "p": pagination,        # Pagination value
        "s": search_term,       # Keep original search term (category only)
        "rf": "after"
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
        driver.get("https://profiles.cyfrin.io/solodit/login")
        wait = WebDriverWait(driver, 10)
        print("Login page opened, login to continue ...")
        input("Press ENTER to continue after you have logged in ...")
    except Exception as e:
        logging.error(f"Login failed: {e}")

def search_solodit(driver, search_term, page):
    try:
        # Wait for and interact with the search input
        url = construct_url(["HIGH", "MEDIUM", "LOW"], pagination=page, search_term=search_term)
        driver.get(url)

        # Find all the link elements
        link_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'loaded-findings')]//button[contains(@class, 'svelte-dpmcg0')]//h3[contains(@class, 'line-clamp-2')]//a"))
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
        By.XPATH, "//*[self::h1 or self::h2 or self::h3 or self::h4 or self::h5 or self::h6][normalize-space(text())='PoC' or " \
        "normalize-space(text())='Proof-of-Concept' or normalize-space(text())='Proof of Concept' or normalize-space(text())='poc' " \
        "or normalize-space(text())='proof of concept']/following-sibling::*"
    )

    if not siblings:
            logging.info("PoC section found, but it has no content.")
            return False

    # Search for a code-block under the poc-heading
    result = []
    for sibling in siblings:
        tag = sibling.tag_name.lower()
        is_code_div = tag == "div" and "ql-code-block-container" in (sibling.get_attribute("class") or "")
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            if not result:
                result.append("empty")
            break  # Stop at next heading
        if is_code_div:
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
                (By.XPATH, "//*[self::h1 or self::h2 or self::h3 or self::h4 or self::h5 or self::h6][normalize-space(text())='PoC' or " \
        "normalize-space(text())='Proof-of-Concept' or normalize-space(text())='Proof of Concept' or normalize-space(text())='poc' " \
        "or normalize-space(text())='proof of concept']/following-sibling::*")
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

def find_mitigation_section(driver):
    """Look for mitigation/patch sections in the audit"""
    mitigation_keywords = [
        "mitigation", "fix", "patch", "solution", "remediation", "corrective", 
        "recommendation", "suggestion", "improvement", "resolution"
    ]
    
    mitigation_content = []
    
    for keyword in mitigation_keywords:
        try:
            # Look for headings containing mitigation keywords
            headings = driver.find_elements(
                By.XPATH, f"//*[self::h1 or self::h2 or self::h3 or self::h4 or self::h5 or self::h6][contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword}')]"
            )
            
            for heading in headings:
                # Get content after this heading until next heading
                siblings = driver.find_elements(
                    By.XPATH, f"//*[self::h1 or self::h2 or self::h3 or self::h4 or self::h5 or self::h6][contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword}')]/following-sibling::*"
                )
                
                content_types = []
                for sibling in siblings:
                    tag = sibling.tag_name.lower()
                    
                    # Check if we hit another heading
                    if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
                        break
                    
                    # Check for code blocks
                    if tag == "div" and "ql-code-block-container" in (sibling.get_attribute("class") or ""):
                        content_types.append("code")
                    
                    # Check for links (especially GitHub)
                    links = sibling.find_elements(By.TAG_NAME, 'a')
                    for link in links:
                        href = link.get_attribute('href')
                        if href and ('github.com' in href or 'commit' in href or 'pull' in href or 'pr' in href):
                            content_types.append("github_link")
                        elif href:
                            content_types.append("link")
                    
                    # Check for text content
                    if tag in {"p", "ul", "ol"} and sibling.text.strip():
                        content_types.append("text")
                
                if content_types:
                    mitigation_content.extend(content_types)
                    logging.info(f"Found mitigation section with: {content_types}")
        
        except Exception as e:
            logging.debug(f"Error searching for {keyword}: {e}")
    
    return list(set(mitigation_content)) if mitigation_content else False

def find_patch_references(driver):
    """Look for specific patch references like GitHub commits, PRs, etc."""
    try:
        # Get all text content
        webpage_text = get_audit_content(driver)
        
        patch_indicators = {
            'github_commit': False,
            'github_pr': False,
            'patch_link': False,
            'fix_commit': False,
            'mitigation_code': False
        }
        
        # Look for GitHub commit patterns
        commit_patterns = [
            r'github\.com/[^/]+/[^/]+/commit/[a-f0-9]+',
            r'commit/[a-f0-9]{40}',
            r'commit/[a-f0-9]{7,}',
            r'fixes?\s+#\d+',
            r'closes?\s+#\d+'
        ]
        
        for pattern in commit_patterns:
            if re.search(pattern, webpage_text, re.IGNORECASE):
                patch_indicators['github_commit'] = True
                break
        
        # Look for GitHub PR patterns
        pr_patterns = [
            r'github\.com/[^/]+/[^/]+/pull/\d+',
            r'pull/\d+',
            r'pr\s*#\d+',
            r'pull\s*request\s*#\d+'
        ]
        
        for pattern in pr_patterns:
            if re.search(pattern, webpage_text, re.IGNORECASE):
                patch_indicators['github_pr'] = True
                break
        
        # Look for general patch/fix links
        if re.search(r'(patch|fix|mitigation).*\.(com|org|io)', webpage_text, re.IGNORECASE):
            patch_indicators['patch_link'] = True
        
        # Look for fix commit messages
        if re.search(r'(fix|patch|mitigate|resolve).*commit', webpage_text, re.IGNORECASE):
            patch_indicators['fix_commit'] = True
        
        # Check if there's mitigation code in the content
        mitigation_section = find_mitigation_section(driver)
        if mitigation_section and 'code' in mitigation_section:
            patch_indicators['mitigation_code'] = True
        
        return patch_indicators
        
    except Exception as e:
        logging.error(f"Error finding patch references: {e}")
        return patch_indicators

def find_detailed_information(driver):
    logging.info("Starting to look for detailed information")
    results = {}
    try:
        try:
            impact_xpath1 = "//span/p[text()='High' or text()='Medium' or text()='Low']"
            impact_xpath2 = "//div[text()='Author(s)']/following-sibling::span"

            # Find ALL elements that match the XPath
            impact_elements1 = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, impact_xpath1)))
            impact_elements2 = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, impact_xpath2)))

            # Loop through them to find the one that's actually visible
            for element in impact_elements1:
                if element.is_displayed():
                    results['impact'] = element.text
                    break # Stop after finding the first visible one
            else: 
                results['impact'] = "Not Found"

            for element in impact_elements2:
                if element.is_displayed():
                    authors = element.text
                    break # Stop after finding the first visible one
            else: 
                authors = "Not Found"

        except Exception:
            results['impact'] = "Not Found"
            authors = "Not Found"

        publication_date = driver.find_element(By.XPATH, "//span[contains(@class, 'text-colors-text-text-quarterary-500')]")
        results['publication_date'] = publication_date.text

        client_source_link = driver.find_element(By.XPATH, "//div[text()='Full report']/following-sibling::a")
        results['client_source_link'] = client_source_link.get_attribute('href')

        results['authors'] = authors
        if authors.endswith(" more"):
            parts = authors.split(" and ")
            list_part = parts[0]
            summary_part = parts[1]
            explicit_count = len(list_part.split(","))
            number_str = summary_part.replace(" more", "").strip()
            more_count = int(number_str)
            nr_authors = explicit_count + more_count
        else:
            nr_authors = len(authors.split(","))
        results['n_authors'] = nr_authors

        webpage_text = get_audit_content(driver)
        if "https://github.com" in webpage_text:
            results['contains_github_link'] = 'yes'
        else:
            results['contains_github_link'] = 'no'
        results['audit_content'] = webpage_text 

        # Find patch references
        patch_refs = find_patch_references(driver)
        results.update(patch_refs)
        
        # Check for mitigation section
        mitigation_content = find_mitigation_section(driver)
        results['mitigation_content_types'] = mitigation_content if mitigation_content else []

        try:
            ai_summary = driver.find_element(By.XPATH, "//div[@data-value='summary']")
            results['ai_summary'] = ai_summary.text
        except Exception:
            results['ai_summary'] = ""

    except Exception as e:
        logging.error(f"An unknown error occurred: {e}")
        return False
    return results

def get_audit_content(driver):
    """Extracts text content using BeautifulSoup."""
    try:
        div = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'overflow-auto')]//div[contains(@class, 'markdown')]"))
        )

        html_content = div.get_attribute('innerHTML')
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for code_block in soup.find_all("div", class_="ql-code-block-container"):
            # Find all individual lines of code.
            lines_of_code = code_block.find_all("div", class_="ql-code-block")
            
            reconstructed_code = "\n".join(line.get_text() for line in lines_of_code)
        
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
    
    # Load existing results to resume if interrupted
    results = load_existing_results()
    disregarded_urls = []
    
    # Load existing disregarded URLs if they exist
    try:
        with open("results/disregarded_links.json", "r", encoding="utf-8") as f:
            disregarded_urls = json.load(f)
            logging.info(f"Loaded {len(disregarded_urls)} existing disregarded URLs")
    except FileNotFoundError:
        logging.info("No existing disregarded URLs file found")
    
    categories = ["access control", "price oracle manipulation", "logic error", "lack of input validation", "reentrancy", 
                  "unchecked external calls", "flash loan", "integer overflow", "integer underflow", "insecure randomness", 
                  "denial of service (DoS)"]
    
    total_categories = len(categories)
    logging.info(f"Starting scraping process for {total_categories} categories")

    # For every OWASP top 10 category, find audits with PoC segments with included code-blocks
    for category_index, category in enumerate(categories, 1):
        logging.info(f"\n{'='*60}")
        logging.info(f"CATEGORY {category_index}/{total_categories}: {category.upper()}")
        logging.info(f"{'='*60}")
        
        urls = []
        pagination = 1
        urls_found = 0
        urls_processed = 0
        urls_added = 0
        urls_disregarded = 0
        
        # Search through all pages for this category
        while True:
            logging.info(f"Searching page {pagination} for '{category}'...")
            search_results = search_solodit(driver, category, pagination)
            if not search_results:
                logging.info(f"No more results found for '{category}' on page {pagination}")
                break
            urls.extend(search_results)
            urls_found += len(search_results)
            logging.info(f"Found {len(search_results)} URLs on page {pagination}")
            pagination += 1
            
            # Save progress after each page
            save_progress(category, urls_found, urls_processed, urls_added, urls_disregarded)
        
        if len(urls) == 0:
            logging.warning(f"No search results found for category: {category}")
            continue
        
        logging.info(f"Total URLs found for '{category}': {len(urls)}")
        
        # Process each URL for this category
        for url_index, url in enumerate(urls, 1):
            logging.info(f"\n--- Processing URL {url_index}/{len(urls)} for '{category}' ---")
            logging.info(f"URL: {url}")
            
            try:
                PoC_finding = find_PoC(driver, url)
                extra_parameters = find_detailed_information(driver)
                urls_processed += 1
                
                if extra_parameters:
                    # Include PoC information in the results
                    extra_parameters['poc_content_types'] = PoC_finding if PoC_finding else []
                    
                    # Check if audit has patches/mitigations OR PoC (both are valuable)
                    has_patch = any([
                        extra_parameters.get('github_commit', False),
                        extra_parameters.get('github_pr', False),
                        extra_parameters.get('patch_link', False),
                        extra_parameters.get('fix_commit', False),
                        extra_parameters.get('mitigation_code', False),
                        extra_parameters.get('mitigation_content_types', [])
                    ])
                    
                    has_poc = PoC_finding is not False and len(PoC_finding) > 0
                    
                    # Include if it has patches OR PoC (both are valuable)
                    if has_patch or has_poc:
                        if url in results:
                            results[url]['vulnerabilities'].append(category)
                        else:
                            results[url] = {
                                'scrapping_date': date.today().isoformat(),
                                'vulnerabilities': [category],
                                **extra_parameters
                            }
                        urls_added += 1
                        
                        if has_patch and has_poc:
                            logging.info(f"✓ Added audit with BOTH patch indicators AND PoC")
                        elif has_patch:
                            logging.info(f"✓ Added audit with patch indicators")
                        else:
                            logging.info(f"✓ Added audit with PoC (no patch indicators)")
                    else:
                        disregarded_urls.append(url)
                        urls_disregarded += 1
                        logging.info(f"✗ Disregarded audit (no patch indicators or PoC)")
                else:
                    disregarded_urls.append(url)
                    urls_disregarded += 1
                    logging.warning(f"✗ Failed to extract information from URL")
                
                # Save progress after each URL
                save_progress(category, urls_found, urls_processed, urls_added, urls_disregarded)
                
            except Exception as e:
                logging.error(f"Error processing URL {url}: {e}")
                disregarded_urls.append(url)
                urls_disregarded += 1
                continue
        
        # Save results after each category is completed
        save_results_incrementally(results, disregarded_urls, category)
        
        logging.info(f"\n✓ COMPLETED CATEGORY '{category.upper()}'")
        logging.info(f"  URLs found: {urls_found}")
        logging.info(f"  URLs processed: {urls_processed}")
        logging.info(f"  URLs added: {urls_added}")
        logging.info(f"  URLs disregarded: {urls_disregarded}")
        logging.info(f"  Total results so far: {len(results)}")

    # Final save
    save_results_incrementally(results, disregarded_urls)
    logging.info(f"\n{'='*60}")
    logging.info(f"SCRAPING COMPLETED!")
    logging.info(f"Total audits found: {len(results)}")
    logging.info(f"Total URLs disregarded: {len(disregarded_urls)}")
    logging.info(f"{'='*60}")

if __name__ == "__main__":
    main()