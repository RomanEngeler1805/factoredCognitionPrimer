import httpx
import os

from ice.recipe import recipe


async def search(query: str) -> dict:
    async with httpx.AsyncClient() as client:
        params = {"q": query, "hl": "en", "gl": "us", "api_key": "e911ab00017f469c1ab142aeba5c524cf31f8ab2f9d42c3a5f6ef71bd08bc7c2"}
        response = await client.get("https://serpapi.com/search", params=params)
        return response.json()


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


async def search_string(
    question: str = "Who is the president of the United States?",
) -> str:
    results = await search(question)
    return render_results(results)


recipe.main(search_string)