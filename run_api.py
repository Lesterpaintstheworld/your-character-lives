from api.api import app
from config import Config

if __name__ == "__main__":
    config = Config()
    app.run(port=config.API_PORT, debug=config.API_DEBUG)
