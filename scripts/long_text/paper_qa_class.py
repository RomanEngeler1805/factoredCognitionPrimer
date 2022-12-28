from ice.paper import Paper
from ice.paper import Paragraph
from ice.recipe import recipe

# make prompt around (paragraph, question) pair
def make_classification_prompt(paragraph: Paragraph, question: str) -> str:
    return f"""Here is a paragraph from a research paper: "{paragraph}"

Question: Does this paragraph answer the question '{question}'? Say Yes or No.
Answer:""".strip()

# classify paragraph (probabilities)
async def classify_paragraph(paragraph: Paragraph, question: str) -> float:
    choice_probs, _ = await recipe.agent().classify(
        prompt=make_classification_prompt(paragraph, question),
        choices=(" Yes", " No"),
    )
    return choice_probs.get(" Yes", 0.0)

# return probability for the first paragraph
async def answer_for_paper(paper: Paper, question: str):
    paragraph = paper.paragraphs[0]
    return await classify_paragraph(paragraph, question)


recipe.main(answer_for_paper)