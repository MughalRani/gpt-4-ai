from typing import Dict, Any, Optional
from jsonpath_ng import parse as jsonpath_parse

from langchain.schema.runnable import RunnableSerializable, RunnableConfig
from langchain.schema.runnable.utils import Input, Output

from ix.utils.json import to_json_serializable


class JSONPath(RunnableSerializable[Input, Output]):
    """Parse a value from inputs using a JSONPath"""

    path: str
    """JSON Path to load."""

    return_list: bool = False
    """If True, return results as a list."""

    def invoke(
        self,
        input: Dict[str, Any],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Output:
        jsonpath_expr = jsonpath_parse(self.path)
        formatted_input = to_json_serializable(input)
        json_matches = jsonpath_expr.find(formatted_input)

        if len(json_matches) > 1 or self.return_list:
            return [match.value for match in json_matches]
        elif len(json_matches) == 0:
            raise ValueError(f"could not find input at {self.path} searched: {input}")
        else:
            return json_matches[0].value