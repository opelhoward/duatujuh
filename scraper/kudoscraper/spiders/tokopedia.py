import json
import math

from scrapy import Request
from scrapy.selector import Selector
from scrapy.spiders import Spider

from scraper.kudoscraper.items import ProductItem


class TokopediaSpider(Spider):
    name = "tokopedia"
    allowed_domains = ["tokopedia.com"]
    start_urls = [
        "https://www.tokopedia.com/"
    ]
    meta_splash = {
        'args': {
            'wait': 0.1,
            'http_method': 'GET'
        },
        'endpoint': 'render.html'
    }

    def parse(self, response):
        sel = Selector(response)
        categories_li = sel.xpath('//ul[@class="allcat"]//li')
        for (index, category_li) in enumerate(categories_li):
            category_href = category_li.xpath('a/@href').extract_first()
            category_title = category_li.xpath('a/span/text()').extract_first()
            yield Request(category_href, callback=self.get_data, meta={
                'category': category_title
            })

    url_format = "https://ace.tokopedia.com/search/v1/product?rows=24&ob=23&sc=%d&start=%d"

    def get_data(self, response):
        sel = Selector(response)
        scripts = sel.xpath('//script')
        m_index = 2
        if len(scripts) is 17:
            m_index += 2
        for (index, script) in enumerate(scripts):
            if index is m_index:
                script_text = script.xpath('text()').extract_first()
                script_text_by_line = script_text.split('\n')
                id = int(script_text_by_line[4].split(' ')[-1][0:-1])
                yield Request(self.url_format % (id, 0), callback=self.get_pages_of_items, meta={
                    'category': response.meta['category'],
                    'id': id
                })

    def get_pages_of_items(self, response):
        response_json = json.loads(response.body_as_unicode())
        for page_idx in xrange(1, int(math.ceil(response_json['header']['total_data'] / float(24)))):
            url = self.url_format % (response.meta['id'], (page_idx - 1) * 24)
            yield Request(url, callback=self.get_products, meta={
                'category': response.meta['category']
            }, dont_filter=True)

    def get_products(self, response):
        response_json = json.loads(response.body_as_unicode())
        data = response_json['data']
        for prod in data:
            yield Request(prod['uri'], callback=self.get_product, meta={
                'category': response.meta['category']
            })

    def get_product(self, response):
        sel = Selector(response)

        title = sel.xpath('//h1[contains(@class, "product-title")]/a/text()').extract_first()
        price_tag_container = sel.xpath('//div[contains(@class, "product-pricetag")]')
        price = price_tag_container.xpath('span/text()').extract_first()
        image_link = sel.xpath('//div[@class="product-imagebig"]/a/@href').extract_first()
        desc = sel.xpath('//p[@itemprop="description"]').extract_first()
        url = response.url
        subcategory = sel.xpath('(//ul[@itemprop="breadcrumb"]/li/h2/a)[last()]/text()').extract_first()

        item = ProductItem()
        item['category'] = response.meta['category']
        item['subcategory'] = subcategory
        item['product_name'] = title
        item['price'] = price
        item['description'] = desc
        item['image_link'] = image_link
        item['product_url'] = url
        yield item
