import json
import yaml
import toml


FORMAT_MAP = {"yml": "yaml", "jsn": "json"}


def load(file, format=None):
    """Read commands from filename, of file object."""

    # Get the text, depending on the input
    ext = None
    if isinstance(file, str):
        ext = file.split(".")[-1].lower()
        with open(file, "rb") as f:
            text = f.read().decode()
    elif hasattr(file, "read"):
        text = file.read()
        if isinstance(text, bytes):
            text = text.decode()
    else:
        raise ValueError(f"Cannot read commands from a {file.__class__.__name__}")

    return loads(text, format or ext)


def loads(text, format=None):
    """Read commands from text."""
    # Guess format from text if format is not provided
    if not format:
        if "[[command]]" in text:
            format = "toml"
        elif "action:" in text:
            format = "yaml"
        elif '"action":' in text or "'action':" in text:
            format = "json"
        elif not text.strip():
            return []
        else:
            raise ValueError("Cannot guess format from text.")

    # Parse!
    format = FORMAT_MAP.get(format, format)
    if format == "toml":
        return toml.loads(text).get("command", [])
    elif format == "yaml":
        commands = list(x for x in yaml.load_all(text, yaml.FullLoader))
        if len(commands) == 1 and isinstance(commands[0], list):
            commands = commands[0]
        return commands
    elif format == "json":
        return json.loads(text)
    else:
        raise ValueError(f"Unknown format '{format}'")


def dump(commands, file, format=None):
    """Write the commands to the given filename or file object."""
    if isinstance(file, str):
        ext = file.split(".")[-1].lower()
        text = dumps(commands, format or ext)
        with open(file, "wb") as f:
            f.write(text.encode())
    elif hasattr(file, "write"):
        text = dumps(commands, format)
        file.write(text)
    else:
        raise ValueError(f"Cannot dump commands from a {file.__class__.__name__}")


def dumps(commands, format):
    """Serialize the commands using the given format."""
    assert isinstance(commands, list)

    format = FORMAT_MAP.get(format, format)
    if format == "toml":
        return toml.dumps({"command": commands})
    elif format == "yaml":
        return yaml.dump_all(commands)
    elif format == "json":
        return json.dumps(commands, indent=4)
    else:
        raise ValueError(f"Unknown format '{format}'")
