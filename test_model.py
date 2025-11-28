import joblib
import pandas as pd

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

def score_example(name, data, model, imputer, scaler, threshold=0.5):
    df = pd.DataFrame([data], columns=FEATURE_NAMES)
    x_imp = imputer.transform(df)
    x_scaled = scaler.transform(x_imp)
    proba = model.predict_proba(x_scaled)[0, 1]
    is_fraud = proba >= threshold

    print(f"\n=== {name} ===")
    print(f"Вероятность мошенничества: {proba:.4f}")
    print(f"Флаг мошенничества (порог {threshold}): {is_fraud}")

def main():
    imputer = joblib.load("trained_model/imputer.pkl")
    scaler = joblib.load("trained_model/scaler.pkl")
    model = joblib.load("trained_model/GradientBoosting_fraud_model.pkl")

    # пример обычной транзакции
    normal_tx = {
        "amount": 30000.0,
        "os_ver_count_30d": 1.0,
        "phone_model_count_30d": 1.0,
        "logins_7d": 5.0,
        "logins_30d": 20.0,
        "logins_per_day_7": 5.0 / 7,
        "logins_per_day_30": 20.0 / 30,
        "rel_change_7_vs_30": 0.2,
        "share_7_of_30": 5.0 / 20.0,
        "mean_interval_30d": 50000.0,
        "std_interval_30d": 80000.0,
        "var_interval_30d": 6.4e9,
        "ewm_interval_7d": 20000.0,
        "burstiness": 0.3,
        "fano_factor": 120000.0,
        "z_score_7d_vs_30d": -0.2,
    }

    # очень подозрительная транзакция
    suspicious_tx = {
        "amount": 1500000.0,
        "os_ver_count_30d": 5.0,
        "phone_model_count_30d": 5.0,
        "logins_7d": 1.0,
        "logins_30d": 2.0,
        "logins_per_day_7": 1.0 / 7,
        "logins_per_day_30": 2.0 / 30,
        "rel_change_7_vs_30": 2.0,
        "share_7_of_30": 0.5,
        "mean_interval_30d": 200000.0,
        "std_interval_30d": 400000.0,
        "var_interval_30d": 1.6e11,
        "ewm_interval_7d": 10000.0,
        "burstiness": 0.9,
        "fano_factor": 500000.0,
        "z_score_7d_vs_30d": 3.0,
    }

    # экстермально подозрительная транзакция
    extreme_tx = {
        "amount": 5000000.0,           # очень крупная сумма
        "os_ver_count_30d": 10.0,      # постоянная смена OS
        "phone_model_count_30d": 8.0,  # множество разных устройств
        "logins_7d": 0.0,              # полное отсутствие активности
        "logins_30d": 1.0,             # всего один вход за месяц
        "logins_per_day_7": 0.0,
        "logins_per_day_30": 1.0 / 30,
        "rel_change_7_vs_30": 10.0,    # резкий спад активности
        "share_7_of_30": 0.0,          # нет логинов за последнюю неделю
        "mean_interval_30d": 2500000.0, # очень большие интервалы
        "std_interval_30d": 1000000.0,  # высокая вариативность
        "var_interval_30d": 1.0e12,     # экстремальная дисперсия
        "ewm_interval_7d": 5000000.0,   # огромные интервалы недавно
        "burstiness": 0.99,             # максимальная "взрывность"
        "fano_factor": 2000000.0,       # экстремальная нестабильность
        "z_score_7d_vs_30d": 5.0,       # сильное отклонение от нормы
    }

    # подозрительная активность после долгого простоя
    dormant_awake_tx = {
        "amount": 2500000.0,
        "os_ver_count_30d": 3.0,       # смена OS после простоя
        "phone_model_count_30d": 2.0,  # новое устройство
        "logins_7d": 15.0,             # внезапная активность
        "logins_30d": 16.0,            # почти все логины за последнюю неделю
        "logins_per_day_7": 15.0 / 7,
        "logins_per_day_30": 16.0 / 30,
        "rel_change_7_vs_30": 8.0,     # резкий всплеск
        "share_7_of_30": 15.0 / 16.0,  # 94% активности за последнюю неделю
        "mean_interval_30d": 1500000.0,
        "std_interval_30d": 800000.0,
        "var_interval_30d": 6.4e11,
        "ewm_interval_7d": 10000.0,    # короткие интервалы недавно
        "burstiness": 0.85,
        "fano_factor": 800000.0,
        "z_score_7d_vs_30d": 4.5,      # сильное отклонение
    }

    # подозрительная активность с множеством устройств
    multi_device_tx = {
        "amount": 3500000.0,
        "os_ver_count_30d": 15.0,      # много разных OS
        "phone_model_count_30d": 12.0, # много устройств
        "logins_7d": 25.0,             # гиперактивность
        "logins_30d": 50.0,
        "logins_per_day_7": 25.0 / 7,
        "logins_per_day_30": 50.0 / 30,
        "rel_change_7_vs_30": 3.0,     # увеличение активности
        "share_7_of_30": 0.5,
        "mean_interval_30d": 50000.0,  # короткие интервалы
        "std_interval_30d": 30000.0,
        "var_interval_30d": 9.0e8,
        "ewm_interval_7d": 2000.0,     # частые логины недавно
        "burstiness": 0.7,
        "fano_factor": 150000.0,
        "z_score_7d_vs_30d": 3.8,
    }

    score_example("Обычная транзакция", normal_tx, model, imputer, scaler)
    score_example("Подозрительная транзакция", suspicious_tx, model, imputer, scaler)
    score_example("ЭКСТРЕМАЛЬНО подозрительная", extreme_tx, model, imputer, scaler)
    score_example("Активность после простоя", dormant_awake_tx, model, imputer, scaler)
    score_example("Множество устройств", multi_device_tx, model, imputer, scaler)

if __name__ == "__main__":
    main()