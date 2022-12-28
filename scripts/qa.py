from ice.recipe import recipe

DEFAULT_CONTEXT = "We're running a hackathon on 9/9/2022 to decompose complex reasoning tasks into subtasks that are easier to automate & evaluate with language models. Our team is currently breaking down reasoning about the quality of evidence in randomized controlled trials into smaller tasks e.g. placebo, intervention adherence rate, blinding procedure, etc."

DEFAULT_QUESTION = "What is happening on 9/9/2022?"

DEFAULT_STEPS = 2

def make_qa_prompt(context: str, question: str) -> str:
    return f"""
    Background text: "{context}"
    
    Answer the following question about the background text above:


    Question: "{question}"
    Answer: "Let's think step by step.
    """.strip()

def make_improved_prompt(context: str, question: str, ansewr: str) -> str:
    return f"""
    Background text: "{context}"
    Question: "{question}"

    Improve the following answer attempt to the question and the background text above:


    Answer attempt: "{answer}"
    Improved answer: "Let's think step by step.
    """.strip()

async def answer(context: str = DEFAULT_CONTEXT, question: str = DEFAULT_QUESTION) -> str:
    prompt = make_qa_prompt(context, question)
    answer = await recipe.agent().complete(prompt=prompt, stop='"')

    improved_answer = ""

    for count in range(DEFAULT_STEPS):
        improved_prompt = make_improved_prompt(context, question, answer)
        improved_answer = await recipe.agent().complete(prompt=improved_prompt, stop='"')
        if answer == improved_answer:
            break
        answer = improved_answer
    return improved_answer

recipe.main(answer)