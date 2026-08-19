# Model Card — Crop Disease Classifier

MobileNetV2 fine-tuned to classify 15 leaf conditions across three crops. Written
because a model a farmer might act on should state where it stops working, not
only where it scores well.

| | |
|---|---|
| **Architecture** | MobileNetV2 (ImageNet pretrained), transfer learning |
| **Task** | Single-label image classification, 15 classes |
| **Crops** | Tomato (8 classes), Corn (4), Potato (3) |
| **Size / latency** | 9.3 MB · ~9 ms GPU · ~30 ms on-device (TFLite) |
| **Training data** | [PlantVillage](https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset), 22,115 images |
| **Split** | 80/20 stratified, seed 42 (17,692 train / 4,423 validation) |
| **License** | Apache-2.0 |

## Intended use

Triage support — a fast first opinion on a leaf photo, to help someone decide
whether a plant needs closer attention. It is designed to run on a phone, offline,
where an agronomist is not a short trip away.

## Out of scope

- **Any crop other than tomato, corn or potato.** The model has 15 outputs and no
  abstain path: a soybean leaf, a pest, a soil photo or a cat still returns one of
  the 15 classes with a confidence attached.
- **Treatment decisions on their own.** The returned guidance is a static lookup
  keyed by the predicted class, not advice conditioned on your field, dose or
  local regulation.
- **Yield estimation, severity grading or disease progression.** The model reports
  a class, not how far along an infection is.

## What the headline number does and does not mean

**97.83% is validation accuracy on a held-out split of PlantVillage, and that split
comes from the same distribution as training.** It is a fair measure of how well the
model learned this dataset. It is not a measure of field performance.

PlantVillage images are captured under laboratory conditions — typically a single
detached leaf on a uniform background, evenly lit. Real photographs contain soil,
sky, hands, several overlapping leaves, shadow and motion blur. Accuracy on such
images has not been measured here and should be assumed to be materially lower
until it is.

## Known failure modes

- **Confidently wrong on out-of-distribution input.** Softmax over 15 classes always
  sums to 1, so there is no "none of these" answer. `outputs/plots/incorrect_predictions.png`
  deliberately plots the highest-confidence errors, which is the honest place to look.
- **Gray Leaf Spot vs Northern Leaf Blight on corn** is the weakest pair (91.4% F1) —
  the two are visually similar, and this is where the confusion matrix concentrates.
- **Thin classes.** Potato Healthy has 152 images. Weighted sampling gets recall up,
  but a class that small cannot represent the variation that exists in the field.
- **Confidence is not calibrated.** The number returned is a softmax probability. It
  has not been checked against observed correctness, so 0.9 does not mean "right nine
  times in ten".

## Evaluation

Reproduce with `notebooks/crop_disease_classification.ipynb`. Per-class accuracy,
the confusion matrix, training curves and the highest-confidence errors are written
to `outputs/plots/`. Weighted precision 0.979, recall 0.978, F1 0.978.

## Responsible use

Present the prediction as a suggestion with its confidence, keep the top-k
alternatives visible rather than only the winner, and make it easy to reach a
human. Do not let it be the last step before someone applies a chemical.
