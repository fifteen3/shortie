import db
import sqlite3

class User:
    def __init__(self,email):
        self.email = email

    def get_user_id(self):
        c = db.get_db().cursor()
        if not c:
            return None
        try:
            c.execute('SELECT rowid FROM users WHERE email = ?', [self.email])
            user_id = c.fetchone()[0]
            return user_id
        except (TypeError,sqlite3.Error) as e:
            print e.message

    def list_urls(self):
        user_id = self.get_user_id()
        conn = db.get_db()
        c = conn.cursor()
        list_query = '''SELECT urls.url as url,v.url_type as url_type,COUNT(v.short_hash) as visits, (julianday('now') - julianday(hashes.created)) as since FROM users AS u JOIN url_hashes AS hashes ON (u.rowid = hashes.user_id) JOIN urls USING (short_hash) JOIN visits AS v ON (urls.short_hash = v.short_hash AND urls.url_type = v.url_type) WHERE u.rowid = ? GROUP BY v.url_type'''
        c.execute(list_query, [user_id])
        rows = c.fetchall()
        data = []
        for n in rows:
            row = {}
            for g in n.keys():
                row[g] = n[g]
            data.append(row)

        return data
