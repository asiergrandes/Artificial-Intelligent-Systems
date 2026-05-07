# -*- coding: utf-8 -*-

import sys
import argparse
import numpy as np
import pickle
import time
import json
import csv
import os

import pandas as pd
from colorama import Fore
from sklearn.naive_bayes import MultinomialNB

# Sklearn
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Imblearn
from imblearn.over_sampling import SMOTE, RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler


name = "knn_model"
name_modelo = name + ".pkl"
name_modelo_csv = name + ".csv"
name_pred_csv = "pred_test_" + name + ".csv"
name_carpeta_model = "OUTPUT_" + name


# =============================
# Argument parsing
# =============================
def parse_args():
    parse = argparse.ArgumentParser(description="IMDb sentiment classifier")
    parse.add_argument("-m", "--mode", required=True, help="train or test")
    parse.add_argument("-f", "--file", required=True, help="CSV file path")
    parse.add_argument("-a", "--algorithm", required=True,
                       choices=["kNN", "decision_tree", "random_forest", "naive_bayes"])
    parse.add_argument("-p", "--prediction", help="Name of the column to predict", required=True)
    parse.add_argument("-v", "--verbose", action="store_true")
    parse.add_argument("--debug", action="store_true")

    args = parse.parse_args()

    with open("classifier.json") as json_file:
        config = json.load(json_file)

    for key, value in config.items():
        setattr(args, key, value)

    return args


# =============================
# Data loading
# =============================
def load_data(file):
    try:
        data = pd.read_csv(file, encoding="utf-8")
        print(Fore.GREEN + "Data loaded succesfully" + Fore.RESET)
        return data
    except Exception as e:
        print(Fore.RED + "Error while loading data" + Fore.RESET)
        print(e)
        sys.exit(1)


# =============================
# Text processing
# =============================
def process_text():
    global data, vectorizer

    text_data = data["review"]

    if args.preprocessing["text_process"] == "tf-idf":
        vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words="english",
            lowercase=True
        )
    else:
        vectorizer = CountVectorizer(
            max_features=5000,
            stop_words="english",
            lowercase=True
        )

    X_text = vectorizer.fit_transform(text_data)
    data._X_text = X_text
    print(Fore.GREEN + "Text vectorization completed" + Fore.RESET)


# =============================
# Sampling
# =============================
def over_under_sampling():
    global data

    if args.mode == "test":
        return

    X = data._X_text
    y = data[args.prediction]

    if args.preprocessing["sampling"] == "oversampling":
        sampler = RandomOverSampler(random_state=42)
    elif args.preprocessing["sampling"] == "undersampling":
        sampler = RandomUnderSampler(random_state=42)
    else:
        return

    X_res, y_res = sampler.fit_resample(X, y)
    data._X_text = X_res
    data[args.prediction] = y_res

    print(Fore.GREEN + f"{args.preprocessing['sampling']} applied successfully" + Fore.RESET)


# =============================
# Train / Test split
# =============================
def divide_data():
    X = data._X_text
    y = data[args.prediction]

    return train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )


# =============================
# Save / Load model
# =============================
def save_model(gs):
    with open(name_carpeta_model + "/" + name_modelo, "wb") as f:
        pickle.dump({
            "model": gs.best_estimator_,
            "vectorizer": vectorizer
        }, f)

    with open(name_carpeta_model + "/" + name_modelo_csv, "w") as file:
        writer = csv.writer(file)
        writer.writerow(["Params", "Score"])
        for p, s in zip(gs.cv_results_["params"], gs.cv_results_["mean_test_score"]):
            writer.writerow([p, s])

    print(Fore.CYAN + "Model and vectorizer saved" + Fore.RESET)


def load_model():
    with open(name_carpeta_model + "/" + name_modelo, "rb") as f:
        data = pickle.load(f)
    return data["model"], data["vectorizer"]


# =============================
# Prediction
# =============================
def predict():
    model, vectorizer = load_model()
    df = pd.read_csv(args.file)

    X_text = vectorizer.transform(df["review"])
    predictions = model.predict(X_text)

    df[args.prediction + "_pred"] = predictions
    df.to_csv(name_carpeta_model + "/" + name_pred_csv, index=False)

    print(Fore.GREEN + "Saved predictions" + Fore.RESET)

    if args.prediction in df.columns:
        print("\nAccuracy:",
              (df[args.prediction] == predictions).mean())
        print(classification_report(df[args.prediction], predictions))


# =============================
# Algorithms
# =============================
def train_model(model, params):
    x_train, x_test, y_train, y_test = divide_data()

    gs = GridSearchCV(model, params, cv=5)

    start = time.time()
    gs.fit(x_train, y_train)
    end = time.time()

    print(Fore.MAGENTA + f"Training time: {end - start:.2f} seconds" + Fore.RESET)

    if args.verbose:
        print(classification_report(y_test, gs.predict(x_test)))

    save_model(gs)


# =============================
# Main
# =============================
if __name__ == "__main__":
    np.random.seed(42)
    args = parse_args()

    os.makedirs(name_carpeta_model, exist_ok=True)

    data = load_data(args.file)
    process_text()
    over_under_sampling()

    if args.mode == "train":
        if args.algorithm == "naive_bayes":
            train_model(MultinomialNB(), args.naive_bayes)
        elif args.algorithm == "kNN":
            train_model(KNeighborsClassifier(), args.kNN)
        elif args.algorithm == "decision_tree":
            train_model(DecisionTreeClassifier(), args.decision_tree)
        elif args.algorithm == "random_forest":
            train_model(RandomForestClassifier(), args.random_forest)

    elif args.mode == "test":
        predict()
