# Bedtime story generator
 
A CLI tool that turns a one-line story request into an age-appropriate (5-10) bedtime
story, using a category-aware prompting pipeline with an LLM judge that critiques and
improves the draft before it's shown to the user.

## Setup
 
```bash
pip install "openai<1.0" python-dotenv
```
 
Create a `.env` file in the project root:
 
```
OPENAI_API_KEY=sk-...
```
 
Then run:
 
```bash
python main.py
```
 
You'll be prompted for a story request, then the pipeline runs automatically. Once a
story is shown, you can type `changes` to request edits, `new` to start a fresh story,
or `done` to quit.

## Architecture
 
```
                    User input
                        |
                        v
              +-------------------+
              | Categorize request|
              | (1 of 5 categories)|
              +-------------------+
                        |
                        v
              +-------------------+
              |  Generate story    |
              | (category-specific |
              |   prompt template) |
              +-------------------+
                        |
                        v
              +-------------------+
   +--------->|  Judge & revise    |
   | changes  | (checks quality,   |
   |          |  revises once max) |
   |          +-------------------+
   |                    |
   |                    v
   |          +-------------------+
   |          | Show story to user |
   |          +-------------------+
   |                    |
   |                    v
   |          +-------------------+
   +----------|  Ask what's next   |
              | (changes / new     |
   new story  |  story / done)     |
   |          +-------------------+
   |                    |
   |                    v done
   v              +-----------+
(loop to          |   Done    |
 Categorize)      +-----------+
```

### Flow
 
- **Categorize request** — an LLM call picks one of five categories (`friendship`,
   `adventure`, `silly`, `lesson`, `comforting`, or `general` as a fallback).
- **Generate story** — a shared base template (age rules, 4-beat arc, length, output
   format) combined with that category's specific guidance.
- **Judge & revise** — a second LLM call scores the draft against a rubric
   (age-appropriateness, arc, engagement, category fit) and returns strict JSON:
   `{"passed": bool, "feedback": str}`. If it fails, one revision pass is made using
   that feedback; capped at one to bound cost/latency. If the judge's response isn't
   valid JSON, the pipeline fails open (treats it as passed) rather than blocking the
   user.
- **Ask what's next** — `changes` loops back into `revise_story` with the user's own
   feedback instead of the judge's; `new` loops back to categorize; `done` exits.



## Original assignment
# Hippocratic AI Coding Assignment
Welcome to the [Hippocratic AI](https://www.hippocraticai.com) coding assignment

## Instructions
The attached code is a simple python script skeleton. Your goal is to take any simple bedtime story request and use prompting to tell a story appropriate for ages 5 to 10.
- Incorporate a LLM judge to improve the quality of the story
- Provide a block diagram of the system you create that illustrates the flow of the prompts and the interaction between judge, storyteller, user, and any other components you add
- Do not change the openAI model that is being used. 
- Please use your own openAI key, but do not include it in your final submission.
- Otherwise, you may change any code you like or add any files

---

## Rules
- This assignment is open-ended
- You may use any resources you like with the following restrictions
   - They must be resources that would be available to you if you worked here (so no other humans, no closed AIs, no unlicensed code, etc.)
   - Allowed resources include but not limited to Stack overflow, random blogs, chatGPT et al
   - You have to be able to explain how the code works, even if chatGPT wrote it
- DO NOT PUSH THE API KEY TO GITHUB. OpenAI will automatically delete it

---

## What does "tell a story" mean?
It should be appropriate for ages 5-10. Other than that it's up to you. Here are some ideas to help get the brain-juices flowing!
- Use story arcs to tell better stories
- Allow the user to provide feedback or request changes
- Categorize the request and use a tailored generation strategy for each category

---

## How will I be evaluated
Good question. We want to know the following:
- The efficacy of the system you design to create a good story
- Are you comfortable using and writing a python script
- What kinds of prompting strategies and agent design strategies do you use
- Are the stories your tool creates good?
- Can you understand and deconstruct a problem
- Can you operate in an open-ended environment
- Can you surprise us

---

## Other FAQs
- How long should I spend on this? 
No more than 2-3 hours
- Can I change what the input is? 
Sure
- How long should the story be?
You decide