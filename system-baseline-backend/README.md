# system-baseline-backend

This repo is for the system-baseline backend service. Its main job is to create, store, retrieve and delete system baselines.

## what is a system baseline?

A system baseline is simply a set of facts. It is an array of hashes. Each hash is of the format `{"name": <fact name>, "value": <fact value>}`. Each baseline has a UUID identifier as well as additional metdata. A full example looks like this:

```json
{
    "account": "123456",
    "baseline_facts": [
        {
            "name": "arch",
            "value": "x86_64"
        },
        {
            "name": "phony.arch.fact",
            "value": "some value"
        }
    ],
    "created": "2019-06-25T03:13:20.960512Z",
    "display_name": "arch baseline",
    "fact_count": 2,
    "id": "e61b732a-1557-4cfc-a59f-43b1b394b7f7",
    "updated": "2019-06-25T03:13:20.960518Z"
}

```

## how are baselines stored?

Each baseline is stored in a postgres database. There should never be a reason to access the database directly; please access it via the service.

The baselines are stored in a table with the following schema:

```
                        Table "public.system_baselines"
     Column     |            Type             | Collation | Nullable | Default
----------------+-----------------------------+-----------+----------+---------
 id             | uuid                        |           | not null |
 account        | character varying(10)       |           |          |
 display_name   | character varying(200)      |           |          |
 created_on     | timestamp without time zone |           |          |
 modified_on    | timestamp without time zone |           |          |
 baseline_facts | jsonb                       |           |          |
 fact_count     | integer                     |           |          |
Indexes:
    "system_baselines_pkey" PRIMARY KEY, btree (id)
```

Note that all of the facts are stored as a single json blob. Normalizing this data would cause more harm than good.

## who uses this service?

This service is used by `drift-frontend`. This frontend app calls both `drift` and `system-baseline` service.


## how do I use the service?

You can list all of your baselines with GET a call to `/v1/baselines`. This will show your baselines but will not show their facts. You can then pull up an individual baseline with a GET call to `/v1/baselines/<UUID>`. A DELETE call will delete the baseline. POSTing to `/v1/baselines` will create a new baseline. The POST data to create two baselines at once looks like this:

```json
[
    {
        "baseline_facts": [
            {
                "name": "arch",
                "value": "x86_64"
            },
            {
                "name": "phony.arch.fact",
                "value": "some value"
            }
        ],
        "display_name": "arch baseline"
    },
    {
        "baseline_facts": [
            {
                "name": "memory",
                "value": "64GB"
            },
            {
                "name": "cpu_sockets",
                "value": "16"
            }
        ],
        "display_name": "cpu + mem baseline"
    }
]
```


This call will return two new baseline UUIDs.

You can also use PATCH calls to a UUID with data like so:

```json
    {
        "baseline_facts": [
            {
                "name": "archarch",
                "value": "x86_64x86_64"
            },
            {
                "name": "phony.arch.fact.2",
                "value": "some value2"
            },
            {
                "name": "phony.arch.fact.3",
                "value": "some value3"
            }
        ]
    }
```

## contributing to this repo

### development requirements

 * `psql` - postgresql client (`sudo dnf install postgresql` on Fedora)


Please ensure the following when making PRs:

 * tests pass (`./run_unit_tests.sh`)
 * commit is of the following form (see https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits):

```
fix: patch title

summary of fix

```

## db changes and migration

The db schema is defined by the objects defined in models.py.  When a change is made to these model objects, a database migration needs to be created.  This migration will be applied automatically when an updated image is spun up in a pod.  The steps to create the database migration are below:

* make changes to model objects in models.py
* in the system-baseline-backend source directory, run `poetry shell`
* spin up the dev database with `docker-compose -f dev.yml up -d`
* run flask to upgrade the dev database to its current state with the command `FLASK_APP=system_baseline.app:get_flask_app_with_migration flask db upgrade`
* now run flask to create migration with the command `FLASK_APP=system_baseline.app:get_flask_app_with_migration flask db migrate -m "migration message"`
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
    "adminPassword": "password",
    "adminUsername": "admUsername",
    "hostname": "localhost",
    "name": "system-baseline",
    "password": "password",
    "port": 5433,
    "sslMode": "disable",
    "username": "username"
  },
  "endpoints": [
    {
      "app": "system-baseline",
      "hostname": "localhost",
      "name": "backend-service",
      "port": 8083
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
      "port": 8003
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
  }
}
```
4. Run virtual environment
```
source .venv/bin/activate
```
5. Run below command

```
sh run_app_locally.sh
```

## To build image and deploy to personal repository in quay:

1. Run below command passing your quay username. In the example `jramos`.

```
sh ephemeral_build_image.sh jramos
```

## To run SonarQube:
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
