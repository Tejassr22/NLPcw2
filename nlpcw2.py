# -*- coding: utf-8 -*-
"""nlpcw2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1L37HYC5vO14ubXsu4vEcpBU8J3dmtkHV
"""

!pip install transformers datasets scikit-learn pandas seaborn matplotlib --quiet

import torch
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from datasets import load_dataset
from sklearn.metrics import (
    confusion_matrix, classification_report, accuracy_score,
    f1_score, precision_recall_fscore_support
)
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    Trainer, TrainingArguments
)

# Load SemEval-style sentiment dataset
dataset = load_dataset("tweet_eval", "sentiment")

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    return {
        "accuracy": accuracy_score(labels, preds),
        "f1": f1_score(labels, preds, average='weighted')
    }

def plot_confusion_matrix(y_true, y_pred, model_name):
    labels = ["Negative", "Neutral", "Positive"]
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels)
    plt.title(f"Confusion Matrix - {model_name}")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.tight_layout()
    plt.show()

def plot_class_metrics(y_true, y_pred, model_name):
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average=None)
    labels = ["Negative", "Neutral", "Positive"]
    x = np.arange(len(labels))
    plt.figure(figsize=(8, 5))
    plt.bar(x, precision, width=0.25, label='Precision')
    plt.bar(x + 0.25, recall, width=0.25, label='Recall')
    plt.bar(x + 0.50, f1, width=0.25, label='F1 Score')
    plt.xticks(x + 0.25, labels)
    plt.title(f"Per-Class Metrics - {model_name}")
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_prediction_distribution(y_pred, model_name):
    labels = ["Negative", "Neutral", "Positive"]
    counts = np.bincount(y_pred, minlength=3)
    plt.bar(labels, counts, color="skyblue")
    plt.title(f"Prediction Distribution - {model_name}")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.show()

def plot_loss_curves(trainer, model_name):
    logs = trainer.state.log_history
    train_loss = [x['loss'] for x in logs if 'loss' in x and 'eval_loss' not in x]
    eval_loss = [x['eval_loss'] for x in logs if 'eval_loss' in x]
    plt.plot(train_loss[:len(eval_loss)], label="Train Loss")
    plt.plot(eval_loss, label="Eval Loss")
    plt.title(f"Loss Curves - {model_name}")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)

def preprocess(example):
    return tokenizer(example["text"], truncation=True, padding="max_length")

tokenized = dataset.map(preprocess, batched=True)
tokenized.set_format("torch", columns=["input_ids", "attention_mask", "label"])

training_args = TrainingArguments(
    output_dir="./results/bert-base",
    evaluation_strategy="epoch",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    learning_rate=2e-5,
    weight_decay=0.01,
    logging_steps=10,
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized["train"],
    eval_dataset=tokenized["validation"],
    compute_metrics=compute_metrics
)

trainer.train()

# Evaluate on test set
preds = trainer.predict(tokenized["test"])
y_true = preds.label_ids
y_pred = preds.predictions.argmax(-1)

# Text report
print(classification_report(y_true, y_pred, target_names=["Negative", "Neutral", "Positive"]))

# Visuals
plot_confusion_matrix(y_true, y_pred, "bert-base")
plot_loss_curves(trainer, "bert-base")
plot_class_metrics(y_true, y_pred, "bert-base")
plot_prediction_distribution(y_pred, "bert-base")

# RoBERTa-base
model_name = "roberta-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)

def preprocess(example):
    return tokenizer(example["text"], truncation=True, padding="max_length")

tokenized = dataset.map(preprocess, batched=True)
tokenized.set_format("torch", columns=["input_ids", "attention_mask", "label"])

training_args = TrainingArguments(
    output_dir="./results/roberta-base",
    evaluation_strategy="epoch",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    learning_rate=2e-5,
    weight_decay=0.01,
    logging_steps=10,
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized["train"],
    eval_dataset=tokenized["validation"],
    compute_metrics=compute_metrics
)

trainer.train()

# Evaluate on test set
preds = trainer.predict(tokenized["test"])
y_true = preds.label_ids
y_pred = preds.predictions.argmax(-1)

# Text report
print(classification_report(y_true, y_pred, target_names=["Negative", "Neutral", "Positive"]))

# Visuals for RoBERTa-base
plot_confusion_matrix(y_true, y_pred, "roberta-base")
plot_loss_curves(trainer, "roberta-base")
plot_class_metrics(y_true, y_pred, "roberta-base")
plot_prediction_distribution(y_pred, "roberta-base")

# BERTweet-base (Fixed for consistent padding)
model_name = "vinai/bertweet-base"
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)

# ✅ FIXED: Added max_length and padding explicitly
def preprocess(example):
    return tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=64  # Fixed max length suitable for tweets
    )

# Tokenize the dataset
tokenized = dataset.map(preprocess, batched=True)
tokenized.set_format("torch", columns=["input_ids", "attention_mask", "label"])

# Define training arguments
training_args = TrainingArguments(
    output_dir="./results/bertweet-base",
    evaluation_strategy="epoch",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    learning_rate=2e-5,
    weight_decay=0.01,
    logging_steps=10,
    report_to="none"
)

# Setup trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized["train"],
    eval_dataset=tokenized["validation"],
    compute_metrics=compute_metrics
)

# 🚀 Train the model
trainer.train()

# Evaluate BERTweet on the test set
preds = trainer.predict(tokenized["test"])
y_true = preds.label_ids
y_pred = preds.predictions.argmax(-1)

# Classification Report
print(classification_report(y_true, y_pred, target_names=["Negative", "Neutral", "Positive"]))

# Visuals for BERTweet
plot_confusion_matrix(y_true, y_pred, "bertweet-base")
plot_loss_curves(trainer, "bertweet-base")
plot_class_metrics(y_true, y_pred, "bertweet-base")
plot_prediction_distribution(y_pred, "bertweet-base")