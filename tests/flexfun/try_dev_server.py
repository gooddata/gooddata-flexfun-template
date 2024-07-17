# (C) 2024 GoodData Corporation
import orjson
import pyarrow.flight


def _list_flexfuns():
    c = pyarrow.flight.FlightClient("grpc://127.0.0.1:17001")
    for flight_info in c.list_flights():
        function_descriptor = orjson.loads(flight_info.descriptor.command)

        print(f"Function name  : {function_descriptor['function_name']}")
        print(f"Function result:\n{flight_info.schema}")


if __name__ == "__main__":
    _list_flexfuns()
