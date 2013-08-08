import sqlalchemy as sa
from sqlalchemy_utils import batch_fetch
from tests import TestCase


class TestBatchFetch(TestCase):
    def create_models(self):
        class Category(self.Base):
            __tablename__ = 'category'
            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.Unicode(255))

        class TextItem(self.Base):
            __tablename__ = 'text_item'
            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.Unicode(255))
            category_id = sa.Column(
                sa.Integer,
                sa.ForeignKey(Category.id)
            )

            type = sa.Column(sa.Unicode(255))

            __mapper_args__ = {
                'polymorphic_on': type
            }

        class Article(TextItem):
            __tablename__ = 'article'
            id = sa.Column(
                sa.Integer, sa.ForeignKey(TextItem.id), primary_key=True
            )
            __mapper_args__ = {
                'polymorphic_identity': u'article'
            }
            category = sa.orm.relationship(
                Category,
                backref=sa.orm.backref(
                    'articles'
                )
            )

        class BlogPost(TextItem):
            __tablename__ = 'blog_post'
            id = sa.Column(
                sa.Integer, sa.ForeignKey(TextItem.id), primary_key=True
            )
            __mapper_args__ = {
                'polymorphic_identity': u'blog_post'
            }
            category = sa.orm.relationship(
                Category,
                backref=sa.orm.backref(
                    'blog_posts'
                )
            )

        self.TextItem = TextItem
        self.Category = Category
        self.Article = Article
        self.BlogPost = BlogPost

    def setup_method(self, method):
        TestCase.setup_method(self, method)
        text_items = [
            self.Article(name=u'Article 1'),
            self.Article(name=u'Article 2'),
            self.Article(name=u'Article 3'),
            self.Article(name=u'Article 4'),
            self.BlogPost(name=u'BlogPost 1'),
            self.BlogPost(name=u'BlogPost 2'),
            self.BlogPost(name=u'BlogPost 3'),
            self.BlogPost(name=u'BlogPost 4')
        ]
        self.session.add_all(text_items)
        self.session.flush()
        category = self.Category(name=u'Category #1')
        category.articles = text_items[0:2]
        category.blog_posts = text_items[4:7]
        category2 = self.Category(name=u'Category #2')
        category2.articles = text_items[2:4]
        category2.blog_posts = text_items[-1:]
        self.session.add(category)
        self.session.add(category2)
        self.session.commit()

    def test_multiple_relationships(self):
        categories = self.session.query(self.Category).all()
        batch_fetch(
            categories,
            'articles',
            'blog_posts'
        )
        query_count = self.connection.query_count
        categories[0].articles[1]
        categories[0].blog_posts[0]
        assert self.connection.query_count == query_count
        categories[1].articles[1]
        categories[1].blog_posts[0]
        assert self.connection.query_count == query_count
