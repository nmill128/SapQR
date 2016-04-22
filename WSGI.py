from app import app
from werkzeug.debug import DebuggedApplication

if __name__ == "__main__":
	#app = DebuggedApplication(app, evalex=True)

    app.run()