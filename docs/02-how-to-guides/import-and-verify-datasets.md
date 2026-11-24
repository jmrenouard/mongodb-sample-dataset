# Import and Verify Sample Datasets

Refer to the [Datasets and Loader Reference](../03-reference/datasets-and-script-spec.md) before you run this procedure.

## Preconditions

1. Make sure that `mongoimport` is installed and available on your `PATH`.
2. Make sure that the target MongoDB instance accepts TCP connections on `PORT`.
3. If authentication is active on the server, obtain a valid `admin` username and password.

## Safety Instructions

**WARNING:** Back up target databases before you run `script.sh`. The loader passes `--drop` to `mongoimport` and deletes previous collections with the same names.

## Procedure

### Import without Authentication

1. Open a Bash shell at the repository root.

2. Run `script.sh` with the target hostname and port:

```bash
./script.sh localhost 27017
```

3. Monitor terminal output as each `sample_*` directory loads into MongoDB.

### Import with Admin Authentication

1. Pass both username and password arguments after the port:

```bash
./script.sh <host> 27017 <username> '<password>'
```

2. Confirm that `Using password authentication!` prints before the first `sample_*` directory.

**NOTE:** If you give a username without a password, `script.sh` stops immediately with exit code `1`.

## Verification Check

1. Open `mongosh` against the target server.

2. Check document counts in `sample_mflix.movies` and `sample_training.inspections`:

```bash
mongosh --host localhost --port 27017 --quiet --eval "printjson({movies: db.getSiblingDB('sample_mflix').movies.countDocuments(), inspections: db.getSiblingDB('sample_training').inspections.countDocuments()})"
```

3. Run the local offline validation suite at the repository root:

```bash
python -B -m unittest discover -s tests -v
```

4. Confirm that all tests pass without error.

## Rollback Procedure

If an unwanted database is loaded or an error occurs, do this procedure:

1. Connect to MongoDB with `mongosh` and drop the unwanted `sample_*` database:

```bash
mongosh --host localhost --port 27017 --quiet --eval "db.getSiblingDB('sample_mflix').dropDatabase()"
```

2. Restore the previous collection backup with `mongorestore` if available.

## Related Documentation

- Reference: [Datasets and Loader Reference](../03-reference/datasets-and-script-spec.md)
- Explanation: [NDJSON Storage and Loader Design](../04-explanation/ndjson-storage-and-loader-design.md)
