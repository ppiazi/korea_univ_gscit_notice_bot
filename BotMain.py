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

from telegram.ext import Updater
import logging
import datetime

__VERSION__ = "0.0.2"
DEFAULT_LIST_NUM = 3
NOTICE_CHECK_PERIOD_H = 6

MSG_START = "고려대학교 컴퓨터정보통신대학원 공지사항 봇 %s\n만든이 : 39기 이주현(ppiazi@gmail.com)\nhttps://github.com/ppiazi/korea_univ_gscit_notice_bot" % __VERSION__
MSG_HELP = """
버전 : %s
/list <num of notices> : 입력 개수만큼 공지사항을 보여줌. 인자가 없으면 기본 개수로 출력.
/help : 도움말을 보여줌.
/status : 현재 봇 상태를 보여줌."""
MSG_NOTICE_USAGE_ERROR = "입력된 값이 잘못되었습니다."
MSG_NOTICE_FMT = "ID : %d\n날짜 : %s\n제목 : %s\n작성자 : %s\nURL : %s\n"
MSG_STATUS = "* 현재 사용자 : %d\n* 최신 업데이트 : %s\n* 공지사항 개수 : %d"

# Enable logging
logging.basicConfig(
#        filename="./BotMain.log",
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger("BOT_MAIN")
job_queue = None

# Global DB
g_bot = None
g_notice_reader = None
g_notice_list = []
g_last_notice_date = "2016-03-01 00:00:00"

import NoticeReader
from BotMainDb import ChatIdDb

g_chat_id_db = ChatIdDb()

def start(bot, update):
    checkChatId(update.message.chat_id)
    bot.sendMessage(update.message.chat_id, text=MSG_START)

def checkChatId(chat_id):
    global g_chat_id_db

    g_chat_id_db.getChatIdInfo(chat_id)

def help(bot, update):
    checkChatId(update.message.chat_id)
    bot.sendMessage(update.message.chat_id, text=MSG_HELP % __VERSION__)

def status(bot, update):
    """
    현재 bot의 상태 정보를 전송한다.

    :param bot:
    :param update:
    :return:
    """
    global g_last_notice_date
    global g_notice_list
    global g_chat_id_db

    l = g_chat_id_db.getAllChatIdDb()
    s = g_chat_id_db.getChatIdInfo()

    checkChatId(update.message.chat_id)
    bot.sendMessage(update.message.chat_id, text=MSG_STATUS % (len(l), str(s), len(g_notice_list)))

def checkNotice(bot):
    """
    주기적으로 Notice를 읽어 최신 정보가 있으면, 사용자들에게 전송한다.

    :return:
    """
    global g_notice_list
    global g_chat_id_db

    updateNoticeList()
    # dict_chat_id = updateListenerList(bot)

    l = g_chat_id_db.getAllList()

    for n_item in g_notice_list:
        tmp_msg_1 = makeNoticeSummary(g_notice_list.index(n_item), n_item)
        # logger.info(tmp_msg_1)

        for t_chat_id in l.keys():
            temp_date_str = t_chat_id[1]
            if n_item['published'] > temp_date_str:
                logger.info("sendMessage to %d (%s : %s)" % (t_chat_id, n_item['published'], n_item['title']))
                bot.sendMessage(t_chat_id, text=tmp_msg_1)
                g_chat_id_db.updateChatId(t_chat_id, n_item['published'])

def updateNoticeList():
    """
    공지사항을 읽어와 내부 데이터를 최신화한다.

    :param bot:
    :return:
    """
    global g_notice_list
    global g_last_notice_date

    logger.info("Try to reread notice list")
    logger.info("Last Notice Date : %s" % g_last_notice_date)

    g_notice_list = g_notice_reader.readAll()

def makeNoticeSummary(i, n_item):
    """
    각 공지사항 별 요약 Text를 만들어 반환한다.

    :param i:
    :param n_item:
    :return:
    """
    tmp_msg_1 = MSG_NOTICE_FMT % (i, n_item['published'], n_item['title'], n_item['author'], n_item['link'])
    return tmp_msg_1

def listNotice(bot, update, args):
    """
    공지사항을 읽어 텔레그렘으로 전송한다.

    :param bot:
    :param update:
    :param args: 읽어드릴 공지사항 개수(최신 args개)
    :return: 없음.
    """
    global g_notice_list
    global g_chat_id_db

    checkChatId(update.message.chat_id)
    chat_id = update.message.chat_id
    # args[0] should contain the time for the timer in seconds
    if len(args) == 0:
        num = DEFAULT_LIST_NUM
    else:
        try:
            num = int(args[0])
        except:
            num = DEFAULT_LIST_NUM
            bot.sendMessage(chat_id, text=MSG_NOTICE_USAGE_ERROR)
            bot.sendMessage(chat_id, text=MSG_HELP)

        if num < 0:
            bot.sendMessage(chat_id, text=MSG_NOTICE_USAGE_ERROR)
            num = DEFAULT_LIST_NUM

    i = 0
    if num >= len(g_notice_list):
        num = g_notice_list

    last_date = ""
    for n_item in g_notice_list[num * -1:]:
        tmp_msg_1 = makeNoticeSummary(g_notice_list.index(n_item), n_item)
        logger.info(tmp_msg_1)
        bot.sendMessage(chat_id, text=tmp_msg_1)
        last_date = n_item['published']

        i = i + 1
        if i == num:
            break
    g_chat_id_db.updateChatId(chat_id, last_date)

def readNotice(bot, update, args):
    """
    특정 공지사항의 내용을 읽어 반환한다.

    :param bot:
    :param update:
    :param args:
    :return:
    """
    global g_dict_chat_id

    g_dict_chat_id[update.message.chat_id] = 1

    pass

def handleNormalMessage(bot, update, error):
    checkChatId(update.message.chat_id)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def main():
    global g_notice_reader
    global g_bot

    g_notice_reader = NoticeReader.KoreaUnivGscitNoticeReader()
    print("Korea University GSCIT Homepage Notice Bot V%s" % __VERSION__)

    global job_queue

    f = open("bot_token.txt", "r")
    BOT_TOKEN = f.readline()
    f.close()

    updater = Updater(BOT_TOKEN)
    job_queue = updater.job_queue

    g_bot = updater.bot

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.addTelegramCommandHandler("start", start)
    dp.addTelegramCommandHandler("help", help)
    dp.addTelegramCommandHandler("h", help)
    dp.addTelegramCommandHandler("list", listNotice)
    dp.addTelegramCommandHandler("l", listNotice)
    dp.addTelegramCommandHandler("read", readNotice)
    dp.addTelegramCommandHandler("r", readNotice)
    dp.addTelegramCommandHandler("status", status)
    dp.addTelegramCommandHandler("s", status)

    # on noncommand i.e message - echo the message on Telegram
    dp.addTelegramMessageHandler(handleNormalMessage)

    # log all errors
    dp.addErrorHandler(error)

    # init db
    updateNoticeList()
    job_queue.put(checkNotice, 60*60*NOTICE_CHECK_PERIOD_H, repeat=True)

    # Start the Bot
    updater.start_polling()

    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
