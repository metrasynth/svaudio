from enum import Enum


class Verb(str, Enum):
    ADDED_TAG = "added tag"
    REMOVED_TAG = "removed tag"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value
