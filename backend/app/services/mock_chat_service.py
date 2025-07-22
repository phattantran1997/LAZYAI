from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize the Groq client with the API key
client = Groq(api_key=os.getenv('API_KEY'))

def post_questions_service(request):

    prompt = f""" As you are the tutor of unit named {request.unit_name}, you will have to answer all student questions from the  {request.unit_name} context. Please try to answer in the unit {request.unit_name} content. Question: {request.message}"""

    print(prompt)
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,  # We can set this to False to get the full response at once
        stop=None
    )
    # Access the message from the response correctly
    message = completion.choices[0].message.content 

    return message
