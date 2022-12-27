from ice.recipe import recipe

DEFAULT_CONTEXT = "Beth bakes 4x 2 dozen batches of cookies in a week."
DEFAULT_QUESTION = "If these cookies are shared amongst 16 people equally, how many cookies does each person consume?"

def make_qa_prompt(context: str, question: str) -> str:
    return f"""
    Background text: "{context}"
    
    Answer the following question about the background text above:


    Question: "{question}"
    Answer: "Let's think step by step.
    """.strip()

async def answer(context: str = DEFAULT_CONTEXT, question: str = DEFAULT_QUESTION) -> str:
    prompt = make_qa_prompt(context, question)
    answer = await recipe.agent().complete(prompt=prompt, stop='"')
    return answer

recipe.main(answer)