import os
import logging
import typing
import sqlite3
import datetime
import calendar

from aiogram import Bot, Dispatcher, executor, types

from sql_queries import get_timetable_for_group_and_day


class TimeTableBot:

    def __init__(self, config: typing.Dict):
        self.config = config
        self.bot = Bot(config["token"])
        self.dp = Dispatcher(bot=self.bot)
        self.bd_conn = sqlite3.connect(config["db"])
        self.cursor = self.bd_conn.cursor()

    def start_polling(self):
        executor.start_polling(self.dp)

    def setup_handlers(self):
        self.dp.register_message_handler(self.welcome_user, commands=['start', 'help'])
        self.dp.register_message_handler(self.cmd_today, commands=['today'])
        self.dp.register_message_handler(self.cmd_weekday, commands=calendar.day_name)

    def on_shutdown(self):
        logging.info('Connection to database is closed')
        self.bd_conn.commit()
        self.bd_conn.close()

    async def welcome_user(self, message: types.Message):
        await message.answer('Hello, user')

    async def cmd_today(self, message: types.Message):
        day = datetime.date.today().weekday()
        day = calendar.day_name[day]
        records = get_timetable_for_group_and_day(self.cursor, 0, day)
        reply_text = "\n".join(
            [" | ".join(row) for row in records]
        )
        await message.answer(reply_text)

    async def cmd_weekday(self, message: types.Message):
        day = message.get_command(pure=True)
        records = get_timetable_for_group_and_day(self.cursor, 0, day)
        reply_text = "\n".join(
            [" | ".join(row) for row in records]
        )
        await message.answer(reply_text)

