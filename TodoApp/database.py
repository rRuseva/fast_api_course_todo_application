from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

# # SQLite3 connection
# SQL_ALCHEMY_DATABASE_URL = "sqlite:///./TodoApp/todosapp.db"
# engine = create_engine(SQL_ALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

db_user_name=os.getenv('DB_USER')
db_password=os.getenv('DB_PASSWORD')
# PostgreSQL connection
SQL_ALCHEMY_DATABASE_URL = f"postgresql://{db_user_name}:{db_password}@ep-bold-hat-b2yar57d-pooler.c-6.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
engine = create_engine(SQL_ALCHEMY_DATABASE_URL)


# PostgreSQL connection
# SQL_ALCHEMY_DATABASE_URL = "postgresql://postgres:admin@localhost/TodoApplicationDatabase"
# engine = create_engine(SQL_ALCHEMY_DATABASE_URL)

# # MySql connection
# SQL_ALCHEMY_DATABASE_URL = "mysql+pymysql://root:admin@localhost:3306/TodoApplicationDatabase"
# engine = create_engine(SQL_ALCHEMY_DATABASE_URL)


SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind=engine)

Base = declarative_base()