from datetime import datetime
import bleach
from markdown import markdown

from flask_sqlalchemy import SQLAlchemy
from flask import Flask

from . import db

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def to_json(self):
        json_post = {
            'url': url_for('posts', id=self.id),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'comments_count': self.comments.count()
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            # need to raise an error here
            return
        return Post(body=body)

    @staticmethod
    def on_change_body(target, value, oldvalue, initiator):
        allow_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                    'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allow_tags, strip=True
        ))

db.event.listen(Post.body, 'set', Post.on_change_body)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def to_json(self):
        if self.disabled:
            return {
                'disabled': True,
                'body': ''
            }
        json_comment = {
            'url': url_for('api.get_comments', id=self.id),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'disabled': self.disabled,
            'post_id': self.post_id
        }
        return json_comment

    @staticmethod
    def from_json(json_comment):
        body = json_post.get(body)
        if body is None or body == '':
            # need to raise an error here
            return
        return Comment(body=body)

    @staticmethod
    def on_change_body(target, value, oldvalue, initiator):
        allowed_tag = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                      'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tag, strip=True
        ))

db.event.listen(Comment.body, 'set', Comment.on_change_body)

class Link(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    link = db.Column(db.Text)
    description = db.Column(db.Text)
