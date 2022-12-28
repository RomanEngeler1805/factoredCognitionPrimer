from ice.paper import Paper
from ice.paper import Paragraph
from ice.recipe import recipe
# use my own implementation
# from ice.recipes.primer.qa import answer
from qa import answer
from ice.utils import map_async

# make prompt around (paragraph, question) pair
def make_classification_prompt(paragraph: Paragraph, question: str) -> str:
    return f"""Here is a paragraph from a research paper: "{paragraph}"

Question: Does this paragraph answer the question '{question}'? Say Yes or No.
Answer:"""

# classify paragraph (probabilities)
async def classify_paragraph(paragraph: Paragraph, question: str) -> float:
    choice_probs, _ = await recipe.agent().classify(
        prompt=make_classification_prompt(paragraph, question),
        choices=(" Yes", " No"),
    )
    return choice_probs.get(" Yes", 0.0)

# rank paragraphs based on the question answer probability
async def get_relevant_paragraphs(
    paper: Paper, question: str, n_tokens: int = 2048
) -> list[Paragraph]:
    probs = await map_async(
        paper.paragraphs, lambda par: classify_paragraph(par, question)
    )
    sorted_pairs = sorted(
        zip(paper.paragraphs, probs), key=lambda x: x[1], reverse=True
    )

    # MYCODE return as many paragraphs as can fit into the prompt (n_tokens)
    # where len(token) ~= 3.5* #characters
    top_n = 0
    prompt_len = 0
    while (prompt_len+ len(str(sorted_pairs[top_n][0]))) < 3.5* n_tokens:
        prompt_len += len(str(sorted_pairs[top_n][0]))
        top_n += 1
    
    # an alternative solution could be (though I don't know which is more efficient)
    # par_lenghts = [len(str(par)) for par, prob in sorted_pairs]
    # cum_par_lenghts = [sum(par_lenghts[:i]) for i in range(len(par_lenghts))]
    # find where cum_par_lenghts > 3.5* n_tokens

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