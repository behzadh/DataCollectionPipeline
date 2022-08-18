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

class Scraper:
    '''
    This class will load a website and accept the cookies if applicable
    '''
    def __init__(self, url='www.google.co.uk'):
        '''
        This function initialize all attributes used in this class.
        '''
        self.url = url
        self.driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()) # Access the Chrome web driver
        self.driver.get(self.url)
        self.action = ActionChains(self.driver) # Sets action chains
        
    def load_web_and_pass_cookies(self, xpath: str = '//*[@id="onetrust-accept-btn-handler"]'):
        '''
        This method loads a website and accepts the cookies.

        It has a delay setup (in seconds) to allow the cookies' frame pops up.

        Parameters
        ----------
        xpath (str)
            The xpath of the Accept Cookies botton
        '''
        delay = 3 # Sets a delay after the webside is loaded to allow the cookies' frame pops up  
        try:
            # Tries to wait for web driver be accessed and the cookies frame pops up. Then, clicks 'accept cookies'
            WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, xpath)))
            accept_cookies_button = WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, xpath)))
            accept_cookies_button.click()
            sleep(0.5)
        except TimeoutException:
            print("Loading took too much time!")

class DataCollection(Scraper):
    '''
    This class will scrape the web details, download related images and store the data locally
    '''
    def search_box(self, search_word: str, xpath_value: str='//div[@class="search-field"]'):
        '''
        This functions finds the search box and types the search_word to be found

        Parameters
        ----------
        search_word (str)
            The word that needs to be searched
        xpath_value (str)
            The value for xpath to find the search box
        '''
        searchTextbox = self.driver.find_element(by=By.XPATH, value=xpath_value) # Finds the search text box position
        self.action.move_to_element(searchTextbox).click().send_keys(search_word).send_keys(Keys.RETURN).perform() # Types a word to the search box
    
    def __get_product_links(self) -> list:
        '''
        This Function gets all links of elements/products in the first page of a webpage

        Returns
        -------
        list
            Returns the links (href) of all products
        '''
        links_list = []
        # Find all elements in a container or a table 
        result_container = self.driver.find_elements(by=By.XPATH, value="//section[@class='results']//div[@class='serp-grid__item search-grid__item product-fragment']/a")
        for result in result_container:
            # Loops on all the elements of the container to extract their links
            link = result.get_attribute("href") # Gets the web link
            links_list.append(link)
            #print(link)
        return links_list

    def __get_more_product_links(self, num_page: int = 2) -> list:
        '''
        This function gets more links by loading more elements or going to the next pages (if applicable)

        Parameters
        ----------
            num_page (int): The number of pages that need to be extracted
        '''
        big_list = []
        for _ in range(num_page):
            big_list.append(self.__get_product_links())
            try:
                self.driver.find_element(By.XPATH, "//a[@class='show-more__button button button--secondary button--small']").click() # Clicks on next page or loading more products
                sleep(2)
            except:
                pass
        more_link_list = list(set([k for sub in big_list for k in sub])) # flatten and unique the list of links
        return more_link_list

    def __download_image(self, img_name: str, dir_name: str = '', download: bool = True):
        '''
        This function is used to download the main image for each product and save it to the 'images' folder

        Parameters
        ----------
        img_name (str)
            Defines the name of the image
        dir_name (str)
            Gives the image name a spesific id (like production id or unique id) as well as creating a parent directory named dir_name for the 'images' folder  
        download (bool)
            If True, downloads the image. Otherwise, just get the src link of the image

        Returens
        --------
        the src link (str) of the image
        '''
        src = self.driver.find_element_by_xpath('//div[@class="pip-product__left-top"]//img[@class="pip-aspect-ratio-image__image"]').get_attribute('src') # Prepares the image source to download
        if download == True:
            if not os.path.exists(f'raw_data/{dir_name}/images'): os.makedirs(f'raw_data/{dir_name}/images') # Creats 'raw_data, {id} and images' folders if it is not exist
            sleep(1)
            try:
                urllib.request.urlretrieve(src, f"./raw_data/{dir_name}/images/{img_name}_{dir_name}.jpg") # saves images to the folder
            except:
                print(f"Couldn't download the main image: {src} for {dir_name} product")
        return src

    def __download_multiple_images(self, img_name: str, dir_name: str = '', download: bool = True):
        '''
        This function is used to download multiple images of a product and save them to the 'multiple_images' folder

        See help(__download_image) for accurate signature
        '''
        src_container = self.driver.find_elements(by=By.XPATH, value="//div[@class='pip-media-grid__grid ']//img") # Prepares an image container source to download
        sleep(0.5)
        img_links_list = []
        for k, srcs in enumerate(src_container):
            # Goops on all the elements of the container to extract their links
            img = srcs.get_attribute("src") # Gets the image link
            img_links_list.append(img)
            if download == True:
                if not os.path.exists(f'raw_data/{dir_name}/multiple_images'): os.makedirs(f'raw_data/{dir_name}/multiple_images') # Creats 'raw_data, {id} and multiple_images' folders if it is not exist
                try:
                    urllib.request.urlretrieve(img, f"./raw_data/{dir_name}/multiple_images/{img_name}_{k}_{dir_name}.jpg") # saves images to the folder
                except:
                    print(f"Couldn't download this image: {img} for {dir_name} product")
            #print(img)
        return img_links_list

    def scrol_down(self, steps: int = 2, speed: int = 300):
        '''
        This function is an action to scrol down a page slowly and step by step like a human.
        Parameters
        ----------
        steps (int)
            Defiens the number of steps to go throw the page.
        speed (int)
            Sets the speed of scroling down in each step. 
        '''
        scrol_speed = speed # This number controls the speed of the scrolling down. If larger, scrols faster
        for _ in range(steps):
            # To scrol down step by step. In order to cover all page scrolling down the range should be larger
            self.driver.execute_script("window.scrollTo(0, "+str(scrol_speed)+")")
            scrol_speed += speed  
            sleep(0.5)

    def generate_uuid(self) -> str:
        '''
        This method will generates Universal Unique IDs. 
        
        UUID is a unique 128-bit label used for information in computer systems. It looks like a 
        32-character sequence of letters and numbers separated by dashes.
        ex: 354d86ec-d243-4a97-9b09-f833d9c7ebfa

        Returns
        -------
        str
            A singal UUID
        '''
        return str(uuid.uuid4())

    def store_raw_data(self, dict: dict, dir_name: str = '_'):
        '''
        This function used to store the raw data dictionaries locally

        Parameters
        ----------
        dict (str)
            It's the name of the dictionary that needs to be stored
        dir_name (str)
            Defines a spesific directory named 'dir_name' (like production id or unique id) to store the dictionary as a json file 
        '''
        if not os.path.exists(f'raw_data/{dir_name}'): os.makedirs(f'raw_data/{dir_name}') # Creats 'raw_data and id' folders if it is not exist
        with open(f'./raw_data/{dir_name}/data.json', 'w') as fp:
            json.dump(dict, fp) # Saves dict in a json file

    def scrape_data(self):
        '''
        This function gets all the methods and actions to extrac/scrape all the needed information from a website.

        It first load the Ikea page, get to search box and types a keyword to be searched (like" desk).
        Then scrols down and gets the URL of all products available, accessing each of them and extracting 
        data for each product. The details will be stored in a dictionary.
        '''
        self.load_web_and_pass_cookies() # Load webpage and pass cookies
        self.search_box('desk')
        sleep(1)
        self.scrol_down(5) # Scroling down the page by (n) steps
        #all_links_list = self.__get_product_links() # Gets all links in the first page
        all_links_list = self.__get_more_product_links(2) # # Gets all links in multiple (n) pages
        for link in all_links_list[:4]: ## temporary sets to first 4 products
            dict_properties = {} # Creats a dictionary
            self.driver.get(link) # Gets each link and open it
            sleep(1)
            product_id = self.driver.find_element(By.XPATH, "//div[@class='pip-product__subgrid product-pip js-product-pip']").get_attribute('data-product-id') # Gets product id
            uuid_number = self.generate_uuid() # Generates universal unique ids
            price = self.driver.find_element(By.XPATH, "//span[@class='pip-price__integer']").text # Gets price
            currency = self.driver.find_element(By.XPATH, "//span[@class='pip-price__currency-symbol pip-price__currency-symbol--leading\n        pip-price__currency-symbol--superscript']").text # Gets currency
            name = self.driver.find_element(By.XPATH, "//span[@class='pip-header-section__title--big notranslate']").text # Gets name
            description = self.driver.find_element(By.XPATH, "//span[@class='pip-header-section__description-text']").text # Gets description
            src_img = self.__download_image(f'{name}_', product_id, False) # If true, downloads the image and save it with their name and product id
            src_multi_img = self.__download_multiple_images(f'{name}_', product_id, False) # If true, downloads the all images of a product and save it with their name, an intiger and product id
            dict_properties.update({'Product_id': [product_id], 'UUID_number': [uuid_number],'Price': [currency + price], 'Name': [name], 'Description': [description], 'Image_link': [src_img], 'Image_all_links': src_multi_img})
            #self.store_raw_data(dict_properties, product_id) # Locally stores the dictionary 
            print(dict_properties)
