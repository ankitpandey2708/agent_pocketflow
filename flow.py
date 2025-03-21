from pocketflow import Flow
from nodes import DecideAction, SearchWeb, AnswerQuestion

def create_agent_flow():
    # Create instances of each node
    decide = DecideAction()
    search = SearchWeb()
    answer = AnswerQuestion()
    
    # Connect the nodes
    # If DecideAction returns "search", go to SearchWeb
    decide - "search" >> search
    
    # If DecideAction returns "answer", go to AnswerQuestion
    decide - "answer" >> answer
    
    # After SearchWeb completes and returns "decide", go back to DecideAction
    search - "decide" >> decide
    
    # Create and return the flow, starting with the DecideAction node
    return Flow(start=decide) 