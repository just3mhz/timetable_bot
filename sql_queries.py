import sqlite3
import typing


def add_new_user(cursor: sqlite3.Cursor, user_id, group_id: int):
    cursor.execute("""
        INSERT INTO users VALUES (?, ?)
    """, (user_id, group_id))


def delete_timetable_for_group(cursor: sqlite3.Cursor, group_id: int):
    cursor.execute("""
        DELETE FROM timetable WHERE group_id = ?
    """, (group_id, ))


def upload_timetable_for_group(cursor: sqlite3.Cursor, group_id: int, timetable: typing.Iterable):
    cursor.executemany(f"""
        INSERT INTO timetable VALUES ({group_id}, ?, ?, ?, ?, ?)
    """, timetable)


def get_timetable_for_group_and_day(cursor: sqlite3.Cursor, group_id: int, weekday: str):
    return cursor.execute("""
        SELECT subject, tutor, place, time
        FROM timetable
        WHERE group_id = ? AND weekday = ?
    """, (group_id, weekday)).fetchall()
