from datetime import datetime
import os
import yaml
import constants


@pyscript_executor
def read(file_name, key_list=None, default_value=None):
    try:
        with open(f"{constants.BASE_FILE_PATH}{file_name}.yaml") as file:
            result = yaml.safe_load(file)

        if key_list and isinstance(result, dict):
            for key in key_list:
                result = result[key]
    except Exception:
        result = default_value

    return result


@pyscript_executor
def write(file_name, key_list=None, value=None):
    path = f"{constants.BASE_FILE_PATH}{file_name}.yaml"
    if os.path.exists(path):
        with open(path) as file:
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

    with open(path, "w") as file:
        yaml.safe_dump(contents, file)


@pyscript_executor
def append(file_name, value=None):
    path = f"{constants.BASE_FILE_PATH}{file_name}.yaml"
    if os.path.exists(path):
        with open(path) as file:
            contents = yaml.safe_load(file)
            if contents is None:
                contents = []
    else:
        contents = []

    if isinstance(contents, dict):
        contents[datetime.now()] = value
    else:
        contents.append(value)

    with open(path, "w") as file:
        yaml.safe_dump(contents, file)


@pyscript_executor
def overwrite(file_name, contents):
    with open(f"{constants.BASE_FILE_PATH}{file_name}.yaml", "w") as file:
        yaml.safe_dump(contents, file)
