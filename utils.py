from openai import OpenAI
from ddgs import DDGS

def call_llm(prompt):    
    #client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
    external_client = OpenAI(
        api_key="",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    r = external_client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content

def search_web(query):
    results = DDGS().text(query, max_results=5)
    # Convert results to a string
    results_str = "\n\n".join([f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}" for r in results])
    return results_str
