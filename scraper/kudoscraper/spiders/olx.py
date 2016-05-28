from scrapy import Request
from scrapy.selector import Selector
from scrapy.spiders import Spider

from kudoscraper.items import ProductItem


class OlxSpider(Spider):
    name = "olx"
    allowed_domains = ["olx.co.id"]
    start_urls = [
        "http://olx.co.id/"
    ]

    def parse(self, response):
        sel = Selector(response)
        main_categories = sel.xpath('//a[@class="tdnone"]')
        for main_category in main_categories:
            url = main_category.xpath('@href').extract_first()
            category = main_category.xpath('span/text()').extract_first()
            yield Request(url, meta={
                'category': category
            },
                          callback=self.get_detail_category)

    def get_detail_category(self, response):
        sel = Selector(response)
        detail_categories = sel.xpath(
            '//ul[@style=""]//a[contains(@class, "link-relatedcategory")]'
        )
        for detail_category in detail_categories:
            url = detail_category.xpath('@href').extract_first()
            subcategory = detail_category.xpath('span/text()').extract_first()
            yield Request(url, meta={
                'category': response.meta['category'],
                'subcategory': subcategory
            },
                          callback=self.get_num_pages_category)

    def get_num_pages_category(self, response):
        sel = Selector(response)
        num_pages = sel.xpath(
            '//div[@class="pager rel clr"]/span[@class="item fleft" and position() = (last()-1)]//span/text()').extract_first()
        query_page_format = '?page=%d'
        for page_num in xrange(2, int(num_pages)):
            yield Request(response.url + (query_page_format % page_num), meta={
                'category': response.meta['category'],
                'subcategory': response.meta['subcategory']
            },
                          callback=self.get_products)
        yield self.get_products(response)

    def get_products(self, response):
        sel = Selector(response)
        details_link = sel.xpath('//a[contains(@class, "detailsLink")]/@href').extract()
        for detail_link in details_link:
            yield Request(detail_link, meta={
                'category': response.meta['category'],
                'subcategory': response.meta['subcategory']
            },
                          callback=self.get_product)

    def get_product(self, response):
        sel = Selector(response)
        title = sel.xpath('//h1[contains(@class, "brkword")]/text()').extract_first()
        price = sel.xpath('//div[contains(@class, "pricelabel")]/strong/text()').extract_first()
        image_link = sel.xpath('//meta[@property="og:image"]/@content').extract_first()
        desc = sel.xpath('//div[@id="textContent"]/p').extract_first()
        url = response.url
        item = ProductItem()
        item['category'] = response.meta['category']
        item['subcategory'] = response.meta['subcategory']
        item['product_name'] = title
        item['price'] = price
        item['description'] = desc
        item['image_link'] = image_link
        item['product_url'] = url
        yield item
