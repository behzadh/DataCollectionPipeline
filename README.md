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
```
This method will first create folders and subfolders and then downloads an image if applicable.

- Unique ID (UID): Usually, each product or element has a unique string to represent that product in a webpage. This ID must be deterministic, as it can be used to prevent re-scraping the same product data later on.

- Universally Unique ID (UUID): Along with the UID, it is typical to reference each record with a universally unique ID (UUID). It's a 128-bit label used for information in computer systems. They can be generated with the python UUID package.

```python
def generate_uuid(self):
    ## Generates Universal Unique IDs
    return str(uuid.uuid4())
```
UUID looks like a 32-character sequence of letters and numbers separated by dashes. For example:

```code
354d86ec-d243-4a97-9b09-f833d9c7ebfa
```
- Once we have the access to all information in a webpage we need to store them. One option is to store info in a dictionary and save it locally. For the Ikea project a dictionary is defiened to record Product_id, UUID_number, Price, Name, Description, Image_link, Image_all_links in a dictionary and store it for each product localy as a json file called 'data.json'.

