from utils.ikea import DataCollection

if __name__ == '__main__':
    get_url = 'https://www.ikea.com/gb/en/'
    scrp = DataCollection(get_url, headless=True) # if True, it works w/o opening the Chrome
    scrp.scrape_data()