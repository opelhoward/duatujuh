from scrapy.cmdline import execute

cmd = "scrapy crawl tokopedia -o scrapeddata/tokopedia.json"
# cmd = "scrapy crawl bukalapak -o scrapeddata/bukalapak2.json"
# cmd = "scrapy crawl olx -o scrapeddata/olx2.json"

execute(cmd.split())
