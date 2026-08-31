import os
import openai
import json 
from dotenv import load_dotenv

load_dotenv() 


# Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:
# - Make the "unclear/gibberish input" behavior configurable rather than
# hardcoded — right now nonsense text gets used literally (including as character
# names), which is fine but not the only reasonable choice.
# - Let the category set grow dynamically instead of staying fixed at five when a request doesn't fit well, have the LLM propose a new category name and write
# its own guidance snippet on the fly, rather than always falling back to `general`.
# - build a simple web UI (the CLI works, but a browser front-end with a text box and a "changes / new story / done" set of buttons would make this actually usable.

CATEGORIES = [
    "friendship",
    "adventure",
    "silly",
    "lesson",
    "comforting",
]

def call_model(prompt: str, max_tokens=3000, temperature=0.1) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY") # please use your own openai api key here.
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        stream=False,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message["content"]  # type: ignore

CATEGORIZE_PROMPT = """Classify this children's bedtime story request into exactly \
one category from this list: {categories}, or "general" if none clearly fit.
 
Request: "{user_input}"
 
Respond with ONLY the single category word, lowercase, nothing else.
"""
 
 
def categorize(user_input: str) -> str:
    prompt = CATEGORIZE_PROMPT.format(categories=", ".join(CATEGORIES), user_input=user_input)
    raw = call_model(prompt, max_tokens=10).strip().lower()
    for category in CATEGORIES:
        if category in raw:
            return category
    return "general"
 
 
CATEGORY_GUIDANCE = {
    "friendship": (
        "Center the story on two characters resolving a small conflict through "
        "kindness or honest communication. Keep the stakes gentle -- a "
        "misunderstanding or hurt feelings, not a big danger. End with the "
        "friendship stronger than before."
    ),
    "adventure": (
        "Give the protagonist a clear goal and one obstacle standing between them "
        "and it. Use energetic, sensory language. End with a satisfying, earned "
        "win -- the character overcomes the obstacle through their own effort."
    ),
    "silly": (
        "Lean into humor, absurdity, and wordplay. Repetition and rhythm are "
        "welcome (kids like reading these lines aloud). The plot can be loose -- "
        "charm and silliness matter more than a tight arc here."
    ),
    "lesson": (
        "Build the story around a character facing a choice, and show the natural "
        "consequence of that choice. Let the lesson emerge from what happens, not "
        "from a character explicitly stating a moral at the end."
    ),
    "comforting": (
        "This is for an anxious moment at bedtime (fear of the dark, a monster, "
        "starting school). Keep intensity low throughout -- mysterious, not "
        "frightening. The fear must be fully resolved by the end so the story "
        "actually helps a child settle down to sleep."
    ),
    "general": (
        "Use a simple, warm story arc: a character wants something, faces a small "
        "bit of friction, and reaches a happy, satisfying resolution."
    ),
}
 
 
BASE_TEMPLATE = """Write a bedtime story for a child aged 5 to 10, based on this \
request: "{user_input}"
 
Category-specific guidance: {category_guidance}
 
Requirements for every story, regardless of category:
- Simple vocabulary appropriate for a 5-10 year old.
- No violence, no unresolved scary content -- mild tension is fine if it resolves.
- A real story arc: a setup, a small problem or tension, a turning point, and a \
resolution. Do not just describe a sequence of events with no shape.
- Use the specific characters, names, and details from the request wherever given.
- Around 400-600 words.
 
Respond with ONLY the story text. No title, no preamble, no notes.
"""
 
 
def generate_story(user_input: str, category: str) -> str:
    guidance = CATEGORY_GUIDANCE.get(category, CATEGORY_GUIDANCE["general"])
    prompt = BASE_TEMPLATE.format(user_input=user_input, category_guidance=guidance)
    return call_model(prompt, max_tokens=1200).strip()
 
JUDGE_PROMPT = """You are a strict but fair children's story editor. Evaluate the \
story below against this rubric:
 
1. Age-appropriateness: suitable for a 5-10 year old. No violence, scares, or \
themes beyond mild, resolved tension. Simple vocabulary for the age range.
2. Story arc: has a clear setup, a small problem or tension, a turning point, and \
a satisfying resolution. Not just a flat description of events.
3. Engagement: has some sensory detail, personality, or charm. Not generic or bland.
4. Category fit: matches the intended category "{category}" (its tone and the kind \
of problem/resolution that category implies).
 
Original request: "{user_input}"
 
Story to evaluate:
---
{story}
---
 
Respond with ONLY a JSON object, no markdown fences, no other text, in this exact \
shape:
{{"passed": true or false, "feedback": "1-3 sentences of specific, actionable \
feedback. If passed is true, briefly say what works. If passed is false, say \
exactly what to fix."}}
"""
 
 
def judge_story(story: str, user_input: str, category: str) -> tuple[bool, str]:
    prompt = JUDGE_PROMPT.format(category=category, user_input=user_input, story=story)
    raw = call_model(prompt, max_tokens=300)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
 
    try:
        data = json.loads(cleaned)
        passed = bool(data["passed"])
        feedback = str(data["feedback"])
    except (json.JSONDecodeError, KeyError, TypeError):
        passed, feedback = True, f"(judge response unparseable, raw: {cleaned[:200]})"
 
    return passed, feedback

REVISE_PROMPT = """You are a children's story editor revising a bedtime story for a \
5-10 year old.

Original story:
---
{story}
---

Feedback to address:
{feedback}

Rewrite the story to address this feedback. Keep the same characters, setting, and \
core idea as the original -- do not start over from scratch. Keep it appropriate for \
ages 5-10 (no violence, no unresolved scares, simple vocabulary), and keep it roughly \
the same length as the original.

Respond with ONLY the revised story text. No preamble, no notes, no markdown.
"""


def revise_story(story: str, feedback: str) -> str:
    prompt = REVISE_PROMPT.format(story=story, feedback=feedback)
    return call_model(prompt, max_tokens=3000).strip()
 
 
 
def main():
    while True:
        user_input = input("\nWhat kind of story do you want to hear? ")
        category = categorize(user_input)
        story = generate_story(user_input, category)
        passed, feedback = judge_story(story, user_input, category)
        if not passed:
            story = revise_story(story, feedback)
 
        while True:
            print(f"\n{story}\n")
            choice = input(
                "Type 'changes' to request edits, 'new' for a new story, "
                "or 'done' to quit: "
            ).strip().lower()
 
            if choice.startswith("change"):
                user_feedback = input("What would you like changed? ")
                story = revise_story(story, user_feedback)
                # loop back to print the revised story and ask again
            elif choice.startswith("new"):
                break  # exits inner loop, outer loop starts a fresh story
            elif choice.startswith("done"):
                return
            else:
                print("Sorry, please type 'changes', 'new', or 'done'.")


if __name__ == "__main__":
    main()