from flask_script import Manager
from app import create_app
from config import config
from datetime import timedelta


app = create_app()
app.secret_key = config.SECRET_KEY
app.permanent_session_lifetime = timedelta(minutes=60)
# manager = Manager(app)

# @manager.option('-h', '--host', dest='host', default='127.0.0.1')
# @manager.option('-p', '--port', dest='port', type=int, default=5000)
# @manager.option('-w', '--workers', dest='workers', type=int, default=2)
# @manager.option('-t', '--timeout', dest='timeout', type=int, default=60)
# def gunicorn(host, port, workers,timeout):
#     """Start the Server with Gunicorn"""
#     from gunicorn.app.base import Application
#
#     class FlaskApplication(Application):
#
#         def init(self, parser, opts, args):
#             return {
#                 'bind': '{0}:{1}'.format(host, port),
#                 'workers': workers, 'timeout': timeout
#
#             }
#
#         def load(self):
#             return app
#
#     application = FlaskApplication()
#     return application.run()


if __name__ == '__main__':
    app.run()

