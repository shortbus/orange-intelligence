import json


def get_available_functions():
    return {"upper_case:": lambda x: x.upper(),
            "lower_case": lambda x: x.lower(),
            "pretty_json": lambda x: json.dumps(json.loads(x), indent=4),
            "pasticcino": lambda x: x + " pasticcino"
            }
