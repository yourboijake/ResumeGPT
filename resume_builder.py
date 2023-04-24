'''
Basic structure:

Resume has 4 components:
1. previous work experience
2. education
3. other relevant experience (projects, volunteering, etc)
4. skills (soft skills, hard skills)

Steps:
1. prompt user to enter in link to the job description
    a. parse job description from html
    b. define job requirements/qualifications based on that description
    c. get GPT to extract hard and soft skills from qualifications and job description
2. prompt user to explain their work experiences in terms of qualifications
    a. for each required skill/experience, ask user to explain how they satisfy it
    b. prompt model to rephrase the user's response in a way that shows how they satisfy the requirement in a resume context
3. Ask about education
    a. ask if user has formal academic credentials (graduate school?, undergrad?, high school/GED, certs?)
    b. details for academic credentials: degree, year started/completed, relevant coursework
4. Ask user to describe any other relevant projects
    a. create bullet pointed sublist for each project
5. Ask about skills
    a. for each skill, ask user to describe their skill level, if any
    b. summarize each point, adding to skills section
6. each section should be summarized, generating a bullet point list of job descriptions
7. For each section, print the section and ask the user if they want to change anything
    - continue prompting until user submits a special character/stop phrase that indicates to move to next section
8. save sections to a txt file, tell user filename and tell them to copy results into a template they like

Other further improvements:
- prompt user to match attributes of resume to job
    - example: if job seems very quantitative, ask user for numbers relating to their work
    - if job seems very human-interaction focused, try to make the language more friendly/likeable
    - if job lists organization ability, try to make sure the sections are well-organized

Obtaining Job Description:
Options:
    - (probably better) send full text from HTML to gpt-3.5-turbo, ask it to summarize job description
      and qualifications in bullet points
    - use text embedding on document, ask questions about text    

'''
import requests
from bs4 import BeautifulSoup
import re
import openai
from k import api_key

#parse html of job description
links = ['https://www.indeed.com/cmp/Acacia-Dental-Group-3/jobs?jk=33bd9bc743f15353&start=0&clearPrefilter=1',
         'https://jobs.xcelenergy.com/job/Control-Room-Supervisor-In-Training-Job-MN-55362/1018497600/',
         'https://careers.walmart.com/us/jobs/WD1110519-truck-driver-otr-regional-loveland-co',
         'https://jobs.brooksource.com/job/business-intelligence-analyst-atlanta-ga/1018497600/']

page = requests.get(links[3])

#use regex to remove all html tags
soup = BeautifulSoup(page.content, 'html.parser')
text = soup.get_text()
text = re.sub('<[^<]+?>', '', text)
text = text.replace('\n', ' ').replace('\xa0', ' ').replace('\t', ' ')

#use gpt-3.5-turbo to get bullet points of job description
openai.organization = "org-kqbJP1qBA8CVuReLEues52fs"
openai.api_key = api_key

'''
#prompt model to summarize job description and qualifications in bullet points
completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful resume building assistant. I'll give you a job description, you tell me about the job."},
        {"role": "user", "content": f"Here is the job description: {text}"},
        {"role": "assistant", "content": "Ok, I understand the role."},
        {"role": "user", "content": "Briefly list the qualifications for the job in bullet points"},
        ],
    temperature=0.2,
    max_tokens=1000)

print('retrieved job description and qualifications')
open('job_req.txt', 'w').write(completion.choices[0].message.content)
qualification_list = completion.choices[0].message.content.split('\n')
'''

qualification_list = open('job_req.txt', 'r').read().split('\n')
#prompt user to explain their work experiences in terms of qualifications
print('How do you satisfy the following qualifications?')
response_list = []
for qual in qualification_list:
    print(qual)
    response = input('> ')
    response_list.append(response)

#prompt model to rephrase the user's response in a way that shows how they satisfy the requirement in a resume context
print('Ok, now I will rephrase your responses to show how you satisfy the qualifications')
responses_fixed = []
for i, response in enumerate(response_list):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful resume building assistant."},
            {"role": "user", "content": f"The qualification is: {qualification_list[i]}"},
            {"role": "user", "content": f"My response is: {response}"},
            {"role": "user", "content": "Rephrase my response to show how I satisfy the qualification in a resume context. Return the result in a list with several bullet points, where each bullet shows a specific part of my experience that is relevant."},
            ],
        temperature=0.2,
        max_tokens=1000)
    responses_fixed.append(completion.choices[0].message.content)

import pdb; pdb.set_trace()

print('done')