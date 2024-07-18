# GoodData FlexFunctions host template

This repository serves as a template that you can use to create your own
Flight RPC server that hosts your custom-made FlexFunctions.

This template lets you focus on building and testing the FlexFunctions themselves;
the infrastructure and boilerplate related to hosting and exposing your functions
is handled by GoodData code.

## What is a FlexFunction

A FlexFunction is custom code that generates tabular data and can be integrated
with GoodData Cloud.

In many ways, the FlexFunction resembles 'table functions' (tabular user-defined-functions)
that are available in many database and data warehouse systems.

The FlexFunctions are intended for integration into the GoodData Cloud's semantic model
and are then used for report computation. These use cases influence how the interface of
FlexFunction looks like:

- The schema of tabular data returned by a function must be known up-front
- The function arguments are prescribed by GoodData Cloud and describe computation context
  in which the function is called

### Technical perspective

A FlexFunction is a class that implements the `FlexFun` interface. The concrete implementations
provide:

- Name of the function
- Schema of the returned tabular data
- Implementation of `call` method to compute and return the data

FlexFunctions are implemented on top of the Apache Arrow. The schema describing the tabular
data is expected to be an Apache Arrow Schema. The returned tabular data is either an Apache Arrow
Table (fully materialized data) or a RecordBatchReader (stream of data).

### FlexFunction hosting

The FlexFunction implementations are supposed to be hosted on a Flight RPC server which is
then added as a data source to GoodData Cloud or Cloud Native: thus, the FlexFunctions become
available in the semantic model and can be used in report computations.

This template project (backed by infrastructure available in GoodData Python SDK) solves and
simplifies the task of creating a production-ready Flight RPC server where the FlexFunctions
run.

The artifact produced by the template is a Docker image containing Flight RPC server with
your FlexFunctions plugged into it.

You then have to deploy and run this Docker image 'somewhere' - for example on some AWS EC2
instance and then add that location as data source to GoodData Cloud or Cloud Native.

## Getting Started

To get started with custom functions is easy. The only prerequisite is a working installation of
Python 3.11 and access to internet:

1.  Clone this template: `git clone git@github.com:gooddata/gooddata-flexfun-template.git <your-directory>`
2.  Navigate to your directory `cd <your-directory>`
3.  Bootstrap development environment `make dev`

    This will create Python Virtual Environment in `.venv` directory.

