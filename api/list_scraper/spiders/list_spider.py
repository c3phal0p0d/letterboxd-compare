import scrapy
from scrapy.crawler import CrawlerProcess

class ListSpider(scrapy.Spider):
    name = "list_spider"

    def start_requests(self):
        yield scrapy.Request(
            url = self.url,
            callback = self.parse
        )

    def parse(self, response):
        movies_info = {}

        list_element = response.css("ul.poster-list")
        for movie_element in list_element:
            movies_info["ids"] = movie_element.css("li.poster-container div::attr('data-film-id')").getall()
            movies_info["titles"] = movie_element.css("li.poster-container div img::attr('alt')").getall()
            movies_info["urls"] = movie_element.css("li.poster-container div::attr('data-film-slug')").getall()

        movies = {}
        for i in range(len(movies_info["ids"])):
            movie = {}
            movie["id"] = movies_info["ids"][i]
            movie["title"] = movies_info["titles"][i]
            movie["url"] = "https://letterboxd.com" + movies_info["urls"][i]
            movies[movie["id"]] = movie

        yield movies

        next_page_url = response.css("a.next::attr('href')").get()
        if next_page_url:
            yield scrapy.Request(
                url = "https://letterboxd.com" + next_page_url,
                callback = self.parse
            )

