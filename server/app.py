from flask import Flask, request, session, make_response, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

from .config import Config


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
        from .Helpers.parallel_scrape_helper import run_parallel_scrapes
        group_result = run_parallel_scrapes(search)
        response = {
            "group_task_id": group_result['group_id'],
            "individal_task_ids": group_result['task_ids'],
            "Search": search if search else None
        }
        return jsonify(response), 202



    @app.route('/scrape/status', methods=['POST'])
    def scrape_status():
        from .celery_app import celery
        data = request.get_json()
        group_id = data.get('group_id')
        task_ids = data.get('task_ids', [])
        
        states = {}
        results = {}
        for task_id in task_ids:
            async_results = celery.AsyncResult(task_id)
            state = async_results.state
            states[task_id] = state
            if state == "SUCCESS":
                results[task_id] = async_results.result


        all_ready = all(state == "SUCCESS" for state in states.values())
        
        response = {
            "group_id": group_id,
            "states": states,
            "all_ready": all_ready,
            "results": results if all_ready else None
        }
        return jsonify(response), 200


    return app




if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)