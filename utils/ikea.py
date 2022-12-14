'''
This code is to work on Data Collection Pipeline project
@author:    Behzad 
@date:      9 September 2022
'''
import os, json, shutil, sys
import argparse
import uuid
import urllib.request
import boto3
import pandas as pd
import configparser
from getpass import getpass
from os import walk
from time import sleep
from sqlalchemy import create_engine
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

class Scraper:

    '''
    This class will load a website and accept the cookies if applicable and has the following methods:

    __init__(self, url='https://www.ikea.com/gb/en/', headless: bool = False)
    accept_cookies(self, xpath: str = '//*[@id="onetrust-accept-btn-handler"]')
    '''
    def __init__(self, url='https://www.ikea.com/gb/en/', headless: bool = False):

        '''
        This function initialize all attributes used in this class and loads the website.

        Parameters
        ----------
        url (str)
            The webpage link
        headless (bool)
            It run the code without openning the chrome (headless) if headless is True
        '''
        if headless:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument("--disable-setuid-sandbox")
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--start-maximized')
            options.add_argument('--disable-dev-shm-usage')
            self.driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(), chrome_options=options) # Access the web driver w/o Chrome pops up
        else:
            self.driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()) # Access the Chrome web driver
        self.driver.get(url)
        self.action = ActionChains(self.driver) # Sets action chains
    
    def accept_cookies(self, xpath: str = '//*[@id="onetrust-accept-btn-handler"]'):

        '''
        This method accepts the cookies.

        It has a delay setup (in seconds) to allow the cookies' frame pops up.

        Parameters
        ----------
        xpath (str)
            The xpath of the Accept Cookies botton
        '''
        delay = 3 # Sets a delay after the webside is loaded to allow the cookies' frame pops up  
        try:
            # Tries to wait for web driver to be accessed and the cookies frame pops up. Then, clicks 'accept cookies'
            accept_cookies_button = WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, xpath)))
            accept_cookies_button.click()
            sleep(0.5)
        except TimeoutException:
            print("Loading took too much time!")

