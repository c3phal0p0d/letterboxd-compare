import scrapy

class ListInfoSpider(scrapy.Spider):
    name = "list_info_spider"

    def start_requests(self):
        yield scrapy.Request(
            url = self.url,
            callback = self.parse
        )

    def parse(self, response):
        list_info = {}

        list_info["name"] = response.css("div.list-title-intro h1.title-1::text").get()
        list_info["creator"] = response.css("a.name span[itemprop='name']::text").get()

        yield list_info