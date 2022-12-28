from ice.paper import Paper
from ice.paper import Paragraph
from ice.recipe import recipe
from ice.utils import map_async

# make prompt around (paragraph, question) pair
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

# rank paragraphs based on the question answer probability
async def get_relevant_paragraphs(
    paper: Paper, question: str
) -> list[Paragraph]:

    # pairwise comparison of paragraphs
    pars = [par for par in paper.paragraphs]
    probs = [] # list of list of probabilities
    # loop over paragraphs corresponding to rows
    for k, par in enumerate(paper.paragraphs):
       ps =  await map_async(paper.paragraphs, lambda p: classify_paragraph(par, p, question))
       ps[k] = 0 # set probability of comparing paragraph to itself to 0
       probs.append(ps)

    return probs


recipe.main(get_relevant_paragraphs)