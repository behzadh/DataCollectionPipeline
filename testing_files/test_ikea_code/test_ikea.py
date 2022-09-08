import sys, os
sys.path.insert(0, '/Users/behzad/AiCore/DataCollectionPipeline/utils/')
import unittest 
from utils.ikea import DataCollection
from unittest.mock import patch, Mock, call
from time import sleep

class DataCollectionTest(unittest.TestCase):

    def setUp(self) -> None:
        self.scraper_obj = DataCollection(url="https://www.ikea.com/gb/en/")
        self.scraper_obj.pass_cookies()
        return super().setUp()

    def test_get_product_links(self):
        self.scraper_obj.driver.get("https://www.ikea.com/gb/en/search/products/?q=desk")
        check_list_product = self.scraper_obj._get_product_links()
        self.assertEqual(len(check_list_product), 22)
        self.assertEqual(check_list_product[-1], "https://www.ikea.com/gb/en/p/smastad-desk-white-grey-with-2-drawers-s19392258/")

    def test_get_more_product_links(self):
        self.scraper_obj.driver.get("https://www.ikea.com/gb/en/search/products/?q=desk")
        check_more_list_product = self.scraper_obj._get_more_product_links(num_page = 3)
        self.assertEqual(len(check_more_list_product), 70)

    def test_get_href_image(self):
        self.scraper_obj.driver.get("https://www.ikea.com/gb/en/p/micke-desk-oak-effect-20351742/")
        test_get_href = self.scraper_obj._get_href_image()
        self.assertEqual(test_get_href, "https://www.ikea.com/gb/en/images/products/micke-desk-oak-effect__0515989_pe640126_s5.jpg?f=s")

    def test_download_image(self):
        self.scraper_obj.driver.get("https://www.ikea.com/gb/en/p/micke-desk-oak-effect-20351742/")
        test_download_false = self.scraper_obj._download_image("image_name", "check_directory")
        self.assertTrue(os.path.exists('raw_data/check_directory'))

    def test_get_href_list_images(self):
        self.scraper_obj.driver.get("https://www.ikea.com/gb/en/p/micke-desk-oak-effect-20351742/")
        test_download_true = self.scraper_obj._get_href_list_images()
        self.assertEqual(len(test_download_true), 8)
        self.assertEqual(test_download_true[0], "https://www.ikea.com/gb/en/images/products/micke-desk-oak-effect__0515989_pe640126_s5.jpg?f=s")

    def test_download_multiple_images_true(self):
        self.scraper_obj.driver.get("https://www.ikea.com/gb/en/p/micke-desk-oak-effect-20351742/")
        test_download_multi = self.scraper_obj._download_multiple_images("image_name", "check_multi_directory")
        self.assertTrue(os.path.exists('raw_data/check_multi_directory'))

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_search_box(self, mock_execute_script: Mock):
        self.scraper_obj.scrol_down()
        mock_execute_script.assert_has_calls(calls=[call("window.scrollTo(0, 300)"), call("window.scrollTo(0, 600)")])

    def test_generate_uuid(self):
        check_uuid = self.scraper_obj.generate_uuid()
        self.assertEqual(len(check_uuid), 36)

    def test_store_raw_data_locally(self):
        check_store = self.scraper_obj.store_raw_data_locally({'test':1, 'this':2}, 'check_dict_dir')
        self.assertTrue(os.path.exists('raw_data/check_dict_dir'))
        self.assertTrue(os.path.exists('raw_data/check_dict_dir/data.json'))

    def test_psycopg2_create_engine(self):
        pass

    def test_create_df(self):
        check_df = self.scraper_obj.create_df({'this':[1], 'is':[2], 'a_dict':[3]})
        self.assertEqual(check_df.iloc[0]['this'], 1)

    def tearDown(self) -> None:
        self.scraper_obj.driver.quit()
        return super().tearDown()

if __name__ == "__main__":
    unittest.main(argv=[""], verbosity=3, exit=True)