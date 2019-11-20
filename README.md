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

# contributing to this repo

Please ensure the following when making PRs:

 * tests pass (`./run_unit_tests.sh`)
 * commit is of the following form (see https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits):

```
fix: patch title

summary of fix

```


