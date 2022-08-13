'''
This code is to work on Data Collection Pipeline project
@author: Behzad 
'''
import os
import urllib.request
from operator import concat
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from time import sleep

class DataCollection:
    def __init__(self, url='www.google.co.uk'):
        ## Initializing all attributes
        self.url = url
        self.driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()) # Access web driver
        self.action = ActionChains(self.driver) # Sets action chains
        
    def load_and_pass_cookies(self):
    ## Loads website and accepts cookies 
        self.driver.get(self.url)
        sleep(1)
        delay = 3 # Sets a delay after webside is loded to allow the cookies' frame pops up  
        try:
            # Tries to wait for web driver be accessed and the cookies frame pops up. Then, clicks 'accept cookies'
            WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')))
            accept_cookies_button = WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')))
            print("Accept Cookies Button Ready!")
            accept_cookies_button.click()
            sleep(2)
        except TimeoutException:
            print("Loading took too much time!")
        sleep(1)

    def get_links(self):
        ## To get all links of elements in the webpage
        link_list = []
        # Find all elements in a container or a table 
        result_container = self.driver.find_elements(by=By.XPATH, value="//section[@class='results']//div[@class='serp-grid__item search-grid__item product-fragment']/a")
        for result in result_container:
            # Goops on all the elements of the container to extract their links
            link = result.get_attribute("href") # Gets the web link
            link_list.append(link)
            #print(link)
        return link_list

    def get_more_links(self, num_page=2):
        ## To get more links by loading more elements or going to the next page (if exist)
        big_list = []
        for i in range(num_page):
            big_list.append(self.get_links())
            try:
                self.driver.find_element(By.XPATH, "//a[@class='show-more__button button button--secondary button--small']").click() # Clicks on next page or loading more products
                sleep(2)
            except:
                pass
        more_link_list = list(set([k for sub in big_list for k in sub])) # flatten and unique the list of links
        #print(len(big_list_unique))
        return more_link_list

    def download_images(self, img_name, i):
        ## Downloads images to the 'images' folder
        self.src = self.driver.find_element_by_xpath('//img[@class="pip-aspect-ratio-image__image"]').get_attribute('src') # Prepares the image source to download
        if not os.path.exists('images'): os.makedirs('images') # Creats 'images' folder if it is not exist
        urllib.request.urlretrieve(self.src, f"./images/{img_name}_{i}.png") # saves images to the folder
        sleep(0.5)

    def scrol_down(self):
        ## Scroling down the page slowly like a human
        scrol_speed = 300 # This number controls the speed of the scrolling down. If larger, scrols faster
        for _ in range(2):
            # To scrol down step by step. In order to cover all page scrolling down the range should be larger
            self.driver.execute_script("window.scrollTo(0, "+str(scrol_speed)+")")
            scrol_speed += 300  
            sleep(0.5)

    def scrape_data(self):
        ## Extrac/scrape all the needed information from a website
        self.load_and_pass_cookies() # Load webpage and pass cookies
        searchTextbox = self.driver.find_element(by=By.XPATH, value='//div[@class="search-field"]') # Finds the search text box position
        self.action.move_to_element(searchTextbox).click().send_keys("beds").send_keys(Keys.RETURN).perform() # Types a word to the search box
        sleep(1.5)
        self.scrol_down() # Scroling down the page
        #all_links_list = self.get_links() # Gets all links in the first page
        all_links_list = self.get_more_links(2) # # Gets all links in multiple pages
        for i, link in enumerate(all_links_list):
            self.driver.get(link) # Gets each link and open it
            sleep(1)
            price = self.driver.find_element(By.XPATH, "//span[@class='pip-price__integer']").text # Gets price
            name = self.driver.find_element(By.XPATH, "//span[@class='pip-header-section__title--big notranslate']").text # Gets name
            description = self.driver.find_element(By.XPATH, "//span[@class='pip-header-section__description-text']").text # Gets description
            self.download_images(f'{name}_beds_', i) # Downloads the image
            print(name, price, description)

def main():
    ## main function to scrape a webpage
    my_url = 'https://www.ikea.com/gb/en/'
    scrp = DataCollection(my_url)
    scrp.scrape_data()

if __name__ == '__main__':
    main()