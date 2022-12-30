# get question
# think step by step with 1., 2., 3., ... (or -, -)
# start veryfing the first step given no context -> iterate;
# iterate through the steps to improve the answer
from ice.recipe import recipe
from ice.recipes.primer.verify.utils import *
from ice.recipes.primer.verify.utils import *

# PROMPTS
def make_qa_prompt(question: str) -> str:
    return f"""
    Answer the following question:


    Question: "{question}"
    Answer: "Let's think step by step:
    """.strip()


def render_prev_steps(steps: list[str]) -> str:
    if not steps:
        return ""
    steps_text = "\n\n".join(f"- {step}\n" for step in steps)
    return f"{steps_text}"


def make_improved_prompt(question: str, prev_steps: list[str], next_step: str) -> str:
    return f"""
    Given the context 
    "{render_prev_steps(prev_steps)}"

    Update the current step to answer the question. Show your reasoning.

    Question "{question}"
    
    Current answer step: "{next_step}"
    Updated answer step: "
    """.strip()

# VERIFICATION
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

# MAIN
async def answer(question: str = DEFAULT_QUESTION, MAX_STEPS: int = 2) -> str:
    # get first shot at the answer
    prompt = make_qa_prompt(question)
    answer = await recipe.agent().complete(prompt=prompt, stop='"')
    steps = [line.strip("- ") for line in answer.split("\n")]

    for k_step in range(len(steps)):
        # track the probability of correctness to only update the current reasoning step
        # if the updated step is more correct than the existing one
        p_correct = await verify_answer(question, steps[:k_step+1])
        p_correct_updated = p_correct

        k_improvements = 0
        while p_correct < 0.8 and k_improvements < MAX_STEPS:
            # make improvements to the current step
            prompt = make_improved_prompt(question, steps[:k_step], steps[k_step])
            answer = await recipe.agent().complete(prompt=prompt, stop='"')

            # verify the updated step
            p_correct_updated = await verify_answer(question, steps[:k_step]+ [answer]) # concatenate with the new step

            # replace the current step with the updated step if it is more correct
            if p_correct_updated > p_correct:
                p_correct = p_correct_updated
                steps[k_step] = answer

            k_improvements += 1

    return steps


recipe.main(answer)