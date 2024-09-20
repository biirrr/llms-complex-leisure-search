# LLM Complex Leisure Search

## Required software

The project is installed using [Hatch](https://hatch.pypa.io). Install that [from here](https://hatch.pypa.io/latest/install/).

## Configuration

Configuration settings are loaded from a `.env` file in the root directory. The following settings can be set

* `IGDB.CLIENT_ID` - IGDB API client identifier
* `IGDB.CLIENT_SECRET` - IGDB API client secret
* `GEMINI.API_KEY` - Gemini API key

## Running the CLI

Run the following command to get help:

```{console}
hatch run lcls --help
```

## Commands

### Data pre-processing

* `hatch run lcls books extract` - Extract all solved books threads into data/books/solved.json
* `hatch run lcls games extract` - Extract all solved games threads into data/games/solved.json
* `hatch run lcls movies extract` - Extract all solved movies threads into data/movies/solved.json

### Data statistics

* `hatch run lcls books stats` - Show basic statistics for the books data-set
* `hatch run lcls games stats` - Show basic statistics for the games data-set
* `hatch run lcls movies stats` - Show basic statistics for the movies data-set

### Experiments

* `hatch run lcls games search --search-mode [default|exact] {NAME}` - Search IGDB by name. `--search-mode` can be used to force exact matches.
* `hatch run lcls gemini process-requests {INPUT} {OUTPUT}` - Use Gemini to run the `templated_request`\ s from the `INPUT` file and write the result to `OUTPUT`.

## Data

All data is in the `data` directory, split into sub-folders by data-set. In the sub-folders the annotation data is in
the `.csv` files. The `solved.json` files contain all threads that have been maked as solved.

## Development

The project uses [pre-commit](https://pre-commit.com/) and [Ruff](https://docs.astral.sh/ruff/) to ensure code-style consistency.
Run

```{console}
pre-commit install
```

to ensure style checks are run before committing changes.
