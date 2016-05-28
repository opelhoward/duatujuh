import urlparse

from scrapy import Request
from scrapy.selector import Selector
from scrapy.spiders import Spider

from kudoscraper.items import ProductItem


class TokopediaSpider(Spider):
    name = "bukalapak"
    allowed_domains = ["bukalapak.com"]
    start_urls = [
        "https://www.bukalapak.com/products"
    ]

    def parse(self, response):
        sel = Selector(response)
        categories_li = sel.xpath(
            '//li[contains(@class, "tree-item") and (not (contains(@class, "tree-item--has-children")))]')
        for category_li in categories_li:
            title = category_li.xpath('a/text()').extract()
            href = category_li.xpath('a/@href').extract()
            abs_url = urlparse.urljoin(response.url, href[0])
            yield Request(abs_url, callback=self.get_pages_of_category)

    def get_pages_of_category(self, response):
        sel = Selector(response)
        number_of_page_span = sel.xpath('//span[@class="last-page"]/text()').extract()
        number_of_page = int(number_of_page_span[0])
        query_page_format = "?page=%d"
        for page_num in xrange(number_of_page):
            url = response.url + (query_page_format % page_num)
            yield Request(url, callback=self.get_products)

    def get_products(self, response):
        sel = Selector(response)
        products = sel.xpath('//article[@class="product-display"]')
        for product in products:
            href = product.xpath('@data-url').extract()[0]
            url = urlparse.urljoin(response.url, href)
            yield Request(url, callback=self.get_product)

    def get_product(self, response):
        sel = Selector(response)
        product_detail = sel.xpath('//div[contains(@class, "product-detailed")]')
        product_id = product_detail.xpath('@data-id').extract_first()
        image_link = sel.xpath('//li[@class="product-image-gallery-image"]/a/img[@class="hidden"]/@src').extract_first()
        title = sel.xpath('(//nav[@id="breadcrumb"]/ol/li/span)[last()]/text()').extract_first()
        price = sel.xpath('//span[@class="amount positive"]/text()').extract_first()
        desc = sel.xpath('//div[@id="product_desc_%s"]/div/p' % product_id).extract_first()
        url = response.url
        categories = sel.xpath('//nav[@id="breadcrumb"]/ol/li/a[not(@href="/")]')
        category = categories.xpath('text()').extract_first()
        subcategory = categories.xpath(
            '(//nav[@id="breadcrumb"]/ol/li/a[not(@href="/")])[last()]/text()').extract_first()
        item = ProductItem()
        item['category'] = category
        item['subcategory'] = subcategory
        item['product_name'] = title
        item['price'] = price
        item['description'] = desc
        item['image_link'] = image_link
        item['product_url'] = url
        yield item
