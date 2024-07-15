from enum import StrEnum

ROYALE_PATTERN = r".*Royale\d*"

class Field(StrEnum):
    """Represents the JSON fields that appear on RePoE reponnses."""
    ID = "id"
    NAME = "name"
    TAGS = "tags"
    DOMAIN = "domain"
    CLASS = "item_class"
    DROP_LEVEL = "drop_level"
    RELEASE_STATE = "release_state"
    FILTER_ITEM_CLASS = "filter_item_class"
    DISPLAY_NAME = "display_name"
    BASE_ITEM = "base_item"
    TAG = "tag"
    WEIGHT = "weight"
    SPAWN_WEIGHTS = "spawn_weights"
    REQUIRED_LEVEL = "required_level"
    GENERATION_TYPE = "generation_type"
