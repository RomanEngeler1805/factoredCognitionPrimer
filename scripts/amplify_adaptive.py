from ice.recipe import recipe
from ice.utils import map_async


Question = str
Answer = str
Subs = list[tuple[Question, Answer]]
Sups = list[Question]

# ================== Generate Prompts ==================
# prompt to evaluate if to further decompose
def make_evaluation_prompt(question: Question, sups: Sups) -> str:
    # get question
    # prompt to evaluate if to further decompose
    superquestions_text = render_superquestion(sups)
    return f"""{superquestions_text}Here is the current subquestion to be answered
    Q:"{question}"

    Question: Do you need more information to answer this subquestion? Say Yes or No.
    Answer:"""

# prompt to generate subquestions
def make_subquestion_prompt(question: str) -> str:
    return f"""Decompose the following question into 2-5 subquestions that would help you answer the question. Make the questions stand alone, so that they can be answered without the context of the original question.

Question: "{question}"
Subquestions:
-""".strip()

# prompt to answer subquestion
def make_qa_prompt(question: str, sups: Sups, subs: Subs) -> str:
    background_text = render_background(subs)
    superquestions_text = render_superquestion(sups)

    return f"""{background_text}{superquestions_text}Answer the following question, using the background information above where helpful:

    Question: "{question}"
    Answer: "
    """.strip()

# prompt with superquestions
def render_superquestion(sups: Sups) -> str:
    if not sups:
        return ""
    sups_text = "\n".join(f"Q: {q}" for q in sups)
    return f"Here are the relevant superquestions to answer:\n\n{sups_text}\n\n"

# prompt with background information
def render_background(subs: Subs) -> str:
    if not subs:
        return ""
    subs_text = "\n\n".join(f"Q: {q}\nA: {a}" for (q, a) in subs)
    return f"Here is relevant background information:\n\n{subs_text}\n\n"


# ================== Generate Subquestions ==================
# evaluate if to further decompose
async def evaluate_decomposition(question: Question, sups: Sups) -> float:
    # get question
    # evaluate if to further decompose
    choice_probs, _ = await recipe.agent().classify(
        prompt=make_evaluation_prompt(question, sups),
        choices=(" Yes", " No")
    )
    return choice_probs.get(" Yes", 0)

# generate subquestions
async def ask_subquestions(
    question: str = "What is the effect of creatine on cognition?",
):
    prompt = make_subquestion_prompt(question)
    subquestions_text = await recipe.agent().complete(prompt=prompt)
    subquestions = [line.strip("- ") for line in subquestions_text.split("\n")]
    return subquestions

# ================== Main Routine ==================
# receive question -> break into subquestions and answer them
async def get_subs(question: str, sups: Sups, depth: int) -> Subs:
    sups_copy = sups.copy() # make copy since passed by reference
    sups_copy.append(question)
    subquestions = await ask_subquestions(question=question)
    subanswers = await map_async(
        subquestions, lambda q: answer_by_amplification(question=q, sups=sups_copy, depth=depth)
    )
    return list(zip(subquestions, subanswers))

# receive question -> break into subquestions and answer them -> answer question
async def answer_by_amplification(
    question: str = "What is the effect of creatine on cognition?", sups: Sups = [], depth: int = 1
):
    # adaptive decomposition
    #subs = await get_subs(question, depth - 1) if depth > 0 else []
    decompose = round(await evaluate_decomposition(question, sups))
    subs = await get_subs(question, sups, depth - 1) if (depth > 0 and decompose == 1) else []
    prompt = make_qa_prompt(question, sups=sups, subs=subs)
    answer = await recipe.agent().complete(prompt=prompt, stop='"')
    return answer


recipe.main(answer_by_amplification)