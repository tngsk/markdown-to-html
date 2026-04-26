import os

def patch_server_file():
    with open("src/server.py", "r") as f:
        content = f.read()

    # Imports to update
    import_block = "from functools import lru_cache\n"
    new_import_block = "from functools import lru_cache\nimport os\n"
    content = content.replace(import_block, new_import_block)

    # Config function to update
    old_get_config = """@lru_cache(maxsize=1)
def get_security_config() -> dict:
    config = {
        "origins": ["http://localhost:8000", "http://127.0.0.1:8000"],
        "max_upload_size": 1024 * 1024  # Default 1MB
    }
    try:
        with open("config.toml", "rb") as f:
            config_data = tomllib.load(f)
            if "security" in config_data:
                sec = config_data["security"]
                if "cors-allowed-origins" in sec:
                    config["origins"] = sec["cors-allowed-origins"]
                if "max-upload-size" in sec:
                    config["max_upload_size"] = sec["max-upload-size"]
    except Exception as e:
        logger.warning(f"Could not load security config from config.toml: {e}")
    return config"""

    new_get_config = """@lru_cache(maxsize=1)
def get_security_config() -> dict:
    config = {
        "origins": ["http://localhost:8000", "http://127.0.0.1:8000"],
        "methods": ["*"],
        "headers": ["*"],
        "max_upload_size": 1024 * 1024  # Default 1MB
    }

    # Load from config.toml
    try:
        with open("config.toml", "rb") as f:
            config_data = tomllib.load(f)
            if "security" in config_data:
                sec = config_data["security"]
                if "cors-allowed-origins" in sec:
                    config["origins"] = sec["cors-allowed-origins"]
                if "max-upload-size" in sec:
                    config["max_upload_size"] = sec["max-upload-size"]
    except Exception as e:
        logger.warning(f"Could not load security config from config.toml: {e}")

    # Enforce production security rules
    is_production = os.environ.get("ENVIRONMENT", "").lower() == "production"
    if is_production:
        # Remove wildcard and null from origins
        config["origins"] = [
            origin for origin in config["origins"]
            if origin not in ("*", "null")
        ]
        # If no origins left, restrict completely
        if not config["origins"]:
            config["origins"] = ["http://localhost:8000"] # fallback to least privilege

        # Restrict methods and headers
        config["methods"] = ["GET", "POST", "OPTIONS"]
        config["headers"] = ["Content-Type", "Content-Length", "Accept"]

    return config"""

    content = content.replace(old_get_config, new_get_config)

    # Middleware to update
    old_middleware = """app.add_middleware(
    CORSMiddleware,
    allow_origins=get_security_config()["origins"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)"""

    new_middleware = """app.add_middleware(
    CORSMiddleware,
    allow_origins=get_security_config()["origins"],
    allow_credentials=False,
    allow_methods=get_security_config()["methods"],
    allow_headers=get_security_config()["headers"],
)"""

    content = content.replace(old_middleware, new_middleware)

    with open("src/server.py", "w") as f:
        f.write(content)

patch_server_file()
