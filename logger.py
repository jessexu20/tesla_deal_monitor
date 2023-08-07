import json
from typing import Dict, Any


class Logger:

    def __init__(self, file_path: str):
        self.file_path = file_path

    async def async_write_log_file(self, content: Dict[str, Any]):
        with open(self.file_path, "a") as file:
            file.write(json.dumps(content) + "\n")
