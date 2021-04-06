import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import WwestbankstrongItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class WwestbankstrongSpider(scrapy.Spider):
	name = 'westbankstrong'
	start_urls = ['https://www.westbankstrong.com/blog']

	def parse(self, response):
		post_links = response.xpath('//div[@class="blog-image"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@class="btn btn-primary"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//div[@class="blog-posted"]/p/text()').get().split()[1]
		title = response.xpath('//div[@class="blog-detail-text"]/text()').get()
		content = response.xpath('//div[@class="blog-detail-content"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=WwestbankstrongItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
