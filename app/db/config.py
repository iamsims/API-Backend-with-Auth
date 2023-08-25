from decouple import config

def read_config_or_secret(config_key, default=None, allow_missing=False):
    result = config(config_key, None)
    if result is None:
        return read_secret(
            config_key, default, allow_missing,
            on_missing=ValueError("Missing both configuration variables :" + config_key + " and " +
                                  config_key + "_FILE")
        )
    return result

def read_secret(config_key, default=None, allow_missing=False, on_missing=None):
    secret_file = config(config_key + "_FILE", None)
    print("read from secret file")
    if secret_file is not None:
        try:
            with open(secret_file) as file:
                return file.read()
        except Exception as e:
            print("Failed to read secret file: ", secret_file, e.__class__.__name__, str(e.args))
    elif allow_missing:
        return default
    else:
        if on_missing:
            raise on_missing
        raise ValueError("Configuration variable is not set :" + config_key + "_FILE")

class DatabaseConfig:
    url = read_config_or_secret("DB_URL")
    print("[Db Connect Url] ", url)