#!/bin/bash
# (C) 2024 GoodData Corporation

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SERVER_CMD="${SCRIPT_DIR}/.venv/bin/gooddata-flight-server"

export PYTHONPATH="${SCRIPT_DIR}/src"

# You can set the following environment variables to override
# any values that may be loaded from configuration.
#
#export GOODDATA_FLIGHT_SERVER__LISTEN_HOST="..."
#export GOODDATA_FLIGHT_SERVER__LISTEN_PORT="..."
#export GOODDATA_FLIGHT_SERVER__ADVERTISE_HOST="..."
#export GOODDATA_FLIGHT_SERVER__ADVERTISE_PORT="..."
#export GOODDATA_FLIGHT_SERVER__AUTHENTICATION_METHOD="token"
#export GOODDATA_FLIGHT_SERVER__TOKEN_VERIFICATION="EnumeratedTokenVerification"
#export GOODDATA_FLIGHT_ENUMERATED_TOKENS__TOKENS='[""]'

$SERVER_CMD start \
              --config \
                config/server.config.toml \
                config/auth.config.toml \
                config/flexfun.config.toml \
              --dev-log