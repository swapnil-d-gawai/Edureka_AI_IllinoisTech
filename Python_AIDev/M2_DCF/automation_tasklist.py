from pathlib import Path

with (Path(__file__).parent / "tasks.txt").open("r", encoding="utf-8") as file:
    print("Reading task from file: \n")
    task = file.readlines()

completed_task = []
pending_task = []

for t in task:
    if "done" in t.lower():
        completed_task.append(t.strip())
    else:
        pending_task.append(t.strip())

print("Completed tasks:")
for t in completed_task:
    print("  ", t)
print("Pending tasks:")
for t in pending_task:
    print("  ", t)

with (Path(__file__).parent / "completed_task.txt").open("w", encoding="utf-8") as file:
    for t in completed_task:
        file.write(t + "\n")

with open(Path(__file__).parent / "pending_task.txt", "w", encoding="utf-8") as file:
    for t in pending_task:
        file.write(t + "\n")

print("Tasks have been written to completed_task.txt and pending_task.txt")