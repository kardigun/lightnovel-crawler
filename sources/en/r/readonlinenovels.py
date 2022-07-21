# -*- coding: utf-8 -*-
import logging
import re

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'http://readonlinenovels.com/novel/search/?keywords=%s'


class ReadOnlineNovelsCrawler(Crawler):
    base_url = ['http://readonlinenovels.com/']

    def initialize(self):
        self.home_url = 'http://readonlinenovels.com/'
    # end def

    # NOTE: Disabled because it takes too long
    # def search_novel(self, query):
    #     soup = self.get_soup(search_url % query)

    #     results = []
    #     for div in soup.select('div.book-context'):
    #         a = div.select_one('a')
    #         title = a.select_one('h4 b').text.strip()
    #         info = div.select_one('div.update-info').text.strip()
    #         results.append({
    #             'title': title,
    #             'url': self.absolute_url(a['href']),
    #             'info': info,
    #         })
    #     # end for

    #     return results
    # # end def

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('.book-info div.title b')
        assert possible_title, 'No novel title'
        self.novel_title = possible_title.text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = soup.select_one(
            '.book-info div.title span').text.strip()
        logger.info('Novel author: %s', self.novel_author)

        possible_image = soup.select_one('div.book-img img')
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        # Extract volume-wise chapter entries
        for a in soup.select('div.slide-item a'):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append({ 'id': vol_id })
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': a.text.strip(),
                'url':  self.absolute_url(a['href']),
            })
        # end for

    # end def

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        contents = soup.select('div.read-context p')
        body = [str(p) for p in contents if p.text.strip()]
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def

# end class