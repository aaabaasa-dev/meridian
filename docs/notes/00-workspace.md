Setup
uv (a fast python package and package manager)  used with a mental model for - Project dependencies (uv add) and tools ( uv tool install )

This project will have several python services so uv workspace applies ( one lockfile and one .venv at the root and each service is a member with its own pyproject.toml )

Version pinned for python 3.12 in .python-version.

Note: dbt, MetricFlow & PySpark are slow to support new python releases.

Then we turn the repo root into a workspace = pyproject.toml

set ingest as the first member with dependencies pydantic, confluent-kafka fastavaro dev pytest


Note: root - set bare project-[uv init --bare --name meridian], for ingest we set package project(installable python packages)- [uv init --package --name meridian-ingest ingest]
meridian-ingest - purpose distribution/poject name
meridian-ingest - python import name
ingest - directory containing the project

this application aims to maybe:
	- receive events from different systems
	- Validate incoming data
	- Convert data into Avro format
	- Send events to Kafka




General approach : one uv workspace, a shared lockfile, centralised git hooks, and CI checks


Development setup:
- Initialise uv workspace
- initialise ingest package
- Add dependencies
- Sync workspace
- write smoke tests
- configure .gitignore
- configure root ruff settings
- install pre-commit
- configure GitHub Actions

approach is setup the foundation for a typical event driven data ingestion service

uv tree --package meridian-ingest --depth 1 to confirm the additions, ( write dependencies into ingest/pyproject.toml, update the uv.lock and installs it. --dev flag for pytest puts pytest in a dev group and stays out of production. (group:dev)

Smoke tests - check that the essential parts of a software package work.( Does the application basically work fundamentally.

for example can the package be imported, application start?, are the required libraries installed, can pydantic validate data, can avro encode and decode a record, can kafka client library load?

so think :
	smoke tests - does the application start, are dependencies working
	Integration tests - can different components communicate
	Unit tests - Does each individual function / class behave correctly
	End to end tests - complete application workflow work?

pre-commit is a tool run across the whole repo. has its own isolated install not .venv
