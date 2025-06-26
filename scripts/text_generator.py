from groq import Groq
import yaml

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

groq_api_key = config['groq-api-key']

client = Groq(
    api_key=groq_api_key,
)

def generate_search_query_v1(content):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": """
                    You are an expert at generating highly relevant image search queries.
                    You have to fill in brackets with relevant image search queries
                    
                    Keep the query short and specific and only return whatever is in bracket in order seperating them with newline
                """
            },
            {
                "role": "user",
                "content": f"""
                    content from which search query has to be generated: {content}
                
                """
            }
        ],
        model="llama-3.3-70b-versatile",
        stream=False,
    )

    return chat_completion.choices[0].message.content.strip()