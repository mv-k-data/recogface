import os
import time
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import base64
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
import requests

class ImageSearchEngine(ABC):
    """Абстрактний клас для пошукових систем зображень."""
    
    def __init__(self, uuid, original_image_path):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.original_image_path = original_image_path
        self.result_image_path = original_image_path[:original_image_path.rfind("/")]
        self.uuid = uuid

    def __del__(self):
        # destroing driver
        self.driver.quit()

    @abstractmethod
    def search_images(self):
        """abstract method for search images"""
        pass


class GoogleImageSearch(ImageSearchEngine):
    """Class for search via Google Images"""

    SEARCH_ENGINE = "google"
    def _search_interaction(self):
        print("Start _search")
        self.driver.get("https://images.google.com/")
        search_button = self.driver.find_element(By.CLASS_NAME, "Gdd5U")
        search_button.click()
        time.sleep(3)
        
        upload_input = self.driver.find_element(By.NAME, "encoded_image")
        upload_input.send_keys(os.path.abspath(self.original_image_path))
        
        time.sleep(5)
        self.soup = BeautifulSoup(self.driver.page_source, "html.parser")
        self.driver.quit()

    def _get_image_text(self, element):
        image_text = element.find("span", class_ = 'Yt787')
        return image_text.text

    def _get_image_url(self, element):
        image_url = element.find("a", class_ = 'LBcIee')  
        return image_url.attrs["href"]

    def _save_image(self, element, result_image_path, result_image_name):
        print("Start _save_image")
        image_full_name = f"{result_image_path}/{result_image_name}"
        if not os.path.exists(result_image_path):
            os.makedirs(result_image_path)    
        print(f"image_full_name: {image_full_name}  result_image_path: {result_image_path} ")
        # self.driver.save_screenshot(f"{result_image_path}/screenshot_{result_image_name}")
        image = element.find("div", class_="gdOPf q07dbf uhHOwf ez24Df").find("img").attrs["src"]
        if image:
            print("Image present", image[:20])
            if image[:5] == "https":

                img_data = requests.get(image).content
                with open(image_full_name, 'wb') as handler:
                    handler.write(img_data)
            else:
                image = image.encode('utf-8')
                image_body = image[image.find(b'/9'):]
                Image.open(BytesIO(base64.b64decode(image_body))).save(image_full_name)

    def search_images(self):
        print("Start search_images")
        result_list = []
        cnt = 1
        self._search_interaction()
        all_divs = self.soup.find_all('div', class_='vEWxFf RCxtQc my5z3d')
        print(f"len(els): {len(all_divs)}")
        for e in all_divs:
            result_dict = {}
            result_image_name =  f"result_image_{cnt}.jpg"
            result_image_path =  f"{self.result_image_path}/{self.SEARCH_ENGINE}"
            result_dict["uuid"] = self.uuid
            result_dict["search_engine"] = self.SEARCH_ENGINE
            result_dict["image_name"] = result_image_name
            result_dict["image_url"] = self._get_image_url(e)
            result_dict["image_text"] = self._get_image_text(e)
            result_dict["full_image_name"] = f"{result_image_path}/{result_image_name}"
            self._save_image(e,result_image_path,result_image_name)
            cnt += 1
            result_list.append(result_dict)
        
        return result_list


class YandexImageSearch(ImageSearchEngine):
    """Клас для пошуку через Yandex Images"""

    def search(self, image_path):
        # self.driver.get("https://yandex.com/images/")

        # upload_button = self.driver.find_element(By.XPATH, "//input[@type='file']")
        # upload_button.send_keys(os.path.abspath(image_path))

        # time.sleep(5)

        # return self.driver.current_url
        result_url = "https://bank.gov.ua/frontend/content/logo-en.png?v=12"
        return result_url

    def get_images(self):
        print("Images saved")


class BingImageSearch(ImageSearchEngine):
    """Клас для пошуку через Bing Images"""

    def search(self, image_path):
        # self.driver.get("https://www.bing.com/visualsearch")

        # upload_button = self.driver.find_element(By.XPATH, "//input[@type='file']")
        # upload_button.send_keys(os.path.abspath(image_path))

        # time.sleep(5)

        # return self.driver.current_url
        result_url = "https://bank.gov.ua/frontend/content/logo-en.png?v=12"
        return result_url

    def get_images(self):
        print("Images saved")


class TinEyeImageSearch(ImageSearchEngine):
    """Клас для пошуку через TinEye"""

    def search(self, image_path):
        # self.driver.get("https://tineye.com/")

        # upload_button = self.driver.find_element(By.XPATH, "//input[@type='file']")
        # upload_button.send_keys(os.path.abspath(image_path))

        # time.sleep(5)

        # return self.driver.current_url
        result_url = "https://bank.gov.ua/frontend/content/logo-en.png?v=12"
        return result_url

    def get_images(self):
        print("Images saved")


class SearchEngineFactory:
    """Factory class for choose search engine"""
    
    @staticmethod
    def get_search_engine(engine_name,uuid,original_image_path):
        search_engines = {
            "google": GoogleImageSearch,
            "yandex": YandexImageSearch,
            "bing": BingImageSearch,
            "tineye": TinEyeImageSearch
        }
        
        if engine_name in search_engines:
            return search_engines[engine_name](uuid, original_image_path)
        else:
            raise ValueError(f"Невідомий пошуковик: {engine_name}")
