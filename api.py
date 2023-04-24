# Chat GPT API integration
from k import api_key
import os
import openai

openai.organization = "org-kqbJP1qBA8CVuReLEues52fs"
openai.api_key = api_key
models = openai.Model.list()
model_choice = "gpt-3.5-turbo"

prompt = input("> ")

completion = openai.ChatCompletion.create(
  model=model_choice,
  messages=[
    {"role": "user", "content": "Hello!"}
  ]
)
import pdb; pdb.set_trace()
