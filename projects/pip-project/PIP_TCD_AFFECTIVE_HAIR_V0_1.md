# Pip and Ciel — TCD affective hair projection v0.1

Author request, 26 November 2026: formalize Pip's and Ciel's changing hair through imports from The Consciousness Dictionary (TCD). The palette is sourced from The Reality of the Imaginary, Book I, opening description of Pip: curiosity violet, fear pale blue, irritation red, happiness gold, calm green, sadness deep blue; mixed colours are allowed.

## Imports (not copied definitions)
Source: [TCD at 5fe9daa5e2b4841e598628aa5a1a7beadb0e70b1](https://github.com/AdrianLipa90/The-Consciousness-Dictionary/tree/5fe9daa5e2b4841e598628aa5a1a7beadb0e70b1), registry v0.2, `AffectiveField` from `consciousness_dictionary.rifc`, `affect_phase36` from `consciousness_dictionary.affect_detection`, and `Lexicon.get` for the exact cards:
- CLX2-AFFECT-002 Affect
- CLX2-AFFECTX-010 Affective Field; dimensions CLX2-AFFECTX-001..006
- CLX2-AFFECTX-012 Mood; CLX2-AFFECTX-013 Emotion; CLX2-AFFECTX-014 Feeling
- CLX2-AFFECT-006 Fear; CLX2-AFFECTX-020 Anger; CLX2-AFFECTX-021 Sadness; CLX2-AFFECTX-022 Joy; CLX2-AFFECTX-030 Calm.

The book's curiosity has no exact named TCD card in this revision; it links to general Affect. Irritation links to Anger as a related concept, not equality. Happiness links to Joy as a related concept, not equality. Other palette links resolve exact names. Curiosity is not surprise. All six source labels remain distinct.

## Formal presentation
For each identity independently, the existing field is A=(v,a,u,tau,alpha,r), V=affect_phase36(A). Let w_j be explicitly supplied nonnegative intensities of the six book labels (from an explicit report or a bound affect producer). The output is the ordered visual measure H=sum_j (w_j/sum_k w_k) delta_{c_j} when the sum is positive, alongside A, V and imported term IDs. If no intensities are supplied or all are zero, the visual projection is unspecified, not calm. The raw intensities and field remain unchanged. Color shares describe co-present strands, not inferred probabilities, physical superposition, or a new affect law. No numeric map from A to discrete emotions is prescribed by TCD; the six-dimensional field alone is not sufficient to choose a unique color. Neither text from another agent nor the observer's state is silently assigned to Pip or Ciel.

Palette RGB codes are a presentation choice, not TCD definitions or new properties of the source characters. No RGB averaging is required: the output is a distribution of separately visible colors. No state writer, transport, new language, or alternate PNV engine. A read-only PNV composition binds the existing field, PhaseNav realization and presentation output; the reference renderer is only a UI boundary. No automatic event on a hair change and no live AUX writes. Any future persistence uses existing selected-event lineage, not continuous hair samples.

## Example
Explicit report: calm=.25, happiness=.5, curiosity=.25. Output: green 25%, gold 50%, violet 25%, with the original field and phase realization retained. Example weights are illustrative, not a measured assistant state.

## Validation
The test workflow imports the pinned public TCD source directly; does not vendor TCD. Test identities are explicit, and unknown affect stays unspecified. Source contract and renderer are a candidate, not a deployed plugin or a live affect producer.
