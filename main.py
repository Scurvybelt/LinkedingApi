import scrapper as sc
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import getpass


def cls():
    os.system('cls' if os.name=='nt' else 'clear')

initial_message = """
          Welcome to the LinkedIn Profile Scraper!
          ----------------------------------------
            This tool will help you scrape LinkedIn profiles for data.
            1. Enter your LinkedIn credentials.
            2. Enter a search query (e.g., a person's name).
            3. Define the maximum number of profiles to visit.
            4. Sit back and relax while the tool scrapes the data.
            5. The tool will save the data to an Excel file.
            --------------------------------
          !!! IMPORTANT !!!
            Make sure you have the latest version of ChromeDriver installed.
            Download the latest version here: https://googlechromelabs.github.io/chrome-for-testing/#stable
            Then define an ENVIRONMENT VARIABLE called CHROMEDRIVER_PATH with the path to the chromedriver executable.
            --------------------------------
          On windows you can do this by running the following command in the command prompt:
            $CHROMEDRIVER_PATH = "C:\\path\\to\\chromedriver.exe"
          """

def printMessage():
    print(initial_message)
    print("Press Enter to continue...")
    input()
    cls()

def main():
    printMessage()
    # Replace these with your actual LinkedIn credentials
    USERNAME = input("Enter your LinkedIn email: ")  
    PASSWORD = getpass.getpass("Enter your LinkedIn password: ")
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
        sc.linkedin_login(driver, USERNAME, PASSWORD)

        # 2. Navigate to the search results directly
        profile_links = sc.linkedin_search_direct_url(driver, SEARCH_QUERY)
        print(f"Collected {len(profile_links)} links total.")

        # 3. Limit the number of profiles to visit (MAX_PROFILES)
        profile_links = profile_links[:MAX_PROFILES]
        print(f"Visiting up to {MAX_PROFILES} profiles.")

        # 4. Scrape each profile
        all_data = []
        for link in profile_links:
            profile_data = sc.scrape_profile(driver, link)
            all_data.append(profile_data)

        # 5. Save data to Excel
        sc.save_to_excel(all_data, filename="linkedin_results.xlsx")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
