import os
import warnings

import toml


TYPES = {"int": int, "str": str, "float": float, "number": (float, int), "list": list}


class Checker:

    commands = None
    enums = None

    def __init__(self, raise_on_error=False):
        if self.commands is None:
            self._load_protocol()
        self._raise_on_error = bool(raise_on_error)
        self._objects = {}

    def _load_protocol(self):

        filename = os.path.abspath(os.path.join(__file__, "..", "protocol.toml"))
        with open(filename, "rt", encoding="utf-8") as f:
            protocol = toml.load(f)

        commands = {}
        for command in protocol["command"]:
            action = command["action"]
            assert action not in commands, f"Duplicate command {action}"
            commands[action] = command

        Checker.enums = protocol["enums"][0]
        Checker.commands = commands

    def check_command(self, command):
        try:
            self._check_command(command)
        except AssertionError as err:
            msg = "Protocol mismatch: " + str(err)
            if self._raise_on_error:
                raise AssertionError(msg)
            else:
                print(msg)

    def _check_command(self, command):
        # Basic checks
        assert isinstance(command, dict), "Commands must be dict."
        assert "action" in command, "Commands must have an 'action' field."

        # Get reference command
        action = command["action"]
        assert action in self.commands, f"Action '{action}' not known."
        ref_command = self.commands[action]

        # Store object?
        if action.startswith("create_"):
            assert command["id"] not in self._objects, "Duplicate id {command['id']}"
            self._objects[command["id"]] = action.partition("_")[2]

        # Check that the fields match
        fields = set(command.keys())
        ref_fields = set(ref_command.keys())
        missing = ref_fields.difference(fields)
        unknown = fields.difference(ref_fields)
        assert not missing, f"Missing fields in {action} command: {missing}"
        assert not unknown, f"Unknown fields in {action} command: {unknown}"

        # Check each field
        for key in fields:
            if key == "action":
                continue
            val = command[key]
            ref_val = ref_command[key]
            if ref_val.startswith("id:"):
                _, _, type = ref_val.partition(":")
                assert (
                    val in self._objects
                ), f"The {key}-id {val} given with {action} is unknown"
                assert (
                    type == self._objects[val]
                ), f"The {key}-id {val} given with {action} is not a {type}"
            elif ref_val.startswith("enum:"):
                _, _, enum_name = ref_val.partition(":")
                values = self.enums[enum_name]  # keyerror is bug in protocol
                assert val in values, f"The {action}.{key} enum {val} is invalid"
            elif ref_val.startswith("list<"):
                count, type = ref_val.partition("<")[2].strip(">").split(",")
                count, type = int(count), TYPES[type]
                assert isinstance(val, list), f"The {action}.{key} must be a list"
                assert (
                    len(val) == count
                ), f"The {action}.{key} must have {count} elements"
                assert all(
                    isinstance(v, type) for v in val
                ), f"The {action}.{key} must have {type} elements"
            else:
                type = TYPES[ref_val]  # keyerror is bug in protocol
                assert isinstance(val, type), f"The {action}.{key} must be a {ref_val}"


def check_commands(commands, raise_on_error=False):
    """Check that the list of commands match the formal protocol."""
    checker = Checker(raise_on_error)
    for command in commands:
        checker.check_command(command)
