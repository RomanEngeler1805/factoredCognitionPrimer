from ice.recipes.primer.debate.types import *

# initialize the debate
def initialize_debate(question: Message) -> Debate:
    return [
        ("Question", question),
        ("Alice", "I'm in favor."),
        ("Bob", "I'm against."),
    ]

# render the debate in turns
def render_debate(debate: Debate, self_name: Name | None = None) -> str:
    debate_text = ""

    # loop over the (speaker, text) tuples in the debate
    for speaker, text in debate:
        # replace the speaker's name with "You" if it's the same as self_name
        if speaker == self_name:
            speaker = "You"
        debate_text += f'{speaker}: "{text}"\n'
    return debate_text.strip()

print(render_debate(my_debate, self_name="Alice"))