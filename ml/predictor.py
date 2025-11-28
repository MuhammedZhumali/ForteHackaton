import numpy as np
import pandas as pd
from typing import Dict, List
import joblib

from ml.model_loader import ModelLoader


class FraudPredictor:

    FEATURE_NAMES = [
        "amount",
        "os_ver_count_30d",
        "phone_model_count_30d",
        "logins_7d",
        "logins_30d",
        "logins_per_day_7",
        "logins_per_day_30",
        "rel_change_7_vs_30",
        "share_7_of_30",
        "mean_interval_30d",
        "std_interval_30d",
        "var_interval_30d",
        "ewm_interval_7d",
        "burstiness",
        "fano_factor",
        "z_score_7d_vs_30d",
    ]

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.imputer = ModelLoader.imputer
        self.scaler = ModelLoader.scaler
        self.model = ModelLoader.get_active_model()

        if not self.model or not self.imputer or not self.scaler:
            raise RuntimeError("Модели не загружены. Проверьте ModelLoader.")

    def predict_single(self, features: Dict) -> Dict:

        feature_values = [features.get(name, 0) for name in self.FEATURE_NAMES]

        df = pd.DataFrame([feature_values], columns=self.FEATURE_NAMES)

        x_imp = self.imputer.transform(df)
        x_scaled = self.scaler.transform(x_imp)

        proba = self.model.predict_proba(x_scaled)[0, 1]
        is_fraud = proba >= self.threshold

        return {
            "fraud_probability": float(proba),
            "is_fraud": bool(is_fraud),
            "model_version": ModelLoader.active_model_name
        }

    def predict_batch(self, features_list: List[Dict]) -> List[Dict]:
        results = []
        for features in features_list:
            result = self.predict_single(features)
            results.append(result)
        return results

    def get_feature_importance(self) -> Dict:
        if not hasattr(self.model, 'feature_importances_'):
            return {"error": "Модель не поддерживает feature_importances_"}

        importances = self.model.feature_importances_

        feature_importance = [
            {"feature": name, "importance": float(imp)}
            for name, imp in zip(self.FEATURE_NAMES, importances)
        ]
        feature_importance.sort(key=lambda x: x['importance'], reverse=True)

        return {
            "model": ModelLoader.active_model_name,
            "features": feature_importance
        }