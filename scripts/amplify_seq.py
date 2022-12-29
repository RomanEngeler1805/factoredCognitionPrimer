from ice.recipe import recipe
from ice.utils import map_async


Question = str
Answer = str
Subs = list[tuple[Question, Answer]]

# render background information for prompt
def render_background(subs: Subs) -> str:
    if not subs:
        return ""
    subs_text = "\n\n".join(f"Q: {q}\nA: {a}" for (q, a) in subs)
    return f"Here is relevant background information:\n\n{subs_text}\n\n"

# render previous questions for prompt
def render_previous_subs(subs: Subs) -> str:
    if not subs:
        return ""
    subs_text = "\n\n".join(f"Q: {q}\nA: {a}" for (q, a) in subs)
    return f"The answers to previous subquestions: \n\n{subs_text}\n\n"

# prompt to generate subquestions
def make_subquestion_prompt(question: str, subs: Subs) -> str:
    previous_subs_text = render_previous_subs(subs)

    return f"""Decompose the following
    Question: "{question}"

    into a single stand alone subquestion that would help you answer the question. \n
    
    {previous_subs_text}
Subquestion: 
""".strip()

#
async def ask_subquestion(
    question: str = "What is the effect of creatine on cognition?", subs: Subs = []
):
    prompt = make_subquestion_prompt(question, subs)
    subquestion = await recipe.agent().complete(prompt=prompt)
    return subquestion

# get background information and answer the question
def make_qa_prompt(question: str, subs: Subs) -> str:
    background_text = render_background(subs)
    return f"""{background_text}Answer the following question, using the background information above where helpful:

    Question: "{question}"
    Answer: "
    """.strip()

# receive question -> break into subquestions and answer them
async def get_subs(question: str, depth: int) -> Subs:
    # make this part sequential
    subquestions = []
    subanswers = []
    for k in range(2): # improvement: include a criteria if the model thinks it shoud stop
        subquestion = await ask_subquestion(question=question, subs=list(zip(subquestions, subanswers)))
        subanswer = await answer_by_amplification(question=subquestion, depth=depth)
        subquestions.append(subquestion)
        subanswers.append(subanswer)
    return list(zip(subquestions, subanswers))

# receive question -> get (subquestion, answer) pairs -> answer question
async def answer_by_amplification(
    question: str = "What is the effect of creatine on cognition?", depth: int = 1
):
    subs = await get_subs(question, depth - 1) if depth > 0 else []
    prompt = make_qa_prompt(question, subs=subs)
    answer = await recipe.agent().complete(prompt=prompt, stop='"')
    return answer


recipe.main(answer_by_amplification)