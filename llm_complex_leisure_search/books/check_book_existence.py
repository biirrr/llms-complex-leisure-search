"""Check whether books exist."""

import gzip
import json
import os
import time

from openlibrary_api import search_openlibrary


def get_author_title(answer):
    """Return the author and title from an answer."""
    title = answer["answer"][0]
    author_list = answer["answer"][1]
    author_string = " ".join(author_list)
    return author_string, title


def get_num_done(output_file):
    """Generate the number of completed entries."""
    if os.path.exists(output_file) is False:
        print("output_file does not exists, creating one")
        return 0
    with gzip.open(output_file, "rt") as fh:
        print("output_file exists, counting checks done.")
        return len([_ for _ in fh])


def check_answers(answers, output_file):
    """Check answers for completness."""
    num_done = get_num_done(output_file)
    print(f"{num_done} answers done")
    with gzip.open(output_file, "at") as fh:
        for ai, answer in enumerate(answers):
            if ai < num_done:
                continue
            author_string, title = get_author_title(answer)
            response = search_openlibrary(author_string, title)
            if response is None:
                response = {"answer_id": ai}
            else:
                response["answer_idx"] = ai
            json_string = json.dumps(response)
            fh.write(f"{json_string}\n")
            time.sleep(1)
            if (ai + 1) % 100 == 0:
                print(f"{ai + 1} answers checked")


def check_output_format(answers):
    """Check the output format."""
    for answer in answers:
        title = answer["answer"][0]
        author_list = answer["answer"][1]
        if isinstance(title, str) is False:
            print(title)
        for author in author_list:
            if isinstance(author, str) is False:
                print(author)


def main():
    """Run the book existence checking."""
    answer_file = "../../data/books/unique-answers.json"
    output_dir = "../../data/books/"
    output_file = os.path.join(output_dir, "openlibrary_answer_check_responses.jsonl.gz")
    with open(answer_file) as fh:
        answers = json.load(fh)

    print(len(answers))
    check_output_format(answers)
    check_answers(answers, output_file)


if __name__ == "__main__":
    main()
