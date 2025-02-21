from peewee import *
from datetime import datetime
import os
import shutil

# Database configuration
DB_NAME = 'mental_health_chat.db'
DB_DIR = 'database'
DB_PATH = os.path.join(DB_DIR, DB_NAME)

# Create database directory if it doesn't exist
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# If a database exists in root directory, move it to database folder
root_db = DB_NAME
if os.path.exists(root_db):
    try:
        # If database folder already has a db, merge or backup the root one
        if os.path.exists(DB_PATH):
            backup_path = os.path.join(DB_DIR, f'backup_{DB_NAME}')
            shutil.copy2(root_db, backup_path)
        else:
            # Move the root database to database folder
            shutil.move(root_db, DB_PATH)
    except Exception as e:
        print(f"Error handling database file: {e}")

# Initialize database connection
db = SqliteDatabase(DB_PATH)

class BaseModel(Model):
    class Meta:
        database = db

class Conversation(BaseModel):
    title = CharField()
    created_at = DateTimeField(default=datetime.now)
    last_updated = DateTimeField(default=datetime.now)

class Message(BaseModel):
    conversation = ForeignKeyField(Conversation, backref='messages')
    role = CharField()  # 'user' or 'assistant'
    content = TextField()
    sentiment = CharField(null=True)
    sentiment_score = FloatField(null=True)
    created_at = DateTimeField(default=datetime.now)

def initialize_db():
    """Initialize database and create tables if they don't exist"""
    db.connect(reuse_if_open=True)
    db.create_tables([Conversation, Message])
    return db