4.  [Optional] The project is set up with `.envrc` - if you use [direnv](https://direnv.net/), then do `direnv allow`

HINT: If you have trouble installing Python 3.11, we recommend using [pyenv](https://github.com/pyenv/pyenv).
First, correctly install pyenv using its installation guide. Then after step #2 above, do `pyenv install` and `pyenv local`.
Then you can continue with `make dev`

If you use PyCharm or IDEA, you can now open the project and:

1. Add existing virtual environment (bootstrapped in previous steps and available in `.venv` directory)
2. Mark `src` as sources root, mark `tests` as test sources root

## Developing FlexFunctions

The template sets initial convention where the FlexFunctions are located in [src/flexfun](./src/flexfun) directory. You
can find the [sample_function.py](./src/flexfun/sample_function.py) there. The easiest way to get poking around is
to modify this function to do your bidding.

### Adding new function

#### Adding the code

The only requirement is that your new FlexFunction must be a file inside the `src` directory and within that you
need to have a class implementing the `FlexFun` interface. See the [sample_function.py](./src/flexfun/sample_function.py)
for inspiration.

How your organize the implementations is completely up to you:

- If you have many small functions, then it may be enough to create file-per-function inside the
  existing `src/flexfun` directory.

- If, however, you expect that the implementation of the function may grow large and be split into
  multiple smaller files, then we recommend that you create a new Python package somewhere under `src`
  directory.

  For example, you can go with layout such as:

  - src/flexfun/function_name1/
    - api.py < this is where you have class implementing the FlexFun interface
    - any other files and sub-packages that the `api.py` depends on

  This way, each possibly complex function is separated in its own package, there is a well-defined
  entry point (the `api.py`) and then bunch of other files needed for the implementation - as you see fit.

IMPORTANT: if you create your own packages and sub-packages, make sure to include the `__init__.py` files -
otherwise you run risk of Import/ModuleLoad errors.

#### Registering the function

In order for the function to be loaded and exposed via Flight RPC, you need to register it to
the server. This is purely a configuration step:

- Open the [config/flexfun.config.toml](./config/flexfun.config.toml) configuration file
- Within that file, there is a `function` setting. This is a list of Python modules that are expected
  to contain the `FlexFun` implementations.

  You add name of Python module that contains the FlexFun. You code this the same way as when doing
  imports in Python.

  For example if you build your FlexFun in `src/flexfun/function_name1/api.py`, then you need to
  register `flexfun.function_name1.api`.

HINT: you can have multiple FlexFun implementations within a single Python source file. All those
implementations will be discovered and registered. This is fine to do if you have many small, trivial
functions. However, as the functions grow in complexity, the single file may grow too big and harder
to manage code-wise.

#### FlexFunctions recommendations

Your concrete FlexFunction implementation is integrated into GoodData Flight server which handles
all the technicalities and boilerplate related to sane operations and function invocations.

For every invocation of FlexFunction via the Flight RPC, the server will create a new instance
of your class. It is strongly recommended that this is as fast as possible and does not perform
any expensive initialization.

**HINT**: expensive one-time initialization can be done by overloading `on_load` method.

The server comes with built-in call queuing and separate thread pool that services the
invocations. You can configure this in [config/server.config.toml](./config/server.config.toml).

**IMPORTANT**: Your code must not make any assumptions that a thread that creates the FlexFunction
instance will be the same thread that invokes the `call`.

### Adding third party dependencies

If your function implementation requires some 3rd party libraries, you should add them to the
[requirements.txt](./requirements.txt) file. After you add the dependency, re-run `make dev`.

This will modify existing `.venv` and reinstall the dependencies. Usually, you do not have to
remove the existing `.venv`.

However, especially when adding more dependencies, removing dependencies or running into issues, we
recommend to re-bootstrap the environment: `rm -rf .venv && make dev`.

### Dev-testing

A FlexFunction is a piece of code like any other. The fact that it is exposed via Flight RPC
is a technical detail.

This template project comes with `pytest` pre-installed. You can test your FlexFunction
implementations as you see fit using the standard techniques. You can run the tests either
from IDE or use the `make test` target.

Typically, if your function does not do any crazy / non-standard stuff, then there is a very
solid guarantee that a function passing tests will run fine once it is running inside the
Flight RPC server.

Additionally, you can run the `make dev-server` which will start the full Flight RPC server
with your functions: you can do end-to-end testing using Flight RPC. For a simple manual smoke
test, look at the [try_dev_server.py](./tests/flexfun/try_dev_server.py) - this lists functions
available on the running dev server.

**HINT**: if you need additional third-party dependencies for dev/test, then add those to
the [requirements-dev.txt](./requirements-dev.txt).

### Template dev infrastructure

This project is set up with:

- [ruff](https://github.com/astral-sh/ruff) for linting, formating, import sorting
- [mypy](https://github.com/python/mypy) for type checking
- [pre-commit](https://github.com/pre-commit/pre-commit) hooks

The pre-commit hooks are enabled by default and run `ruff` and other basic hooks.
The use of `mypy` is optional - but we strongly encourage it especially if your functions
grow large.

There are a few Makefile targets for the usual tasks:

- `make mypy` - run type checker
- `make format-fix` - run ruff format and ruff check in auto-fix mode on all files
- `make fix-staged` - runs pre-commit on all staged files.
  this will do ruff format and check in auto-fix mode but just on the files you have modified.

**IMPORTANT**: Do keep in mind that pre-commit will not auto-stage files that were modified
as it was running the configured hooks. What this means is that commits will fail if
the `pre-commit` hooks getting involved and modify (auto-fix) the files. You typically
then have to re-drive the commit. The recommended workflow is to run `make fix-staged` first,
and when green proceed with the commit itself.

#### Secrets for dev and dev testing

During the bootstrap, the `make dev` will create `.secrets` file. This file is included in .gitignore
and will not be committed to git. It is intended to hold any env variables that contain secrets.

If you use `direnv`, then the contents of this file will be automatically sourced when you navigate to
the directory. Otherwise, you may want to source the file manually (or finally get around and install
direnv).

As the name indicates, the `.secrets` file is useful for holding any sensitive information:

- GDCN_LICENSE_KEY - the license key to use if you are doing end-to-end testing using docker-compose
  (see below)

- GOODDATA_FLIGHT_ENUMERATED_TOKENS__TOKENS - can be used to specify list of secret tokens
  used for authentication.

  This one is a bit tricky, you have to specify an array of tokens: `'["...", "..."]'`

## Building Docker image

The `make docker` target is available and builds Docker image `flexfun-server`. You may want
to modify the image name and specify your own custom one.

The Docker image build will:

- Install all dependencies from `requirements.txt` file

  IMPORTANT: dependencies from requirements-dev.txt are intentionally not installed.

- Copy content of the entire `src` folder and make sure it is added on PYTHONPATH

  IMPORTANT: contents of `tests` directory is not copied to the image.

- Copy content of the entire `config` folder

## Running and testing locally using Docker Compose

The template comes with `docker-compose.yaml` which consists of two services:

1.  The GoodData Cloud Native Container Edition (gooddata-cn-ce). This runs the entire Cloud Native
    in a single container.

2.  The server hosting your FlexFunctions (gooddata-flexfun-server)

To start it all up, you do the usual: `docker compose up -d --build`. At the time of startup, the
Docker image with server hosting your functions will be built (see section above).

Right now, you have to add your server as a data source to GoodData CN manually. Do POST the following
payload to http://localhost:3000/api/v1/entities/dataSources:

```json
{
  "data": {
    "id": "flexfun-server",
    "type": "dataSource",
    "attributes": {
      "url": "grpc://gooddata-flexfun-server:17001",
      "name": "flexfun-server",
      "type": "FLIGHTRPC",
      "schema": "",
      "cacheStrategy": "NEVER"
    }
  }
}
```

Use token authorization using the `YWRtaW46Ym9vdHN0cmFwOmFkbWluMTIz` token.

If you make some changes and want to rebuild & restart just the FlexFun server
run: `docker compose up -d --build gooddata-flexfun-server`.

Rebuild and restart of your server is usually very quick so this should allow you to iterate
very fast. Still, even faster and more natural is to use the typical tests that you
can write in `tests` directory.

We recommend doing most of the testing using programmatic tests and then use the end-to-end
testing using docker compose for final verification.

## Getting ready for deployment

### Configuration

The underlying server infrastructure uses [Dynaconf](https://www.dynaconf.com/) to manage
configuration.

The configuration can be loaded from one or more TOML files and/or may be also loaded
from environment variables. **The values from environment variables always win.**

Upon server startup, you can specify none or multiple configuration files and complement
this with environment variables.

This gives a lot of flexibility in how you can approach the configuration. If you don't know
where to start, here is a recommendation:

- Have configuration files in the `config` directory

- Keep existing files set up so that they work out of the box in your localhost deployment

- Override localhost-specific settings using environment variables

  For list of environment variables, see for example the `run-server.sh`. The environment
  variables are derived from setting names:

  - Always start with `GOODDATA_FLIGHT`
  - The section name (e.g. `[server]`) comes next, so for example `GOODDATA_FLIGHT_SERVER`
  - Then comes the setting name itself (e.g. `listen_host`), separated with two underscores;
    so you end up with `GOODDATA_FLIGHT_SERVER__LISTEN_HOST`

  All settings that can be specified in the TOML file can be also set via environment
  variable.

Alternatively, you can have multiple different configuration files and use one set for
localhost and one for production. So for example you can keep a single `flexfun.config.toml`
for both localhost and production, and then have one set of auth & config for localhost
and one for production.

Furthermore, we recommend checking the Dynaconf documentation - it has a lot of additional
features which you can take advantage of. It even has its own templating.

### Setting up hostnames

This part can get somewhat tricky if you do not read the documentation. We recommend to
check out the comments in the `server.config.toml`.

For production, go as follows:

- Set `listen_host` to `0.0.0.0`
- Set `advertise_host` to either public IP or public hostname of your server.

  Essentially, this is the value that you would also use when adding the server
  as data source to the GoodData Cloud.

NOTE: Setting correct `advertise_host` is essential because the primary flow to
invoke functions is the GetFlightInfo -> DoGet flow. Where GetFlightInfo call returns
information where and how to consume the function result. The server infrastructure
needs your input (e.g. the `advertise_host`) so that it can fill the 'where' part.

### Deployment without Docker

Deploying and running your server without use of Docker is a viable approach and in
many cases can be the simplest or most straightforward.

1. You have to get the whole template project to a host

   - You can do this by zipping the whole directory (minu)
   - Or, probably better is to use Git repository. Keep the template in the repository
     and then check out the contents from the host

2. Install production dependencies:

   - Your host must have Python 3.11 installed
   - Navigate to directory with checked-out contents
   - Run `make prod` - this will install production dependencies

3. Start the server

  - Easiest is to use `run-server.sh`
  - This will start server using the configuration stored in `config` directory
  - Typically, you will need to specify host-specific settings, you can do
    so using environment variables or have a prod-specific settings files.
  - If you have not already, see the 'Configuration' section above for additional
    detail.

### Dockerized deployment

TODO

## Adding Data Source to GoodData Cloud

Now that you have the Flight RPC server with your FlexFunctions up and running, you can
add it as data source to GoodData.

At the moment, this is only possible using the REST API.

You need to do a POST request on the `/api/v1/entities/dataSources` resource. The payload
should look like this:

```json
{
  "data": {
    "id": "my-flexfun",
    "type": "dataSource",
    "attributes": {
      "url": "grpc+tls://<your-hostname>:<port>",
      "token": "<secret authentication token>",
      "name": "my-flexfun",
      "type": "FLIGHTRPC",
      "schema": "",
      "cacheStrategy": "NEVER"
    }
  }
}
```

### TLS and custom certificate

If your server has TLS enabled and uses self-signed certificates, then you also have to
provide this certificate as a parameter of the data source:

```json
{
  "data": {
    "id": "my-flexfun",
    "type": "dataSource",
    "attributes": {
      "url": "grpc+tls://<your-hostname>:<port>",
      "token": "<secret authentication token>",
      "name": "my-flexfun",
      "type": "FLIGHTRPC",
      "schema": "",
      "cacheStrategy": "NEVER",
      "parameters": [
        {
          "name": "tlsRootCertificate",
          "value": "..."
        }
      ]
    }
  }
}
```

The `value` of the `tlsRootCertificate` is Base64 encoded content of the CA certificate .pem file. You can
do the base64 encoding for example using something like this:

```python
import base64

with open("ca-cert.pem", "rb") as file:
    print(base64.b64encode(file.read()))
```

### Cache strategy

The `cacheStrategy` set to 'NEVER' means that GoodData Cloud will never cache any
results obtained when invoking FlexFunctions on your server.

You can set this to `ALWAYS` if you want to add caching layer on top of your server - just
keep in mind that then you have to do POST on `/api/v1/actions/dataSources/my-flexfun/uploadNotification`
every time you want to invalidate the caches.

The use of caching on top of server running FlexFunctions is at your discretion - in many
cases it depends on what your FlexFunctions do. For example if the function does complex
computations on top of mostly static data - then using the caching is a no-brainer especially
in production deployments.
