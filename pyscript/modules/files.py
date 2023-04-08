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
    except:
        result = default_value

    return result


@pyscript_executor
def write(file_name, key_list=None, value=None):
    if os.path.exists(f"{constants.BASE_FILE_PATH}{file_name}.yaml"):
        with open(f"{constants.BASE_FILE_PATH}{file_name}.yaml") as file:
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

    contents_edit[key_list[-1]] = value

    with open(file_name, "w") as file:
        yaml.safe_dump(contents, file)


@pyscript_executor
def append(file_name, value=None):
    if os.path.exists(f"{constants.BASE_FILE_PATH}{file_name}.yaml"):
        with open(f"{constants.BASE_FILE_PATH}{file_name}.yaml") as file:
            contents = yaml.safe_load(file)
            if contents is None:
                contents = []
    else:
        contents = []

    if isinstance(contents, dict):
        contents[datetime.now()] = value
    else:
        contents.append(value)

    with open(file_name, "w") as file:
        yaml.safe_dump(contents, file)
