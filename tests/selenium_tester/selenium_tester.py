import multiprocessing

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
import json
import unittest
import time

start_locations = [
{ 'id': [39.87, -88.89], 'name': 'Illinois Industrial Carbon Capture and Storage Project'},
{ 'id': [45, -85], 'name': 'MRCSP Development Phase - Michigan Basin Project' },
{ 'id': [35, -98], 'name': 'PurdySho-Vel-Tum EOR Project'},
{ 'id': [30, -101], 'name': 'Val Verde NG Plants'},
{ 'id': [39.863, -88.913], 'name': 'Illinois Industrial Carbon Capture and Storage'},
{ 'id': [37.106767, -100.7977], 'name': 'Arkalon'},
{ 'id': [37.959112, -100.83676], 'name': 'Bonanza BioEnergy'},
{ 'id': [37.047329, -95.604094], 'name': 'Coffeyville Plant'},
{ 'id': [45.113, -84.652], 'name': 'Core Energy CO2-EOR'},
{ 'id': [46.8839, -102.3157], 'name': 'Red Trail'},
{ 'id': [36.378636, -97.762739], 'name': 'Enid Fertilizer'},
{ 'id': [29.866, -93.967], 'name': 'Air Products Port Arthur Facility'},
{ 'id': [30.3718, -101.8449], 'name': 'Terrell Gas Processing'},
{ 'id': [31.009, -88.025], 'name': 'SECARB Development Phase - Citronelle Project'},
{ 'id': [37.536, -105.104], 'name': 'Oakdale NG Processing'},
{ 'id': [40.530, -89.682], 'name': 'NRG Powerton Station'},
{ 'id': [38.272, -89.668], 'name': 'Prairie State Energy Campus'},
{ 'id': [37.046, -95.604], 'name': 'CO2 Capture from Coffeyville Fertilizer Plant'},
{ 'id': [37.7903, -84.7144], 'name': 'EW Brown Generating Station'},
{ 'id': [39.594529, -78.745292], 'name': 'AES Warrior Run'},
{ 'id': [42.0916, -71.48352], 'name': 'Bellingham Cogeneration Facility'},
{ 'id': [47.3727, -101.15679], 'name': 'Great River Energy'},
{ 'id': [40.90214, -82.03784], 'name': 'Touchstone Bioconversion Pilot Plant'},
{ 'id': [36.37858, -97.76379], 'name': 'Purdy Sho-Vel-Tum EOR Project'},
{ 'id': [29.86493, -93.966697], 'name': 'Air Products and Chemicals Inc. CCS Project'},
{ 'id': [31, -103], 'name': 'Century Plant Gas Processing'},
{ 'id': [33.216456, -97.772382], 'name': 'Mitchell Energy Bridgeport Plant'},
{ 'id': [29.47678, -95.637769], 'name': 'W.A. Parish Post-Combustion CO2 Capture and Sequestration Project'},
{ 'id': [39.501027, -112.581819], 'name': 'Intermountain Power Agency'},
{ 'id': [42.535541, -87.903483], 'name': 'We Energies Pleasant Prairie Field Pilot'},
{ 'id': [35.760591, -117.379211], 'name': 'Searles Valley Minerals'},
{ 'id': [41.88568, -110.0926], 'name': 'Shute Creek Plant'},
{ 'id': [30.692226, -88.042569], 'name': 'Fuel Cell Carbon Capture Pilot Plant'},
{ 'id': [31.01124, -88.024597], 'name': 'Linde/BASF FEED'},
{ 'id': [33.2343, -86.4836], 'name': 'National Carbon Capture Center (NCCC)'},
{ 'id': [33.417905, -111.928358], 'name': 'Center for Negative Carbon Emissions'},
{ 'id': [35.27444, -119.32301], 'name': 'Elk Hills CCS'},
{ 'id': [37.510632, -121.997288], 'name': 'Membrane Technology & Research, Inc.'},
{ 'id': [37.458009, -122.175774], 'name': 'SRI International Post-combustion Sorbent'},
{ 'id': [39.79121, -105.137092], 'name': 'TDA Research Post-combustion'},
{ 'id': [39.791215, -105.136744], 'name': 'TDA Research Pre-combustion'},
{ 'id': [31.006474, -88.008697], 'name': 'Gas Technology Institute'},
{ 'id': [40.116306, -88.243522], 'name': 'Linde/Illinois'},
{ 'id': [38.24935, -89.75296], 'name': 'Prairie State Generating Station CCS'},
{ 'id': [37.106778, -100.799611], 'name': 'Arkalon Bioethanol'},
{ 'id': [37.958806, -100.836556], 'name': 'Bonanza Bioethanol'},
{ 'id': [37.050663, -95.604763], 'name': 'Coffeyville Fertilizer'},
{ 'id': [38.03501, -84.504821], 'name': 'University of Kentucky Center for Applied Energy Research'},
{ 'id': [38.03501, -84.504821], 'name': 'University of Kentucky Research Foundation'},
{ 'id': [30.218533, -91.052119], 'name': 'PCS Nitrogen'},
{ 'id': [39.594529, -78.745292], 'name': 'Warrior Run'},
{ 'id': [45.1, -84.65], 'name': 'Core Energy'},
{ 'id': [41.0809508, -101.1433768], 'name': 'Gerald Gentleman Coal Power Plant'},
{ 'id': [40.764619, -73.971056], 'name': 'Global Thermostat'},
{ 'id': [40.71217, -74.007155], 'name': 'Infinitree'},
{ 'id': [35.905909, -78.863898], 'name': 'Research Triangle Institute'},
{ 'id': [47.11495, -101.1725], 'name': 'Project Tundra'},
{ 'id': [47.9198, -97.0605], 'name': 'University of North Dakota Energy and Environmental Research Center'},
{ 'id': [35.194006, -94.646982], 'name': 'Shady Point'},
{ 'id': [29.865806, -93.967361], 'name': 'Air Products Steam Methane Reformer'},
{ 'id': [30.608764, -102.57876], 'name': 'Century Plant'},
{ 'id': [29.646611, -95.055917], 'name': 'NET Power'},
{ 'id': [33.63559, -96.60902], 'name': 'Panda Energy Fund'},
{ 'id': [29.477964, -95.635209], 'name': 'Petra Nova'},
{ 'id': [29.477964, -95.635209], 'name': 'Petra Nova'},
{ 'id': [32.972554, -102.74361], 'name': 'University of Texas'},
{ 'id': [44.388212, -105.459617], 'name': 'Dry Fork Power Plant CCS'},
{ 'id': [43.280518, -107.6022], 'name': 'Lost Cabin'},
{ 'id': [44.388212, -105.45961], 'name': 'Wyoming Integrated Test Center'},
{ 'id': [47.361953, -101.838103], 'name': 'Great Plains Synfuel Plant'},
]


