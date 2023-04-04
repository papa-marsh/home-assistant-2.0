import yaml
import constants


@pyscript_executor
def read(file_name, key_list=None, default_value=None, file_type="yaml"):
    try:
        with open(f"{constants.BASE_FILE_PATH}{file_name}.yaml") as file:
            if file_type == "yaml":
                result = yaml.safe_load(file)
            else:
                result = file.read()

        if key_list and isinstance(result, dict):
            for key in key_list:
                result = result[key]
    except:
        result = default_value

    return result