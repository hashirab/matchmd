from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

INTENTS = [
    "match programs to applicant profile",
    "search programs by location or state",
    "ask about application strategy or tips",
    "ask about visa sponsorship",
    "ask about observerships or clinical experience",
    "general residency question"
]

def classify_intent(message: str) -> dict:
    result = classifier(message, INTENTS)
    top_intent = result["labels"][0]
    top_score = result["scores"][0]
    return {
        "intent": top_intent,
        "confidence": round(top_score, 3),
        "all": dict(zip(result["labels"], [round(s,3) for s in result["scores"]]))
    }

# Test it
if __name__ == "__main__":
    tests = [
        "What programs match my Step 2 score of 240 as an IMG?",
        "Show me psychiatry programs in Texas",
        "How do I write a strong personal statement?",
        "Which programs sponsor H1B visas?",
        "How do I find observerships in New York?",
        "What is the SOAP process?",
    ]
    for t in tests:
        result = classify_intent(t)
        print(f"\nQ: {t}")
        print(f"Intent: {result['intent']} (confidence: {result['confidence']})")
