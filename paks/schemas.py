__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

## ContainerConfig Schema

schema_url = "https://json-schema.org/draft-07/schema/#"

## Settings.yml (loads as json)

# Currently all of these are required
settingsProperties = {
    "updated_at": {"type": ["string", "null"]},
    "username": {"type": ["string", "null"]},
    "email": {"type": ["string", "null"]},
}

settings = {
    "$schema": schema_url,
    "title": "Settings Schema",
    "type": "object",
    "required": [],
    "properties": settingsProperties,
    "additionalProperties": False,
}
