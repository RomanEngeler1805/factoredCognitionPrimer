from ice.recipe import recipe
from ice.recipes.primer.verify.utils import *

def make_verification_prompt(question: str, steps: list[str]) -> str:
    return f"""Consider the
    Question: {question}
    
    Given the reasoning steps: {render_steps(steps)}

    Q: Is step {len(steps)} correct, assuming that the previous steps are correct? Say Yes or No.
    A: """


async def check_step(question: str, steps: list[str]) -> float:
    prompt = make_verification_prompt(question=question, steps=steps)
    choice_probs, _ = await recipe.agent().classify(
        prompt=prompt, choices=(" Yes", " No")
    )
    return choice_probs.get(" Yes", 0)


async def verify_answer(question: str = DEFAULT_QUESTION, steps: list[str] = DEFAULT_STEPS):
    return await check_step(question=question, steps=steps)


recipe.main(verify_answer)