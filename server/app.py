from flask import Flask, request, session, make_response, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

from config import Config


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
api = Api()

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    bcrypt.init_app(app)
    api.init_app(app)
    CORS(app)

    @app.route('/scrape/<search>', methods=['GET'])
    def scrape(search):
        from celery_app import celery
        from tasks.scraper import run_scrape
        task = run_scrape.delay(search)
        task_result = celery.AsyncResult(task.id)
        response = {
            "task_id": task.id,
            "state": task_result.state,
            "Search": search if search else None
        }
        return jsonify(response), 202

    @app.route('/scrape/status/<task_id>', methods=['GET'])
    def scrape_status(task_id):
        from celery_app import celery
        task_result = celery.AsyncResult(task_id)
        response = {
            "task_id": task_id,
            "state": task_result.state,
            "result": task_result.result
        }
        return jsonify(response), 200


    return app




if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)