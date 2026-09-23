from agents.retrieval_agent import retrieval_agent


query = input("Enter your issue: ")

result = retrieval_agent(query)

print("=" * 60)
print("Retrieval Agent Output")
print("=" * 60)

for key, value in result.items():
    print(f"{key}: {value}")