'''
Inputs:
- Takes in a txt file with user's existing resume/work experience
- takes in a txt file with the job description
Output: generate a customized resume tailored to the job description

Approaches:
1. Iterate through job description, answering using entire user resume (extracting data)
2. Use text embeddings:
- embed user's resume
- iterate through job requirements, pulling data from user's resume
- rewrite sentences from the user's resume, rewriting to match as best as possible
'''

import openai
from openai.embeddings_utils import get_embedding
from keys import api_key
import re
import pandas as pd

#set up input params
openai.organization = "org-kqbJP1qBA8CVuReLEues52fs"
openai.api_key = api_key
embedding_model = "text-embedding-ada-002"
embedding_encoding = "cl100k_base"
max_tokens = 8000

#split input file based on sentences, get text embeddings and save
user_resume = open('user_resume.txt', 'r').read().strip()
user_resume_sentences = re.split(". |'\n' ")
embeddings = [get_embedding(s, engine=embedding_model) for s in user_resume_sentences]
with open('user_resume_embedded.txt', 'w') as f:
    [f.write(emb) for emb in embeddings]

#load input file as dataframe
emb_df = pd.read_csv('user_resume_embedded.txt', names=['emb'])

#get job description text
job_text = open('job_raw.txt', 'w').read()

#prompt model to summarize job description and qualifications in bullet points
completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful resume building assistant. I'll give you a job description, you tell me about the job."},
        {"role": "user", "content": f"Here is the job description: {job_text}"},
        {"role": "assistant", "content": "Ok, I understand the role."},
        {"role": "user", "content": "Briefly list the qualifications for the job in bullet points. Only output the qualifications, without any filler."},
        ],
    temperature=0.2,
    max_tokens=1000)

print('retrieved job description and qualifications')
open('job_req.txt', 'w').write(completion.choices[0].message.content)
qualification_list = completion.choices[0].message.content.split('\n')

#take top three most similar sentences. Use as input for model
for qual in qualification_list:
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful resume building assistant. I'll give you a job requirement, and my relevant qualifications. You write bullet points describing how my experience matches the job requirement."},
        {"role": "user", "content": f"Job requirement: {qual}"},
        {"role": "user", "content": "My experience: "},
        ],
    temperature=0.2,
    max_tokens=1000)