from list_scraper.spiders.list_spider import ListSpider
from list_scraper.spiders.list_info_spider import ListInfoSpider
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from twisted.internet import reactor, defer

from flask import (
    Flask,
    redirect, 
    render_template,
    request,
    url_for
)

import json
import os

app = Flask(__name__)

@app.route("/", methods = ["POST", "GET"])
def index():
    if request.method == "POST":
        url_1 = request.form["list-1-url"]
        url_2 = request.form["list-2-url"]

        return redirect(url_for("index", url_1=url_1, url_2=url_2))
    else:
        url_1 = request.args.get("url_1", None)
        url_2 = request.args.get("url_2", None)
        if url_1 and url_2:
            scrape_lists(url_1, url_2)
            data = parse_lists()
            return render_template("index.html", data=data)
        else:
            return render_template("index.html")
    
def parse_lists():
    data = {}

    # read saved json data
    with open("list_1.json", "r") as f:
        list_1_data = json.load(f)[0]

    with open("list_1_info.json", "r") as f:
        list_1_info_data = json.load(f)[0]

    with open("list_2.json", "r") as f:
        list_2_data = json.load(f)[0]

    with open("list_2_info.json", "r") as f:
        list_2_info_data = json.load(f)[0]

    # find movies that appear on both lists
    shared_movies = list(set([list(list_1_data[i].values())[1] for i in list_1_data]).intersection(set([list(list_2_data[i].values())[1] for i in list_2_data])))
    print(shared_movies)
    
    # set variables
    data["combined"] = {
        "num_shared_movies": len(shared_movies),
        "shared_movies": shared_movies
    }

    data["list_1"] = {
        "name": list(list_1_info_data.values())[0],
        "creator": list(list_1_info_data.values())[1],
        "num_movies": len(list_1_data.keys()),
    }
    data["list_1"]["similarity_percentage"] = int(round((data["combined"]["num_shared_movies"]/data["list_1"]["num_movies"]*100), 0))
    print(data["list_1"])

    data["list_2"] = {
        "name": list(list_2_info_data.values())[0],
        "creator": list(list_2_info_data.values())[1],
        "num_movies": len(list_2_data.keys()),
    }
    data["list_2"]["similarity_percentage"] = int(round((data["combined"]["num_shared_movies"]/data["list_2"]["num_movies"]*100), 0))

    # delete json files that were created
    os.remove("list_1.json")
    os.remove("list_1_info.json")
    os.remove("list_2.json")
    os.remove("list_2_info.json")

    return data

def scrape_lists(url_1, url_2):
    configure_logging()

    # scrape first list & its info
    list_1_runner = CrawlerRunner(settings={
        "FEEDS": {
            "list_1.json": {"format":"json"},
        },
    })

    list_1_info_runner = CrawlerRunner(settings={
        "FEEDS": {
            "list_1_info.json": {"format":"json"},
        },
    })

    
    # scrape second list & its info
    list_2_process = CrawlerRunner(settings={
        "FEEDS": {
            "list_2.json": {"format":"json"},
        },
    })

    list_2_info_process = CrawlerRunner(settings={
        "FEEDS": {
            "list_2_info.json": {"format":"json"},
        },
    })
    
    @defer.inlineCallbacks
    def crawl():
        yield list_1_runner.crawl(ListSpider, url=url_1)
        yield list_1_info_runner.crawl(ListInfoSpider, url=url_1)
        yield list_2_process.crawl(ListSpider, url=url_2)
        yield list_2_info_process.crawl(ListInfoSpider, url=url_2)

        reactor.stop()

    crawl()
    reactor.run()
