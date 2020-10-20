from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text, Unicode, String
from sqlalchemy.orm import sessionmaker
from db_credentials import DBConfig


def return_engine_and_session():
    host = DBConfig.host
    database = DBConfig.database
    user = DBConfig.user
    password = DBConfig.password
    engine = create_engine('mysql+pymysql://{}:{}@{}/{}?charset=utf8'.format(user, password, host, database))

    # Creating a session connected with our DB
    Session = sessionmaker(bind=engine)
    session = Session()

    return engine, session


# Creating a base class for the creation of our custom classes (tables)
Base = declarative_base()


# Declaring a table as a custom class inheriting the Base class
class Comment(Base):
    __tablename__ = 'comments_idnes'

    id = Column(Integer, primary_key=True)
    article_id = Column(String(100))
    author = Column(Unicode(200))
    content = Column(Text)
    plus = Column(Integer)
    minus = Column(Integer)

    def __repr__(self):
        return "<Comment(author='{}', plus='{}', minus='{}')>".format(
            self.author, self.plus, self.minus)


# Declaring a table as a custom class inheriting the Base class
class Article(Base):
    __tablename__ = 'articles_idnes'

    id = Column(String(100), primary_key=True)
    name = Column(Unicode(200))
    link = Column(Unicode(500))
    comment_amount = Column(Integer)

    def __repr__(self):
        return "<Article(id={}, name='{}')>".format(
            self.id, self.name)


if __name__ == "__main__":
    engine, session = return_engine_and_session()

    # Creates all the specified tables (if they do not already exist)
    Base.metadata.create_all(engine)
    session.commit()
