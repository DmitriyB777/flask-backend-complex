class Config(object):
    username = 'postgres'
    password = 'root'
    host = '127.0.0.1'
    port = 5433
    database = 'flask-backend-complex-db'
    SQLALCHEMY_DATABASE_URI = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = '978911cd-9c20-4a38-a9c2-add9b5928a7e'