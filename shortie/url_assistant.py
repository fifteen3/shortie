import sqlite3
import hashlib
import user_agents
import db

class UrlEncoder:
    def __init__(self,**kwargs):
        self.url = kwargs.get('url')

    def encode_url(self,user):
        url_bytes = self.url.encode('utf-8')
        user_bytes = user.email.encode('utf-8')
        m = hashlib.sha1(url_bytes + user_bytes)
        long_hash = m.hexdigest()
        return long_hash


class UrlFinder:
    def __init__(self,**kwargs):
        self.url = kwargs.get('url')
        self.url_hash = kwargs.get('url_hash')
        self.ua_string = kwargs.get('ua_string')

    def lookup_device_type(self):
        dt = "desktop"
        ua = user_agents.parse(self.ua_string)
        if ua.is_mobile:
            dt = "mobile"
        elif ua.is_tablet:
            dt = "tablet"
        return dt

    def lookup_url(self):
        url_hash = self.url_hash
        device = self.lookup_device_type()
        conn = db.get_db()
        c = conn.cursor()
        c.execute('SELECT url FROM urls WHERE short_hash = ? AND url_type = ?', [url_hash, device])
        url = c.fetchone()[0]
        if url:
            try:
                c.execute('INSERT INTO visits (short_hash,url_type) VALUES (?,?)', [url_hash,device])
                conn.commit()
            except sqlite3.Error as e:
                print e.message
            return url

class UrlSaver:

    def __init__(self,db):
        self.db = db

    def store_urls(self,urls,encoded_url,user):
        conn = self.db.get_db()
        c = conn.cursor()
        if not c:
            return "Database connection Error."
        #generate the uuid and insert it and
        shortie = encoded_url[:7]
        try:
            insert_hash_query = 'INSERT INTO url_hashes (short_hash,long_hash,user_id) VALUES (?,?,?)'
            user_id = user.get_user_id()
            c.execute(insert_hash_query, [shortie,encoded_url,user_id])
            for url_type,url in urls.iteritems():
                try:
                    insert_url_query = 'INSERT INTO urls (short_hash,url_type,url) VALUES (?,?,?)'
                    c.execute(insert_url_query, [shortie, url_type, url])
                except sqlite3.Error as e:
                    return e.message
        except sqlite3.Error as e:
            return e.message
        conn.commit()

