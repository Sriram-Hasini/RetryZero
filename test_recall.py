from memory import recall_memories, close_memory


print("Starting Hindsight recall test...")
print("Query: payments-api returning 504 on checkout")
print()

try:
    memories = recall_memories(
        "payments-api returning 504 on checkout"
    )

    print(f"MEMORIES FOUND: {len(memories)}")
    print()

    for i, memory in enumerate(memories, start=1):
        print(f"--- MEMORY {i} ---")

        try:
            print(memory.text)
        except AttributeError:
            print(memory)

        print()

except Exception as error:
    print("RECALL ERROR:")
    print(type(error).__name__)
    print(str(error))

finally:
    close_memory()
    print("Hindsight client closed.")