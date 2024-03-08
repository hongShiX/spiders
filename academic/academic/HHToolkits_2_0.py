import json
import os
import re
import hashlib
import secrets
import string
from pathlib import Path
from datetime import datetime
import requests
import io

# JSON用法封装
class JsonCleaner:
    def __init__(self) -> None:
        # json列表，清洗过后的数据会放到此处，也可以通过文件导入
        self.json_lst = []
        
        # 原始文件夹路径
        self.init_dir = ''
        
        # 原始文件路径
        self.init_file = ''
        
        # 目标文件路径
        self.target_file = ''
        
        
    def __init__(self, init_file='', target_file='', init_dir='', json_lst=[], encoding='utf-8') -> None:
        self.json_lst = json_lst
        self.init_dir = init_dir
        self.init_file = init_file
        self.target_file = target_file
        self.encoding = encoding

    # 将json_lst中的数据写入到文件中
    def to_jsonfile(self, outer_file: str=None):
        if self.target_file != '':
            with open(self.target_file, 'w', encoding=self.encoding) as file:
                json.dump(self.json_lst, file, ensure_ascii=False)
                print(f'写入到路径：{os.path.abspath(file.name)}')
                print(f'一共 {self.json_len()} 条')
        elif outer_file != '':
            with open(outer_file, 'w', encoding=self.encoding) as file:
                json.dump(self.json_lst, file, ensure_ascii=False)
                print(f'写入到路径：{os.path.abspath(file.name)}')
                print(f'一共 {self.json_len()} 条')
        else:
            raise Exception('请至少传入一个目标文件路径：该类的实例属性 *target_file* 或者自行指定一个路径 *outer_file*')

    # 向已存在的json文件中追加json，不覆盖之前的内容（未测试）
    def add_to_jsonfile(self, outer_file: str=None):
        if self.target_file != '':
            mode = 'a' if os.path.exists(self.target_file) else 'w'
            with open(self.target_file, mode, encoding=self.encoding) as file:
                json.dump(self.json_lst, file, ensure_ascii=False)
                print(f'写入到路径：{os.path.abspath(file.name)}')
                print(f'一共 {self.json_len()} 条(条数不准确)')
        elif outer_file != '':
            mode = 'a' if os.path.exists(outer_file) else 'w'
            with open(outer_file, mode, encoding=self.encoding) as file:
                json.dump(self.json_lst, file, ensure_ascii=False)
                print(f'写入到路径：{os.path.abspath(file.name)}')
                print(f'一共 {self.json_len()} 条(条数不准确)')
        else:
            raise Exception('请至少传入一个目标文件路径：该类的实例属性 *target_file* 或者自行指定一个路径 *outer_file*')
    """
        查看json数据前n条
        
        parameters:
            n(int): 
                json数据前n条
            replace(bool): 
                为True的话会直接将得到的结果覆盖掉原来的json_lst, 为False则不做任何操作
                默认为False
        
        returns:
            list: 返回此对象的json_lst属性
    """
    def find_json(self, n: int, replace=False) -> list:
        if replace:
            self.json_lst = self.json_lst[:n]
        return self.json_lst[:n]

    
    """     
        当json中某个字段的值含有某个关键字时，就删除 
    """
    def delete_by_keywords(self, field: str, word):
        if type(word) == str:
            self.json_lst = [d for d in self.json_lst if word not in d.get(field)]
        if type(word) == list:
            self.json_lst = [d for d in self.json_lst if all(w not in d.get(field) for w in word)]
        return self

    """     
        当json中某个字段的值含有某个关键字时，就保留 
    """
    def remain_by_keywords(self, field: str, word):
        if type(word) == str:
            self.json_lst = [d for d in self.json_lst if word in d.get(field)]
        if type(word) == list:
            self.json_lst = [d for d in self.json_lst if all(w in d.get(field) for w in word)]
        return self

    """
        根据一定的规则，删除json_lst中的数据，符合规则的则删除
        
        parameters:
            rule(dict): 
                key为json中的key，
                value为与之匹配的正则表达式，value也可以为多个正则表达式构成的数组
        returns:
            list: json_lst
    """

    def remain_by_rule(self, rule: dict):
        # 将规则中的值转换为列表形式
        regex_dict = {key: value if isinstance(value, list) else [value] for key, value in rule.items()}
        
        # 根据规则筛选字典
        self.json_lst = [d for d in self.json_lst if all(any(re.search(regex, str(d.get(key))) for regex in regex_list) for key, regex_list in regex_dict.items())]
        return self

    """
        根据一定的规则，删除json_lst中的数据，符合规则的则删除
        
        parameters:
            rule(dict): 
                key为json中的key，
                value为与之匹配的正则表达式，value也可以为多个正则表达式构成的数组
        
        returns:
            list: json_lst
    """
    def delete_by_rule(self, rule: dict):
        temp = []
        for data in self.json_lst:
            if rule == None or rule == {}:
                return
            else:
                flag = True
                for key, regex in rule.items():
                    if type(regex) == list:
                        iter = list(map(lambda r : self._re_match(data[key], r), regex))
                        if False in iter:
                            flag = False
                            break
                    elif type(regex) == str:
                        flag = self._re_match(data[key], regex)
                        if flag == False:
                            break
                    else:
                        raise TypeError('rule字典值的必须是 字符串 或者 正则表达式列表')
                if not flag:
                    temp.append(data)
        self.json_lst = temp
        return self
        
    """ 
        替换json中某个字段的值(按正则表达式)
    """
    def replace_field_by_re(self, field, replaced_val, regex):
        for j in self.json_lst:
            j[field] = re.sub(regex, replaced_val, j[field])
        return self
    
    """
        直接修改json字段的值
    """
    def modify_field(self, field, replaced_val):
        for j in self.json_lst:
            j[field] = replaced_val
        return self
        
    
    """
        将文件中的json导入到json_lst中
        
        parameters:
            path(str): 
                文件路径，可以是文件夹或json文件，注意：不以json结尾的会被认定为文件夹
                
        returns:
            list: json_lst
    """
    def to_json_lst(self, path: str=''):
        if path not in ('', None):
            pass
        elif self.init_dir not in ('', None):
            path = self.init_dir
        elif self.init_file not in ('', None):
            path = self.init_file
        
        self.json_lst.clear()
        if path.endswith('.json'):
            with open(path, 'r', encoding=self.encoding) as file:
                json_data = json.load(file, strict=False)
                for j in json_data:
                    self.json_lst.append(j)
        else:
            for filename in os.listdir(self.init_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.init_dir, filename)
                    with open(file_path, 'r', encoding=self.encoding) as file:
                        # 遍历所有json
                        json_data = json.load(file, strict=False)
                        for j in json_data:
                            self.json_lst.append(j)
        return self
    
    """
        根据某些字段的值进行去重，
        如果多个json之间，指定的字段的值相等，那么就认定这几个json是重复的，只会保留一个
        
        parameters:
            fields(list[str]): 
                里面存放字段值，用于去重的对比
            replace(bool): 
                True表示得到的结果重新赋值给json_lst，False表示不改变json_lst，默认为False
            
        returns:
            list: 
                去重之后的json列表
        
    """
    def drop_duplicate(self, fields: list, replace: bool=False) -> list:
        unique_items = []
        unique_values = set()
        fields = list(fields)
        for item in self.json_lst:
            # 生成唯一标识符，用于判断是否重复
            identifier = tuple(item[field] for field in fields)
            
            if identifier not in unique_values:
                unique_items.append(item)
                unique_values.add(identifier)
        
        if replace:
            self.json_lst = unique_items

        return unique_items
    
    # 返回每个json指定字段的值，返回一个新的json列表
    def field_value(self, field):
        return [j[field] for j in self.json_lst]
    
    
    """ 
        返回每个json多个字段的值，返回一个字典组成的列表 
        
        parameters:
            fields(list): 字段名组成的列表
        
        returns:
            list: 返回一个由字段名和字段值配对的字典组成的列表    
    """
    def fields_value(self, fields: list):
        result = []
        for f in fields:
            d = {}
            for j in self.json_lst:
                d[f] = j[f]
            result.append(d)
        return result


    
    # 返回json_lst长度
    def json_len(self) -> int:
        return len(self.json_lst)
    
    
    # 进行正则匹配
    def _re_match(self, value, regex, is_not=False):
        flag = True
        if (re.search(regex, value) == None) != is_not:
                flag = False
        return flag
    
    # 判断初始文件夹是否为空
    def _is_file_empty(self):
        return self.init_dir not in ('', None) and self.init_file not in ('', None)
    
                    
                    

