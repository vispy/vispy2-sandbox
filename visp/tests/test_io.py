import os
import tempfile


from visp import load, loads, dump, dumps


ref_commands = [
    {
        "action": "create_canvas",
        "id": 1,
        "width": 10,
        "height": 10,
    },
    {
        "action": "create_node",
        "id": 2,
    },
]


text_toml = """
[[command]]
action = "create_canvas"
id = 1
width = 10
height = 10

[[command]]
action = "create_node"
id = 2
"""

text_yaml1 = """
action: create_canvas
height: 10
id: 1
width: 10
---
action: create_node
id: 2
"""

text_yaml2 = """
- action: create_canvas
  height: 10
  id: 1
  width: 10

- action: create_node
  id: 2
"""

text_json = """
[
    {
        "action": "create_canvas",
        "id": 1,
        "width": 10,
        "height": 10
    },
    {
        "action": "create_node",
        "id": 2
    }
]
"""


def test_toml():
    assert ref_commands == loads(text_toml)

    assert text_toml.strip() == dumps(ref_commands, "toml").strip()

    filename = os.path.join(tempfile.gettempdir(), "visp_io.toml")
    dump(ref_commands, filename)
    assert load(filename) == ref_commands


def test_yaml():
    assert ref_commands == loads(text_yaml1)
    assert ref_commands == loads(text_yaml2)

    assert text_yaml1.strip() == dumps(ref_commands, "yaml").strip()

    filename = os.path.join(tempfile.gettempdir(), "visp_io.yaml")
    dump(ref_commands, filename)
    assert load(filename) == ref_commands


def test_json():
    assert ref_commands == loads(text_json)

    assert text_json.strip() == dumps(ref_commands, "json").strip()

    filename = os.path.join(tempfile.gettempdir(), "visp_io.json")
    dump(ref_commands, filename)
    assert load(filename) == ref_commands


if __name__ == "__main__":
    for ob in list(globals().values()):
        if callable(ob) and ob.__name__.startswith("test_"):
            print(f"Running {ob.__name__} ...")
            ob()
    print("Done")
