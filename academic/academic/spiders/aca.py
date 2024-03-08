import scrapy
from scrapy import Request, Selector
import json
import time
import re
from academic.HHToolkits_2_0 import JsonCleaner, Utils
from academic.items import AcademicItem

class AcaSpider(scrapy.Spider):
    name = 'aca'
    allowed_domains = ['sci-hub.ru']
    start_urls = ['https://sci-hub.wf/']

    def start_requests(self):
        with open('/tmp/systemd-private-a1d2cd73bc2c4e679895a335271fa990-chronyd.service-NfubUX/tmp/hh/academic/limit10.txt', 'r') as file:
            lines = file.readlines()
        for line in lines:
            line = line.replace('\n', '')
            yield Request(
                url=self.start_urls[0] + line,
                cb_kwargs={
                    'source_url': self.start_urls[0] + line
                }
            )

    def parse(self, response, **kwargs):
        sel = Selector(response)
        d_url = sel.xpath('//div[@id="buttons"]/ul/li/a/@onclick')
        if d_url:
            d_url = d_url.extract_first().replace('location.href=', '')
        else:
            ''
        create_time = Utils.generate_date()
        website_name = 'Sci-hub'
        content = sel.xpath('//div[@id="citation"]/text()')
        release_time = ''
        title = sel.xpath('//div[@id="citation"]/i/text()')
        if title:
            title = title.extract_first().strip()
        else:
            title = ''
        if content:
            content = (content.extract_first() + title).strip()
            rt = re.search(r'\(\d{4}\)', content)
            release_time = rt.group()[1:-1] if rt else ''
        else:
            content = ''

        

        ac = AcademicItem()
        ac['unique_key'] = Utils.sha256_encrypt(kwargs.get('source_url'))
        ac['website_name'] = website_name
        ac['sourse_url'] = kwargs.get('source_url')
        ac['download_url'] = d_url
        ac['create_time'] = create_time
        ac['release_time'] = release_time
        ac['title'] = title
        ac['content'] = content
        yield ac