# 工具类 
class Utils:  
    """ 
        截取json文件中的json（未测试）
    """
    @staticmethod
    def intercept_json(file_path: str, target_path: str, n: int, encoding: str='utf-8') -> None:
        res = []
        if file_path.endswith('.json'):
            with open(file_path, 'r', encoding=encoding) as file:
                json_data = json.load(file)
                for i in range(n):
                    res.append(json_data[i])
            with open(target_path, 'w', encoding=encoding) as file:
                json.dump(res, file, ensure_ascii=False)
        else:
            raise Exception('文件要以".json"结尾')
        
    """
        将json文件分割成多份
        
        params:
            init_file(str): 
                json文件的路径，注意要带.json
            target_dir(str): 
                分割之后的文件放入的文件夹路径
            n(int): 
                以多少个长度的json为一个文件
            encoding(str): 
                文件的编码，默认为utf-8
    """ 
    @staticmethod
    def split_jsonfile(init_file, target_dir, n, encoding='utf-8'):
        init_filename = ''
        with open(init_file, 'r', encoding=encoding) as file:
            init_filename = Path(file.name).stem
            json_data = json.load(file)
            file_num = 1
            temp = []
            for i in range(0, len(json_data), n):
                temp.append(json_data[i:i + n])
            for t in temp:
                with open(f'{target_dir}/{init_filename}_{file_num}.json', 'w', encoding=encoding) as file:
                    json.dump(t, file, ensure_ascii=False)
                    file_num += 1


    # 给定一个字符串，生成sha256的十六进制串
    @staticmethod
    def sha256_encrypt(message):
        sha256_hash = hashlib.sha256()
        sha256_hash.update(message.encode('utf-8'))
        encrypted_message = sha256_hash.hexdigest()
        return encrypted_message
    
    
    # 传入日期format格式，返回当前日期，模式默认为'%Y-%m-%d %H:%M:%S'
    @staticmethod
    def generate_date(pattern='%Y-%m-%d %H:%M:%S'):
        now = datetime.now()
        return now.strftime(pattern)
    
    # 生成一个sha256加密串，直接调用方法即可，不需要再额外传入字符串，注意：有可能会导致重复
    @staticmethod
    def generate_sha256_hash():
        characters = string.ascii_letters + string.digits
        random_string = ''.join(secrets.choice(characters) for _ in range(20))
        sha256_hash = hashlib.sha256(random_string.encode()).hexdigest()
        return sha256_hash

    # 生成一个长度为n的随机字符串
    def ran_string(n):
        characters = string.ascii_letters + string.digits
        random_string = ''.join(secrets.choice(characters) for _ in range(n))
    
    """
        下载pdf
        
        parameters:
            save_path(str): 
                保存路径，末尾要加/
            pdf_name(str):
                保存的pdf文件名，不需要加后缀 
            pdf_url(str):
                pdf下载地址
    """
    @staticmethod
    def download_pdf(save_path,pdf_name,pdf_url):
        send_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
            "Connection": "keep-alive",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8"
        }
        response = requests.get(pdf_url, headers=send_headers)
        bytes_io = io.BytesIO(response.content)
        with open(save_path + "%s.pdf" % pdf_name, mode='wb') as f:
            f.write(bytes_io.getvalue())
            print('%s.pdf,下载成功！' % (pdf_name))
            
    # 返回文件的行数
    @staticmethod
    def count_lines(filename):
        with open(filename, 'r') as file:
            line_count = sum(1 for _ in file)
        return line_count
    
    # 判断文件夹是否存在
    @staticmethod
    def is_dir_exist(dir_path):
        if os.path.exists(dir_path):
            return True
        else:
            return False

    # 创建文件夹
    @staticmethod
    def create_dir(dir_path):
        if not Utils.is_dir_exist(dir_path):
            os.makedirs(dir_path)
