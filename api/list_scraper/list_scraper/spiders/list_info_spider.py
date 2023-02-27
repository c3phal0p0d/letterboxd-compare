import scrapy

class ListInfoSpider(scrapy.Spider):
    name = "list_info_spider"

    start_urls = [
        "https://letterboxd.com/dave/list/official-top-250-narrative-feature-films/"
    ]

    def parse(self, response):
        list_info = {}

        list_info["name"] = response.css("a.name span[itemprop='name']::text").get()
        list_info["creator"] = response.css("div.list-title-intro h1.title-1::text").get()

        yield list_info