class StoreData:

    '''
    This class is responsible for storing data locally or on AWS cloud and has the following methods:

    __init__(self)
    check_config_file(self)
    check_data_exist_locally(self)
    check_images_exist(self)
    check_data_exist_on_s3(self)
    check_data_exist_on_rds(self)
    user_store_data_options(self)
    store_raw_data_locally(self, dict: dict, dir_name: str = '_')
    store_to_S3_boto3(self, dir_name: str = '_')
    psycopg2_create_engine(self)
    store_tables_on_rds(self, df_name: pd.DataFrame)
    '''
    def __init__(self):

        '''
        This function initialize all attributes.
        '''
        self.store_data_locally = False
        self.store_data_on_S3 = False
        self.store_data_in_rds_table = False
        self.save_img = False
        self.pid_list_locally = []
        self.pid_list_s3 = []
        self.pid_list_rds = []
        self.pid_list_images = []
        self.config = configparser.ConfigParser() # Loads a config file to pass the passwords for S3 and RDS connections
        self.config.read('config_file') # Reads the config file

    def check_config_file(self):

        '''
        Checks to have correct config file with keys defined
        '''
        if(self.config.get('KEY','AWSAccessKeyId')==''):
            print('Please fill your config file for S3 Keys to process your data ...')
            sys.exit()
        elif(self.config.get('KEY','DATABASE_TYPE')==''):
            print('Please fill your config file for RDS Keys to process your data ...')
            sys.exit()

    def check_data_exist_locally(self):

        '''
        Checks if the data is already exist locally to avoid rescraping
        '''
        self.pid_list_locally = next(walk(f'./{self.folder_name}/'), (None, None, []))[1] # Returns a list of previouse recordes to avoid data rescraping locally
        if self.pid_list_locally==None:
            self.pid_list_locally = ['pid'] # This is to hack if the product id list is empty, continue with processing

    def check_images_exist(self):

        '''
        Checks if the data is already exist locally to avoid rescraping
        '''
        self.pid_list_images = next(walk(f'./{self.folder_name}/images'), (None, None, []))[1] # Returns a list of previouse recordes to avoid data rescraping locally
        if self.pid_list_images==None:
            self.pid_list_images = ['pid'] # This is to hack if the product id list is empty, continue with processing

    def check_data_exist_on_s3(self):
        
        '''
        Checks if the data is already exist on AWS S3 to avoid rescraping
        '''
        self.check_config_file()
        self.s3_client = boto3.client('s3',aws_access_key_id=self.config.get('KEY','AWSAccessKeyId'), aws_secret_access_key= self.config.get('KEY','AWSSecretKey'))
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.config.get('KEY','AWSBucketName'), Delimiter='/', Prefix=f'{self.folder_name}/')
            self.pid_list_s3 = [obj["Prefix"].lstrip(f'{self.folder_name}/').rstrip('/') for obj in response["CommonPrefixes"]] # Returns a list of previouse recordes to avoid data rescraping on S3
        except:
            print('No data found on the Amazon S3')
            self.pid_list_s3 = ['pid'] # This is to hack if the product id list is empty, continue with processing

    def check_data_exist_on_rds(self):

        '''
        Checks if the data is already exist on AWS RDS to avoid rescraping
        ''' 
        self.check_config_file()
        self.engine = self.psycopg2_create_engine()
        with self.engine.connect() as conn:
            try:
                product_id_column = conn.execute(f'SELECT "Product_id" FROM {self.table_name}')
                for p_id in product_id_column:
                    self.pid_list_rds.append(''.join(p_id)) # Returns a list of previouse recordes to avoid data rescraping on RDS
                product_id_column.close()
            except:
                print(f'No table found with {self.table_name} name on the Amazon RDS')
                self.pid_list_rds = ['pid'] # This is to hack if the product id list is empty, continue with processing

    def user_store_data_options(self):

        '''
        Gets arguments options from user to store data locally, on S3 or/and RDS
        '''
        parser = argparse.ArgumentParser()
        parser.add_argument('--local', action='store_true', default=False, help='Store data locally')
        parser.add_argument('--s3', action='store_true', default=False, help='Store data on AWS S3')
        parser.add_argument('--rds', action='store_true', default=False, help='Store data on RDS')
        parser.add_argument('--imgs', action='store_true', default=False, help='Store images')

        parser.add_argument('--folder', type=str, default='raw_data', help='Folder\'s name to store data (ex: raw_data)')
        parser.add_argument('--word', type=str, default='desk', help='word to be typed in search bar (ex: desk)')
        parser.add_argument('--table', type=str, default='table_name', help='user rds table (ex: table_name)')
        
        args = parser.parse_args()
        self.search_word = args.word

        if args.local:
            self.folder_name = args.folder
            self.store_data_locally = True
            self.check_data_exist_locally()
        else:
            print('To store data locally add --local')
        if args.s3:
            self.store_data_on_S3 = True
            self.check_data_exist_on_s3()
        else:
            print('To store data on AWS S3 add --s3')
        if args.rds:
            self.table_name = args.table
            self.store_data_in_rds_table = True
            self.check_data_exist_on_rds()
        else:
            print('To store data on RDS add --rds')
        if args.imgs:
            self.save_img = True
            self.check_images_exist()
        else:
            print('To store images add --imgs')
        print('\nData scraping is in progress ...\n')
        
    def store_raw_data_locally(self, dict: dict, dir_name: str = '_'):

        '''
        This function used to store raw data locally. It stores each product dictionary as a jsone file.

        Parameters
        ----------
        dict (dict)
            It's a dictionary that needs to be stored locally
        dir_name (str)
            Defines a spesific directory named 'dir_name' (like production id or unique id) to store the dictionary as a json file 
        '''
        print('Storing data locally ...')
        if not os.path.exists(f'{self.folder_name}/{dir_name}'): os.makedirs(f'{self.folder_name}/{dir_name}') # Creats folders and subfolders if they're not exist
        with open(f'./{self.folder_name}/{dir_name}/data.json', 'w') as fp:
            json.dump(dict, fp) # Saves dict in a json file

    def store_to_S3_boto3(self, dir_name: str = '_'):

        '''
        This function used to store data on the AWS S3 using boto3 module. It stores data on AWS S3 and keeps the same structure as we store data locally.

        Parameters
        ----------
        dir_name (str)
            Defines a spesific directory named 'dir_name' (like production id or unique id) to store data 
        '''
        print('Storing data on S3 ...')
        bucket_name = self.config.get('KEY','AWSBucketName') # It's the bucket name from AWS S3
        directory_name = f'{self.folder_name}/{dir_name}' 
        for root,dirs,files in os.walk(directory_name):
            #print(root,dirs,files)
            for file in files:
                self.s3_client.upload_file(os.path.join(root,file),bucket_name,os.path.join(root,file))

    def psycopg2_create_engine(self):

        '''
        This method will create a psycopg2 engine 
        
        Returns
        -------
        engine
            Returns engine to access to a postgresql database
        '''
        DATABASE_TYPE = self.config.get('KEY','DATABASE_TYPE')
        DBAPI = self.config.get('KEY','DBAPI')
        ENDPOINT = self.config.get('KEY','ENDPOINT')
        USER = self.config.get('KEY','USER')
        PASSWORD = self.config.get('KEY','PASSWORD')
        PORT = self.config.get('KEY','PORT')
        DATABASE = self.config.get('KEY','DATABASE')
        engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")       
        #print(engine.connect())
        return engine
    
    def store_tables_on_rds(self, df_name: pd.DataFrame):

        '''
        This functions stores data as a table on the AWS RDS

        Parameters
        ----------
        df_name (DataFrame)
            It's the data frame that will be stored as a table on the RDS
        ''' 
        print('Storing data on RDS ...')
        df_name.to_sql(self.table_name, self.engine, if_exists='append') # if_exist='replace' or 'append'

