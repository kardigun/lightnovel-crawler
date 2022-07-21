# -*- coding: utf-8 -*-
import json
import logging
import re
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://readnovelfull.com/search?keyword=%s'
full_chapter_url = 'https://readnovelfull.com/ajax/chapter-archive?novelId=%s'


class ReadNovelFullCrawler(Crawler):
    base_url = 'https://readnovelfull.com/'

    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)

        results = []
        for result in soup.select('div.col-novel-main div.list.list-novel div.row')[:5]:
            url = self.absolute_url(
                result.select_one('h3.novel-title a')['href'])
            title = result.select_one('h3.novel-title a')['title']
            last_chapter = result.select_one('span.chr-text').text.strip()
            results.append({
                'url': url,
                'title': title,
                'info': 'last chapter : %s' % last_chapter,
            })
        # end for
        return results
    # end def

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url + '?waring=1')

        possible_title = soup.select_one('h3.title')
        assert possible_title, 'No novel title'
        self.novel_title = possible_title.text.strip()
        logger.info('Novel title: %s', self.novel_title)

        possible_image = soup.select_one('div.book img')
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        author = []
        for a in soup.select('ul.info.info-meta li')[1].select('a'):
            author.append(a.text.strip())
        # end for

        self.novel_author = ", ".join(author)

        logger.info('Novel author: %s', self.novel_author)

        novel_id = soup.select_one('div#rating')['data-novel-id']

        chapter_url = full_chapter_url % novel_id
        logger.debug('Visiting %s', chapter_url)

        chapter_soup = self.get_soup(chapter_url)
        chapters = chapter_soup.select('li a')
        for a in chapters:
            for span in a.findAll('span'):
                span.extract()
            # end for
        # end for

        for x in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append({ 'id': vol_id })
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url': self.absolute_url(x['href']),
                'title': x['title'] or ('Chapter %d' % chap_id),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        content = soup.select_one('#chr-content')
        return self.cleaner.extract_contents(content)
    # end def
# end class