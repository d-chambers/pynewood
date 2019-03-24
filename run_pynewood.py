"""
Run this to start the test server.
"""
from app import app

if __name__ == "__main__":
    # app = create_app()
    app.run(debug=False)
