import os

from typing import Optional
from typing_extensions import TypedDict

from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from langgraph.graph import END, START, StateGraph

from dotenv import load_dotenv
load_dotenv()


#State Graph
class SelfDiscoverState(TypedDict):
    reasoning_modules: str
    selected_modules: Optional[str]
    adapted_modules: Optional[str]
    reasoning_structure: Optional[str]
    task: str
    solution: Optional[str]

model = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)

# STAGE 1 

def select_reasoning_modules(state):
    """
    Step 1: SELECT relevant reasoning modules for the task.
    """
    select_prompt=f"Given the task: {state['task']}, which of the following reasoning modules are relevant? Do not elaborate on why.\n\n" + "\n".join(state['reasoning_modules'])
    select_chain = select_prompt | model | StrOutputParser()
    return {"selected_modules": select_chain.invoke(state)}


def adapt_reasoning_modules(state):
    """
    Step 2: ADAPT the selected reasoning modules to be more specific to the task.
    """
    adapt_prompt=f"Without working out the full soulution, adapt the following reasoning modules to be specific to our task:\n{state['selected_modules']}\n\nOur task:\n{state['task']}"
    adapt_chain = adapt_prompt | model | StrOutputParser()
    return {"adapted_modules": adapt_chain.invoke(state)}


def reasoning_structure(state):
    """
    Step 3: Implement the adapted reasoning modules into an actionable reasoning structure.
    """
    reasoning_prompt=f"Without working out the full solution, create an actionable reasoning structure for the task using these adapted reasoning modules:\n{state['adapted_modules']}\n\nTask:\n{state['task']}"
    reasoning_chain = reasoning_prompt | model | StrOutputParser()
    return {"reasoning_structure": reasoning_chain.invoke(state)}


#STAGE 2

def execute_reasoning_structure(state):
    """
    Execute the reasoning structure to solve a specific task instance.
    """
    sol_prompt=f"Using the following reasoning structure: {state['reasoning_structure']}\n\nSolve this task, providing your final answer: {state['task']}"
    solution_chain = sol_prompt | model | StrOutputParser()
    return {"solution": solution_chain.invoke(state)}


graph_builder = StateGraph(SelfDiscoverState)
graph_builder.add_node(select_reasoning_modules)
graph_builder.add_node(adapt_reasoning_modules)
graph_builder.add_node(reasoning_structure)
graph_builder.add_node(execute_reasoning_structure)
graph_builder.add_edge(START, "select_reasoning_modules")
graph_builder.add_edge("select_reasoning_modules","adapt_reasoning_modules")
graph_builder.add_edge("adapt_reasoning_modules","reasoning_structure")
graph_builder.add_edge("reasoning_structure","execute_reasoning_structure")
graph_builder.add_edge("execute_reasoning_structure", END)

graph = graph_builder.compile()


reasoning_modules = [
    "1. How could I devise an experiment to help solve that problem?",
        "2. Make a list of ideas for solving this problem, and apply them one by one to the problem to see if any progress can be made.",
        #"3. How could I measure progress on this problem?",
        "4. How can I simplify the problem so that it is easier to solve?",
        "5. What are the key assumptions underlying this problem?",
        "6. What are the potential risks and drawbacks of each solution?",
        "7. What are the alternative perspectives or viewpoints on this problem?",
        "8. What are the long-term implications of this problem and its solutions?",
        "9. How can I break down this problem into smaller, more manageable parts?",
        "10. Critical Thinking: This style involves analyzing the problem from different perspectives, questioning assumptions, and evaluating the evidence or information available. It focuses on logical reasoning, evidence-based decision-making, and identifying potential biases or flaws in thinking.",
        "11. Try creative thinking, generate innovative and out-of-the-box ideas to solve the problem. Explore unconventional solutions, thinking beyond traditional boundaries, and encouraging imagination and originality.",
        #"12. Seek input and collaboration from others to solve the problem. Emphasize teamwork, open communication, and leveraging the diverse perspectives and expertise of a group to come up with effective solutions.",
        "13. Use systems thinking: Consider the problem as part of a larger system and understanding the interconnectedness of various elements. Focuses on identifying the underlying causes, feedback loops, and interdependencies that influence the problem, and developing holistic solutions that address the system as a whole.",
        "14. Use Risk Analysis: Evaluate potential risks, uncertainties, and tradeoffs associated with different solutions or approaches to a problem. Emphasize assessing the potential consequences and likelihood of success or failure, and making informed decisions based on a balanced analysis of risks and benefits.",
        #"15. Use Reflective Thinking: Step back from the problem, take the time for introspection and self-reflection. Examine personal biases, assumptions, and mental models that may influence problem-solving, and being open to learning from past experiences to improve future approaches.",
        "16. What is the core issue or problem that needs to be addressed?",
        "17. What are the underlying causes or factors contributing to the problem?",
        "18. Are there any potential solutions or strategies that have been tried before? If yes, what were the outcomes and lessons learned?",
        "19. What are the potential obstacles or challenges that might arise in solving this problem?",
        "20. Are there any relevant data or information that can provide insights into the problem? If yes, what data sources are available, and how can they be analyzed?",
        "21. Are there any stakeholders or individuals who are directly affected by the problem? What are their perspectives and needs?",
        "22. What resources (financial, human, technological, etc.) are needed to tackle the problem effectively?",
        "23. How can progress or success in solving the problem be measured or evaluated?",
        "24. What indicators or metrics can be used?",
        "25. Is the problem a technical or practical one that requires a specific expertise or skill set? Or is it more of a conceptual or theoretical problem?",
        "26. Does the problem involve a physical constraint, such as limited resources, infrastructure, or space?",
        "27. Is the problem related to human behavior, such as a social, cultural, or psychological issue?",
        "28. Does the problem involve decision-making or planning, where choices need to be made under uncertainty or with competing objectives?",
        "29. Is the problem an analytical one that requires data analysis, modeling, or optimization techniques?",
        "30. Is the problem a design challenge that requires creative solutions and innovation?",
        "31. Does the problem require addressing systemic or structural issues rather than just individual instances?",
        "32. Is the problem time-sensitive or urgent, requiring immediate attention and action?",
        "33. What kinds of solution typically are produced for this kind of problem specification?",
        "34. Given the problem specification and the current best solution, have a guess about other possible solutions."
        "35. Let’s imagine the current best solution is totally wrong, what other ways are there to think about the problem specification?"
        "36. What is the best way to modify this current best solution, given what you know about these kinds of problem specification?"
        "37. Ignoring the current best solution, create an entirely new solution to the problem."
        #"38. Let’s think step by step."
        "39. Let’s make a step by step plan and implement it with good notation and explanation."
]


task_example = "Lisa has 10 apples. She gives 3 apples to her friend and then buys 5 more apples from the store. How many apples does Lisa have now?"

for s in graph.stream(
    {"task": task_example, "reasoning_modules": reasoning_modules}
):
    print(s)