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
#from openai.embeddings_utils import get_embedding, cosine_similarity
import re
import pandas as pd
import json
import argparse

#openai.organization = "org-kqbJP1qBA8CVuReLEues52fs"
#openai.api_key = api_key

class ResumeBuilder:
    def __init__(self, config_json):
        self.organization = config_json['organization']
        openai.organization = self.organization
        self.api_key = config_json['api_key']
        openai.api_key = self.api_key

    #function to write finalized resume
    def write_resume(self, new_resume_text, filename='new_resume.txt'):
        open(filename, 'w').write(new_resume_text)

    def embed_resume(self, resume_text_string):
        #set up input params
        self.embedding_model = "text-embedding-ada-002"
        self.embedding_encoding = "cl100k_base"
        self.max_embedding_tokens = 8000

        #split input file based on sentences, get text embeddings and save
        user_resume_sentences = re.split(". |'\n' ", resume_text_string)
        emb_df = pd.DataFrame({'sentences': user_resume_sentences})
        emb_df['emb'] = [get_embedding(s, engine=self.embedding_model) for s in user_resume_sentences]
        return emb_df

    def get_qualification_list(self, job_listing_string):
        #get job description text
        job_listing_string = open('job_raw.txt', 'w').read()

        #prompt model to summarize job description and qualifications in bullet points
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful resume building assistant. I'll give you a job description, you tell me about the job."},
                {"role": "user", "content": f"Here is the job description: {job_listing_string}"},
                {"role": "assistant", "content": "Ok, I understand the role."},
                {"role": "user", "content": "Briefly list the qualifications for the job in bullet points. Only output the qualifications, without any filler."},
                ],
            temperature=0.2,
            max_tokens=1000)

        print('retrieved job description and qualifications')
        return completion.choices[0].message.content.split('\n')

    def rewrite_from_embeddings(self, qualification_list, emb_df):
        #take top three most similar sentences. Use as input for model
        rewrite_list = []
        for qual in qualification_list:
            req_embedding = get_embedding(
                qual,
                engine="text-embedding-ada-002"
            )
            emb_df['similarity'] = emb_df['emb'].apply(lambda x: cosine_similarity(x, req_embedding))
            top3 = emb_df.sort_values("similarity", ascending=False).head(3)
            top3 = ','.join(top3['sentences'].to_list())

            #rewrite experiences to match job qualification
            completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful resume building assistant. I'll give you a job requirement, and my relevant qualifications. You write bullet points describing how my experience matches the job requirement."},
                {"role": "user", "content": f"Job requirement: {qual}"},
                {"role": "user", "content": f"My experience: {top3}"},
                ],
            temperature=0.2,
            max_tokens=1000)

            rewrite_list.append(completion.choices[0].message.content)
        
        return '\n'.join(rewrite_list)

    #rewrites resume to fit qualifications using raw text of user resume
    def rewrite_step_by_step(self, qualification_list, resume_text_string):
        #take top three most similar sentences. Use as input for model
        rewrite_list = []
        for qual in qualification_list:
            #rewrite experiences to match job qualification
            completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful resume building assistant. I'll give you a job requirement, and my resume. You write bullet points describing how my experience matches the job requirement."},
                {"role": "user", "content": f"Job requirement: {qual}"},
                {"role": "user", "content": f"My experience: {resume_text_string}"},
                ],
            temperature=0.2,
            max_tokens=1000)

            rewrite_list.append(completion.choices[0].message.content)
        
        #store in class attributes
        return '\n'.join(rewrite_list)

    #rewrite the entire resume. Include both job description and user resume in prompt
    def rewrite_single_context(self, job_listing_string, resume_text_string):
        print('rewriting resume using single prompt/context')
        #rewrite experiences to match job qualification
        completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful resume building assistant."},
            {"role": "user", "content": f"Job listing: {job_listing_string}"},
            {"role": "user", "content": f"My current resume: {resume_text_string}"},
            {"role": "user", "content": f"Rewrite my current resume to show how I satisfy the job listing. Use professional and quantitative language."},
            ],
        temperature=0.2,
        max_tokens=1000)

        return completion.choices[0].message.content
    
    #main API, available methods are: single_prompt, step_by_step, text_embeddings
    def rewrite_resume(self, job_listing_string, resume_text_string, method='single_prompt'):
        print('rewriting resume using method: ', method)
        if method == 'single_prompt':
            new_resume = self.rewrite_single_context(job_listing_string, resume_text_string)
        elif method == 'step_by_step':
            pass
        elif method == 'text_embeddings':
            emb_df = self.embed_resume(resume_text_string)
            qualification_list = self.get_qualification_list(job_listing_string)
            new_resume = self.rewrite_from_embeddings(qualification_list, emb_df)
        else:
            raise ValueError('method must be one of: single_prompt, step_by_step, text_embeddings')

        filename = f'new_resume_{method}.txt'        
        print('writing new resume to filename:', filename)
        self.write_resume(new_resume, filename)
        return new_resume

config = json.loads(open('config.json', 'rb').read())
listing, curr_resume = open('job_raw.txt', 'r').read(), open('user_resume.txt', 'r').read()
rb = ResumeBuilder(config)

#rewrite using single prompt
new_single_prompt = rb.rewrite_resume(listing, curr_resume, method='single_prompt')
import pdb; pdb.set_trace()