# Colab Runbook

## 1) Setup
```bash
!git clone https://github.com/Orkhan-Mustafayev/gpt.git
%cd /content/gpt
!pip install -e .
```

## 2) Train
```bash
!python -m football_ml.training.train_xgb
```

## 3) Predict
```bash
!python -m football_ml.prediction.predict_upcoming
```
