import sys, os
sys.path.insert(0, '/Users/behzad/AiCore/DataCollectionPipeline/utils/')
import unittest 
from utils.ikea import DataCollection
from unittest.mock import patch, Mock, call
from time import sleep

class DataCollectionTest(unittest.TestCase):

    def setUp(self) -> None:
        self.scraper_obj = DataCollection(url="https://www.ikea.com/gb/en/")
        return super().setUp()

    def test_get_product_links(self):
        self.scraper_obj.driver.get("https://www.ikea.com/gb/en/search/products/?q=desk")
        self.scraper_obj.load_web_and_pass_cookies()
        check_list_product = self.scraper_obj._get_product_links()
        self.assertEqual(len(check_list_product), 22)
        self.assertEqual(check_list_product[-1], "https://www.ikea.com/gb/en/p/smastad-desk-white-grey-with-2-drawers-s19392258/")

    def test_get_more_product_links(self):
        self.scraper_obj.driver.get("https://www.ikea.com/gb/en/search/products/?q=desk")
        self.scraper_obj.load_web_and_pass_cookies()
        check_more_list_product = self.scraper_obj._get_more_product_links(num_page = 3)
        self.assertEqual(len(check_more_list_product), 70)

    def test_download_multiple_images_false(self):
        self.scraper_obj.driver.get("https://www.ikea.com/gb/en/p/micke-desk-oak-effect-20351742/")
        test_download_false = self.scraper_obj._download_multiple_images("image_name", "check_directory", download=False)
        self.assertEqual(len(test_download_false), 8)
        self.assertEqual(test_download_false[0], "https://www.ikea.com/gb/en/images/products/micke-desk-oak-effect__0515989_pe640126_s5.jpg?f=s")
        self.assertFalse(os.path.exists('raw_data/check_directory'))

    def test_download_multiple_images_true(self):
        self.scraper_obj.driver.get("https://www.ikea.com/gb/en/p/micke-desk-oak-effect-20351742/")
        test_download_true = self.scraper_obj._download_multiple_images("image_name", "check_directory", download=True)
        self.assertEqual(len(test_download_true), 8)
        self.assertEqual(test_download_true[0], "https://www.ikea.com/gb/en/images/products/micke-desk-oak-effect__0515989_pe640126_s5.jpg?f=s")
        self.assertTrue(os.path.exists('raw_data/check_directory'))

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_search_box(self, mock_execute_script: Mock):
        self.scraper_obj.scrol_down()
        mock_execute_script.assert_has_calls(calls=[call("window.scrollTo(0, 300)"), call("window.scrollTo(0, 600)")])

    def test_generate_uuid(self):
        check_uuid = self.scraper_obj.generate_uuid()
        self.assertEqual(len(check_uuid), 36)

    def test_store_raw_data(self):
        check_store = self.scraper_obj.store_raw_data({'test':1, 'this':2}, 'check_dict_dir')
        self.assertTrue(os.path.exists('raw_data/check_dict_dir'))
        self.assertTrue(os.path.exists('raw_data/check_dict_dir/data.json'))

    def tearDown(self) -> None:
        self.scraper_obj.driver.quit()
        return super().tearDown()

if __name__ == "__main__":
    unittest.main(argv=[""], verbosity=3, exit=True)