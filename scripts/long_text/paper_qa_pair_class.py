from ice.paper import Paper
from ice.paper import Paragraph
from ice.recipe import recipe

# make prompt around (paragraph, question) pair
def make_classification_prompt(paragraph1: Paragraph, paragraph2: Paragraph, question: str) -> str:
    return f"""Here are two paragraphs from a research paper:
    1. "{paragraph1}"
    2. "{paragraph2}"

    Question: Which paragraph is more relevant to the question '{question}'? Say 1 or 2.
Answer:""".strip()

# classify paragraph (probabilities)
async def classify_paragraph(paragraph1: Paragraph, paragraph2: Paragraph, question: str) -> float:
    choice_probs, _ = await recipe.agent().classify(
        prompt=make_classification_prompt(paragraph1, paragraph2, question),
        choices=(" 1", " 2"),
    )
    return choice_probs.get(" 1", 0.0)

# return probability for the first paragraph
async def answer_for_paper(paper: Paper, question: str):
    paragraph1 = paper.paragraphs[0]
    paragraph2 = paper.paragraphs[11]
    return await classify_paragraph(paragraph1, paragraph2, question)


recipe.main(answer_for_paper)