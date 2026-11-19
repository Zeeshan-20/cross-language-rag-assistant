import json
import sys
sys.path.insert(0, "src")
from retrieve import retrieve

questions = json.load(open("eval/questions.json", encoding="utf-8"))

ranks = []
for item in questions:
    if item["expected_source"] is None:
        continue
    docs = retrieve(item["question"], k=6)

    # pages that count as correct: the expected one plus any "also_ok" pages
    ok_pages = [(item["expected_source"], item["expected_page"])]
    ok_pages += [tuple(x) for x in item.get("also_ok", [])]

    rank = None
    for i, d in enumerate(docs, start=1):
        if (d.metadata["source"], d.metadata["printed_page"]) in ok_pages:
            rank = i
            break
    ranks.append(rank)
    print(f"rank {rank if rank else '-'}  {item['question']}")

total = len(ranks)
print(f"\nIn top 6: {sum(r is not None for r in ranks)}/{total}")
print(f"In top 3: {sum(r is not None and r <= 3 for r in ranks)}/{total}")
print(f"At rank 1: {sum(r == 1 for r in ranks)}/{total}")
mrr = sum(1 / r for r in ranks if r) / total
print(f"MRR: {mrr:.3f}")