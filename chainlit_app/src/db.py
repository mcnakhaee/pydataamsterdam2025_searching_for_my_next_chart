import os
import uuid
import asyncio
import json
import psycopg2
import psycopg2.extras
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")  # Changed from localhost to db
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "chainlit")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

# Rest of your code remains the same

class DBClient:
    _connection = None
    _lock = asyncio.Lock()  # Lock for thread safety

    @classmethod
    async def get_connection(cls):
        """Get or create the database connection"""
        if cls._connection is None or cls._connection.closed:
            cls._connection = psycopg2.connect(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                dbname=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD
            )
            cls._connection.autocommit = True
            await cls.initialize_tables()
        return cls._connection

    @classmethod
    async def initialize_tables(cls):
        """Create necessary tables if they don't exist"""
        conn = await cls.get_connection()
        cursor = conn.cursor()
        
        # Create chat_sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id VARCHAR PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_ip VARCHAR
            )
        ''')
        
        # Create chat_messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id VARCHAR PRIMARY KEY,
                session_id VARCHAR REFERENCES chat_sessions(id),
                user_message TEXT,
                ai_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSONB
            )
        ''')
        cursor.close()
        print("Database tables initialized")

    @classmethod
    async def create_session(cls, user_ip=None):
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        async with cls._lock:
            conn = await cls.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO chat_sessions (id, user_ip) VALUES (%s, %s)',
                (session_id, user_ip)
            )
            cursor.close()
        return session_id

    @classmethod
    async def log_message(cls, session_id, user_message, ai_response, metadata=None):
        """Log a chat message to the database"""
        message_id = str(uuid.uuid4())
        async with cls._lock:
            conn = await cls.get_connection()
            cursor = conn.cursor()
            
            # Convert metadata to JSON if it's not None
            if metadata is not None and not isinstance(metadata, str):
                metadata = json.dumps(metadata)
            
            # Insert the message
            cursor.execute(
                'INSERT INTO chat_messages (id, session_id, user_message, ai_response, metadata) VALUES (%s, %s, %s, %s, %s)',
                (message_id, session_id, user_message, ai_response, metadata)
            )
            
            # Update session timestamp
            cursor.execute(
                'UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = %s',
                (session_id,)
            )
            cursor.close()
        return message_id

    @classmethod
    async def get_chat_history(cls, session_id, limit=10):
        """Retrieve chat history for a session"""
        async with cls._lock:
            conn = await cls.get_connection()
            cursor = conn.cursor(cursor_fac