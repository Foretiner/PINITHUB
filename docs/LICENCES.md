# Model and dataset licence register

Scope: non-commercial research prototype. A package or model licence does not establish rights for its training data, biometric use, redistribution, or commercial deployment. No dataset images, embeddings, model weights, or derived biometric data belong in this repository.

| Asset | Source/version | Licence/provenance evidence | Project decision |
|---|---|---|---|
| Face landmarks | MediaPipe Face Landmarker float16 v1 task; SHA-256 `64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff` | Published model card states Apache-2.0 | Local development only; not an identity model. |
| Face detection | InsightFace `buffalo_l` / `det_10g.onnx` (SCRFD-10GF); official release archive SHA-256 `80ffe37d8a5940d59a7384c201a2a38d4741f2f3c51eef46ebb28218a7b0ca2f`; extracted ONNX SHA-256 `5838f7fe053675b1c7a08b633df49e7af5495cee0493c7dcf6697200b85b5b91` | InsightFace model-zoo terms restrict pretrained model packs to non-commercial research. The model pack's training-data provenance is upstream. | Local non-commercial research only; model is integrated in the local pipeline. |
| Face recognition | InsightFace `buffalo_l` / `w600k_r50.onnx` (ResNet50 ArcFace, 512-D); official release archive SHA-256 `80ffe37d8a5940d59a7384c201a2a38d4741f2f3c51eef46ebb28218a7b0ca2f`; extracted ONNX SHA-256 `4c06341c33c2ca1f86781dab0e829f88ad5b64be9fba56e56bc9ebdefc619e43` | InsightFace model-zoo terms restrict pretrained model packs to non-commercial research. The code licence does not grant commercial rights to pretrained weights or training data. | Local non-commercial research only; model is integrated for evaluation, not account identity decisions. No training or fine-tuning is planned. |
| PAD baseline | OpenVINO OMZ `anti-spoof-mn3` ONNX; SHA-384 `6de4534964b723397b3e8c995cadcf43bc007cc2f9930b95ae25f76adccece5d1d4d058d0b15117b9e4a9f758424f92a` | Model card points to MIT-licensed upstream model; trained on CelebA-Spoof, whose terms restrict use to non-commercial research/education and restrict commercial use of images/derived data. User approved research-only use on 27 Oct 2026. | Research-only baseline; no fine-tuning. Not for commercial/production use. |
| LFW | Labeled Faces in the Wild | Microsoft Research datasheet says images were crawled from news sources and reports no dataset licence. This is inconsistent with the instruction never to use scraped photos. | Do not download/use unless the project owner clarifies that use of this curated benchmark is allowed despite internet-sourced imagery and licence uncertainty. |
| CFP-FP | Celebrities in Frontal-Profile | Current official domain does not provide verifiable access/terms in the reviewed source. Image provenance and licence remain unverified. | Do not download/use until official terms, provenance, and permitted research use are verified. |
| AgeDB | AgeDB | Official iBUG page describes non-commercial research use; images are sourced from the internet and distribution/reproduction rights are not granted for images/annotations/derived data. Access requires agreement/password from the dataset owner. | Do not download/use under the current no-scraped-photos instruction without explicit resolution and documented access terms. |
| Own captures | Participant's own face, recorded with informed consent | Must be collected locally under applicable school/organization approval; capture protocol and retention/deletion plan apply. | Allowed for this study after consent and required approval; keep frames local and out of GitHub/Supabase. |
| Synthetic vectors | Generated non-biometric vectors | Synthetic values are not face data and cannot measure recognition accuracy. | Allowed only for 1M-vector speed/scale testing. Never report as accuracy evidence. |

## Sources

- [MediaPipe FaceMesh model card](https://storage.googleapis.com/mediapipe-assets/Model%20Card%20MediaPipe%20Face%20Mesh%20V2.pdf)
- [Open Model Zoo anti-spoof-mn3 model card](https://github.com/openvinotoolkit/open_model_zoo/blob/master/models/public/anti-spoof-mn3/README.md)
- [CelebA-Spoof official repository and terms](https://github.com/ZhangYuanhan-AI/CelebA-Spoof)
- [OpenVINO OMZ ArcFace candidate](https://github.com/openvinotoolkit/open_model_zoo/blob/master/models/public/face-recognition-resnet100-arcface-onnx/README.md)
- [InsightFace model-zoo licence and model details](https://github.com/deepinsight/insightface/blob/master/python-package/docs/model_zoo.md)
- [InsightFace official buffalo_l model-zoo release](https://github.com/deepinsight/insightface/releases/tag/model-zoo)
- [LFW datasheet](https://www.microsoft.com/en-us/research/uploads/prod/2019/01/1803.09010.pdf)
- [AgeDB official iBUG resource page](https://ibug.doc.ic.ac.uk/resources/agedb/)
- CFP-FP official domain: https://cfpw.org/ (terms were not verifiable at review time)

## Approval record needed

For each dataset/model used, record the exact version, source URL, licence text or agreement, checksum where applicable, collection/access date, permitted use, and reviewer. Do not infer permission from a paper or benchmark result. Do not commit assets or samples.
