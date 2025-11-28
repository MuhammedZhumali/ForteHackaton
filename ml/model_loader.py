import joblib
from pathlib import Path
from datetime import datetime


class ModelLoader:

    models = {}
    imputer = None
    scaler = None
    active_model_name = "GradientBoosting"

    @classmethod
    def load_models(cls):
        model_dir = Path(__file__).parent.parent / "trained_model"

        if not model_dir.exists():
            raise FileNotFoundError(f"Директория с моделями не найдена: {model_dir}")

        imputer_path = model_dir / "imputer.pkl"
        scaler_path = model_dir / "scaler.pkl"

        if not imputer_path.exists() or not scaler_path.exists():
            raise FileNotFoundError("Не найдены imputer.pkl или scaler.pkl")

        cls.imputer = joblib.load(imputer_path)
        cls.scaler = joblib.load(scaler_path)

        print(f"Загружены imputer и scaler")

        model_files = {
            "GradientBoosting": "GradientBoosting_fraud_model.pkl",
            "XGBoost": "XGBoost_fraud_model.pkl",
            "RandomForest": "RandomForest_fraud_model.pkl",
            "LogisticRegression": "LogisticRegression_fraud_model.pkl"
        }

        for name, filename in model_files.items():
            model_path = model_dir / filename
            if model_path.exists():
                try:
                    model = joblib.load(model_path)
                    cls.models[name] = {
                        "model": model,
                        "loaded_at": datetime.utcnow().isoformat(),
                        "version": "1.0",
                        "path": str(model_path)
                    }
                    print(f"Загружена модель: {name}")
                except Exception as e:
                    print(f"⚠Ошибка загрузки {name}: {e}")
            else:
                print(f"⚠Файл не найден: {filename}")

        if not cls.models:
            raise RuntimeError("Ни одна модель не была загружена")

        print(f"Всего загружено моделей: {len(cls.models)}")

    @classmethod
    def get_active_model(cls):
        if cls.active_model_name not in cls.models:
            cls.active_model_name = list(cls.models.keys())[0]

        return cls.models[cls.active_model_name]["model"]

    @classmethod
    def set_active_model(cls, model_name: str):
        if model_name not in cls.models:
            raise ValueError(f"Модель {model_name} не загружена")
        cls.active_model_name = model_name
