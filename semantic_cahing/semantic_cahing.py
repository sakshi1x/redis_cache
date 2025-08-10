from redisvl.extensions.router import Route, SemanticRouter
from redisvl.utils.vectorize import HFTextVectorizer
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 1. Define routes with sample references and answers/

# to do . 

routes = [
    Route(
        name="technology",
        references=[
            "what are the latest advancements in AI?",
            "tell me about the newest gadgets",
            "what's trending in tech?"
        ],
        metadata={"answer": "Tech stuff: AI is booming and gadgets are lit!"},
        distance_threshold=0.71
    ),
    Route(
        name="sports",
        references=[
            "who won the game last night?",
            "tell me about upcoming sports events",
            "what's the latest in sports?"
        ],
        metadata={"answer": "Sports update: Team X crushed it last night!"},
        distance_threshold=0.72
    ),
    Route(
        name="entertainment",
        references=[
            "what are the top movies right now?",
            "who won the best actor award?",
            "what's new in entertainment?"
        ],
        metadata={"answer": "Entertainment buzz: New blockbusters and award winners!"},
        distance_threshold=0.7
    )
]

# 2. Initialize SemanticRouter
router = SemanticRouter(
    name="simple-router",
    vectorizer=HFTextVectorizer(),
    routes=routes,
    redis_url="redis://localhost:6379",
    overwrite=True
)

def answer_question(question: str):
    match = router(question)
    if match.name:
        # Pull the answer from metadata of matched route
        route = next(r for r in routes if r.name == match.name)
        print(f"Question: {question}")
        print(f"Route matched: {match.name} (distance: {match.distance:.3f})")
        print(f"Answer: {route.metadata['answer']}")
    else:
        print(f"Question: {question}")
        print("No good route match found. Try rephrasing?")

if __name__ == "__main__":
    while True:
        q = input("Ask me anything (or type 'exit'): ").strip()
        if q.lower() == "exit":
            break
        answer_question(q)
