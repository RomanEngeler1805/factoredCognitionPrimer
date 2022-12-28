from ice.agents.base import Agent
from ice.recipe import recipe
from ice.recipes.primer.debate.prompt import *
from ice.recipes.primer.debate.types import *
from ice.recipes.primer.debate.utils import *

# initialize the debate
def initialize_debate(question: Message, agent_names: list) -> Debate:
    return [
        ("Question", question),
        (agent_names[0], "I'm in favor."),
        (agent_names[1], "I'm against."),
    ]

# render the debate in turns (used to render the debate history)
def render_debate(debate: Debate, self_name: Name | None = None) -> str:
    debate_text = ""

    # loop over the (speaker, text) tuples in the debate
    for speaker, text in debate:
        # replace the speaker's name with "You" if it's the same as self_name
        if speaker == self_name:
            speaker = "You"
        debate_text += f'{speaker}: "{text}"\n'
    return debate_text.strip()

# MYCODE render the judge prompt
def render_judge_prompt(agent_name: str, debate: Debate) -> str:
    prompt = f"""
    You are {agent_name}. You are trying to decide who won the debate. Output a name. You have the following information:
    
    {render_debate(debate, agent_name)}
    You: The winner is "
    """.strip()
    return prompt

# MYCODE generate the judge decision
async def make_judge_decision(debate: Debate, agent: Agent, agent_name: Name, debate_stage: str):
    prompt = render_judge_prompt(agent_name, debate)
    answer = await agent.complete(prompt=prompt, stop="\n")
    return (agent_name, f"The winner {debate_stage} the debate is "+ answer.strip('" '))

# debate prompt to generate a single turn of the debate
def render_debate_prompt(agent_name: str, debate: Debate, turns_left: int) -> str:
    prompt = f"""
You are {agent_name}. There are {turns_left} turns left in the debate. You are trying to win the debate using reason and evidence. Don't repeat yourself. No more than 1-2 sentences per turn.

{render_debate(debate, agent_name)}
You: "
""".strip()
    return prompt

# generate a single turn of the debate
async def turn(debate: Debate, agent: Agent, agent_name: Name, turns_left: int):
    prompt = render_debate_prompt(agent_name, debate, turns_left)
    answer = await agent.complete(prompt=prompt, stop="\n")
    return (agent_name, answer.strip('" '))

# rollout the debate
async def _debate(question: str = "Should we legalize all drugs?"):
    # initialize the debate
    agents = [recipe.agent(), recipe.agent()]
    agent_names = ["Bob", "Jessica"]
    judge = recipe.agent()
    debate = initialize_debate(question, agent_names)

    # judge the debate (before the debate starts)
    decision_before = await make_judge_decision(debate, judge, "Judge", "before")

    # loop over the turns
    turns_left = 3
    while turns_left > 0:
        for agent, agent_name in zip(agents, agent_names):
            response = await turn(debate, agent, agent_name, turns_left)
            debate.append(response)
            turns_left -= 1
    
    # judge the debate (after the debate ends)
    decision_after = await make_judge_decision(debate, judge, "Judge", "after")
    debate.append(decision_before)
    debate.append(decision_after)
    return debate

# MYCODE generate a question and debate
async def debate():
    prompt = f"""Generate a question for the debate. It should be a yes/no question.
    
    Question: """
    question = await recipe.agent().complete(prompt=prompt, stop='"')
    debate = await _debate(question.strip('" '))
    return render_debate(debate)

recipe.main(debate)