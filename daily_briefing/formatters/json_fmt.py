"""JSON formatter — structured output for piping."""

import json


def format_json(results):
    return json.dumps(results, indent=2)
