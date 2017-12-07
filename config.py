import os

basedir = os.path.abspath(os.path.dirname(__file__))

class config:
    SECRET_KEY = '^@maiqing_090412$^'
    MAIL_SUBJECT_PREFIX = '[AukeyIT]'
    MAIL_SENDER = 'Towell Admin<Towell@blog.com>'
    db_config = dict(
        host='10.1.1.86',
        user='sa',
        passwd='sa@aukey2017',
        port=3306,
        db='sa',
        charset='utf8')
    POSTS_PER_PAGE = 10
    debug = True

    @staticmethod
    def init_app(app):
        pass
