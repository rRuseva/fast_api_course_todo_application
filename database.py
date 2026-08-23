from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLite3 connection
# SQL_ALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"
# engine = create_engine(SQL_ALCHEMY_DATABASE_URL,
#                        connect_args={"check_same_thread": False})

# PostgreSQL connection
# SQL_ALCHEMY_DATABASE_URL = "postgresql://postgres:admin@localhost/TodoApplicationDatabase"
# engine = create_engine(SQL_ALCHEMY_DATABASE_URL)

# MySql connection
SQL_ALCHEMY_DATABASE_URL = "mysql+pymysql://root:admin@localhost:3306/TodoApplicationDatabase"
engine = create_engine(SQL_ALCHEMY_DATABASE_URL)


SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind=engine)

Base = declarative_base()