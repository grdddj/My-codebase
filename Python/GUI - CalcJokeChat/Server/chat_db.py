import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import sessionmaker

WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

db_file_path = "chat.sqlite"
db_file_path = os.path.join(WORKING_DIRECTORY, db_file_path)

# TODO: Notifications table - storing notification and IP addresses who saw them
# TODO: User settings table - to remember user preferences


def return_engine_and_session():
    engine = create_engine(f'sqlite:///{db_file_path}?check_same_thread=False')

    Session = sessionmaker(bind=engine)
    session = Session()

    return engine, session


Base = declarative_base()


class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    id = Column(Integer, primary_key=True)
    chat_name = Column(String)
    user_name = Column(String)
    message_type = Column(String)
    message = Column(String)
    answer_to_message = Column(String)
    timestamp = Column(Float)
    ip_address = Column(String)
    details = Column(String)

    def __repr__(self):
        return (
            f"<Chat(chat_name='{self.chat_name}', user_name='{self.user_name}', "
            f"message='{self.message}'), answer_to_message='{self.answer_to_message}'), "
            f"timestamp='{self.timestamp}', ip_address='{self.ip_address}'), "
            f"details='{self.details}'>"
        )


class LastUpdate(Base):
    __tablename__ = 'last_update'

    id = Column(Integer, primary_key=True)
    version_identifier = Column(String)
    timestamp = Column(Float)
    details = Column(String)

    def __repr__(self):
        return "<LastUpdate(version_identifier='{}', timestamp='{}', details='{}')>".format(
            self.version_identifier, self.timestamp, self.details)


if __name__ == "__main__":
    engine, session = return_engine_and_session()

    # Creates all the specified tables (if they do not already exist)
    Base.metadata.create_all(engine)
    session.commit()
