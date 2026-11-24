# [MongoDB Sample Dataset](https://docs.atlas.mongodb.com/sample-data/available-sample-datasets/)

MongoDB Database Tools (`mongoimport`) need to be installed to import these collections. Download them from [MongoDB Database Tools](https://www.mongodb.com/try/download/database-tools?tck=docs_databasetools).

See [Documentation Index](docs/index.md) for guided tutorials, ASD-STE100 import procedures, collection metrics, and schema notes.

> Fork of [mcampo2/mongodb-sample-databases](https://github.com/mcampo2/mongodb-sample-databases) and [neelabalan/mongodb-sample-dataset](https://github.com/neelabalan/mongodb-sample-dataset), replacing binary BSON dumps with 21 NDJSON files imported by [script.sh](script.sh).

Atlas provides sample datasets to explore CRUD operations, aggregation pipelines, and MongoDB Charts. MongoDB hosts 7 sample databases (`21` collections total), stored here as separate newline-delimited JSON files inside each `sample_*` directory.

## Dataset Import Flow

```mermaid
flowchart LR
  Loader["script.sh (host, port, auth)"] -->|"For each sample_* dir"| Scan["sample_*/*.json (21 NDJSON files)"]
  Scan -->|"mongoimport --drop"| Import["7 MongoDB Databases"]
  Import --> Check["Verify with mongosh"]
```

## Sample Datasets

| Dataset Name | Directory | Collections |
| :--- | :--- | :--- |
| [Sample AirBnB Listings Dataset](https://docs.atlas.mongodb.com/sample-data/sample-airbnb/) | `sample_airbnb` | `listingsAndReviews` |
| [Sample Analytics Dataset](https://docs.atlas.mongodb.com/sample-data/sample-analytics/) | `sample_analytics` | `accounts`, `customers`, `transactions` |
| [Sample Geospatial Dataset](https://docs.atlas.mongodb.com/sample-data/sample-geospatial/) | `sample_geospatial` | `shipwrecks` |
| [Sample Mflix Dataset](https://docs.atlas.mongodb.com/sample-data/sample-mflix/) | `sample_mflix` | `comments`, `movies`, `sessions`, `theaters`, `users` |
| [Sample Supply Store Dataset](https://docs.atlas.mongodb.com/sample-data/sample-supplies/) | `sample_supplies` | `sales` |
| [Sample Training Dataset](https://docs.atlas.mongodb.com/sample-data/sample-training/) | `sample_training` | `companies`, `grades`, `inspections`, `posts`, `routes`, `stories`, `trips`, `tweets`, `zips` |
| [Sample Weather Dataset](https://docs.atlas.mongodb.com/sample-data/sample-weather/) | `sample_weatherdata` | `data` |

## Running in Docker

Start a local MongoDB container (`docker-compose.yaml` or `docker run`) and import all 7 databases:

```bash
# Option 1: Docker Compose on port 27017
docker compose up -d

# Option 2: Standalone container on port 27017
docker run -d --name mongo -p 27017:27017 -v ~/mongodb/mongo:/data/db mongo:latest

# Import all sample_* datasets into localhost:27017
./script.sh localhost 27017

# Start MongoDB shell inside the container
docker exec -it mongo mongosh
```
