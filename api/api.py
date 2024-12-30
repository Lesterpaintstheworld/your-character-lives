from functools import wraps
from flask import Flask, request, jsonify
from flask_restful import Resource, Api, abort
from marshmallow import ValidationError

from .api_models import MemorySchema, PerformanceSchema, ConfigSchema
from ..config import Config
import psutil
import time
import logging

app = Flask(__name__)
api = Api(app)
config = Config()
logger = logging.getLogger(__name__)

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            abort(401, message="Missing or invalid authorization header")
        token = auth_header.split(' ')[1]
        if token != config.API_TOKEN:
            abort(401, message="Invalid token")
        return f(*args, **kwargs)
    return decorated

class MemoryResource(Resource):
    @require_auth
    def get(self, memory_id=None):
        try:
            if memory_id:
                # Get specific memory
                memory = {"id": memory_id, "content": "Sample memory", "timestamp": time.time()}
                return MemorySchema().dump(memory)
            # Get all memories
            memories = [{"id": "1", "content": "Sample memory", "timestamp": time.time()}]
            return MemorySchema(many=True).dump(memories)
        except Exception as e:
            logger.error(f"Error in GET /memory: {str(e)}")
            abort(500, message="Internal server error")

    @require_auth
    def post(self):
        try:
            data = MemorySchema().load(request.json)
            # Process memory creation
            return {"message": "Memory created", "id": data["id"]}, 201
        except ValidationError as err:
            abort(400, message=str(err.messages))
        except Exception as e:
            logger.error(f"Error in POST /memory: {str(e)}")
            abort(500, message="Internal server error")

    @require_auth
    def delete(self, memory_id):
        try:
            # Process memory deletion
            return "", 204
        except Exception as e:
            logger.error(f"Error in DELETE /memory: {str(e)}")
            abort(500, message="Internal server error")

class PerformanceResource(Resource):
    @require_auth
    def get(self):
        try:
            performance = {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.Process().memory_info().rss / 1024 / 1024,
                "uptime": time.time() - psutil.boot_time(),
                "active_threads": len(psutil.Process().threads()),
                "audio_latency": 0.0  # Placeholder for actual audio latency
            }
            return PerformanceSchema().dump(performance)
        except Exception as e:
            logger.error(f"Error in GET /performance: {str(e)}")
            abort(500, message="Internal server error")

class ConfigResource(Resource):
    @require_auth
    def get(self):
        try:
            config_data = {
                "screenshot_interval": config.SCREENSHOT_INTERVAL,
                "audio_format": config.AUDIO_FORMAT,
                "channels": config.CHANNELS,
                "sample_rate": config.SAMPLE_RATE,
                "record_duration": config.RECORD_DURATION
            }
            return ConfigSchema().dump(config_data)
        except Exception as e:
            logger.error(f"Error in GET /config: {str(e)}")
            abort(500, message="Internal server error")

    @require_auth
    def put(self):
        try:
            data = ConfigSchema().load(request.json)
            # Update configuration
            return {"message": "Configuration updated"}, 200
        except ValidationError as err:
            abort(400, message=str(err.messages))
        except Exception as e:
            logger.error(f"Error in PUT /config: {str(e)}")
            abort(500, message="Internal server error")

# Register resources
api.add_resource(MemoryResource, '/api/memory', '/api/memory/<string:memory_id>')
api.add_resource(PerformanceResource, '/api/performance')
api.add_resource(ConfigResource, '/api/config')

@app.errorhandler(404)
def not_found(error):
    return jsonify({"message": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"message": "Internal server error"}), 500
