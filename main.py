from utils.ikea import DataCollection

if __name__ == '__main__':
    get_url = 'https://www.ikea.com/gb/en/'
    scrp = DataCollection(get_url)
    scrp.scrape_data()