"""
Reorders data/topic_queue.json to prioritize breadth-first multi-paper diversity.

Waves:
- Wave 1 (35 videos): Part 1 (or 1/1) of EVERY single paper (10 AI Agents + 5 AI Evals + 20 GOAT papers).
- Wave 2 (25 videos): Part 2 of all multi-part papers (5 AI Agents + 20 GOAT papers).
- Wave 3 (20 videos): Part 3 of all 20 GOAT papers.
- Wave 4 (20 videos): Part 4 of all 20 GOAT papers.
- Wave 5 (20 videos): Part 5 of all 20 GOAT papers.

Total: 120 videos across 35 frontier and foundation AI papers.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOPIC_QUEUE_FILE = PROJECT_ROOT / "data" / "topic_queue.json"

def get_paper_group(item):
    item_id = item["id"]
    if item_id.startswith("goat_"):
        parts = item_id.split("_")
        slug = "_".join(parts[1:-2])
        return f"goat_{slug}"
    elif any(item_id.startswith(p) for p in ["react_", "reflexion_", "generative_agents_", "tree_of_thoughts_", "voyager_"]):
        for p in ["react", "reflexion", "generative_agents", "tree_of_thoughts", "voyager"]:
            if item_id.startswith(p):
                return p
    return item_id

def get_part_num(item):
    part_str = item.get("part", "1/1")
    try:
        return int(part_str.split("/")[0])
    except Exception:
        return 1

def main():
    with open(TOPIC_QUEUE_FILE, "r", encoding="utf-8") as f:
        active = json.load(f)

    # 1. Update AI Eval papers to part 1/1 since each represents an independent research paper
    eval_ids = {
        "llm_as_a_judge_mt_bench_biases",
        "mmlu_benchmark_multitask_saturation",
        "humaneval_pass_at_k_functional_testing",
        "gsm8k_outcome_verifiers_math_reasoning",
        "data_contamination_eval_leakage_crisis"
    }
    for item in active:
        if item["id"] in eval_ids:
            item["part"] = "1/1"

    # 2. Group items by paper while preserving category flow
    paper_order = []
    paper_items = {}

    for item in active:
        grp = get_paper_group(item)
        if grp not in paper_items:
            paper_items[grp] = []
            paper_order.append(grp)
        paper_items[grp].append(item)

    # Sort items within each paper by part number
    for grp in paper_items:
        paper_items[grp].sort(key=get_part_num)

    # 3. Partition into Wave 1 (all Part 1s), Wave 2 (all Part 2s), Wave 3, Wave 4, Wave 5
    wave_1 = []
    wave_2 = []
    wave_3 = []
    wave_4 = []
    wave_5 = []

    for grp in paper_order:
        items = paper_items[grp]
        for it in items:
            p_num = get_part_num(it)
            if p_num == 1:
                wave_1.append(it)
            elif p_num == 2:
                wave_2.append(it)
            elif p_num == 3:
                wave_3.append(it)
            elif p_num == 4:
                wave_4.append(it)
            elif p_num == 5:
                wave_5.append(it)

    reordered = wave_1 + wave_2 + wave_3 + wave_4 + wave_5

    print(f"Total active items: {len(active)}")
    print(f"Wave 1 (Part 1 of all remaining papers): {len(wave_1)} videos")
    print(f"Wave 2 (Part 2 of multi-part papers): {len(wave_2)} videos")
    print(f"Wave 3 (Part 3 of GOAT papers): {len(wave_3)} videos")
    print(f"Wave 4 (Part 4 of GOAT papers): {len(wave_4)} videos")
    print(f"Wave 5 (Part 5 of GOAT papers): {len(wave_5)} videos")
    print(f"Total reordered: {len(reordered)} videos")

    assert len(active) == len(reordered), f"Length mismatch: {len(active)} vs {len(reordered)}"
    assert len(set(x["id"] for x in reordered)) == len(active), "Duplicate IDs detected!"
    # Ensure every single item in wave_1 is part 1
    assert all(get_part_num(x) == 1 for x in wave_1), "Non-part-1 found in Wave 1!"
    # Ensure wave_1 has exactly one entry per remaining paper group
    assert len(wave_1) == len(paper_order), f"Wave 1 length {len(wave_1)} doesn't match unique paper groups {len(paper_order)}"

    with open(TOPIC_QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(reordered, f, indent=2)

    print(f"✅ Successfully reordered {TOPIC_QUEUE_FILE.name} into breadth-first waves!")

if __name__ == "__main__":
    main()
