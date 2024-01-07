from pprint import pprint
import requests

# News categories by market
class Market:
    China = "zh-CN"

class ChinaCategory:
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

    def searchImage(self, q:str, mkt:str=Market.China):
        response = requests.get(
            self.endpoint + "images/search",
            headers=self.headers,
            params={
                'q': q,
                'mkt': mkt
            })
        response.raise_for_status()
        return response.json()["value"]

    def newsCategoryTrending(self, category:str, mkt:str=Market.China):
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