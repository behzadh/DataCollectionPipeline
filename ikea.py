'''
This code is to work on Data Collection Pipeline project
@author: Behzad 
'''
import os, json
import uuid # To creat universal unique IDs
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
        self.driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()) # Access the Chrome web driver
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

    def download_images(self, img_name, id=0, download=True):
        ## Downloads image to the 'images' folder
        if not os.path.exists('raw_data'): os.makedirs('raw_data') # Creats 'raw_data' folder if it is not exist
        os.chdir(f'raw_data') # Go to 'raw_data' folder
        if not os.path.exists(f'{id}'): os.makedirs(f'{id}') # Creats 'raw_data' folder if it is not exist
        os.chdir(f'{id}') # Go to '{id}' folder
        if not os.path.exists('images'): os.makedirs('images') # Creats 'images' folder if it is not exist
        os.chdir('images') # Go to 'images' folder
        src = self.driver.find_element_by_xpath('//div[@class="pip-product__left-top"]//img[@class="pip-aspect-ratio-image__image"]').get_attribute('src') # Prepares the image source to download
        if download == True:
            try:
                urllib.request.urlretrieve(src, f"./{img_name}_{id}.jpg") # saves images to the folder
            except:
                print(f"Couldn't download the main image: {src} for {id} product")
        sleep(0.5)
        os.chdir('../../..') # Goes back to parent directory
        return src

    def download_multiple_images(self, img_name, id=0, download=True):
        ## Downloads multiple images of a product to the 'multiple_images' folder
        if not os.path.exists('raw_data'): os.makedirs('raw_data') # Creats 'raw_data' folder if it is not exist
        os.chdir(f'raw_data') # Go to 'raw_data' folder
        if not os.path.exists(f'{id}'): os.makedirs(f'{id}') # Creats 'raw_data' folder if it is not exist
        os.chdir(f'{id}') # Go to '{id}' folder
        if not os.path.exists('multiple_images'): os.makedirs('multiple_images') # Creats 'multiple_images' folder if it is not exist
        os.chdir('multiple_images') # Go to 'multiple_images' folder
        src_container = self.driver.find_elements(by=By.XPATH, value="//div[@class='pip-media-grid__grid ']//img")
        sleep(0.5)
        img_links_list = []
        for k, srcs in enumerate(src_container):
            # Goops on all the elements of the container to extract their links
            img = srcs.get_attribute("src") # Gets the image link
            img_links_list.append(img)
            if download == True:
                try:
                    urllib.request.urlretrieve(img, f"./{img_name}_{k}_{id}.jpg") # saves images to the folder
                except:
                    print(f"Couldn't download this image: {img} for {id} product")
            #print(img)
        os.chdir('../../..') # Goes back to parent directory
        return img_links_list

    def scrol_down(self):
        ## Scroling down the page slowly like a human
        scrol_speed = 300 # This number controls the speed of the scrolling down. If larger, scrols faster
        for _ in range(2):
            # To scrol down step by step. In order to cover all page scrolling down the range should be larger
            self.driver.execute_script("window.scrollTo(0, "+str(scrol_speed)+")")
            scrol_speed += 300  
            sleep(0.5)

    def generate_uuid(self):
        ## Generates Universal Unique IDs
        return str(uuid.uuid4())

    def save_raw_data(self, dict, id=0):
        # To save the raw data dictionaries locally
        if not os.path.exists('raw_data'): os.makedirs('raw_data') # Creats 'raw_data' folder if it is not exist
        os.chdir(f'raw_data') # Go to 'raw_data' folder
        if not os.path.exists(f'{id}'): os.makedirs(f'{id}') # Creats 'raw_data' folder if it is not exist
        os.chdir(f'{id}') # Go to '{id}' folder
        sleep(0.5)
        with open('data.json', 'w') as fp:
            json.dump(dict, fp) # Saves dict in a json file
        os.chdir('../..') # Goes back to parent directory

    def scrape_data(self):
        ## Extrac/scrape all the needed information from a website
        self.load_and_pass_cookies() # Load webpage and pass cookies
        searchTextbox = self.driver.find_element(by=By.XPATH, value='//div[@class="search-field"]') # Finds the search text box position
        self.action.move_to_element(searchTextbox).click().send_keys("desk").send_keys(Keys.RETURN).perform() # Types a word to the search box
        sleep(1.5)
        self.scrol_down() # Scroling down the page
        #all_links_list = self.get_links() # Gets all links in the first page
        all_links_list = self.get_more_links(2) # # Gets all links in multiple pages
        for i, link in enumerate(all_links_list):
            dict_properties = {'Product_id': [], 'UUID_number': [],'Price': [], 'Name': [], 'Description': [], 'Image_link': [], 'Image_all_links': []} # puts all info to a dictionary
            self.driver.get(link) # Gets each link and open it
            sleep(1)
            # extract the price, address, number of bedrooms and the description:
            product_id = self.driver.find_element(By.XPATH, "//div[@class='pip-product__subgrid product-pip js-product-pip']").get_attribute('data-product-id') # Gets product id
            dict_properties['Product_id'].append(product_id) # Adds info to the dictionary
            uuid_number = self.generate_uuid() # Generates universal unique ids
            dict_properties['UUID_number'].append(uuid_number)
            price = self.driver.find_element(By.XPATH, "//span[@class='pip-price__integer']").text # Gets price
            dict_properties['Price'].append(price)
            name = self.driver.find_element(By.XPATH, "//span[@class='pip-header-section__title--big notranslate']").text # Gets name
            dict_properties['Name'].append(name)
            description = self.driver.find_element(By.XPATH, "//span[@class='pip-header-section__description-text']").text # Gets description
            dict_properties['Description'].append(description)
            src_img = self.download_images(f'{name}_', product_id, True) # If true, downloads the image and save it with their name and product id
            dict_properties['Image_link'].append(src_img)
            src_multi_img = self.download_multiple_images(f'{name}_', product_id, True) # If true, downloads the all images of a product and save it with their name, an intiger and product id
            dict_properties['Image_all_links'].append(src_multi_img)
            #print(product_id, name, price, description, src_img, src_multi_img)
            #print(dict_properties)
            self.save_raw_data(dict_properties, product_id)

def main():
    ## main function to scrape a webpage
    get_url = 'https://www.ikea.com/gb/en/'
    scrp = DataCollection(get_url)
    scrp.scrape_data()

if __name__ == '__main__':
    main()