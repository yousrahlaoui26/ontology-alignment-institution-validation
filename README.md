# Progressive Ontology Enrichment for Supervised Alignment with Institution-Based Semantic Validation

This repository provides the reconstructed Pizza ontology fragments, candidate feature matrix, reference alignments, and Python/HermiT validation scripts reproducing the semantic validation experiments (Tables 8 and 9) in the *Journal of Web Semantics* manuscript.

## Repository Contents

- `O1_Pizza.owl`, `O2_Pizza.owl`: Reconstructed source and target OWL ontology fragments (10 named classes, subclass hierarchies, disjointness axioms, and named individuals).
- `reconstructed_features_25_pairs.csv`: The 25 candidate class pairs with explicitly reported similarity features ($d_{\text{vis}} \in \{9, 12, 49\}$) and binary gold labels.
- `alignment_reference_corrected.csv`: Reference alignment $G$ (5 correspondences).
- `alignment_with_false_positive.csv`: Perturbed alignment ($G \cup \{\text{SohoPizza}_{\mathcal{O}_1} \equiv \text{MargheritaPizza}_{\mathcal{O}_2}\}$) used in the controlled semantic stress test.
- `run_pizza_validation.py`: Reproduces 5-fold stratified out-of-fold predictions and HermiT reasoning checks ($Cons$, $Coh$, $Comp_{\tau}$).
- `aggregate_results.py`: Aggregates per-run JSON outputs into a summary CSV table.
- `pizza_validation_summary.csv`: Pre-computed summary output matching Tables 8 and 9.

## Requirements & Execution

1. Ensure **Java (JRE/JDK 8+)** is installed (required by the HermiT reasoner bundled in `owlready2`).
2. Install Python dependencies:
   ```bash
   pip install owlready2 scikit-learn pandas numpy
