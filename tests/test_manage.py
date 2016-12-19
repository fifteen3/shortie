import os
import pytest
import sqlite3
from shortie import manage,db

def test_pop_db():
    manage.create_db()
    with manage.app.app_context():
        m = manage.clear_users()
        assert ('cleared users table' == m)
        c = manage.pop_db()
        assert (c == 'Database populated.')
        d = db.get_db().cursor()
        d.execute('SELECT email FROM USERS where rowid = 1')
        rs = d.fetchone()
        assert (rs[0] == 'jason@seaver.com')
        g = manage.clear_users()
        assert ('cleared users table' == g)
    manage.delete_db()

