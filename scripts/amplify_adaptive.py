from ice.recipe import recipe
from ice.recipes.primer.subquestions import ask_subquestions
from ice.utils import map_async


Question = str
Answer = str
Subs = list[tuple[Question, Answer]]


def make_evaluation_prompt(question: Question) -> str:
    # get question
    # prompt to evaluate if to further decompose
    return f"""Here is the question to be answered "{question}"

    Question: Do you need more information to answer this question? Say Yes or No.
    Answer:"""


async def evaluate_decomposition(question: Question) -> float:
    # get question
    # evaluate if to further decompose
    choice_probs, _ = await recipe.agent().classify(
        prompt=make_evaluation_prompt(question),
        choices=(" Yes", " No")
    )
    return choice_probs.get(" Yes", 0)


def render_background(subs: Subs) -> str:
    if not subs:
        return ""
    subs_text = "\n\n".join(f"Q: {q}\nA: {a}" for (q, a) in subs)
    return f"Here is relevant background information:\n\n{subs_text}\n\n"


def make_qa_prompt(question: str, subs: Subs) -> str:
    background_text = render_background(subs)
    return f"""{background_text}Answer the following question, using the background information above where helpful:

Question: "{question}"
Answer: "
""".strip()


async def get_subs(question: str, depth: int) -> Subs:
    subquestions = await ask_subquestions(question=question)
    subanswers = await map_async(
        subquestions, lambda q: answer_by_amplification(question=q, depth=depth)
    )
    return list(zip(subquestions, subanswers))


async def answer_by_amplification(
    question: str = "What is the effect of creatine on cognition?", depth: int = 1
):
    # adaptive decomposition
    #subs = await get_subs(question, depth - 1) if depth > 0 else []
    decompose = round(await evaluate_decomposition(question))
    subs = await get_subs(question, depth - 1) if (depth > 0 and decompose == 1) else []
    prompt = make_qa_prompt(question, subs=subs)
    answer = await recipe.agent().complete(prompt=prompt, stop='"')
    return answer


recipe.main(answer_by_amplification)