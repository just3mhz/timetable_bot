import os
import typing
import datetime
import calendar

from aiogram import Bot, Dispatcher, executor, types

from timetable_base import Database, User, TimetableRecord
from timetable_loader import get_loader


def run_bot(config: typing.Dict):
    bot_backend = TimeTableBot(config)
    bot_backend.setup_handlers()
    bot_backend.start_polling()
    bot_backend.on_shutdown()


class TimeTableBot:

    HELP_MESSAGE = """
/start     - Start bot
/help      - Show help message
/today     - Show timetable for today
/[weekday] - Show timetable for [weekday]
[document] - Upload new timetable
"""

    def __init__(self, config: typing.Dict):
        self.config = config
        self.bot = Bot(config['token'])
        self.dp = Dispatcher(bot=self.bot)
        self.db = Database(url=config['db_uri'])
        self.scheme = set(config['columns'].split(','))

    def start_polling(self):
        executor.start_polling(self.dp)

    def setup_handlers(self):
        self.dp.register_message_handler(self.cmd_start, commands=['start'])
        self.dp.register_message_handler(self.cmd_help, commands=['help'])
        self.dp.register_message_handler(self.cmd_today, commands=['today'])
        self.dp.register_message_handler(self.cmd_weekday, commands=calendar.day_name)
        self.dp.register_message_handler(self.handle_file, content_types=['document'])

    def on_shutdown(self):
        pass

    def _user_is_registered(self, user_id):
        return self.db.session.query(User).get(user_id) is not None

    def _get_timetable_for_day(self, user_id, weekday):
        timetable_for_weekday = []
        for row in self.db.session.query(TimetableRecord).filter_by(user_id=user_id, weekday=weekday):
            timetable_for_weekday.append((row.weekday, row.time, row.subject, row.lecturer, row.place))
        if not timetable_for_weekday:
            return 'You are free for this day'
        else:
            return '\n'.join([' '.join(row) for row in timetable_for_weekday])

    async def cmd_start(self, message: types.Message):
        user_id = message.from_user.id
        if not self._user_is_registered(user_id):
            self.db.session.add(User(user_id))
            self.db.session.commit()
        await message.answer(f'Hello, {message.from_user.username}')

    async def cmd_help(self, message: types.Message):
        await message.answer(self.HELP_MESSAGE)

    async def cmd_today(self, message: types.Message):
        user_id = message.from_user.id
        if not self._user_is_registered(user_id):
            await message.answer('You are not registered. Run /start to register')
            return
        weekday = calendar.day_name[datetime.datetime.today().weekday()]
        await message.answer(self._get_timetable_for_day(user_id, weekday))

    async def cmd_weekday(self, message: types.Message):
        user_id = message.from_user.id
        if not self._user_is_registered(user_id):
            await message.answer('You are not registered. Run /start to register')
            return
        weekday = message.get_command(pure=True).capitalize()
        await message.answer(self._get_timetable_for_day(user_id, weekday))

    async def handle_file(self, message: types.Message):
        user_id = message.from_user.id
        if not self._user_is_registered(user_id):
            await message.answer('You are not registered. Run /start to register')
            return
        file_id = message.document.file_id
        root, ext = os.path.splitext(message.document.file_name)
        loader = get_loader(ext)
        if loader is None:
            await message.answer('Unsupported extension: "%s"' % ext)
        else:
            tmp_file = 'tmp' + ext
            await self.bot.download_file_by_id(file_id, tmp_file)
            try:
                new_records = [TimetableRecord(user_id=user_id, **record) for record in loader(tmp_file, self.scheme)]
                self.db.session.query(TimetableRecord).filter_by(user_id=user_id).delete()
                self.db.session.add_all(new_records)
                self.db.session.commit()
                await message.answer('Your timetable has been uploaded')
            # TODO: Make exception handlers
            except Exception:
                self.db.session.rollback()
                await message.answer('Something went wrong')
            os.remove(tmp_file)
