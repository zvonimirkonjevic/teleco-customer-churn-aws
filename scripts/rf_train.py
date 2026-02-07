#!/usr/bin/env python3
"""
Random Forest training script for SageMaker.
Expects CSV with headers, target column as last column.
"""
import argparse
import os
import glob
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score


def find_csv(directory):
    """Find the first CSV file in a directory."""
    files = glob.glob(os.path.join(directory, '*.csv'))
    if files:
        return files[0]
    raise FileNotFoundError(f'No CSV found in {directory}')


def model_fn(model_dir):
    """Load model for inference (required by SageMaker)."""
    return joblib.load(os.path.join(model_dir, 'model.joblib'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--n-estimators', type=int, default=100)
    parser.add_argument('--max-depth', type=int, default=10)
    parser.add_argument('--min-samples-split', type=int, default=2)
    parser.add_argument('--min-samples-leaf', type=int, default=1)
    parser.add_argument('--max-features', type=str, default='sqrt')
    parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN'))
    parser.add_argument('--test', type=str, default=os.environ.get('SM_CHANNEL_TEST'))
    
    # Parse known args only (ignore SageMaker's internal hyperparameters)
    args, _ = parser.parse_known_args()
    
    print(f'Train dir: {args.train}')
    print(f'Test dir: {args.test}')
    print(f'Train files: {os.listdir(args.train)}')
    print(f'Test files: {os.listdir(args.test)}')
    
    train_file = find_csv(args.train)
    test_file = find_csv(args.test)
    print(f'Loading train: {train_file}')
    print(f'Loading test: {test_file}')
    
    train_df = pd.read_csv(train_file)
    test_df = pd.read_csv(test_file)
    
    print(f'Train shape: {train_df.shape}')
    print(f'Test shape: {test_df.shape}')
    
    X_train, y_train = train_df.iloc[:, :-1], train_df.iloc[:, -1]
    X_test, y_test = test_df.iloc[:, :-1], test_df.iloc[:, -1]
    
    print(f'Training RF with n_estimators={args.n_estimators}, max_depth={args.max_depth}')
    model = RandomForestClassifier(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        min_samples_split=args.min_samples_split,
        min_samples_leaf=args.min_samples_leaf,
        max_features=args.max_features,
        n_jobs=-1,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    auc = roc_auc_score(y_test, y_prob)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print(f'AUC: {auc:.4f}')
    print(f'Accuracy: {acc:.4f}')
    print(f'F1: {f1:.4f}')
    
    model_path = os.path.join(args.model_dir, 'model.joblib')
    joblib.dump(model, model_path)
    print('Training complete')
