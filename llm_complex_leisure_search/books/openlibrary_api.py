import requests
import urllib.parse


BASE_URL = "https://openlibrary.org/search.json"


def extract_matches(response):
    # simplistic assumption: if there are no results, it doesn't exist
    if response['numFound'] == 0:
        return None
    # even more simplistic assumption: if there are no exact matches, it doesn't exist
    if response['numFoundExact'] == False:
        return None
    # results have many duplites, reduce to set
    item_set = set()
    for doc in response['docs']:
        item_tup = ('; '.join(response['docs'][0]['author_name']), response['docs'][0]['title'])
        item_set.add(item_tup)
    items = []
    for author, title in item_set:
        item = {'author': author, 'title': title}
        items.append(item)
    return items


def search_openlibrary(author: str, title: str):
    # url-encoded title and author 
    title = urllib.parse.quote_plus(title)
    author = urllib.parse.quote_plus(author)
    url = f'{BASE_URL}?title={title}&author={author}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def main():
    author = 'tolkien'
    title = 'lord of the rings'
    response = search_openlibrary(author, title)
    matches = extract_matches(response)
    print(matches)


if __name__ == "__main__":
    main()
