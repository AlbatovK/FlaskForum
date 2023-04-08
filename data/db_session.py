import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists

SqlAlchemyBase = sqlalchemy.ext.declarative.declarative_base()

__factory = None


def global_init(db_file, app):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise ValueError()

    conn_str = 'sqlite:///' + db_file.strip() + '?check_same_thread=False'

    from . import __all_models

    engine = sqlalchemy.create_engine(conn_str, echo=app.debug)

    do_prepopulate = not database_exists(engine.url)

    __factory = sqlalchemy.orm.sessionmaker(bind=engine)

    SqlAlchemyBase.metadata.create_all(engine)

    if do_prepopulate:
        with sqlalchemy.orm.Session(bind=engine) as prepopulate_session:
            tags = [
                __all_models.tag.Tag(name='TestTag'),
                __all_models.tag.Tag(name='Kotlin'),
                __all_models.tag.Tag(name='Java'),
                __all_models.tag.Tag(name='Python'),
                __all_models.tag.Tag(name='Machine Learning'),
                __all_models.tag.Tag(name='Android Developing'),
                __all_models.tag.Tag(name='Web Backend'),
                __all_models.tag.Tag(name='Databases'),
                __all_models.tag.Tag(name='Algorithms')
            ]

            user = __all_models.user.User(
                name='Admin',
                about='I like cats',
                email='idk@idk.com'
            )

            user.set_password('test')

            post = __all_models.post.Post(
                title="Welcome! This is a test post.",
                content="Hope that finally works...",
                user=user,
                tags=tags[1:3]
            )

            thread_message = __all_models.thread_message.ThreadMessage(
                content='Try Reddit',
                user=user,
                post=post
            )

            post.thread_messages.append(thread_message)

            prepopulate_session.add_all(tags)
            prepopulate_session.add(user)
            prepopulate_session.add(post)

            prepopulate_session.commit()


session = None


def create_session() -> Session:
    global __factory, session
    if not session:
        session = __factory(expire_on_commit=False) if callable(__factory) else None
    return session
