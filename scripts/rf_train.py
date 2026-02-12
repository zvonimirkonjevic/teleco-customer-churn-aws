#!/usr/bin/env python3
"""
Random Forest training script for SageMaker with Hyperparameter Tuning support.
"""
import argparse
import json
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


def predict_fn(input_data, model):
    """Return class-1 probabilities for churn prediction."""
    return model.predict_proba(input_data)[:, 1].tolist()


def load_data(train_dir, test_dir):
    """Load and split train/test data."""
    train_file = find_csv(train_dir)
    test_file = find_csv(test_dir)
    
    print(f'Loading train: {train_file}')
    print(f'Loading test: {test_file}')
    
    train_df = pd.read_csv(train_file)
    test_df = pd.read_csv(test_file)
    
    print(f'Train shape: {train_df.shape}')
    print(f'Test shape: {test_df.shape}')
    
    # Scikit-learn data has headers with 'Churn' as target column
    y_train = train_df['Churn'].astype(int)
    X_train = train_df.drop('Churn', axis=1)
    y_test = test_df['Churn'].astype(int)
    X_test = test_df.drop('Churn', axis=1)
    
    return X_train, y_train, X_test, y_test


def train_model(args, X_train, y_train):
    """Train Random Forest model."""
    print(f'Training RF: n_estimators={args.n_estimators}, max_depth={args.max_depth}, '
          f'min_samples_split={args.min_samples_split}, min_samples_leaf={args.min_samples_leaf}')
    
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
    return model


def evaluate_model(model, X, y, prefix='Test'):
    """Evaluate model and return metrics."""
    y_pred = model.predict(X)
    y_prob = model.predict_proba(X)[:, 1]
    
    metrics = {
        f'{prefix}-AUC': roc_auc_score(y, y_prob),
        f'{prefix}-Accuracy': accuracy_score(y, y_pred),
        f'{prefix}-F1': f1_score(y, y_pred)
    }
    return metrics


def save_model(model, model_dir):
    """Save model to model directory."""
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'model.joblib')
    joblib.dump(model, model_path)
    print(f'Model saved to {model_path}')


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    
    # Hyperparameters (tunable)
    parser.add_argument('--n-estimators', type=int, default=100)
    parser.add_argument('--max-depth', type=int, default=10)
    parser.add_argument('--min-samples-split', type=int, default=2)
    parser.add_argument('--min-samples-leaf', type=int, default=1)
    parser.add_argument('--max-features', type=str, default='sqrt')
    
    # SageMaker environment
    parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR', '/opt/ml/model'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN', '/opt/ml/input/data/train'))
    parser.add_argument('--test', type=str, default=os.environ.get('SM_CHANNEL_TEST', '/opt/ml/input/data/test'))
    parser.add_argument('--output-data-dir', type=str, default=os.environ.get('SM_OUTPUT_DATA_DIR', '/opt/ml/output/data'))
    
    args, _ = parser.parse_known_args()
    return args


def main():
    args = parse_args()
    
    print(f'Train dir: {args.train}')
    print(f'Test dir: {args.test}')
    
    # Load data
    X_train, y_train, X_test, y_test = load_data(args.train, args.test)
    
    # Train model
    model = train_model(args, X_train, y_train)
    
    # Evaluate on test set
    test_metrics = evaluate_model(model, X_test, y_test, prefix='Test')
    
    # Evaluate on train set (overfitting analysis)
    train_metrics = evaluate_model(model, X_train, y_train, prefix='Train')
    
    # Print metrics (SageMaker HPO parses these from logs)
    for name, value in {**test_metrics, **train_metrics}.items():
        print(f'{name}: {value:.4f}')
    
    # Save metrics to JSON for CloudWatch/analysis
    all_metrics = {**test_metrics, **train_metrics}
    os.makedirs(args.output_data_dir, exist_ok=True)
    with open(os.path.join(args.output_data_dir, 'metrics.json'), 'w') as f:
        json.dump(all_metrics, f, indent=2)
    
    # Save model
    save_model(model, args.model_dir)
    print('Training complete')


if __name__ == '__main__':
    main()
