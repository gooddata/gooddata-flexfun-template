# (C) 2024 GoodData Corporation
import orjson
import pyarrow.flight

#
# Few sample end-to-end tests which exercise the FlexFunction by making
# Flight RPC calls.
#


def test_list_flexfuns(testing_flexfun_server):
    c = pyarrow.flight.FlightClient(testing_flexfun_server.location)

    for flight_info in c.list_flights():
        function_descriptor = orjson.loads(flight_info.descriptor.command)

        assert function_descriptor["function_name"] == "SampleFlexFunction"


def test_function_call(testing_flexfun_server):
    c = pyarrow.flight.FlightClient(testing_flexfun_server.location)

    flight_info = c.get_flight_info(
        pyarrow.flight.FlightDescriptor.for_command(
            orjson.dumps({"function_name": "SampleFlexFunction"})
        )
    )
    data: pyarrow.Table = c.do_get(flight_info.endpoints[0].ticket).read_all()

    assert data.num_rows == 6
    assert data.num_columns == 6
