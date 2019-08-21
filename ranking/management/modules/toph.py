#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
from pprint import pprint
from datetime import datetime
import urllib.parse
import re
from concurrent.futures import ThreadPoolExecutor as PoolExecutor
import tqdm

from common import REQ
from common import BaseModule, parsed_table


class Statistic(BaseModule):

    def __init__(self, **kwargs):
        super(Statistic, self).__init__(**kwargs)

    def get_standings(self, users=None):
        page = REQ.get(self.url)

        page = REQ.get(self.url.strip('/') + '/statistics')
        table = parsed_table.ParsedTable(html=page)
        problem_names = [list(r.values())[0].value for r in table]

        standings_url = self.url.strip('/') + '/standings'
        next_url = standings_url

        urls = []
        results = {}
        problems_info = collections.OrderedDict()
        n_page = 1
        while next_url:
            page = REQ.get(next_url)
            table = parsed_table.ParsedTable(html=page)
            for r in table:
                to_get_handle = False
                row = {}
                problems = row.setdefault('problems', {})
                for k, v in r.items():
                    if k == '#':
                        row['place'] = v.value
                    elif not k:
                        name, score = v

                        row['name'] = name.value
                        hrefs = name.column.node.xpath('.//a[contains(@href,"/u/")]/@href')
                        if hrefs:
                            row['member'] = hrefs[0].split('/')[-1]
                        else:
                            to_get_handle = True
                            row['member'] = f'{row["name"]}, {self.start_time.year}'

                        title = score.column.node.xpath('.//div[@title]/@title')[0]
                        row['solving'], row['penalty'] = title.replace(',', '').split()
                    else:
                        letter = k.split()[0]
                        problems_info[letter] = {'short': letter}
                        if len(letter) == 1:
                            if v.value:
                                title = v.column.node.xpath('.//div[@title]/@title')[0]
                                *_, time, attempt = title.split()
                                time = int(time)
                                attempt = sum(map(int, re.findall('[0-9]+', attempt)))

                                if time:
                                    result = '+' if attempt == 1 else f'+{attempt - 1}'
                                else:
                                    result = f'-{attempt}'

                                p = problems.setdefault(letter, {})
                                p.update({'time': time, 'result': result})

                                hrefs = v.column.node.xpath('.//a[contains(@href,"submissions")]/@href')
                                if hrefs:
                                    url = urllib.parse.urljoin(next_url, hrefs[0])
                                    p['url'] = url
                                    if to_get_handle:
                                        urls.append((row['member'], url))
                                        to_get_handle = False
                if not problems:
                    continue
                results[row['member']] = row
            n_page += 1
            match = re.search(f'<a[^>]*href="(?P<href>[^"]*standings[^"]*)"[^>]*>{n_page}</a>', page)
            next_url = urllib.parse.urljoin(next_url, match.group('href')) if match else None

        if urls:
            def fetch(info):
                member, url = info
                return member, REQ.get(url)
            with PoolExecutor(max_workers=20) as executor, tqdm.tqdm(total=len(urls), desc='handling') as pbar:
                for member, page in executor.map(fetch, urls):
                    t = parsed_table.ParsedTable(html=page)
                    t = next(iter(t))
                    handle = t['Author'].value
                    results[handle] = results.pop(member)
                    results[handle]['member'] = handle
                    pbar.update()

        problems = []
        for info, name in zip(problems_info.values(), problem_names):
            info['name'] = name
            problems.append(info)

        ret = {
            'url': standings_url,
            'problems': problems,
            'result': results,
        }
        return ret


if __name__ == "__main__":
    statictic = Statistic(
        name='DIU Intra University Programming Contest 2019 (Replay)',
        url='https://toph.co/c/diu-inter-section-summer-2019-preliminary-a',
        key='diu-inter-section-summer-2019-preliminary-a',
        start_time=datetime.strptime('20.09.2019', '%d.%m.%Y'),
    )
    pprint(statictic.get_standings())
    statictic = Statistic(
        name='DIU Intra University Programming Contest 2019 (Replay)',
        url='https://toph.co/c/diu-intra-2019-r',
        key='diu-intra-2019-r',
        start_time=datetime.strptime('20.09.2019', '%d.%m.%Y'),
    )
    pprint(statictic.get_standings())