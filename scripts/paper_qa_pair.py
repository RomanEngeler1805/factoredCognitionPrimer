from ice.paper import Paper
from ice.paper import Paragraph
from ice.recipe import recipe
# use my own implementation
# from ice.recipes.primer.qa import answer
from qa import answer
from ice.utils import map_async

# MYCODE make prompt around (paragraph, question) pair
def make_classification_prompt(paragraph1: Paragraph, paragraph2: Paragraph, question: str) -> str:
    return f"""Here are two paragraphs from a research paper:
    1. "{paragraph1}"
    2. "{paragraph2}"

    Question: Which paragraph better answers the question '{question}'? Say 1 or 2.
Answer:"""

# classify paragraph (probabilities)
async def classify_paragraph(paragraph1: Paragraph, paragraph2: Paragraph, question: str) -> float:
    choice_probs, _ = await recipe.agent().classify(
        prompt=make_classification_prompt(paragraph1, paragraph2, question),
        choices=(" 1", " 2"),
    )
    return choice_probs.get(" 1", 0.0)

# MYCODE derive ranking from pairwise comparison of paragraphs
def get_wins(probs: list[list[float]]) -> list[int]:
    probs_int = [[round(p) for p in ps] for ps in probs] # convert to 0/1
    wins = [sum(ps) for ps in probs_int] # count number of wins
    return wins

# MYCODE rank paragraphs based on the question answer probability
async def get_relevant_paragraphs(
    paper: Paper, question: str, top_n: int = 3
) -> list[Paragraph]:

    # pairwise comparison of paragraphs
    pars = [par for par in paper.paragraphs]
    probs = [] # list of list of probabilities
    # loop over paragraphs corresponding to rows
    for k, par in enumerate(paper.paragraphs):
       ps =  await map_async(paper.paragraphs, lambda p: classify_paragraph(par, p, question))
       ps[k] = 0 # set probability of comparing paragraph to itself to 0
       probs.append(ps)

    # average probabilities as probs should be symmetric -> averages the effect of asking is A better as B ,or B better as A
    probs_T = list(map(list, zip(*probs)))
    probs_avg = [[(p1 + p2) / 2 for p1, p2 in zip(ps1, ps2)] for ps1, ps2 in zip(probs, probs_T)]

    sorted_pairs = sorted(
        zip(paper.paragraphs, get_wins(probs_avg)), key=lambda x: x[1], reverse=True
    )

    return [par for par, prob in sorted_pairs[:top_n]]


# return answer based on the top paragraphs
async def answer_for_paper(
    paper: Paper, question: str = "What was the study population?"
):
    relevant_paragraphs = await get_relevant_paragraphs(paper, question)
    relevant_str = "\n\n".join(str(p) for p in relevant_paragraphs) # join paragraphs together
    response = await answer(context=relevant_str, question=question) # answer the question
    return response


recipe.main(answer_for_paper)