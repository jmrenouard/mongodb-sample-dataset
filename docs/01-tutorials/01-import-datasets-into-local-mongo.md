# Tutorial: Import Sample Datasets into Local MongoDB

> **Learning Goal:** Verify loader options offline, start a disposable local MongoDB container (`docker-compose.yaml`), and import all `21` sample collections with `script.sh`.
>
> **Environment Warning:** `script.sh` passes `--drop` to `mongoimport`, which replaces identically named collections (`sample_airbnb`, `sample_mflix`, and other `sample_*` databases) on the target server. Never run it against a database holding live data.

## Prerequisites

Make sure your workstation has:

- Docker Engine and Docker Compose v2
- MongoDB Database Tools (`mongoimport`) available on your `PATH`
- Bash shell and Python 3.8+ for local verification tests

## Step 1: Inspect Loader Options and Dataset Files

Print `script.sh` usage without touching any database:

```bash
./script.sh --help
```

Expected output:

```text
Usage: ./script.sh [host] [port] [username] [password]

Import all sample_*/*.json collections into matching MongoDB databases.
```

## Step 2: Start Local MongoDB with Docker Compose

Launch the container defined in `docker-compose.yaml` on TCP port `27017`:

```bash
docker compose up -d
```

Expected output:

```text
[+] Running 2/2
 ✔ Network mongodb-sample-dataset_default  Created
 ✔ Container mongodb-sample-dataset-mongodb-1  Started
```

## Step 3: Load All 7 Databases Using `script.sh`

Run the loader against `localhost` port `27017`:

```bash
./script.sh localhost 27017
```

Each `sample_*` folder name becomes a database (`sample_airbnb`, `sample_analytics`, `sample_geospatial`, `sample_mflix`, `sample_supplies`, `sample_training`, `sample_weatherdata`), and each `.json` stem becomes its collection.

## Step 4: Inspect Collections with `mongosh`

Check loaded databases and sample counts inside the container:

```bash
docker compose exec mongodb mongosh --quiet --eval "db.adminCommand('listDatabases').databases.map(d => d.name)"
```

Expected output includes all seven `sample_*` database names.

## Step 5: Stop the Sandbox Container

Shut down the container when finished:

```bash
docker compose down
```

## Next Steps

- Strict ASD-STE100 procedures: [Import and Verify Datasets](../02-how-to-guides/import-and-verify-datasets.md)
- Dataset counts and `script.sh` specification: [Datasets and Loader Reference](../03-reference/datasets-and-script-spec.md)
- NDJSON and `--drop` trade-offs: [NDJSON Storage and Loader Design](../04-explanation/ndjson-storage-and-loader-design.md)
