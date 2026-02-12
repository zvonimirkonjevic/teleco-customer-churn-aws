#!/usr/bin/env python3
"""
SVM training script for SageMaker with Hyperparameter Tuning support.
"""
import argparse
import json
import os
import glob
import pandas as pd
import joblib
from sklearn.svm import SVC
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    # Hyperparameters (tunable)
    parser.add_argument('--C', type=float, default=1.0)
    parser.add_argument('--kernel', type=str, default='rbf')
    parser.add_argument('--gamma', type=str, default='scale')
    
    # SageMaker environment
    parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR', '/opt/ml/model'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN', '/opt/ml/input/data/train'))
    parser.add_argument('--test', type=str, default=os.environ.get('SM_CHANNEL_TEST', '/opt/ml/input/data/test'))
    parser.add_argument('--output-data-dir', type=str, default=os.environ.get('SM_OUTPUT_DATA_DIR', '/opt/ml/output/data'))
    
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
    
    # Scikit-learn data has headers with 'Churn' as target column
    y_train = train_df['Churn'].astype(int)
    X_train = train_df.drop('Churn', axis=1)
    y_test = test_df['Churn'].astype(int)
    X_test = test_df.drop('Churn', axis=1)
    
    print(f'Training SVM with C={args.C}, kernel={args.kernel}')
    model = SVC(C=args.C, kernel=args.kernel, gamma=args.gamma, probability=True)
    model.fit(X_train, y_train)
    
    # Evaluate on test set
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    test_metrics = {
        'Test-AUC': roc_auc_score(y_test, y_prob),
        'Test-Accuracy': accuracy_score(y_test, y_pred),
        'Test-F1': f1_score(y_test, y_pred)
    }
    
    # Evaluate on train set (overfitting analysis)
    y_train_pred = model.predict(X_train)
    y_train_prob = model.predict_proba(X_train)[:, 1]
    
    train_metrics = {
        'Train-AUC': roc_auc_score(y_train, y_train_prob),
        'Train-Accuracy': accuracy_score(y_train, y_train_pred),
        'Train-F1': f1_score(y_train, y_train_pred)
    }
    
    # Print metrics (SageMaker HPO parses these from logs)
    all_metrics = {**test_metrics, **train_metrics}
    for name, value in all_metrics.items():
        print(f'{name}: {value:.4f}')
    
    # Save metrics to JSON for CloudWatch/analysis
    os.makedirs(args.output_data_dir, exist_ok=True)
    with open(os.path.join(args.output_data_dir, 'metrics.json'), 'w') as f:
        json.dump(all_metrics, f, indent=2)
    
    # Save model
    os.makedirs(args.model_dir, exist_ok=True)
    model_path = os.path.join(args.model_dir, 'model.joblib')
    joblib.dump(model, model_path)
    print(f'Model saved to {model_path}')
    print('Training complete')
