# Datasets and Loader Reference

Complete inventory of the 7 databases (`21` NDJSON collection files), `script.sh` arguments, and `docker-compose.yaml` configuration.

## Collection Inventory (`sample_*`)

| Database (`--db`) | File Path | Documents (Lines) | Size (Bytes) |
| :--- | :--- | :--- | :--- |
| `sample_airbnb` | `sample_airbnb/listingsAndReviews.json` | `5555` | `99656721` |
| `sample_analytics` | `sample_analytics/accounts.json` | `1746` | `302693` |
| `sample_analytics` | `sample_analytics/customers.json` | `500` | `246237` |
| `sample_analytics` | `sample_analytics/transactions.json` | `1746` | `20141601` |
| `sample_geospatial` | `sample_geospatial/shipwrecks.json` | `11095` | `4789546` |
| `sample_mflix` | `sample_mflix/comments.json` | `50304` | `18231014` |
| `sample_mflix` | `sample_mflix/movies.json` | `23539` | `43456152` |
| `sample_mflix` | `sample_mflix/sessions.json` | `1` | `560` |
| `sample_mflix` | `sample_mflix/theaters.json` | `1564` | `454202` |
| `sample_mflix` | `sample_mflix/users.json` | `185` | `33082` |
| `sample_supplies` | `sample_supplies/sales.json` | `5000` | `4866111` |
| `sample_training` | `sample_training/companies.json` | `9500` | `38563354` |
| `sample_training` | `sample_training/grades.json` | `100000` | `37840131` |
| `sample_training` | `sample_training/inspections.json` | `80047` | `28000656` |
| `sample_training` | `sample_training/posts.json` | `500` | `17215951` |
| `sample_training` | `sample_training/routes.json` | `66985` | `16137490` |
| `sample_training` | `sample_training/stories.json` | `9842` | `11947834` |
| `sample_training` | `sample_training/trips.json` | `10000` | `7112796` |
| `sample_training` | `sample_training/tweets.json` | `24832` | `49887461` |
| `sample_training` | `sample_training/zips.json` | `29470` | `5700122` |
| `sample_weatherdata` | `sample_weatherdata/data.json` | `10000` | `18832901` |

## Loader Script (`script.sh`)

| Argument / Flag | Position | Default | Behavior |
| :--- | :--- | :--- | :--- |
| `-h` / `--help` | `$1` | N/A | Print usage summary and exit `0` |
| `host` | `$1` | `localhost` | Target `--host` passed to `mongoimport` |
| `port` | `$2` | `27017` | Target `--port` passed to `mongoimport` |
| `username` | `$3` | Unset | Passed with `-u` (`--authenticationDatabase admin`) |
| `password` | `$4` | Unset | Passed with `-p` (required when `username` is given) |

`script.sh` sets `set -euo pipefail`, validates `mongoimport` availability, and iterates exclusively over `sample_*/*.json`.

## Docker Compose (`docker-compose.yaml`)

| Field | Value | Notes |
| :--- | :--- | :--- |
| Service | `mongodb` | Runs `mongo:latest` |
| Port | `27017:27017` | Exposes MongoDB on host `localhost:27017` |
| Volume | `~/mongodb/mongo:/data/db` | Persists database files under host home directory |
