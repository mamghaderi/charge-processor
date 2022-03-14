import falcon
from charge.api import Rate


def create():
    app = falcon.App()
    app.add_route('/rate', Rate())
    return app


app = create()
