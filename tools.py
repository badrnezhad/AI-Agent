import json

from email_service import send_gmail
from rag import search_rules_in_rag
from tool.web_search_tool import web_search

TOOLS = [
    {
        "type": "function",
        "name": "search_company_rules",
        "description": (
            "Search the company's internal rules"
            "using RAG."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "A focused query for"
                        "searching company rules."
                    )
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        }
    },
    {
        "type": "function",
        "name": "send_email",
        "description": (
            "Sends an email through the configured Gmail account."
            "This tool has an external side effect and must always "
            "require human approval before the email is sent."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "Recipient email address."
                },
                "subject": {
                    "type": "string",
                    "description": "Subject of the email."
                },
                "body": {
                    "type": "string",
                    "description": "Body of the email."
                }
            },
            "required": ["to", "subject", "body"],
            "additionalProperties": False,
        }
    },
    {
        "type": "function",
        "name": "web_search",
        "description": (
            "Reads the Holosen courses page."
            "Use it to answer questions about "
            "Holosen courses and prices."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }
    }
]


def ask_email_apporval(to, subject, body):
    print("Asking email apporval...")
    print("To: ", to)
    print("Subject: ", subject)
    print("Body: ", body)
    print("\n")
    answer = input("آیا این ایمیل ارسال شود؟ (yes/no)")

    answer = answer.lower().strip()
    if answer == "yes":
        return True
    return False


def execute_tool(tool_name, arguments, rag_index):
    if tool_name == "search_company_rules":
        user_query = arguments['query']
        tool_results = search_rules_in_rag(rag_index, user_query)

        tool_result_dump = json.dumps(
            [doc.model_dump() for doc in tool_results],
            ensure_ascii=False
        )

    elif tool_name == "send_email":
        to = arguments['to']
        subject = arguments['subject']
        content = arguments['body']

        approved = ask_email_apporval(to, subject, content)
        if not approved:
            return json.dumps({
                "status": "canceled_by_human",
                "message": "The user did not approve sending the email."
            })

        mail_result = send_gmail(to, subject, content)
        tool_result_dump = json.dumps(mail_result, ensure_ascii=False)

    elif tool_name == "web_search":
        tool_result_dump = web_search()
    else:
        tool_result_dump = json.dumps({
            "status": "error",
            "message": "Unknown tool. " + tool_name
        })

    return tool_result_dump
