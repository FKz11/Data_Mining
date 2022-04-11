import sqlalchemy.exc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models


class Database:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        models.Base.metadata.create_all(bind=self.engine)
        self.maker = sessionmaker(bind=self.engine)

    def _get_or_create(self, session, model, filter_field, **data):
        instance = session.query(model).filter_by(**{filter_field: data[filter_field]}).first()
        if not instance:
            instance = model(**data)
        return instance

    def add_post(self, data):
        session = self.maker()
        post = self._get_or_create(session, models.Post, "id", **data["post_data"])
        author = self._get_or_create(session, models.Author, "url", **data["author_data"])
        tags = map(
            lambda tag_data: self._get_or_create(session, models.Tag, "name", **tag_data),
            data["tags_data"],
        )
        comments = map(
            lambda comment_data: self._get_or_create(session, models.Comment, "id", **comment_data),
            data["comments_data"],
        )
        post.author = author
        post.tags.extend(tags)
        post.comments.extend(comments)
        for comment in post.comments:
            if comment.parent_id:
                comment.parent = session.query(models.Comment).filter_by(id=comment.parent_id).first()
        try:
            session.add(post)
            session.commit()
        except sqlalchemy.exc.IntegrityError as error:
            print(error)
            session.rollback()
        finally:
            session.close()
