# historical-system-profiles-backend
A service to return older system profile records


### dev setup
(need to fill this in)
 * make sure you have `libpq-devel` and `postgresql` (for psql) installed

## Required dependencies:
- pipenv
- pre-commit

## Work with pre-commit hooks

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

## db changes and migration

The db schema is defined by the objects defined in models.py.  When a change is made to these model objects, a database migration needs to be created.  This migration will be applied automatically when an updated image is spun up in a pod.  The steps to create the database migration are below:

* make changes to model objects in models.py
* in the historical-system-profiles-backend source directory, run `pipenv shell`
* spin up the dev database with `docker-compose -f dev.yml up -d`
* run flask to upgrade the dev database to its current state with the command `FLASK_APP=historical_system_profiles.app:get_flask_app_with_migration flask db upgrade`
* now run flask to create migration with the command `FLASK_APP=historical_system_profiles.app:get_flask_app_with_migration flask db migrate -m "migration message"`
* be sure to include the newly created migration file in migrations/versions/ in your pull request

## To run locally with Clowder
We are using the structure used in Clowder to run our app locally. So we created a file called `local_cdappcofig.json` and a script `run_app_locally` to automate the spin up process.

To run follow below process:

1. Make sure you have Ephemeral Envinroment running (https://github.com/RedHatInsights/drift-dev-setup#run-with-clowder)
2. Add a file with the following name and content to the app folder (this is needed just once). File name: `local_cdappconfig.json`
3. Content to be added into `local_cdappconfig.json`:

```
{
  "database": {
    "adminPassword": "postgres",
    "adminUsername": "T0gvQZjRlQAA7n36",
    "hostname": "localhost",
    "name": "historical-system-profiles",
    "password": "FGhpSR1U7TUAnpY4",
    "port": 5434,
    "sslMode": "disable",
    "username": "z7ZM6jgpUNGttKwF"
  },
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
      "port": 8085
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
    "hostname": "env-ephemeral-02-featureflags.ephemeral-02.svc",
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
4. Run virtual environment
```
source .venv/bin/activate
```
5. Run below command to run HSP backend

```
sh run_app_locally.sh
```

5. To run Kafka services, you need to setup specific environment variables and add one hostname to `/etc/hosts`.

```
SERVICE_MODE=LISTENER LISTENER_TYPE=ARCHIVER sh run_app_locally.sh
```

6. You will see in the logs something like below:

```
MainThread ERROR kafka.conn - DNS lookup failed for env-ephemeral-09-7fd90ba6-kafka-0.env-ephemeral-09-7fd90ba6-kafka-brokers.ephemeral-09.svc:9092 (AddressFamily.AF_UNSPEC)
```

7. Add this to `/etc/hosts/`

```
env-ephemeral-09-7fd90ba6-kafka-0.env-ephemeral-09-7fd90ba6-kafka-brokers.ephemeral-09.svc
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
