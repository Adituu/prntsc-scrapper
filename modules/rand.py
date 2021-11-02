import random

import tinydb
import tinydb_smartcache


class Rand():
    def __init__(self):
        tinydb.TinyDB.table_class = tinydb_smartcache.SmartCacheTable
        self.db = tinydb.TinyDB('./database/db.json')

    def generate_filename(self, charset='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
        def random_string(): return ''.join(
            random.sample(charset, (random.randint(6, 7))))

        gen_strings_table = self.db.table('generated_strings')
        gen_strings = [list(dct.values())[0]
                       for dct in gen_strings_table.all()]

        while (secure_name := random_string()) in gen_strings:
            secure_name = random_string()
        else:
            gen_strings_table.insert({'string': secure_name})
            return secure_name

    @staticmethod
    def random_proxy(proxylist: list):
        proxy = proxylist[random.randint(0, len(proxylist)-1)]
        return {'https': f'socks5h://{proxy}'}

    @staticmethod
    def random_useragent(useragents: list):
        return useragents[random.randint(0, len(useragents)-1)]
