import httpx

from ice.recipe import recipe

# prompt to answer question given {query, context}
def make_search_result_prompt(context: str, query: str, question: str) -> str:
    return f"""
Search results from Google for the query "{query}": "{context}"

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

# search with the given query
async def search(query: str) -> dict:
    async with httpx.AsyncClient() as client:
        params = {"q": query, "hl": "en", "gl": "us", "api_key": "e911ab00017f469c1ab142aeba5c524cf31f8ab2f9d42c3a5f6ef71bd08bc7c2"}
        response = await client.get("https://serpapi.com/search", params=params)
        return response.json()

# format search results
def render_results(data: dict) -> str:
    if not data or not data.get("organic_results"):
        return "No results found"

    results = []
    for result in data["organic_results"]:
        title = result.get("title")
        link = result.get("link")
        snippet = result.get("snippet")
        if not title or not link or not snippet:
            continue
        results.append(f"{title}\n{link}\n{snippet}\n")

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
    results_str = render_results(results)
    prompt = make_search_result_prompt(results_str, query, question)
    answer = await recipe.agent().complete(prompt=prompt, stop='"')
    return answer


recipe.main(answer_by_search)