#List of possible CCS ending locations
ending_locations = [
{ 'id': [39.87, -88.89], 'name': 'Illinois Industrial Carbon Capture and Storage Project'},
{ 'id': [45, -85], 'name': 'MRCSP Development Phase - Michigan Basin Project' },
{ 'id': [43, -106], 'name': 'LINC Energy - Wyoming EOR'},
{ 'id': [35, -98], 'name': 'PurdySho-Vel-Tum EOR Project'},
{ 'id': [40, -109], 'name': 'Rangely-Webber EOR'},
{ 'id': [42, -109], 'name': 'Salt CreekMonellSussex Unit EOR'},
{ 'id': [36, -101], 'name': 'SWP Development Phase - Farnsworth Unit Ochiltree Project'},
{ 'id': [30, -101], 'name': 'Val Verde NG Plants'},
{ 'id': [31, -102], 'name': 'Yates Oil Field EOR Operations'},
]


num_start_locations = len(start_locations)
num_end_locations = len(ending_locations)

class SeleniumTestChrome:

    
    
    def __init__(self, source_indices, url="http://localhost:5000/", headless=False):
        """Set up Chrome driver before each test"""
        self.url = url
        self.headless = headless
        self.source_indices = source_indices
        self.end_indices = list(range(num_end_locations))  # Test all end locations for each source
        self.time_pairs = []
        self.verification_results = []
        self.name_pairs = []
        

    def get_test_data(self):
        return {
            "time_pairs": self.time_pairs,
            "verification_results": self.verification_results,
            "name_pairs": self.name_pairs
        }
    
    '''
    def get_location_options_data(self, dropdown_div_XPATH,indices):
        dropdown_div = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, dropdown_div_XPATH))
        )
     
        dropdown_locator = dropdown_div.find_element(By.CSS_SELECTOR, "div[role='combobox'].rw-dropdown-list")
        actions = ActionChains(self.driver)
        actions.move_to_element(dropdown_locator).perform()  # Move to the dropdown to ensure it's in view
        actions.click(dropdown_locator).perform()  # Click the dropdown to open it
        dropdown_locator = dropdown_div.find_element(By.CSS_SELECTOR, "div[role='combobox'].rw-dropdown-list")
        list_id = dropdown_locator.get_attribute("aria-controls")
        
        options_loc = (By.CSS_SELECTOR, f"#{list_id} .rw-list-option, #{list_id} li")
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(options_loc))
            
        options = self.driver.find_elements(*options_loc)
        names = [options[i].text for i in indices if i < len(options)]
        return names
    '''   

  
    def get_clickdropdown_element(self,dropdown_div_XPATH, index,driver):
        wait = WebDriverWait(driver, 100)
        # locate the dropdown element within the div
        

        dropdown_div = WebDriverWait(  driver, 100).until(
        EC.presence_of_element_located((By.XPATH, dropdown_div_XPATH))
        )

        dropdown_locator = dropdown_div.find_element(By.CSS_SELECTOR, "div[role='combobox'].rw-dropdown-list")
        actions = ActionChains(driver)
        actions.move_to_element(dropdown_locator).perform()  # Move to the dropdown to ensure it's in view
        actions.click(dropdown_locator).perform()  # Click the dropdown to open it
        dropdown_locator = dropdown_div.find_element(By.CSS_SELECTOR, "div[role='combobox'].rw-dropdown-list")
        list_id = dropdown_locator.get_attribute("aria-controls")
        
        #dropdown_element.click()

        options_loc = (By.CSS_SELECTOR, f"#{list_id} .rw-list-option, #{list_id} li")
        wait.until(EC.visibility_of_element_located(options_loc))
            
        # Find all options again
        options = driver.find_elements(*options_loc)

        # Safety check
        if index < len(options):
            target_option = options[index]
            
                
            # Click the assigned option
            
            actions.move_to_element(target_option).perform()
            actions.click(target_option).perform()

            
    
    def test_example(self):
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(100)
        
     

        """Example test case"""
        driver.get(f"{self.url}researcher-apps/co2-pipeline-routing-tool/")
        
        # Wait for page to load
        click_understood = WebDriverWait(driver, 100).until(
            EC.element_to_be_clickable((By.XPATH, 
                                        "//button[text()='Understood']"))
        )

        click_understood.click()

        # Find the div with the specific heading
        start_location_div_XPATH = "//div[./h4[contains(string(),'Add Start Location in World Geodetic System WGS 1984 (WGS 84)')]]"
        end_location_div_XPATH = "//div[./h4[contains(string(),'Add End Location in WGS84')]]" 
   

        #start_options_list = self.get_location_options_data(start_location_div_XPATH,indices = self.source_indices)
        #end_options_list = self.get_location_options_data(end_location_div_XPATH, indices = self.end_indices)

        start_options_list = [start_locations[i]['name'] for i in self.source_indices if i < len(start_locations)]
        end_options_list = [ending_locations[i]['name'] for i in self.end_indices if i < len(ending_locations)]

        print(f"Start options: {start_options_list}")
        print(f"End options: {end_options_list}")

        

        for i,start_choice in enumerate(start_options_list):
            for j,end_choice in enumerate(end_options_list):
                print(f"Selected start: {start_choice}, end: {end_choice}")
                if start_choice == end_choice:
                    print("Warning: Start and end locations are the same, skipping this combination.")
                    self.time_pairs.append((0,0))  # Append 0 time for skipped cases
                    self.verification_results.append(True)  
                    self.name_pairs.append((start_choice, end_choice))
                    # Mark as True since it's not a failure of the pipeline generation, just an invalid test case
                    continue
                
                print(f"Testing combination: Start - {start_choice}, End - {end_choice} @ {time.strftime('%Y-%m-%d %H:%M:%S')}")
                self.get_clickdropdown_element(start_location_div_XPATH, self.source_indices[i], driver)
                self.get_clickdropdown_element(end_location_div_XPATH, self.end_indices[j], driver)

                generate_button = WebDriverWait(driver, 100).until(
                   EC.element_to_be_clickable((By.XPATH, 
                                        "//button[text()='Generate Pipeline']"))
                )
                actions = ActionChains(driver)
                actions.move_to_element(generate_button).perform()
                actions.click(generate_button).perform()

                start_time = time.time()
                try:
                    #wait until the notification disappears, which indicates the pipeline has been generated
                    loading_notification_XPATH = './/div[contains(text(),"Loading")]'
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, loading_notification_XPATH)))
                    time.sleep(3)
                    WebDriverWait(driver, 3600).until(EC.invisibility_of_element_located((By.XPATH, loading_notification_XPATH)))
                    stop_time = time.time()
                    elapsed_time = stop_time - start_time
                    self.time_pairs.append((start_time, stop_time))
                    
                    print(f"Pipeline notification gone in {elapsed_time:.2f} seconds for start: {start_choice}, end: {end_choice} @ {time.strftime('%Y-%m-%d %H:%M:%S')}")
                   
                   
                
                except TimeoutException:


                    stop_time = time.time()
                    elapsed_time = stop_time - start_time
                    self.time_pairs.append((start_time, stop_time))
                    self.verification_results.append(False)
                except Exception as e:
                    print(f"Error during pipeline generation for start: {start_choice}, end: {end_choice}: {e}")
                    import traceback
                    traceback.print_exc()
                    
                    self.time_pairs.append((-1, -1))  # Append -1 for unexpected errors
                    self.verification_results.append(False)
                    time.sleep(5*60)  # Wait for 5 minutes before trying the next test case to avoid overwhelming the server
                finally:

                    self.name_pairs.append((start_choice, end_choice))


                    error_notification_XPATH = './/div[contains(text(),"Error")]'
                    error_notification = driver.find_elements(By.XPATH, error_notification_XPATH)
                    if len(error_notification) > 0:
                        print(f"Error notification detected for start: {start_choice}, end: {end_choice}")
                        self.verification_results.append(False)
                    else:    
                        self.verification_results.append(True)  # Mark as passed if no error notification is present
                    
                    
                    #refresh and reset for next test case
                    driver.get(f"{self.url}researcher-apps/co2-pipeline-routing-tool/")
        
                    # Wait for page to load
                    click_understood = WebDriverWait(driver, 100).until(
                        EC.element_to_be_clickable((By.XPATH, 
                                                    "//button[text()='Understood']"))
                    )

                    click_understood.click()
                    continue
        driver.quit()
      
                






