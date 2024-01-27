from pprint import pprint
import requests
from enum import Enum

# News categories by market
class Market(Enum):
    China = "zh-CN"

class ChinaCategory(Enum):
    Auto = "Auto"
    Business = "Business"
    China = "China"
    Education = "Education"
    Entertainment = "Entertainment"
    Military = "Military"
    RealEstate = "RealEstate"
    ScienceAndTechnology = "ScienceAndTechnology"
    Society = "Society"
    Sports = "Sports"
    World = "World"

class BingSearchAdapter:
    def __init__(self, bing_search_api:str, bing_search_key:str):
        self.endpoint = bing_search_api
        self.headers = {'Ocp-Apim-Subscription-Key': bing_search_key}

    def search_image(self, q:str, mkt:str=Market.China):
        response = requests.get(
            self.endpoint + "images/search",
            headers=self.headers,
            params={
                'q': q,
                'mkt': mkt
            })
        response.raise_for_status()
        return response.json()["value"]

    def news_category_trending(self, category:str, mkt:str=Market.China.value):
        params = {'category': category, 'mkt': mkt}
        response = requests.get(self.endpoint + "news", headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()["value"]

    def search(self, q:str):
        response = requests.get(self.endpoint + "search", headers=self.headers, params={
            "q": q
        })
        response.raise_for_status()
        return response.json()