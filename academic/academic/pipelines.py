# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import codecs
import os
import json


class AcademicPipeline:
    def __init__(self):
        self.json_file = codecs.open('/tmp/systemd-private-a1d2cd73bc2c4e679895a335271fa990-chronyd.service-NfubUX/tmp/hh/academic/academic/data/data.json', 'w+', encoding='utf8')

    def open_spider(self, spider):
        self.json_file.write('[\n')

    def process_item(self, item, spider):
        item_json = json.dumps(dict(item), ensure_ascii=False)
        self.json_file.write(item_json + ',\n')
        return item

    def close_spider(self, spider):
        # 在结束后，需要对 process_item 最后一次执行输出的 “逗号” 去除
        # 当前文件指针处于文件尾，我们需要首先使用 SEEK 方法，定位到文件尾前的两个字符（一个','(逗号), 一个'\n'(换行符)）的位置
        self.json_file.seek(-2, os.SEEK_END)
        # 使用 truncate() 方法，将后面的数据清空
        self.json_file.truncate()
        # 重新输出'\n'，并输出']'，与 open_spider(self, spider) 时输出的 '[' 相对应，构成一个完整的数组格式
        self.json_file.write('\n]')
        # 关闭文件
        self.json_file.close()
