import os
from pathlib import Path

import uvicorn

# Change dir to project root (three levels up from this file)
os.chdir(Path(__file__).parents[2])
# Set environment variable for uvicorn
os.environ["UVICORN_APP"] = "src.api.app:app"

uvicorn.main()
