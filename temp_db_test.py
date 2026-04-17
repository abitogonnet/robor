import os
import psycopg2
from urllib.parse import urlparse

url = "postgresql://abito_web_user:LCVGpSIRf6wAfFRuylAY0SmLRqjgpfTc@dpg-d7cimldckfvc739qt08g-a.virginia-postgres.render.com/abito_web_db"
print('URL:', url)
conn = psycopg2.connect(url)
print('Connected to', conn.dsn)
cur = conn.cursor()
cur.execute("SELECT current_database(), current_user;")
print('DB info:', cur.fetchone())
cur.close()
conn.close()
