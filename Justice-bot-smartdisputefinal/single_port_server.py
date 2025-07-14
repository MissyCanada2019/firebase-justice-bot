
#!/usr/bin/env python3
from app import app
import logging

logging.basicConfig(level=logging.INFO)
logging.info("Starting single port server on port 5000...")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
