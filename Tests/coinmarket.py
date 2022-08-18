'''
This code is to work on Data Collection Pipeline project
@author: Behzad 
'''
from email.mime import image
from operator import concat
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep

class DataCollection:
    def __init__(self, url='www.google.co.uk'):
        ## Initializing all attributes
        self.url = url

    def load_and_pass_cookies(self):
    ## Scrap browsers with selenium method
        driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        driver.get(self.url)
        sleep(2)
        driver.find_element(by=By.XPATH, value="//div[@class='gv-close']").click()
        sleep(1)
        driver.find_element(by=By.XPATH, value="//div[@class='cmc-cookie-policy-banner__close']").click()
        sleep(2) # Wait a couple of seconds, so the website doesn't suspect you are a bot
        actionChains = ActionChains(driver)
        row_inspect = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/div[1]/div[2]/div/div[1]/div[5]/table/tbody/tr[1]")
        actionChains.context_click(row_inspect).perform()
        #actionChains.click('Inspect')
        #actionChains.send_keys(Keys.COMMAND, Keys.SHIFT, 'c')
        actionChains.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ARROW_DOWN).send_keys(Keys.RETURN).perform()
        sleep(5)
        return driver

    def get_links(self):
        driver = self.load_and_pass_cookies()
        table_container = driver.find_elements(by=By.XPATH, value="//table[@class='h7vnx2-2 czTsgW cmc-table  ']//div[@class='sc-16r8icm-0 escjiH']/a")
        y = 300
        for timer in range(0,30):
            driver.execute_script("window.scrollTo(0, "+str(y)+")")
            y += 300  
            sleep(1)
        link_list = []
        for coin_element in table_container:
            link = coin_element.get_attribute("href")
            link_list.append(list)
            print(link)
        print(len(link_list))
        return link_list

    def scrape_data(self):
        driver = self.load_and_pass_cookies()
        #coin_info = driver.find_element(by=By.XPATH, value='//div[@class="sc-16r8icm-0 escjiH"]') # Change this xpath with the xpath the current page has in their properties
        coin_info = driver.find_element(by=By.XPATH, value='//div[@class="h7vnx2-1 bFzXgL"]')
        a_tag = coin_info.find_element_by_tag_name('a')
        link = a_tag.get_attribute('href')
        print(link)
        driver.get(link)
        price = driver.find_element(by=By.XPATH, value='//div[@class="priceValue "]').text
        price_min = driver.find_element(by=By.XPATH, value='//div[@class="sc-16r8icm-0 lipEFG"]').text
        price_max = driver.find_element(by=By.XPATH, value='//div[@class="sc-16r8icm-0 SjVBR"]').text
        print(price, price_max, price_min)
        sleep(2)
        rows_list = []
        for tag_no in range(1, 21):
            current_element = driver.find_element(by=By.XPATH, value=f"//td[{tag_no}][@class='sc-16r8icm-0 escjiH']")
            a_tag = current_element.find_element_by_tag_name('a')
            link = a_tag.get_attribute('href')
            print(link)
            rows_list.append(link)


def main():
    ## main function to scrape a webpage
    my_url = 'https://coinmarketcap.com/'
    scrp = DataCollection(my_url)
    scrp.get_links()

if __name__ == '__main__':
    main()