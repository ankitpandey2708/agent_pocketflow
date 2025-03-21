from pocketflow import Node
from utils import call_llm, search_web
import yaml

class DecideAction(Node):
    def prep(self, shared):
        """Prepare the context and question for the decision-making process."""
        # Get the current context (default to "No previous search" if none exists)
        context = shared.get("context", "No previous search")
        # Get the question from the shared store
        question = shared["question"]
        # Return both for the exec step
        return question, context
        
    def exec(self, inputs):
        """Call the LLM to decide whether to search or answer."""
        question, context = inputs
        
        print(f"🤔 Agent deciding what to do next...")
        
        # Create a prompt to help the LLM decide what to do next
        prompt = f"""
### CONTEXT
You are a research assistant that can search the web only if you dont know the exact answer. If you know the answer yourself dont search web.
Question: {question}
Previous Research: {context}

### ACTION SPACE
[1] answer
  Description: Answer the question with current knowledge
  Parameters:
    - answer (str): Final answer to the question

[2] search
  Description: Look up more information on the web only if you dont find the answer yourself
  Parameters:
    - query (str): What to search for

## NEXT ACTION
Decide the next action based on the context and available actions.
Return your response in this format:

```yaml
thinking: |
    <your step-by-step reasoning process>
action: search OR answer
reason: |
    <why you chose this action>
search_query: <specific search query if action is search>
```
IMPORTANT: Make sure to:
1. Use proper indentation (4 spaces) for all multi-line fields
2. Use the | character for multi-line text fields
3. Keep single-line fields without the | character
"""
        
        # Call the LLM to make a decision
        response = call_llm(prompt)
        
        # Parse the response to get the decision
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        print(yaml_str + "\n****")
        decision = yaml.safe_load(yaml_str)
        return decision
    
    def post(self, shared, prep_res, exec_res):
        """Save the decision and determine the next step in the flow."""
        # If LLM decided to search, save the search query
        if exec_res["action"] == "search":
            shared["search_query"] = exec_res["search_query"]
            print(f"🔍 LLM decided to search for: {exec_res['search_query']}")
        else:
            shared["context"] = exec_res["answer"]
            print(f"💡 LLM decided to answer the question")
        
        # Return the action to determine the next node in the flow
        return exec_res["action"]

class SearchWeb(Node):
    def prep(self, shared):
        """Get the search query from the shared store."""
        return shared["search_query"]
        
    def exec(self, search_query):
        """Search the web for the given query."""
        # Call the search utility function
        results = search_web(search_query)
        return results
    
    def post(self, shared, prep_res, exec_res):
        """Save the search results and go back to the decision node."""
        # Add the search results to the context in the shared store
        previous = shared.get("context", "")
        shared["context"] = previous + "\n\nSEARCH: " + shared["search_query"] + "\nRESULTS: " + exec_res
        print(f"📚 Web search completed.")
        
        # Always go back to the decision node after searching
        return "decide"

class AnswerQuestion(Node):
    def prep(self, shared):
        """Get the question and context for answering."""
        return shared["question"], shared.get("context", "")
        
    def exec(self, inputs):
        """Call the LLM to generate a final answer."""
        question, context = inputs
        # Create a prompt for the LLM to answer the question
        prompt = f"""
### CONTEXT
Based on the following information, answer the question.
Question: {question}
Research: {context}

## YOUR ANSWER:
Provide a comprehensive answer using the research results.
"""
        # Call the LLM to generate an answer
        answer = call_llm(prompt)
        return answer
    
    def post(self, shared, prep_res, exec_res):
        """Save the final answer and complete the flow."""
        # Save the answer in the shared store
        shared["answer"] = exec_res        
        # We're done - no need to continue the flow
        return "done" 