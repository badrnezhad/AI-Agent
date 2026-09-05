import json

from openai import OpenAI

from config import CHAT_MODEL, MAX_ITERATIONS, MAX_MEMORY_SIZE
from tools import TOOLS, execute_tool

client = OpenAI()

AGENT_INSTRUCTIONS = """
You are a simple AI agent for a company.

Your responsibilities:
1. Answer the user in Persian.
2. Use search_company_rules when company rules are relevant.
3. Never invent company rules.
4. If the user asks to send an email, use send_email.
5. The application will ask the human for approval before email is actually sent.
6. After every tool result, decide whether another tool is needed or whether the task is complete.
7. If a tool fails, explain the problem or choose another reasonable path.
8. Keep answers clear and concise.
9. For questions about Holosen Courses, use web_search tool.

Important:
- A tool is not automatically required for every request.
- Company policy claims must be grounded in search_company_rules results.
- We don't have any extra application like Slack or Calendar. just a rules file.
"""

PLANNER_INSTRUCTIONS = """
Create a short high-level execution plan for an ai agent.

Rules:
- Write the plan in Persian.
- Do not solve the task.
- Do not reveal private chain-of-thought.
- Only list observable actions the agent may perform.
- Mention tool names when a tool will probably be needed.
- Keep the plan between 1 and 5 numbered steps.
- We don't have any extra application like Slack or Calendar. just a rules file.
"""


def create_plan(user_input, memory):
    planner_input = []
    for message in memory[-MAX_MEMORY_SIZE:]:
        planner_input.append(message)

    planner_input.append({
        "role": "user",
        "content": user_input
    })

    try:
        response = client.responses.create(
            model=CHAT_MODEL,
            instructions=PLANNER_INSTRUCTIONS,
            input=planner_input
        )
        plan = response.output_text.strip()
        return plan
    except Exception as e:
        return "خطا در پلنینگ " + str(e)


def run_agent(user_input, memory, rag_index):
    print("\n====== Agent Started ======\n")
    state = {
        "goal": user_input,
        "plan": create_plan(user_input, memory),
        "iteration": 0,
        "last_tool": None,
        "status": "running"
    }
    print("\n===== Agent Plan =====\n")
    print(state["plan"])

    input_items = []
    for message in memory[-MAX_MEMORY_SIZE:]:
        input_items.append(message)

    input_items.append({
        "role": "user",
        "content": user_input
    })

    runtime_instructions = (
            AGENT_INSTRUCTIONS
            + "\n\n"
            + "Current execution plan:\n"
            + state["plan"]
            + "\n\n"
            + ("Follow this plan as a guide"
               "If a tool result shows that a astep is unnessesary "
               "or another action is required, adapt the execution")
    )

    for iteration in range(1, MAX_ITERATIONS + 1):
        state["iteration"] = iteration
        print("State: \n", json.dumps(state, ensure_ascii=False, indent=2))

        try:
            response = client.responses.create(
                model=CHAT_MODEL,
                instructions=runtime_instructions,
                input=input_items,
                tools=TOOLS,
                tool_choice="auto"
            )
        except Exception as e:
            state["status"] = "llm_error"
            return "خطا در ارتباط با مدل " + str(e)

        answer = response.output
        input_items.extend(answer)

        function_calls = []
        for item in answer:
            if item.type == "function_call":
                function_calls.append(item)

        if len(function_calls) == 0:
            final_answer = response.output_text.strip()
            state["status"] = "completed"
            memory.append({
                "role": "user",
                "content": user_input
            })
            memory.append({
                "role": "assistant",
                "content": final_answer
            })
            print("State: \n", json.dumps(state, ensure_ascii=False, indent=2))
            return final_answer

        for item in function_calls:
            tool_name = item.name
            state["last_tool"] = tool_name
            print("Tool Call: ", tool_name)
            arguments = json.loads(item.arguments)

            tool_result = execute_tool(tool_name, arguments, rag_index)

            print("Tool Result: ", tool_result)

            input_items.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": tool_result
            })

    state["status"] = "max_iterations_reached"
    print("State: \n", json.dumps(state, ensure_ascii=False, indent=2))
    return ("\n====== Agent Stopped ======\n"
            "Max Iterations Reached.")
