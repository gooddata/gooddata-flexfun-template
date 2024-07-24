# (C) 2024 GoodData Corporation
import orjson
import pyarrow.flight


def _list_flexfuns():
    c = pyarrow.flight.FlightClient("grpc://127.0.0.1:17001")
    for flight_info in c.list_flights():
        function_descriptor = orjson.loads(flight_info.descriptor.command)

        print(f"Function name  : {function_descriptor['function_name']}")
        print(f"Function result:\n{flight_info.schema}")


def _call_sample_function():
    c = pyarrow.flight.FlightClient("grpc://127.0.0.1:17001")
    flight_info = c.get_flight_info(
        pyarrow.flight.FlightDescriptor.for_command(
            orjson.dumps({"function_name": "SampleFlexFunction"})
        )
    )
    data = c.do_get(flight_info.endpoints[0].ticket).read_all()

    print(data)


if __name__ == "__main__":
    _list_flexfuns()
    _call_sample_function()
