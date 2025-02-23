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
import json
from loguru import logger


class ImageSearchEngine(ABC):
    """Abstract class for image search"""

    WAIT_AFTER_CLICK_SEC = 2
    WAIT_AFTER_LOAD_SEC = 4
    SEARCH_ENGINE = ""

    def __init__(self, uuid, original_image_path):
        chrome_options = Options()
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument("--headless=new")         
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_window_size(1920, 1080)
        self.original_image_path = original_image_path
        self.result_image_path = original_image_path[: original_image_path.rfind("/")]
        self.uuid = uuid
        logger.debug(f"Class for {self.SEARCH_ENGINE} initialized")

    def __del__(self):
        # destroing driver
        logger.debug(f"Class for {self.SEARCH_ENGINE} destroyed")
        self.driver.quit()

    @abstractmethod
    def search_images(self):
        """abstract method for search images"""
        pass

class GoogleImageSearch(ImageSearchEngine):
    """Class for search via Google Images"""

    SEARCH_ENGINE = "google"

    def _search_interaction(self):
        logger.debug("Start _search")
        self.driver.get("https://images.google.com/")
        search_button = self.driver.find_element(By.CLASS_NAME, "Gdd5U")
        search_button.click()
        time.sleep(self.WAIT_AFTER_CLICK_SEC)

        upload_input = self.driver.find_element(By.NAME, "encoded_image")
        upload_input.send_keys(os.path.abspath(self.original_image_path))

        time.sleep(self.WAIT_AFTER_LOAD_SEC)
        self.soup = BeautifulSoup(self.driver.page_source, "html.parser")
        self.driver.quit()

    def _get_image_text(self, element):
        image_text = element.find("span", class_="Yt787")
        return image_text.text

    def _get_image_url(self, element):
        image_url = element.find("a", class_="LBcIee")
        return image_url.attrs["href"]

    def _save_image(self, element, result_image_path, result_image_name):
        logger.debug(f"Start _save_image ({self.SEARCH_ENGINE})")
        image_full_name = f"{result_image_path}/{result_image_name}"
        if not os.path.exists(result_image_path):
            os.makedirs(result_image_path)
        logger.debug(
            f"image_full_name: {image_full_name} result_image_path: {result_image_path} "
        )
        # self.driver.save_screenshot(f"{result_image_path}/screenshot_{result_image_name}")
        image = (
            element.find("div", class_="gdOPf q07dbf uhHOwf ez24Df")
            .find("img")
            .attrs["src"]
        )
        if image:
            logger.debug(f"Image present: {image[:20]}")
            if image[:5] == "https":
                img_data = requests.get(image).content
                with open(image_full_name, "wb") as handler:
                    handler.write(img_data)
            else:
                image = image.encode("utf-8")
                image_body = image[image.find(b"/9") :]
                Image.open(BytesIO(base64.b64decode(image_body))).save(image_full_name)
        logger.debug(f"Complete _save_image ({self.SEARCH_ENGINE})")

    def search_images(self):
        logger.debug(f"Start search_images ({self.SEARCH_ENGINE})")
        result_list = []
        cnt = 1
        self._search_interaction()
        try:
            all_divs = self.soup.find_all("div", class_="vEWxFf RCxtQc my5z3d")
            logger.debug(f"len(els): {len(all_divs)}")
            for e in all_divs:
                result_dict = {}
                result_image_name = f"result_image_{cnt}.jpg"
                result_image_path = f"{self.result_image_path}/{self.SEARCH_ENGINE}"
                result_dict["uuid"] = self.uuid
                result_dict["search_engine"] = self.SEARCH_ENGINE
                result_dict["image_name"] = result_image_name
                result_dict["image_url"] = self._get_image_url(e)
                result_dict["image_text"] = self._get_image_text(e)
                result_dict["full_image_name"] = f"{result_image_path}/{result_image_name}"
                self._save_image(e, result_image_path, result_image_name)
                cnt += 1
                result_list.append(result_dict)
        except Exception as e:
            logger.warning(f"Error in search_images ({self.SEARCH_ENGINE}):  {e}")

        logger.debug(f"End search_images ({self.SEARCH_ENGINE})")
        return result_list

class BingImageSearch(ImageSearchEngine):
    """Class for search via Bing Images"""

    SEARCH_ENGINE = "bing"

    def _search_interaction(self):
        self.driver.get("https://www.bing.com/visualsearch")

        upload_button = self.driver.find_element(By.XPATH, "//input[@type='file']")
        upload_button.send_keys(os.path.abspath(self.original_image_path))

        time.sleep(self.WAIT_AFTER_LOAD_SEC)

        self.soup = BeautifulSoup(self.driver.page_source, "html.parser")
        self.driver.quit()

    def _get_image_text(self, element):
        image_text = element.find("div", class_="captionContainer").find("span", class_="tit")
        return image_text.text

    def _get_image_url(self, element):
        image_url = element.find("a", class_="richImgLnk")
        return json.loads(image_url.attrs["data-m"])["purl"]

    def _save_image(self, element, result_image_path, result_image_name):
        logger.debug(f"Start _save_image ({self.SEARCH_ENGINE})")
        image_full_name = f"{result_image_path}/{result_image_name}"
        if not os.path.exists(result_image_path):
            os.makedirs(result_image_path)
        logger.debug(
            f"image_full_name: {image_full_name} result_image_path: {result_image_path} "
        )
        image = element.find("img").attrs["src"]
        img_data = requests.get(image).content
        with open(image_full_name, "wb") as handler:
            handler.write(img_data)
        
        logger.debug(f"Complete _save_image ({self.SEARCH_ENGINE})")

    def search_images(self):
        logger.debug(f"Start search_images ({self.SEARCH_ENGINE})")
        result_list = []
        self._search_interaction()
        try: 
            image_block = self.soup.find("div", id="i_results")
            blocks = image_block.find_all("div", class_="richImage relImg")
            logger.debug(f"count: {len(blocks)}")
            cnt = 1
            for e in blocks:
                result_dict = {}
                result_image_name = f"result_image_{cnt}.jpg"
                result_image_path = f"{self.result_image_path}/{self.SEARCH_ENGINE}"
                result_dict["uuid"] = self.uuid
                result_dict["search_engine"] = self.SEARCH_ENGINE
                result_dict["image_name"] = result_image_name
                result_dict["image_url"] = self._get_image_url(e)
                result_dict["image_text"] = self._get_image_text(e)
                result_dict["full_image_name"] = f"{result_image_path}/{result_image_name}"
                self._save_image(e, result_image_path, result_image_name)
                cnt += 1
                result_list.append(result_dict)
        except Exception as e:
            logger.warning(f"Error in search_images ({self.SEARCH_ENGINE}):  {e}")

        logger.debug(f"End search_images ({self.SEARCH_ENGINE})")
        return result_list

