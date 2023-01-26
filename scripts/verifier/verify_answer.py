from ice.recipe import recipe

def make_verification_prompt(question :str, answer: str) -> str:
    return f"""Consider the
    Question: {question}
    Potential Answer: {answer}

    Is the potential answer above correct? Say Yes or No:"""

async def verify_answer(question :str, answer: str) -> float:
    prompt = make_verification_prompt(question= question, answer= answer)
    choice_probs, _ = await recipe.agent().classify(
        prompt=prompt, choices=(" Yes", " No")
    )
    return choice_probs.get(" Yes", 0)

recipe.main(verify_answer)