class DataCollection(Scraper, StoreData):

    '''
    This class will scrape the web details, download related images and store the data locally or/and on AWS cloud and has the following methods:

    __init__(self, url='https://www.ikea.com/gb/en/', headless: bool = False)
    search_box(self, search_word: str, xpath_value: str='//div[@class="search-field"]')
    get_product_links(self, num_page: int = 1) 
    _get_href_image(self)
    _download_image(self, img_name: str, dir_name: str = '_')
    _get_href_list_images(self)
    _download_multiple_images(self, img_name: str, dir_name: str = '_')
    scrol_down(self, steps: int = 2, speed: int = 300)
    generate_uuid(self)
    retrieve_product_details(self)
    store_data_final(self)
    scrape_data(self)
    '''
    def __init__(self, url='https://www.ikea.com/gb/en/', headless: bool = False):

        '''
        Initialize the __init__ functions of StoreData and Scraper classes
        '''
        StoreData.__init__(self)
        Scraper.__init__(self, url, headless) 
    
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

    def get_product_links(self, num_page: int = 1) -> list:

        '''
        This function gets products links and can be set to go to the next pages (if applicable)

        Parameters
        ----------
            num_page (int): The number of pages that need to be extracted
        '''
        more_link_list = []
        for _ in range(num_page):
            links_list = []
            sleep(3)
            # Find all elements in a container or a table 
            result_container = self.driver.find_elements(by=By.XPATH, value="//section[@class='results']//div[@class='serp-grid__item search-grid__item product-fragment']/a")
            for result in result_container:
                # Loops on all the elements of the container to extract their links
                link = result.get_attribute("href") # Gets the web link
                links_list.append(link)
            more_link_list.append(links_list)
            try:
                self.driver.find_element(By.XPATH, "//a[@class='show-more__button button button--secondary button--small']").click() # Clicks on next page or loading more products
            except:
                pass
        all_link_list = list(set([k for sub in more_link_list for k in sub])) # flatten and unique the list of links
        return all_link_list 
    
    def _get_href_image(self): 

        '''
        This function will return the link of main image.

        Returens
        --------
        str
            the src link of the image
        '''
        src = self.driver.find_element(by=By.XPATH, value='//div[@class="pip-product__left-top"]//img[@class="pip-aspect-ratio-image__image"]').get_attribute('src') # Prepares the image source to download
        return src
    
    def _download_image(self, img_name: str, dir_name: str = '_'):
        
        '''
        This function is used to download the main image for each product and save it to the 'images' folder

        Parameters
        ----------
        img_name (str)
            Defines the name of the image
        dir_name (str)
            Gives the image name a spesific id (like production id or unique id) as well as creating a parent directory named dir_name for the 'images' folder  
        '''
        src = self._get_href_image()
        if not os.path.exists(f'{self.folder_name}/{dir_name}/image'): os.makedirs(f'{self.folder_name}/{dir_name}/image') # Creats 'folder_name, {id} and image' folders if it is not exist
        sleep(1)
        try:
            urllib.request.urlretrieve(src, f"./{self.folder_name}/{dir_name}/image/{img_name}_{dir_name}.jpg") # saves images to the folder
        except:
            print(f"Couldn't download the main image: {src} for {dir_name} product")

    def _get_href_list_images(self):

        '''
        This function will return the links of images for each product.
        
        Returens
        --------
        list
            list of images links
        '''
        src_container = self.driver.find_elements(by=By.XPATH, value="//div[@class='pip-media-grid__grid ']//img") # Prepares an image container source to download
        sleep(0.5)
        img_links_list = []
        for srcs in src_container:
            # Loops on all the elements of the container to extract their links
            img = srcs.get_attribute("src") # Gets the image link
            img_links_list.append(img)
        return img_links_list

    def _download_multiple_images(self, img_name: str, dir_name: str = '_') -> list:
        
        '''
        This function is used to download multiple images of a product and save them to the 'multiple_images' folder

        See help(__download_image) for accurate signature
        '''
        img_links_list = self._get_href_list_images()
        if not os.path.exists(f'{self.folder_name}/{dir_name}/images'): os.makedirs(f'{self.folder_name}/{dir_name}/images') # Creats 'folder_name, {id} and images' folders if it is not exist
        for k,link in enumerate(img_links_list):
            try:
                urllib.request.urlretrieve(link, f"./{self.folder_name}/{dir_name}/images/{img_name}_{k}_{dir_name}.jpg") # saves images to the folder
            except:
                print(f"Couldn't download this image: {link} for {dir_name} product")
    
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

    def retrieve_product_details(self):
        
        '''
        This method retrieve product data

        Returns
        -------
        dict
            A product dictionary
        '''
        dict_properties = {}
        product_id = self.driver.find_element(By.XPATH, "//div[@class='pip-product__subgrid product-pip js-product-pip']").get_attribute('data-product-id') # Gets product id
        uuid_number = self.generate_uuid() # Generates universal unique ids
        price = self.driver.find_element(By.XPATH, "//span[@class='pip-price__integer']").text # Gets price
        currency = self.driver.find_element(By.XPATH, "//span[@class='pip-price__currency-symbol pip-price__currency-symbol--leading\n        pip-price__currency-symbol--superscript']").text # Gets currency
        name = self.driver.find_element(By.XPATH, "//span[@class='pip-header-section__title--big notranslate']").text # Gets name
        description = self.driver.find_element(By.XPATH, "//span[@class='pip-header-section__description-text']").text # Gets description
        src_img = self._get_href_image() # Gets the image link
        src_multi_img = self._get_href_list_images() # Gets the images links
        # -------- Product dictionary -------- #
        dict_properties.update({'Product_id': [product_id], 'UUID_number': [uuid_number],'Price': [currency + price], 'Name': [name], 'Description': [description], 'Image_link': [src_img], 'Image_all_links': [src_multi_img]})
        print(product_id)
        return dict_properties

    def store_data_final(self):

        '''
        This method will store data when is requested
        '''
        dict_properties = self.retrieve_product_details()
        product_id = dict_properties['Product_id'][0]
        name = dict_properties['Name'][0].replace(" ", "")
        # ------- Store Data locally ------- #
        if self.store_data_locally and (product_id not in self.pid_list_locally): 
            self.store_raw_data_locally(dict_properties, product_id) 
            self.pid_list_locally.append(product_id)
        # ---------- Store images ---------- #
        if self.save_img and (product_id not in self.pid_list_images): 
            self._download_image(f'{name}_', product_id) 
            self._download_multiple_images(f'{name}_', product_id) 
        # -------- Store Data on S3 -------- #
        if self.store_data_on_S3 and (product_id not in self.pid_list_s3): 
            if not self.store_data_locally:
                self.store_raw_data_locally(dict_properties, product_id) # Locally stores the dictionary
                self.store_to_S3_boto3(product_id) 
                shutil.rmtree(f'./{self.folder_name}/{product_id}') # Removes directory after uploading on the S3 
                print('Record removed successfully after storing it on the S3 bucket')
                self.pid_list_s3.append(product_id)
            else:
                self.store_to_S3_boto3(product_id) 
                self.pid_list_s3.append(product_id)
        # -------- Store Data on RDS ------- #
        if self.store_data_in_rds_table and (product_id not in self.pid_list_rds): 
            df_products = pd.DataFrame(dict_properties)
            self.store_tables_on_rds(df_products)

    def scrape_data(self):

        '''
        This function gets all the methods and actions to extrac/scrape all the necessary information from a website.

        It first loads the Ikea page, gets to search box and types a keyword to be searched (like 'desk').
        Then scrols down, and gets the URL of all products available, accessing each of them and extracting 
        data for each product. The details will be stored in a dictionary. Then, stores data locally, on AWS 
        S3 or in a table on RDS.
        '''
        self.user_store_data_options() 
        self.accept_cookies() 
        self.search_box(f'{self.search_word}') 
        sleep(1)
        self.scrol_down(1)
        links_list = self.get_product_links(2) # Gets all links in multiple (n) pages
        for link in links_list[:3]: ## temporary sets to first 3 products 
            self.driver.get(link) # Gets each link and open it
            sleep(0.5)
            self.store_data_final()
        self.driver.close()