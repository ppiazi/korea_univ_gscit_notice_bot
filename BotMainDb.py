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

import datetime

from BotMain import logger
import pickle

DEFAULT_CHAT_ID_DB = "chat_id.db"

class ChatIdDb:
    def __init__(self):
        self._db = {}
        self._load()

    def _load(self):
        try:
            f = open(DEFAULT_CHAT_ID_DB, "rb")

            # 파일이 있다면, 기존 사용자를 로드한다.
            self._db = pickle.load(f)
        except Exception as e:
            logger.error(e)
            self._save()

    def _save(self):
        f = open(DEFAULT_CHAT_ID_DB, "wb")
        pickle.dump(self._db, f)
        f.close()

    def getAllChatIdDb(self):
        return self._db

    def getChatIdInfo(self, chat_id):
        """
        주어진 chat_id를 확인하여,
            1.기존에 있는 사용자면 사용자 정보를 반환한다.
            2.기존에 없는 사용자면 새롭게 등록한다.

        :param chat_id:
        :return:    chat_id에 해당하는 정보를 반환함.
        """
        self.updateChatId(chat_id)

        return self._db[chat_id]

    def updateChatId(self, chat_id, update_time = None):
        try:
            self._db[chat_id] = self._db[chat_id]

            if update_time != None:
                self._db[chat_id] = update_time
        except Exception as e:
            if update_time == None:
                logger.info("New Commer : %d" % (chat_id))
                d = datetime.datetime.today()
                td = datetime.timedelta(days=90)
                d = d - td
                self._db[chat_id] = str(d)
            else:
                self._db[chat_id] = update_time

        self._save()

    def removeChatId(self, chat_id):
        del self._db[chat_id]

        self._save()
