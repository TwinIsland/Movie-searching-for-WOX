# encoding:utf-8

from wox import Wox  # , WoxAPI
import requests
from lxml import etree
import webbrowser
import time
import json


class Main(Wox):

    # define a request function which use proxies provided in Wox setting
    def request(self, url):
        if self.proxy and self.proxy.get("enabled") and self.proxy.get("server"):
            proxies = {
                "http": "http://{}:{}".format(self.proxy.get("server"), self.proxy.get("port")),
                "https": "http://{}:{}".format(self.proxy.get("server"), self.proxy.get("port"))}
            return requests.get(url, proxies=proxies, timeout=5).content
        else:
            return requests.get(url, timeout=5).content

    # craw the website resources page with etree form return
    def getUrlTree(self, content):
        time.sleep(0.5)  # avoid ban by website
        url = 'http://ifkdy.com/index.php?p=1&q=' + content
        return etree.HTML(self.request(url))

    def query(self, key):

        # when no parameter provided
        if key == '':
            return [{
                "Title": 'Movie Searcher',
                "SubTitle": "input movie name to search",
                "IcoPath": 'IMAGE/icon.ico'
            }]
        else:

            results = []
            pageResource = self.getUrlTree(key)

            for movieCount in range(1, 20):
                xpAddr = '/html/body/div[2]/div[1]/ul/li[' + str(movieCount) + ']/a/span[1]/text()'
                xpDesc = '/html/body/div[2]/div[1]/ul/li[' + str(movieCount) + ']/a/span[2]/text()'
                xpUrl = '/html/body/div[2]/div[1]/ul/li[' + str(movieCount) + ']/a/@href'
                try:
                    results.append({
                        "Title": pageResource.xpath(xpAddr)[0] + pageResource.xpath(xpDesc)[0],
                        "SubTitle": pageResource.xpath(xpUrl)[0],
                        "IcoPath": 'IMAGE/find.png',
                        "JsonRPCAction": {
                            "method": "openUrl",  # open the resources link
                            "parameters": [pageResource.xpath(xpUrl)[0]],
                            "dontHideAfterAction": True
                        }
                    })
                except Exception as e:
                    if str(e) == 'list index out of range':
                        break
                    else:
                        with open('plugin.json', 'r') as f:
                            error_report_web = json.loads(f.read())['Website']
                        return [{
                            "Title": 'Program Error',
                            "SubTitle": 'program meet error when executed. Error Type: ' + str(e),
                            "IcoPath": 'IMAGE/error.png',
                            "JsonRPCAction": {
                                "method": "openUrl",  # open the resources link
                                "parameters": [error_report_web],
                                "dontHideAfterAction": True
                            }
                        }]

            if len(results) >= 1:
                results.insert(0,
                               {
                                   "Title": 'Movie Searcher',
                                   "SubTitle": 'Find "' + str(len(results)) + '" movies',
                                   "IcoPath": 'IMAGE/icon.ico'
                               })
                return results

            else:
                return [{
                    "Title": 'Nothing There',
                    "SubTitle": 'Sorry, we can\'t find the movie you want',
                    "IcoPath": 'IMAGE/error.png'
                }]

    def openUrl(self, url):
        webbrowser.open(url)
        # WoxAPI.change_query(url)


if __name__ == "__main__":
    Main()
