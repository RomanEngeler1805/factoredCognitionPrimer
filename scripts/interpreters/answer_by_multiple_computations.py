from fvalues import F
from ice.recipe import recipe


def make_computation_choice_prompt(question: str) -> str:
    return F(
        f"""You've been asked to answer the question "{question}".

You have access to a Python interpreter.

Enter expressions that will help you answer the question. Start each expression with ">>>" on a new line. Don't print the result.
Format according to the black formatter.

>>>"""
    )


def make_compute_qa_prompt(question: str, expression: str, result: str) -> str:
    return F(
        f"""A recording of a Python interpreter session:

>>> {expression}: {result}

Answer the following question, using the Python session if helpful:

Question: "{question}"
Answer: "
"""
    ).strip()


def exec_python(expression: str) -> str:
    '''Execute a Python expression and return the result as a string.'''
    try:
        result = exec(expression)
    except Exception as e:
        result = F(f"Error: {e}")
    return str(result)


async def choose_computation(question: str) -> str:
    prompt = make_computation_choice_prompt(question)
    answer = await recipe.agent().complete(prompt=prompt, stop='"')
    return answer


async def answer_by_computation(question: str):
    expression = await choose_computation(question)
    expression = expression.replace('>>>', '').replace('...', '')
    print(expression)
    print(isinstance(expression, str))
    result = exec_python(expression)
    print(result)
    prompt = make_compute_qa_prompt(question, expression, result)
    answer = await recipe.agent().complete(prompt=prompt, stop='"')
    return answer

recipe.main(answer_by_computation)