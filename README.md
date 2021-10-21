# drift-backend
System drift analysis service

This is a flask app that provides an API for drift-frontend. It listens on port
8080 by default with gunicorn. Prometheus stats will be stored in a temp
directory.

## Coding guidelines
1. All python code must be python 3.8 compatible
1. The code should follow linting from pylint
1. The code should follow formatter from black
1. The code should follow imports order from isort

## Required dependencies:
- pipenv
- pre-commit

### Work with pre-commit hooks

```bash
# installs pre-commit hooks into the repo
pre-commit install --install-hooks

# run pre-commit hooks for staged files
pre-commit run

# run pre-commit hooks for all files in repo
pre-commit run --all-files

# bump versions of the pre-commit hooks automatically
pre-commit autoupdate

# bypass pre-commit check
git commit --no-verify
```

### To set up pipenv:
```bash
yum install -y pipenv
pipenv install # will pull in deps and create virtualenv, and will print next steps to run
```
### To run unit tests

With your `pipenv shell` activated.

Run: `./run_unit_tests.sh` to run all unit test. Since we use `pytest` we can pass all pytest args to this script, for example:

- Run with verbose
```bash
./run_unit_tests.sh -vv
```

- Run only one test
```bash
./run_unit_tests.sh -k TEST_NAME
```
you can aggregate pytest args in same command, eg: `./run_unit_tests.sh -k TEST_NAME -vv`

### to set up temp directory (command will return a temp dir that you'll use later)
```
mktemp -d
```

### To run (inventory service URL can be obtained from drift or platform team):

`prometheus_multiproc_dir=`mktemp -d` INVENTORY_SVC_URL=<inventory service url> ./run_app.sh`


### To set the debug level (`info` by default):

`LOG_LEVEL=debug prometheus_multiproc_dir=/tmp/tempdir INVENTORY_SVC_URL=<inventory service url> ./run_app.sh`

The prometheus_multiproc_dir should be a path to a directory for sharing info
between app processes. If the dir does not already exist, the app will create
one.

The same info as above, but in handy table form:

| env var name              | required? | expected values | description                                       |
| ------------              | --------- | --------------- | ------------                                      |
| INVENTORY_SVC_URL         | yes       | URL             | URL for inventory service (do not include path)   |
| LOG_LEVEL                 | no        | string          | lowercase log level (info by default)             |
| prometheus_multiproc_dir  | yes       | string          | path to dir for sharing stats between processes   |
| PATH_PREFIX               | no        | string          | API path prefix (default: `/api`)                 |
| APP_NAME                  | no        | string          | API app name (default: `drift`)                   |

If you would like to use this service with insights-proxy, you can use the
included `local-drift-backend.js` like so:

`SPANDX_CONFIG=drift-backend/local-drift-backend.js bash insights-proxy/scripts/run.sh`


If you use `run_app.sh`, drift app will be invoked via gunicorn. This should be
OK in most cases; even `pdb` runs fine inside of gunicorn.

However, if you want to use flask's server, use `python3 standalone_flask_server.py`
with the aforementioned environment vars.

## To run locally with Clowder
We are using the structure used in Clowder to run our app locally. So we created a file called `local_cdappcofig.json` and a script `run_app_locally` to automate the spin up process.

To run follow below process:

1. Make sure you have Ephemeral Envinroment running (https://github.com/RedHatInsights/drift-dev-setup#run-with-clowder)
2. Add a file with the following name and content to the app folder (this is needed just once). File name: `local_cdappconfig.json`
3. Content to be added into `local_cdappconfig.json`:

```
{
  "endpoints": [
    {
      "app": "system-baseline",
      "hostname": "localhost",
      "name": "backend-service",
      "port": 8003
    },
    {
      "app": "host-inventory",
      "hostname": "localhost",
      "name": "service",
      "port": 8082
    },
    {
      "app": "rbac",
      "hostname": "localhost",
      "name": "service",
      "port": 8086
    },
    {
      "app": "historical-system-profiles",
      "hostname": "localhost",
      "name": "backend-service",
      "port": 8004
    }
  ],
  "kafka": {
    "brokers": [
      {
        "hostname": "localhost",
        "port": 9092
      }
    ],
    "topics": [
      {
        "name": "platform.notifications.ingress",
        "requestedName": "platform.notifications.ingress"
      },
      {
        "name": "platform.payload-status",
        "requestedName": "platform.payload-status"
      }
    ]
  },
  "featureFlags": {
    "hostname": "non-use-for-now",
    "port": 4242,
    "scheme": "http"
  },
  "logging": {
    "cloudwatch": {
      "accessKeyId": "",
      "logGroup": "",
      "region": "",
      "secretAccessKey": ""
    },
    "type": "null"
  },
  "metricsPath": "/metrics",
  "metricsPort": 9000,
  "privatePort": 10000,
  "publicPort": 8000,
  "webPort": 8000
}
```

4. Run below command

```
sh run_app_locally.sh
```

### To build image and deploy to personal repository in quay:

1. Run below command passing your quay username. In the example `jramos`.

```
sh ephemeral_build_image.sh jramos
```

### To run SonarQube:
1. Make sure that you have SonarQube scanner installed.
2. Duplicate the `sonar-scanner.properties.sample` config file.
```
  cp sonar-scanner.properties.sample sonar-scanner.properties
```
3. Update `sonar.host.url`, `sonar.login` in `sonar-scanner.properties`.
4. Run the following command
```
java -jar /path/to/sonar-scanner-cli-4.6.0.2311.jar -D project.settings=sonar-scanner.properties
```
5. Review the results in your SonarQube web instance.
