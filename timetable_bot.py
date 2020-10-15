import os
import logging
import typing
import sqlite3
import datetime
import calendar

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageTextIsEmpty

from sql_queries import get_timetable_for_group_and_day, upload_timetable_for_group
from timetable_loader import get_loader


class UploadForm(StatesGroup):
    upload_file = State()


class TimeTableBot:

    def __init__(self, config: typing.Dict):
        self.config = config
        self.bot = Bot(config["token"])
        self.storage = MemoryStorage()
        self.dp = Dispatcher(bot=self.bot, storage=self.storage)
        self.bd_conn = sqlite3.connect(config["db"])
        self.cursor = self.bd_conn.cursor()

    def start_polling(self):
        executor.start_polling(self.dp)

    def setup_handlers(self):
        self.dp.register_message_handler(self.welcome_user, commands=['start', 'help'])
        self.dp.register_message_handler(self.cmd_today, commands=['today'])
        self.dp.register_message_handler(self.cmd_weekday, commands=calendar.day_name)
        self.dp.register_message_handler(self.cmd_upload_timetable, commands=['upload'], state="*")
        self.dp.register_message_handler(self.handle_file, content_types=['document'], state=UploadForm.upload_file)

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
        try:
            await message.answer(reply_text)
        except MessageTextIsEmpty:
            await message.answer('You are free!')

    async def cmd_weekday(self, message: types.Message):
        day = message.get_command(pure=True)
        records = get_timetable_for_group_and_day(self.cursor, 0, day)
        reply_text = "\n".join(
            [" | ".join(row) for row in records]
        )
        try:
            await message.answer(reply_text)
        except MessageTextIsEmpty:
            await message.answer('You are free!')

    async def cmd_upload_timetable(self, message: types.Message):
        await UploadForm.upload_file.set()
        await message.answer('Waiting for file')

    async def handle_file(self, message: types.Message):
        await UploadForm.next()
        file_id = message.document.file_id
        root, ext = os.path.splitext(message.document.file_name)
        loader = get_loader(ext)
        if loader is None:
            await message.answer('Unsupported extension: "%s"' % ext)
        else:
            tmp_file = 'tmp' + ext
            await self.bot.download_file_by_id(file_id, tmp_file)
            upload_timetable_for_group(self.cursor, loader(path_to_file=tmp_file, group_id=0))
            os.remove(tmp_file)
