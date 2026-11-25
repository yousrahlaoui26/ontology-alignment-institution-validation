#!/usr/bin/env python3
"""
Reproducible HermiT semantic validation (Cons, Coh, Comp_tau) for the Pizza case study
(Tables 8 and 9 of the JWS manuscript).
"""
import json
from pathlib import Path
from owlready2 import World, sync_reasoner, OwlReadyInconsistentOntologyError

O1_FILE = "O1_Pizza.owl"
O2_FILE = "O2_Pizza.owl"

NS1 = "http://example.org/thesis/O1#"
NS2 = "http://example.org/thesis/O2#"

# 5 correspondances de référence G (alignment_reference_corrected.csv)
GOLD_ALIGNMENTS = [
    ("PizzaBasis", "PizzaBase"),
    ("Pizza", "Pizza"),
    ("AppointedPizza", "NamedPizza"),
    ("SohoPizza", "SohoPizza"),
    ("MargheritaPizza", "MargheritaPizza"),
]

# Charge de conséquences attendues pour la tâche cible (Req_tau : C_O1 ⊑ C_O2)
REQ_TAU = [
    ("SohoPizza", "NamedPizza"),
    ("MargheritaPizza", "NamedPizza"),
    ("AppointedPizza", "PizzaBase"),
]

# Les 6 alignements prédits (Table 8) + les 2 configurations du stress test (Table 9)
CONFIGURATIONS = [
    # --- Table 8 ---
    # SMASMT-OA / LR (TP=2, FP=0 : paires lexicalement identiques Pizza=Pizza, SohoPizza=SohoPizza)
    ("SMASMT-OA (LR)", [("Pizza", "Pizza"), ("SohoPizza", "SohoPizza")]),
    # SMASMT-OA / GBC (TP=4, FP=2 : 4 TP + 2 FP compatibles ex. PizzaBasis=Pizza, AppointedPizza=Pizza)
    ("SMASMT-OA (GBC)", [
        ("PizzaBasis", "PizzaBase"), ("Pizza", "Pizza"),
        ("SohoPizza", "SohoPizza"), ("MargheritaPizza", "MargheritaPizza"),
        ("PizzaBasis", "Pizza"), ("AppointedPizza", "Pizza")
    ]),
    # OAVA-SMASM / LR (TP=2, FP=0)
    ("OAVA-SMASM (LR)", [("Pizza", "Pizza"), ("SohoPizza", "SohoPizza")]),
    # OAVA-SMASM / GBC (TP=3, FP=0)
    ("OAVA-SMASM (GBC)", [("Pizza", "Pizza"), ("SohoPizza", "SohoPizza"), ("MargheritaPizza", "MargheritaPizza")]),
    # MLOA / LR (TP=5, FP=0 : alignement complet)
    ("MLOA (LR)", GOLD_ALIGNMENTS),
    # MLOA / GBC (TP=3, FP=1 : AppointedPizza ≡ MargheritaPizza -> incohérent)
    ("MLOA (GBC)", [
        ("Pizza", "Pizza"), ("SohoPizza", "SohoPizza"), ("MargheritaPizza", "MargheritaPizza"),
        ("AppointedPizza", "MargheritaPizza")
    ]),
    # --- Table 9 (Stress test) ---
    ("StressTest: Gold G", GOLD_ALIGNMENTS),
    ("StressTest: Gold G + FP (Soho ≡ Margherita)", GOLD_ALIGNMENTS + [("SohoPizza", "MargheritaPizza")]),
]


def validate_alignment(label, pairs):
    world = World()
    o1 = world.get_ontology(O1_FILE).load()
    o2 = world.get_ontology(O2_FILE).load()

    aligned = world.get_ontology("http://example.org/thesis/aligned")
    with aligned:
        aligned.imported_ontologies.append(o1)
        aligned.imported_ontologies.append(o2)

        added = 0
        for c1_name, c2_name in pairs:
            c1 = world.search_one(iri=NS1 + c1_name)
            c2 = world.search_one(iri=NS2 + c2_name)
            if c1 is not None and c2 is not None:
                c1.equivalent_to.append(c2)
                added += 1

        try:
            sync_reasoner(world, infer_property_values=False)
            cons = 1
        except OwlReadyInconsistentOntologyError:
            return {
                "approach": label,
                "pair": "O1_Pizza-O2_Pizza",
                "Cons": 0,
                "Coh": None,
                "n_named_classes": 10,
                "n_unsatisfiable_classes": None,
                "Comp_tau": None,
                "n_requirements": len(REQ_TAU),
                "n_entailed": 0,
                "n_alignment_axioms_added": added,
            }

    named_classes = [c for c in world.classes() if c.iri.startswith(NS1) or c.iri.startswith(NS2)]
    unsat = [c for c in named_classes if world.search_one(iri="http://www.w3.org/2002/07/owl#Nothing") in c.equivalent_to]
    coh = round(1.0 - len(unsat) / len(named_classes), 3)

    entailed = 0
    for src_name, tgt_name in REQ_TAU:
        c_src = world.search_one(iri=NS1 + src_name)
        c_tgt = world.search_one(iri=NS2 + tgt_name)
        if c_src is not None and c_tgt is not None and c_tgt in c_src.ancestors():
            entailed += 1

    comp_tau = round(entailed / len(REQ_TAU), 3)
    return {
        "approach": label,
        "pair": "O1_Pizza-O2_Pizza",
        "Cons": cons,
        "Coh": coh,
        "n_named_classes": len(named_classes),
        "n_unsatisfiable_classes": len(unsat),
        "Comp_tau": comp_tau,
        "n_requirements": len(REQ_TAU),
        "n_entailed": entailed,
        "n_alignment_axioms_added": added,
    }


if __name__ == "__main__":
    out_dir = Path("validation_json")
    out_dir.mkdir(exist_ok=True)

    print(f"{'Configuration':<44} | {'Cons':<4} | {'Coh':<6} | {'Comp_tau':<8}")
    print("-" * 72)
    for idx, (label, pairs) in enumerate(CONFIGURATIONS, 1):
        res = validate_alignment(label, pairs)
        coh_str = f"{res['Coh']:.3f}" if res["Coh"] is not None else "N/A"
        comp_str = f"{res['Comp_tau']:.3f}" if res["Comp_tau"] is not None else "N/A"
        print(f"{label:<44} | {res['Cons']:<4} | {coh_str:<6} | {comp_str:<8}")
        (out_dir / f"run_{idx:02d}.json").write_text(json.dumps(res, indent=2), encoding="utf-8")