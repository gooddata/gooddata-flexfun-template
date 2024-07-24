# (C) 2024 GoodData Corporation
from typing import Optional

import gooddata_flight_server as gf
import pyarrow
import structlog
from gooddata_flight_server import ServerContext
from gooddata_flight_server.tasks.base import ArrowData

_LOGGER = structlog.get_logger("sample_flex_function")


class SampleFlexFunction(gf.FlexFun):
    """
    A sample FlexFunction. This serves static data. It is not very useful but is
    good starting point to explain FlexFunctions:

    - Specify a nice name in `Name` field -> this will be visible in GoodData's
      semantic model
    - Specify `Schema` which describes the result -> this information will be used
      to populate data set columns in GoodData's semantic model

    The `call` method does the heavy lifting. This is where you add your custom code
    that is supposed to generate the result. Typically, the `call` method should inspect
    the parameters and do the computation as necessary.

    NOTE: when GoodData invokes your FlexFunction, it may provide hint on which
    columns it is interested in - it will be always a subset of all columns defined in
    the `Schema`.

    Your code MAY take this into account and return only those desired  columns. This is
    just a basic optimization that your can leverage to save bandwidth. The presence of
    `columns` does not mean your function should perform additional aggregations or alter
    how it does the computation - it only tells your code that you can trim some columns
    from the result.

    If you want to learn more, check out the class documentation on the `gf.FlexFun`
    class.
    """

    Name = "SampleFlexFunction"
    Schema = pyarrow.schema(
        [
            pyarrow.field("attribute1", pyarrow.string()),
            pyarrow.field("attribute2", pyarrow.string()),
            pyarrow.field("attribute3", pyarrow.bool_()),
            pyarrow.field("fact1", pyarrow.float64()),
            pyarrow.field("fact2", pyarrow.float64()),
            pyarrow.field("fact3", pyarrow.int64()),
        ]
    )

    _StaticData = pyarrow.table(
        {
            "attribute1": ["id1", "id2", "id3", "id4", "id5", "id6"],
            "attribute2": ["value1", "value2", "value3", "value1", "value2", "value3"],
            "attribute3": [True, True, True, False, False, False],
            "fact1": [123.456, 23.45, 8.76, 1.23, 34.56, 567.89],
            "fact2": [0.1, 0.2, 0.3, 0.15, 0.25, 0.35],
            "fact3": [111, 222, 333, 444, 555, 666],
        }
    )

    def call(
        self,
        parameters: dict,
        columns: Optional[tuple[str, ...]],
        headers: dict[str, list[str]],
    ) -> ArrowData:
        _LOGGER.info("function_called", parameters=parameters)

        return self._StaticData

    @staticmethod
    def on_load(ctx: ServerContext) -> None:
        """
        You can do one-time initialization here. This function will be invoked
        exactly once during startup.

        Most often, you want to perform function-specific initialization that may be
        further driven by external configuration (e.g. env variables or TOML files).

        The FlexFunction host uses Dynaconf to work with configuration. You can access
        all available configuration via `ctx.settings`.

        :param ctx: server context
        :return: nothing
        """
        # value = ctx.settings.get("your-setting")
        pass
