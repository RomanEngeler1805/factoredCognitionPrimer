import httpx

from ice.recipe import recipe


def make_qa_prompt(context: str, question: str) -> str:
    return f"""
Background text: "{context}"

Answer the following question about the background text above:

Question: "{question}"
Answer: "
""".strip()


async def search(query: str = "Who is the president of the United States?") -> dict:
    async with httpx.AsyncClient() as client:
        params = {"q": query, "hl": "en", "gl": "us", "api_key": "e911ab00017f469c1ab142aeba5c524cf31f8ab2f9d42c3a5f6ef71bd08bc7c2"}
        response = await client.get("https://serpapi.com/search", params=params)
        return response.json()


recipe.main(search)