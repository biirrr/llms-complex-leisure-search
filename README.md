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

### LLM processing

* `hatch run lcls books query-gemini` - Use Gemini to process all solved book requests.

### Data statistics

* `hatch run lcls books stats` - Show basic statistics for the books data-set
* `hatch run lcls games stats` - Show basic statistics for the games data-set
* `hatch run lcls movies stats` - Show basic statistics for the movies data-set

### Other

* `hatch run lcls games search --search-mode [default|exact] {NAME}` - Search IGDB by name. `--search-mode` can be used to force exact matches.

## Data

All data is in the `data` directory, split into sub-folders by data-set. In the sub-folders the annotation data is in
the `.csv` files. The `solved.json` files contain all threads that have been maked as solved. The `gemini.json` contains
the responses generated by the Google Gemini LLM.

### Data formats

#### `solved.json`

JSON-formated file, containing a list of objects. Each object has the following fields:

* `thread_id`: The unique id for this thread
* `request`: The original request text
* `prompt`: The request text embedded in the standard LLM prompt
* `solved`: Boolean to indicate that the thread has a solution
* `confirmed`: Boolean to indicate that the thread has been marked as confirmed
* `title`: The title of the book / game / movie
* `author`: The author of the book (only in `books/solved.json`)
* `years`: The release years of the game (only in `games/solved.json`)
* `year`: The release year of the movie (only in `movies/solved.json`)

### `gemini.json`

JSON-formated file, containing a list of objects. Each object has the following fields:

* `thread_id`: The uniqe id of the thread that this set of responses is for
* `results`: A list of up to three sub-lists, each sub-list containing objects with the following fields:

  * `answer`: The LLM-provided answer
  * `explanation`: The LLM-provided explanation
  * `confidence`: The LLM-provided confidence
  * `title`: The title of the book / game / movie
  * `author`: The author of the book (only in `books/gemini.json`)

  If less than three sub-lists are present, then Gemini was not able to generate valid JSON (allowing for
  up to 10 attempts).

## Development

The project uses [pre-commit](https://pre-commit.com/) and [Ruff](https://docs.astral.sh/ruff/) to ensure code-style consistency.
Run

```{console}
pre-commit install
```

to ensure style checks are run before committing changes.
