from scrapy.cmdline import execute

cmd = "scrapy crawl tokopedia -o scrapeddata/tokopedia.json"
# cmd = "scrapy crawl bukalapak -o scrapeddata/bukalapak.json"
# cmd = "scrapy crawl olx -o scrapeddata/olx.json"

execute(cmd.split())
