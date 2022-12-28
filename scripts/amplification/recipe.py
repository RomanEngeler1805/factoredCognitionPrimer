from ice.recipe import recipe
from utils import *
from ice.recipes.primer.subquestions import ask_subquestions
from ice.utils import map_async

# get subquestions and answer them
async def get_subs(question: str) -> Subs:
    subquestions = await ask_subquestions(question=question)
    subanswers = await map_async(subquestions, answer)
    return list(zip(subquestions, subanswers))

# get the answer to a (sub-) question
async def answer(question: str, subs: Subs = []) -> str:
    prompt = make_qa_prompt(question, subs=subs)
    answer = await recipe.agent().complete(prompt=prompt, stop='"')
    return answer

# get subquestions and their answer to answer the original question
async def answer_by_amplification(
    question: str = "What is the effect of creatine on cognition?",
):
    subs = await get_subs(question)
    response = await answer(question=question, subs=subs)
    return response


recipe.main(answer_by_amplification)