class YandexImageSearch(ImageSearchEngine):
    """Class for search via Yandex Images"""

    SEARCH_ENGINE = "yandex"

    def _search_interaction(self):
        self.driver.get("https://yandex.com/images/")

        upload_button = self.driver.find_element(By.XPATH, "//input[@type='file']")
        upload_button.send_keys(os.path.abspath(self.original_image_path))

        time.sleep(self.WAIT_AFTER_LOAD_SEC)

        self.soup = BeautifulSoup(self.driver.page_source, "html.parser")
        self.driver.quit()

    def _get_image_text(self, element):
        ...
        
    def _get_image_url(self, element):
        ...

    def _save_image(self, element, result_image_path, result_image_name):
        ...

    def search_images(self):
        ...

class TinEyeImageSearch(ImageSearchEngine):
    """Class for search via TinEye"""

    SEARCH_ENGINE = "tineye"

    def _search_interaction(self):
        logger.debug(f"Start _search_interaction ({self.SEARCH_ENGINE})")
        self.driver.get("https://tineye.com/")
        time.sleep(self.WAIT_AFTER_CLICK_SEC)
        # self.driver.save_screenshot(f'{self.SEARCH_ENGINE}_1.png')

        upload_button= self.driver.find_element(By.ID, "upload-box")
        upload_button.send_keys(os.path.abspath(self.original_image_path))

        time.sleep(self.WAIT_AFTER_LOAD_SEC)
        # self.driver.save_screenshot(f'{self.SEARCH_ENGINE}_2.png')
        # with open(f"content_{self.SEARCH_ENGINE}.html","w") as f:
        #     f.writelines(self.driver.page_source)

        self.soup = BeautifulSoup(self.driver.page_source, "html.parser")
        self.driver.quit()
        logger.debug(f"End _search_interaction ({self.SEARCH_ENGINE})")

    def _get_image_text(self, element):
        image_url = element.find("a")
        return image_url.text
    
    def _get_image_url(self, element):
        image_url = element.find("a")
        return image_url.attrs["href"]

    def _save_image(self, element, result_image_path, result_image_name):
        logger.debug(f"Start _save_image ({self.SEARCH_ENGINE})")
        image_full_name = f"{result_image_path}/{result_image_name}"
        if not os.path.exists(result_image_path):
            os.makedirs(result_image_path)
        logger.debug(
            f"image_full_name: {image_full_name} result_image_path: {result_image_path} "
        )        
        image = element.find("img").attrs["src"]
        # image = image.replace("?size=160", "size=640")
        img_data = requests.get(image).content
        with open(image_full_name, "wb") as handler:
            handler.write(img_data)        
        logger.debug(f"Complete _save_image ({self.SEARCH_ENGINE})")

    def search_images(self):
        logger.debug(f"Start search_images ({self.SEARCH_ENGINE})")
        result_list = []
        self._search_interaction()
        try:
            block = self.soup.find("div", class_="basis-full")
            blocks = block.select("div[class*='flex items-start gap-8']")
            logger.debug(f"count: {len(blocks)}")
            cnt = 1
            for e in blocks:
                result_dict = {}
                result_image_name = f"result_image_{cnt}.jpg"
                result_image_path = f"{self.result_image_path}/{self.SEARCH_ENGINE}"
                result_dict["uuid"] = self.uuid
                result_dict["search_engine"] = self.SEARCH_ENGINE
                result_dict["image_name"] = result_image_name
                result_dict["image_url"] = self._get_image_url(e)
                result_dict["image_text"] = self._get_image_text(e)
                result_dict["full_image_name"] = f"{result_image_path}/{result_image_name}"
                self._save_image(e, result_image_path, result_image_name)
                cnt += 1
                result_list.append(result_dict)
        except Exception as e:
            logger.warning(f"Error in search_images ({self.SEARCH_ENGINE}):  {e}")

        logger.debug(f"End search_images ({self.SEARCH_ENGINE})")
        return result_list


class SearchEngineFactory:
    """Factory class for choose search engine"""

    @staticmethod
    def get_search_engine(engine_name, uuid, original_image_path):
        search_engines = {
            "google": GoogleImageSearch,
            "yandex": YandexImageSearch,
            "bing": BingImageSearch,
            "tineye": TinEyeImageSearch,
        }

        if engine_name in search_engines:
            return search_engines[engine_name](uuid, original_image_path)
        else:
            raise ValueError(f"Unknow search engine: {engine_name}")
