# LLM Complex Leisure Search

## Required software

The project is installed using [Hatch](https://hatch.pypa.io). Install that [from here](https://hatch.pypa.io/latest/install/).

## Configuration

Configuration settings are loaded from a `.env` file in the root directory. The following settings must be set

* `IGDB.CLIENT_ID` - IGDB API client identifier
* `IGDB.CLIENT_SECRET` - IGDB API client secret

## Running the CLI

Run the following command to get help:

```{console}
hatch run lcls --help
```

## Commands

* `games search {NAME}` - Search IGDB by name
