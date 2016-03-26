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
import NoticeReader

__VERSION__ = "0.0.1"
DEFAULT_LIST_NUM = 5

MSG_START = "고려대학교 컴퓨터정보통신대학원 공지사항 봇 %s\n만든이 : 39기 이주현(ppiazi@gmail.com)\nhttps://github.com/ppiazi/korea_univ_gscit_notice_bot" % __VERSION__
MSG_HELP = "사용법: /list <num of notices>\n값이 잘못되거나 아무것도 안 넣으면 10개를 보여줌."
MSG_NOTICE_USAGE_ERROR = "입력된 값이 잘못되었습니다."
MSG_NOTICE_FMT = "ID : %d\n날짜 : %s\n제목 : %s\n작성자 : %s\nURL : %s\n"
MSG_STATUS = "* 현재 사용자 : %d\n* 최신 업데이트 : %s"

# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger("BOT_MAIN")
job_queue = None

# Global DB
g_bot = None
g_notice_reader = None
g_notice_list = []
g_last_notice_date = "2016-03-01 00:00:00"
g_dict_chat_id = {}

def start(bot, update):
    global g_dict_chat_id

    bot.sendMessage(update.message.chat_id, text=MSG_START)
    g_dict_chat_id[update.message.chat_id] = 1

def help(bot, update):
    global g_dict_chat_id

    bot.sendMessage(update.message.chat_id, text=MSG_HELP)
    g_dict_chat_id[update.message.chat_id] = 1

def updateListenerList(bot):
    """
    현재 bot과 대화하고 있는 chat_id를 수집한다.

    :param bot:
    :return:
    """
    global g_dict_chat_id

    """
    updates = bot.getUpdates()
    dict_chat_id = {}
    for u in updates:
        chat_id = u.message.chat_id
        message = u.message.text

        logger.info(str(chat_id) + message)

        try:
            dict_chat_id[chat_id] = dict_chat_id[chat_id] + 1
        except KeyError:
            dict_chat_id[chat_id] = 1
    """

    return g_dict_chat_id

def status(bot, update):
    """
    현재 bot의 상태 정보를 전송한다.

    :param bot:
    :param update:
    :return:
    """
    global g_last_notice_date
    global g_dict_chat_id

    g_dict_chat_id[update.message.chat_id] = 1

    bot.sendMessage(update.message.chat_id, text=MSG_STATUS % (len(g_dict_chat_id.keys()), g_last_notice_date))

def checkNotice(bot):
    """
    주기적으로 Notice를 읽어 최신 정보가 있으면, 사용자들에게 전송한다.

    :return:
    """
    new_item_list = updateNoticeList()
    dict_chat_id = updateListenerList(bot)

    for n_item in new_item_list:
        tmp_msg_1 = makeNoticeSummary(g_notice_list.index(n_item), n_item)
        logger.info(tmp_msg_1)

        for t_chat_id in dict_chat_id.keys():
            chat_id = t_chat_id
            bot.sendMessage(chat_id, text=tmp_msg_1)

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
    new_item_list = []

    for n_item in g_notice_list:
        if n_item['published'] <= g_last_notice_date:
            continue
        new_item_list.append(n_item)
        g_last_notice_date = n_item['published']

    logger.info("New Article : (%d) / Last Updated(%s)" % (len(new_item_list), g_last_notice_date))

    return new_item_list

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
    global g_dict_chat_id

    g_dict_chat_id[update.message.chat_id] = 1

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

    for n_item in g_notice_list[num * -1:]:
        tmp_msg_1 = makeNoticeSummary(g_notice_list.index(n_item), n_item)
        logger.info(tmp_msg_1)
        bot.sendMessage(chat_id, text=tmp_msg_1)

        i = i + 1
        if i == num:
            break

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

    # log all errors
    dp.addErrorHandler(error)

    #updateNoticeList()
    job_queue.put(checkNotice, 10, repeat=True)

    # Start the Bot
    updater.start_polling()

    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
