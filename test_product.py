from utils.ikea import DataCollection
import unittest


class ProductTestCase(unittest.TestCase):
    def test_dictionary(self):
        test = DataCollection()
        #expected_value = 
        actual_value = test.scrape_data()
        print(self.assertTrue(actual_value))

    
bot = ProductTestCase()
bot.test_dictionary()