def get_chunks(n, l):
    """
    Splits the range(0, n) into l roughly equal chunks.
    Example: n=10, l=3 -> [[0, 1, 2, 3], [4, 5, 6], [7, 8, 9]]
    """
    indices = list(range(n))
    k, m = divmod(len(indices), l)
    return [indices[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(l)]

def worker_function(STC):
    STC.test_example()
    
       

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description='Run Selenium tests for CO2 Pipeline Routing Tool')
    parser.add_argument('--processes', type=int, default=1, help='Number of processes to use for testing')
    parser.add_argument('--url', type=str, default="http://localhost:5000/", help='root URL of the application to test')
    parser.add_argument('--headless', action='store_true', help='Run Chrome in headless mode')
    parser.add_argument('--test-all', action='store_true', help='Run tests for all start and end location combinations (default is to test only the first 5 start locations)')
    


    args = parser.parse_args()
    num_processes = args.processes

    #for test testing we'll just do 5
    
    num_start_locations = len(start_locations)
    source_chunks = get_chunks(num_start_locations, num_processes)

    #for now skip multiprocessing pooling and only test first 5 to test the testcases 
    # then implement multiprocessing pooling after confirming testcases work\

    testers = [SeleniumTestChrome(chunk, url=args.url, headless=args.headless) for chunk in source_chunks]
    try:
        with multiprocessing.Pool(processes=num_processes) as pool:
            pool.map(worker_function, testers)
    except Exception as e:
        print(f"Error during multiprocessing: {e}")
        import traceback
        traceback.print_exc()
        # If there's an error, we can still gather results from any testers that completed
    finally:
        data = [tester.get_test_data() for tester in testers]

        json.dump(data, open("selenium_test_results.json", "w"), indent=4)



