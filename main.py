from checkpoints import CHECKPOINTS
from graph import build_graph

app = build_graph()

print("Available Learning topics:")
for i, cp in enumerate(CHECKPOINTS):
    print(f"{i}. {cp['topic']}")

start = int(input("Select checkpoint number to start from: "))

for idx in range(start, len(CHECKPOINTS)):
    cp = CHECKPOINTS[idx]
    print(f"\n=== LEARNING CHECKPOINT {idx}: {cp['topic']} ===")

    state = {
        "topic": cp["topic"],
        "objectives": cp["objectives"],
        "retry_count": 0,
        "max_retries": 2
    }

    result = app.invoke(state)

    if result["score"] < 70:
        print("❌ Checkpoint not mastered. Stopping.")
        break
    else:
        print("✅ Checkpoint mastered. Moving on.")
