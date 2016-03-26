# -*- coding: utf-8 -*-
"""
Copyright 2016 Joohyun Lee(ppiazi@gmail.com)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import feedparser
from BotMain import logger

FEED_URL = "http://wizard.korea.ac.kr/rssList.jsp?siteId=gscit&boardId=861704"

class KoreaUnivGscitNoticeReader:
    def __init__(self, feed_url = FEED_URL):
        self.feed_url = feed_url

    def readAll(self):
        try:
            logger.info("Try to open %s" % self.feed_url)
            self.rss_reader = feedparser.parse(self.feed_url)
            self.feed_list = self.rss_reader['items']

            # published 값으로 descending 정렬하기 위함임.
            # 간혹 published 값으로 정렬되지 않은 경우가 있음.
            temp_dict = {}
            for i in self.feed_list:
                temp_dict[i['published'] + i['title']] = i

            keylist = list(temp_dict.keys())
            keylist.sort()

            final_list = []
            for key in keylist:
                final_list.append(temp_dict[key])

            logger.info("Successfully read %d items." % len(self.feed_list))
        except:
            logger.error("%s is not valid." % self.feed_url)
            self.rss_reader = None
            self.feed_list = None
            final_list = None

        return final_list

