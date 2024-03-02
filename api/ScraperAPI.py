from flask import Flask, request, jsonify
from flask_cors import CORS
from ProcessSearcher import ProcessSearcher

class ScraperAPI:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)

        @self.app.route("/", methods=["POST"])
        def search_process():
            data_request = request.get_json()
            data_response = ProcessSearcher(data_request)
            return data_response.json_response
        
        self.app.run(debug=True)