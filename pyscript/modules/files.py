from datetime import datetime
import os
import yaml
from typing import Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from . import constants
    from .dummy import *
else:
    import constants


class File:
    def __init__(self, file_name: str) -> None:
        """
        Requires the filename in string format without the .yaml extension
        """
        self.path = f"{constants.BASE_FILE_PATH}{file_name}.yaml"

    @pyscript_executor
    def read(self, key_list: List[str] = None, default_value: Any = None):
        """
        Reads the full contents of a file or the value at a given key path if provided.
        If key_list is provided, read the value at the corresponding dictionary path.
        """
        try:
            with open(self.path) as file:
                result = yaml.safe_load(file)

            if key_list and isinstance(result, dict):
                for key in key_list:
                    result = result[key]
        except Exception:
            result = default_value

        return result

    @pyscript_executor
    def write(self, key_list: List[str] = None, value: Any = None) -> None:
        """
        Writes to a file or the value at a given key path.
        If key_list is provided, write/overwrite the value at the corresponding dictionary path.
        Will create the file if it doesn't exist.
        """
        if os.path.exists(self.path):
            with open(self.path) as file:
                contents = yaml.safe_load(file)
                if contents is None:
                    contents = {}
        else:
            contents = {}

        contents_edit = contents
        for key in key_list[:-1]:
            if key not in contents_edit:
                contents_edit[key] = {}
            contents_edit = contents_edit[key]

        if key_list:
            contents_edit[key_list[-1]] = value

        with open(self.path, "w") as file:
            yaml.safe_dump(contents, file)

    @pyscript_executor
    def append(self, value: Any = None) -> None:
        """
        Appends a line at the end of the given file.
        Works for List and Dict files. Dict key is set to current timestamp.
        Will create the file as a List if it doesn't exist.
        """
        if os.path.exists(self.path):
            with open(self.path) as file:
                contents = yaml.safe_load(file)
                if contents is None:
                    contents = []
        else:
            contents = []

        if isinstance(contents, dict):
            contents[datetime.now()] = value
        else:
            contents.append(value)

        with open(self.path, "w") as file:
            yaml.safe_dump(contents, file)

    @pyscript_executor
    def overwrite(self, contents: Any) -> None:
        """
        Completely overwrites a file with the value of the contents arg.
        Will create the file if it doesn't exist.
        """
        with open(self.path, "w") as file:
            yaml.safe_dump(contents, file)
