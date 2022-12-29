from ice.recipe import recipe
from ice.recipes.primer.subquestions import ask_subquestions
from ice.utils import map_async


Question = str
Answer = str
Subs = list[tuple[Question, Answer]]
Sups = list[Question]

# render background information for prompt
def render_background(subs: Subs) -> str:
    if not subs:
        return ""
    subs_text = "\n\n".join(f"Q: {q}\nA: {a}" for (q, a) in subs)
    return f"Here is relevant background information:\n\n{subs_text}\n\n"

# render superquestion prompt
def render_superquestion(sups: Sups) -> str:
    if not sups:
        return ""
    sups_text = "\n".join(f"Q: {q}" for q in sups)
    return f"Here are the relevant superquestions to answer:\n\n{sups_text}\n\n"

# get background information and answer the question
def make_qa_prompt(sups: Sups, question: str, subs: Subs) -> str:
    background_text = render_background(subs)
    superquestions_text = render_superquestion(sups)

    return f"""{background_text}{superquestions_text}Answer the following question, using the background information above where helpful:

    Question: "{question}"
    Answer: "
    """.strip()

# receive question -> break into subquestions and answer them
async def get_subs(sups: Sups, question: str, depth: int) -> Subs:
    sups_copy = sups.copy() # make copy since passed by reference
    sups_copy.append(question)
    subquestions = await ask_subquestions(question=question)
    subanswers = await map_async(
        subquestions, lambda q: answer_by_amplification(superquestions=sups_copy, question=q, depth=depth)
    )
    return list(zip(subquestions, subanswers))

# receive question -> get (subquestion, answer) pairs -> answer question
async def answer_by_amplification(sups: Sups = [],
    question: str = "What is the effect of creatine on cognition?", depth: int = 1
):
    subs = await get_subs(sups, question, depth - 1) if depth > 0 else [] # (subquestion, answer) pairs
    prompt = make_qa_prompt(sups, question, subs=subs)
    answer = await recipe.agent().complete(prompt=prompt, stop='"') # answer question with (subquestion, answer) pairs as context
    return answer


recipe.main(answer_by_amplification)