# Data Collection Pipeline

> The idea of this project is to collect data from any website and build pipelines to store data locally and/or on the cloud.

### Web Scraping

> Web scraping is the act to use a program to grab and download data from the Web.

- There are several modules in Python to scrape data from web pages such as:
    - Webbrowser: Opens a page in a browser
    - Requests: Downloads files and web pages from the Internet.
    - Beautiful Soup: Parses HTML.
    - Selenium: Launches and controls a web browser.

- For this project, all the above modules have been tested in the 'test_scrappers.py' file.

- For scrapping data from the Coin Market website and Ikea, the Selenium method is been used. Please check 'coin_market.py' and 'ikea.py' for more details.

### Retrieve data from a page

> For this milestone, we use the Selenium module and XPath expressions to select the details and extract them from the web pages.

- These could be done by creating different methods to get a text or images from a website. For example:

```python
    def __download_image(self, img_name, id=0, download=True):
        '''
        This function is used to download the main image for each product and save it to the 'images' folder

        Args
        ----
        img_name (str)
            Defines the name of the image
        id (str)
            Gives the image name a spesific id (like production id or unique id) as well as creating a parent directory named id for the 'images' folder  
        download (bool)
            If True, downloads the image. Otherwise, just get the src link of the image

        Returens
        --------
        the src link (str) of the image
        '''
        src = self.driver.find_element_by_xpath('//div[@class="pip-product__left-top"]//img[@class="pip-aspect-ratio-image__image"]').get_attribute('src') # Prepares the image source to download
        if download == True:
            if not os.path.exists(f'raw_data/{id}/images'): os.makedirs(f'raw_data/{id}/images') # Creats 'raw_data, {id} and images' folders if it is not exist
            sleep(1)
            try:
                urllib.request.urlretrieve(src, f"./raw_data/{id}/images/{img_name}_{id}.jpg") # saves images to the folder
            except:
                print(f"Couldn't download the main image: {src} for {id} product")
        return src
```
This method which is a private method will first create folders and subfolders and then downloads an image if applicable.

- Unique ID (UID): Usually, each product or element has a unique string to represent that product in a webpage. This ID must be deterministic, as it can be used to prevent re-scraping the same product data later on.

- Universally Unique ID (UUID): Along with the UID, it is typical to reference each record with a universally unique ID (UUID). It's a 128-bit label used for information in computer systems. They can be generated with the python UUID package.

```python
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
```
UUID looks like a 32-character sequence of letters and numbers separated by dashes. For example:

```code
354d86ec-d243-4a97-9b09-f833d9c7ebfa
```
- Once we have the access to all information in a webpage we need to store them. One option is to store info in a dictionary and save it locally. For the Ikea project a dictionary is defiened to record Product_id, UUID_number, Price, Name, Description, Image_link, Image_all_links in a dictionary and store it for each product localy as a json file called 'data.json'.

