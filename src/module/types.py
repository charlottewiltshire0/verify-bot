from sqlalchemy.types import TypeDecorator, String
import json


class JSONType(TypeDecorator):
    """Represents an immutable structure as a JSON-encoded string."""
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return None