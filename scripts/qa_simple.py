from ice.recipe import recipe

# assemble the prompt
def make_qa_prompt(question: str) -> str:
    return f"""Answer the following question:

Question: "{question}"
Answer: "
""".strip()

# the answer function calling the agent with the prompt
async def answer(question: str = "What is happening on 9/9/2022?"):
    prompt = make_qa_prompt(question)
    answer = await recipe.agent().complete(prompt=prompt, stop='"')
    return answer

# the main function calling the answer function
recipe.main(answer)