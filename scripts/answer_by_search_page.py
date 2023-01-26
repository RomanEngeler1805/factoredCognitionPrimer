import httpx
from ice.recipe import recipe
from urllib.request import urlopen
from bs4 import BeautifulSoup


def get_page(url: str) -> str:
    html = urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text


# prompt to answer question given {query, context}
def make_search_result_prompt(context: str, query: str, question: str) -> str:
    return f"""
Search results from Google for the query "{query}":

"{context}"


Answer the following question, using the search results if helpful:

Question: "{question}"
Answer: "
""".strip()

# prompt to choose query given {question}
def make_search_query_prompt(question: str) -> str:
    return f"""
You're trying to answer the question {question}. You get to type in a search query to Google, and then you'll be shown the results. What query do you want to search for?

Query: "
""".strip(
        '" '
    )


def make_search_expansion_prompt(context: str, question: str) -> str:
    return f"""
You're trying to answer the question {question}. You have extracted the following website snippets from the search results:

"{context}".


Which website do you want to extract the full text from? Answer with a single number "Website <number>".

Answer: Website "
    """.strip(
        '" '
    )


# search with the given query
async def search(query: str) -> dict:
    async with httpx.AsyncClient() as client:
        params = {"q": query, "hl": "en", "gl": "us", "api_key": "e911ab00017f469c1ab142aeba5c524cf31f8ab2f9d42c3a5f6ef71bd08bc7c2"}
        response = await client.get("https://serpapi.com/search", params=params)
        return response.json()

async def get_website_text(context_str: str, context_list: list, question: str) -> int:
    # let GPT choose which website to expand
    prompt = make_search_expansion_prompt(context_str, question)
    website_idx_str = await recipe.agent().complete(prompt=prompt, stop='"')
    website_idx_str = website_idx_str.strip()

    # check if it returned a number
    if website_idx_str.isdigit():
        website_idx = int(website_idx_str)
    else:
        website_idx = 0

    # expand website text
    link = context_list[website_idx][1]
    website_text = get_page(link)
    return website_idx, website_text

def extract_results(data: dict) -> list:
    if not data or not data.get("organic_results"):
        return []

    results = []
    for result in data["organic_results"]:
        title = result.get("title")
        link = result.get("link")
        snippet = result.get("snippet")
        if not title or not link or not snippet:
            continue
        results.append([title, link, snippet])
    
    return results

# format search results
def render_results(data: list) -> str:
    if len(data) == 0:
        return "No results found"

    results = []
    for k, result in enumerate(data):
        title = result[0]
        link = result[1]
        snippet = result[2]
        results.append(f"Website {k}\n{title}\n{link}\n{snippet}\n")

    return "\n".join(results)

# choose query based on question to answer
async def choose_query(question: str) -> str:
    prompt = make_search_query_prompt(question)
    query = await recipe.agent().complete(prompt=prompt, stop='"')
    return query

# get search query, perform search, construct answer based on search results
async def answer_by_search(
    question: str = "Who is the president of the United States?",
) -> str:
    query = await choose_query(question)
    results = await search(query)

    # extract list of results [[title, link, snippet], ...]
    results_list = extract_results(results)

    # render results with number for each result
    results_str = render_results(results_list)

    # add text of chosen website 
    website_idx, website_text = await get_website_text(results_str, results_list, question)

    # replace snippet with full text of website
    # TODO: for now have a hard limit for the length; in the future, recursively summarise
    results_list[website_idx][2] = website_text[:1000]

    results_str = render_results(results_list)

    prompt = make_search_result_prompt(results_str, query, question)
    answer = await recipe.agent().complete(prompt=prompt, stop='"')
    return answer


recipe.main(answer_by_search)