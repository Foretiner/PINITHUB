# Model and dataset licence register

Do not use an asset commercially until the exact licence and permitted use are verified. Source-code licence, model-weight licence, training-data rights, and intended use are separate review items. Record source, version, checksum, licence evidence, and reviewer decision here.

| Asset | Candidate/source | Licence and provenance status | Decision |
|---|---|---|---|
| Face detector / landmarks | Not selected | Not checked | Blocked |
| Face recognition | OpenVINO Open Model Zoo ArcFace ONNX is a candidate; exact download, checksum, and upstream training-data rights not reviewed | Its model card says Apache-2.0; this does not settle all data-provenance or deployment questions | Evaluation candidate only; legal review required |
| Liveness / anti-spoof | Not selected | Not checked | Blocked |
| Evaluation dataset | Not selected | Not checked | Blocked |

The InsightFace public model zoo states that its pretrained models are for non-commercial research only. Do not use those weights for commercial deployment without a separate grant. No model weights or biometric datasets are included in this repository.

## Evidence to record before approval

- Exact model and dataset URLs, versions, SHA-256 digests, and archived licence text.
- Explicit permission to use and redistribute the model weights, including the intended commercial/production use.
- Training-data provenance and any biometric/privacy restrictions.
- Dataset licence, consent, demographic coverage, and evaluation split design.
- Reviewer and decision date.
