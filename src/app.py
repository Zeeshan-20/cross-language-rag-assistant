import gradio as gr
from answer import answer


def to_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(c.get("text", "") for c in content if isinstance(c, dict))
    return str(content)


def to_pairs(history):
    """Gradio history -> list of (question, answer) pairs."""
    pairs = []
    pending = None
    for item in history:
        if isinstance(item, dict):
            if item["role"] == "user":
                pending = to_text(item["content"])
            elif item["role"] == "assistant" and pending is not None:
                pairs.append((pending, to_text(item["content"])))
                pending = None
        else:
            pairs.append((to_text(item[0]), to_text(item[1])))
    return pairs


def chat(message, history):
    return answer(to_text(message), to_pairs(history))


demo = gr.ChatInterface(
    fn=chat,
    title="German University Regulations Assistant",
    description=(
        "Ask in English. Answers come from German documents (Master Applied Computer Science, "
        "Hochschule Schmalkalden) with quotes and page numbers. "
        "Unofficial student project, not legal advice."
    ),
    examples=[
        "In which semester is the seminar and how many CP does it have?",
        "How long do I have to write the master thesis?",
        "What happens if I am ill on the day of an exam?",
    ],
    save_history=True,
)

if __name__ == "__main__":
    demo.launch()