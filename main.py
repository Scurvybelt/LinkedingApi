import time
import urllib.parse
from openpyxl import Workbook
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def linkedin_login(driver, username, password):
    """
    Logs into LinkedIn using the provided credentials.
    """
    driver.get("https://www.linkedin.com/")
    time.sleep(3)

    # Attempt to click the 'Sign in' button if present.
    try:
        sign_in_btn = driver.find_element(By.LINK_TEXT, "Sign in")
        sign_in_btn.click()
        time.sleep(2)
    except Exception as e:
        print("Sign in button not found or not needed:", e)

    # Locate username and password fields, input credentials, and sign in.
    try:
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")

        username_field.send_keys(username)
        password_field.send_keys(password)
        time.sleep(1)

        # Click on login (submit) button
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        time.sleep(5)  # Wait for the feed or homepage to load
    except Exception as e:
        print("Could not complete the login process:", e)

def linkedin_search_direct_url(driver, search_query):
    """
    Navigates directly to LinkedIn search results for the given query string.
    Returns a list of profile links if found.
    """
    import urllib.parse
    # Encode the query (e.g. "Leonardo Contreras Martinez" -> "Leonardo%20Contreras%20Martinez")
    encoded_query = urllib.parse.quote(search_query)

    # Create the direct search URL
    search_url = f"https://www.linkedin.com/search/results/people/?keywords={encoded_query}"
    driver.get(search_url)

    # Optional: wait for page load if needed
    time.sleep(5)

    # Now collect profile links from the search results
    profile_links = []
    try:
        # Look for anchor tags that contain '/in/' which usually correspond to user profile URLs
        results = driver.find_elements(By.XPATH, "//a[contains(@href, '/in/')]")
        for result in results:
            link = result.get_attribute("href")
            if link and link not in profile_links:
                profile_links.append(link)
    except Exception as e:
        print("Error extracting profile links:", e)

    if not profile_links:
        print(f"No results found for '{search_query}'.")

    return profile_links

def scrape_profile(driver, profile_url):
    """
    Given a LinkedIn profile URL, opens the page, extracts:
    - Name
    - Role (Headline)
    - Location
    - Current Company
    Returns a dictionary of the extracted info.
    """
    data = {
        "Name": None,
        "Role": None,
        "Location": None,
        "Company": None,
        "Profile": profile_url
    }

    try:
        driver.get(profile_url)
        time.sleep(3)

        # Example locators only; adjust for your environment
        # Name
        try:
            name_elem = driver.find_element(By.XPATH, "//h1[contains(@class, 'qnCfiZjDENQFxaQmQvqHeoVjVxEhVrpZeiDFs')]")
            data["Name"] = name_elem.text.strip()
        except Exception:
            print(f"Could not find name for {profile_url}")

        # Headline (Role)
        try:
            role_elem = driver.find_element(By.XPATH, "//div[contains(@class, 'text-body-medium break-words')]")
            data["Role"] = role_elem.text.strip()
        except Exception:
            print(f"Could not find role/headline for {profile_url}")

        # Location
        try:
            location_elem = driver.find_element(By.XPATH, "//span[contains(@class, 'text-body-small inline t-black--light')]")
            data["Location"] = location_elem.text.strip()
        except Exception:
            print(f"Could not find location for {profile_url}")

        # Current Company
        try:
            # Sometimes in the "Experience" section or in the top card
            company_elem = driver.find_element(By.XPATH, "//div[contains(@class, 'tlPcUBtieUVaOTvICXTlBsVCukQSUjcna')]")
            data["Company"] = company_elem.text.strip()
        except Exception:
            print(f"Could not find company for {profile_url}")

    except Exception as e:
        print(f"Error scraping profile {profile_url}:", e)

    return data

def save_to_excel(data_list, filename="linkedin_results.xlsx"):
    """
    Saves a list of dictionaries to an Excel file using openpyxl.
    """
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "LinkedIn Data"

    # Write headers
    headers = ["Name", "Role", "Location", "Company", "Profile"]
    ws.append(headers)

    # Write each row
    for record in data_list:
        ws.append([
            record.get("Name"),
            record.get("Role"),
            record.get("Location"),
            record.get("Company"),
            record.get("Profile")
        ])

    wb.save(filename)
    print(f"Data successfully saved to {filename}")

def main():
    # Replace these with your actual LinkedIn credentials
    USERNAME = input("Enter your LinkedIn email: ")  
    PASSWORD = input("Enter your LinkedIn password: ")
    SEARCH_QUERY = input("Enter the search query (a person's name): ")

    # Define how many profiles you want to visit at most
    MAX_PROFILES = int(input("Enter the maximum number of profiles to visit: "))

        # Create an instance of ChromeOptions
    chrome_options = Options()
    
    # Set the desired window size
    # Example: 1280 x 800
    chrome_options.add_argument("--window-size=1280,800")

    # Initialize the WebDriver with these options
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 1. Login
        linkedin_login(driver, USERNAME, PASSWORD)

        # 2. Navigate to the search results directly
        profile_links = linkedin_search_direct_url(driver, SEARCH_QUERY)
        print(f"Collected {len(profile_links)} links total.")

        # 3. Limit the number of profiles to visit (MAX_PROFILES)
        profile_links = profile_links[:MAX_PROFILES]
        print(f"Visiting up to {MAX_PROFILES} profiles.")

        # 4. Scrape each profile
        all_data = []
        for link in profile_links:
            profile_data = scrape_profile(driver, link)
            all_data.append(profile_data)

        # 5. Save data to Excel
        save_to_excel(all_data, filename="linkedin_results.xlsx")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
