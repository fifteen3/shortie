import os
import pytest
import sqlite3
from shortie import db

def test_get_db():
    c = db.get_db().cursor()
    assert ('Cursor' == type(c).__name__)
