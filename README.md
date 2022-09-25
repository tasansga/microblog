# microblog aggregator

## What's this?
It's a *within a single day* rapid-prototyped demo application for a ELT pipeline that:
* fetches data from microblogging sources like twitter
* transforms the data into an unified message data format
* makes a data product available through an OpenAPI interface

The only data source defined so far is twitter. It's quite limited though, it assumes the
only available attributes are `id` and `text` and it supports exactly one rule. And no, it
doesn't deduplicate messages either.

So. This is a demo. Yep. It's purely for demonstration purposes. Do not use in production.


## How to use
For the CLI, set `SQLITE_PATH` to a valid location, for example `/tmp/microblog-test`.
Also set `MB_SOURCE_TWITTER_BEARER_TOKEN` and `MB_SOURCE_TWITTER_RULE` as environment variables.
Hint: See possible options by running `./cli.sh --help` and perhaps set `LOG_LEVEL=DEBUG`.

Now run the CLI with `./cli.sh capture twitter` to fetch some data from twitter's stream.
The data will be immediately on capture stored raw in the given SQLite database.
Note: This only fetches sample data, check `twitter.py` and change `sample()` to `filter()`
for the real thing. No proper error handling and checking in place, keep an eye on
the rate limit - this is a rapid-prototyped demo, after all!

Worth noting that while `MB_SOURCE_TWITTER_RULE` must be set it doesn't really have an effect
unless used in combination with `filter()` instead of `sample()`.

To process the raw data, run `./cli.sh transfer twitter`. Sorry, no manual transformation
definitions supported!

Finally, start the OpenAPI server with `./cli.sh serve` and grab the results.
That's as easy as running `curl http://127.0.0.1:5000/openapi/v1/messages` while the server runs.
Hint: The OpenAPI schema is available on the server at `http://127.0.0.1:5000/openapi/v1/openapi.yaml`.

Oh, there's also some test cases, although not really enough - check out the `tests`
directory or run `./test.sh`.

Everything runs single-threaded and synchronous, but of course it's no fuss to just run different
jobs next to each other.


## Rationale

### Why barebone and not tools like Spark, Kafka/logstash, Benthos,... or libraries like Pandas?
There's usually a lot more to teach, learn and/or demonstrate by simply implementing the basics
instead of configuring an existing product. However, for any real world purposes, don't use
this. It's really only good as a showcase demo.
Although, let's be fair, using SQLAlchemy and Flask isn't that low level either.

### Why SQLite?
Why not? SQLite is perfect for rapid prototyping. It's easy to set up, test and demonstrate
principles with SQLite, and this project isn't here to solve real problems anyway.
Besides, with SQLAlchemy it's a matter of a few line changes to also support, say, PostgreSQL,
and we don't have any infrastructure to ship with the application either.

### Why ELT and not ETL?
In theory twitter's stream can send a lot of data, so instead of spending time in transformation
processes immediately it's nicer to do so decoupled in a separate process and just write the raw
data as-is.
