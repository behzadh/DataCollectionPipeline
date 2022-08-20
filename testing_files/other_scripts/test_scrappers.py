'''
This code is to work on Data Collection Pipeline project
@author: Behzad 
'''
import webbrowser
import requests
from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.common.by import By
import time

class DataCollection:
    def __init__(self, url='www.google.co.uk'):
        ## Initializing all attributes
        self.url = url
        self.res = requests.get(self.url) # takes a string of a URL to download.

    def web_browser(self):
        ## This function opens the web browser
        webbrowser.open(self.url)

    def web_request(self):
        ## Scrap browsers with request method
        # checks program to stop as soon as some unexpected error happens.
        try:
            self.res.raise_for_status() # ensures that a program halts if a bad download occurs.
        except Exception as exc:
            print('There was a problem: %s' % (exc)) # prints the error
        self.res.status_code == requests.codes.ok # the status code for “OK” in the HTTP protocol is 200

    def web_bs4(self):
        ## Scrap browsers with beautiful soup method
        # checks program to stop as soon as some unexpected error happens.
        try:
            self.res.raise_for_status() # ensures that a program halts if a bad download occurs.
        except Exception as exc:
            print('There was a problem: %s' % (exc)) # prints the error
        #html = page.text # gets the content of the webpage
        self.soup = BeautifulSoup(self.res.text, 'html.parser')

    def web_selenium(self):
    ## Scrap browsers with selenium method
        driver = webdriver.Chrome()
        driver.get(self.url)
        time.sleep(3) # Wait a couple of seconds, so the website doesn't suspect you are a bot
        try:
            driver.switch_to_frame('gdpr-consent-notice') # This is the id of the frame
            accept_cookies_button = driver.find_element(by=By.XPATH, value='//*[@id="save"]')
            accept_cookies_button.click()
            time.sleep(1)
        except AttributeError:
            driver.switch_to.frame('gdpr-consent-notice') # This is the id of the frame
            accept_cookies_button = driver.find_element(by=By.XPATH, value='//*[@id="save"]')
            accept_cookies_button.click()
        except:
            pass # If there is no cookies button, we won't find it, so we can pass
        time.sleep(2)
        return driver

    def scrape_by_request(self):
        ## scrape data with request for your website
        self.web_request()
        html_string = self.res.text # gets the content of the webpage
        print(html_string[:250])

    def scrape_by_bs4(self):
        ## scrape data with bs4 for your website
        self.web_bs4()
        for item in self.soup.find_all("a"):
            #if not item.text.startswith("Method"): continue
            print(item.get('href'))

    def scrape_by_selenium(self):
        ## scrape data with selenium for your website
        driver = self.web_selenium()
        house_property = driver.find_element(by=By.XPATH, value='//*[@id="listing_62162461"]') # Change this xpath with the xpath the current page has in their properties
        a_tag = house_property.find_element_by_tag_name('a')
        link = a_tag.get_attribute('href')
        print(link)
        driver.get(link)
        time.sleep(3)
        # extract the price, address, number of bedrooms and the description:
        dict_properties = {'Price': [], 'Address': [], 'Bedrooms': [], 'Description': []} # puts all info to a dictionary
        price = driver.find_element(by=By.XPATH, value='//p[@data-testid="price"]').text
        dict_properties['Price'].append(price)
        address = driver.find_element(by=By.XPATH, value='//address[@data-testid="address-label"]').text
        dict_properties['Address'].append(address)
        n_bedrooms = driver.find_element(by=By.XPATH, value='//div[@class="c-PJLV c-PJLV-iiNveLf-css"]').text
        dict_properties['Bedrooms'].append(n_bedrooms)
        #description = driver.find_element(by=By.XPATH, value='//div[@class="css-14s800p ed7xmpl3"]').text
        div_tag = driver.find_element(by=By.XPATH, value='//div[@data-testid="truncated_text_container"]')
        span_tag = div_tag.find_element(by=By.XPATH, value='.//span')
        description = span_tag.text
        dict_properties['Description'].append(description)
        print(dict_properties)

    def get_links(self, driver: webdriver.Chrome) -> list:
        prop_container = driver.find_element(by=By.XPATH, value='//div[@class="css-1itfubx e152w0qi0"]')
        prop_list = prop_container.find_elements(by=By.XPATH, value='./div')
        link_list = []

        for house_property in prop_list:
            a_tag = house_property.find_element(by=By.TAG_NAME, value='a')
            link = a_tag.get_attribute('href')
            link_list.append(link)

        return link_list

    def scrape_by_selenium_list(self):
        big_list = []
        driver = self.web_selenium()
        for i in range(2):
            big_list.append(self.get_links(driver))
            driver.find_element(By.XPATH, "//a[@class='eaoxhri5 css-xtzp5a-ButtonLink-Button-StyledPaginationLink eaqu47p1']").click() 
            time.sleep(2)
            print(len(big_list))
        big_list_flaten = [j for sub in big_list for j in sub]
        print(big_list_flaten, len(big_list_flaten))
        dict_properties = {'Price': [], 'Address': [], 'Bedrooms': [], 'Description': []} # puts all info to a dictionary
        for link in big_list_flaten:
            driver.get(link)
            time.sleep(3)
            price = driver.find_element(by=By.XPATH, value='//p[@data-testid="price"]').text
            dict_properties['Price'].append(price)
            address = driver.find_element(by=By.XPATH, value='//address[@data-testid="address-label"]').text
            dict_properties['Address'].append(address)
            n_bedrooms = driver.find_element(by=By.XPATH, value='//div[@class="c-PJLV c-PJLV-iiNveLf-css"]').text
            dict_properties['Bedrooms'].append(n_bedrooms)
            #description = driver.find_element(by=By.XPATH, value='//div[@class="css-14s800p ed7xmpl3"]').text
            div_tag = driver.find_element(by=By.XPATH, value='//div[@data-testid="truncated_text_container"]')
            span_tag = div_tag.find_element(by=By.XPATH, value='.//span')
            description = span_tag.text
            dict_properties['Description'].append(description)
        print(dict_properties)

def main():
    ## main function to scrape a webpage
    my_url = 'https://www.zoopla.co.uk/new-homes/property/london/?q=London&results_sort=newest_listings&search_source=new-homes&page_size=25&pn=1&view_type=list'
    scrp = DataCollection(my_url)
    scrp.scrape_by_selenium_list()

if __name__ == '__main__':
    main()