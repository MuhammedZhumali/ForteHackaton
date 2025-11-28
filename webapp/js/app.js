const API_BASE = "";

function $(selector) {
    return document.querySelector(selector);
}

function formatPercent(value) {
    if (value === null || value === undefined) return "-";
    return (value * 100).toFixed(1) + "%";
}

function formatTenge(amount) {
    if (amount === null || amount === undefined) return "-";
    return amount.toLocaleString("ru-RU", { maximumFractionDigits: 0 }) + " ₸";
}

function setText(el, text) {
    if (!el) return;
    el.textContent = text;
}

function setRiskChip(el, riskLevel) {
    if (!el) return;
    el.className = "chip";
    if (!riskLevel) {
        el.textContent = "-";
        return;
    }
    const level = riskLevel.toUpperCase();
    if (level === "LOW") el.classList.add("chip-low");
    else if (level === "MEDIUM") el.classList.add("chip-medium");
    else if (level === "HIGH") el.classList.add("chip-high");
    else if (level === "CRITICAL") el.classList.add("chip-critical");
    el.textContent = level;
}

function initTabs() {
    const buttons = document.querySelectorAll(".tab-button");
    const panels = document.querySelectorAll(".tab-panel");
    buttons.forEach((btn) => {
        btn.addEventListener("click", () => {
            const tabId = btn.dataset.tab;
            buttons.forEach((b) => b.classList.remove("active"));
            panels.forEach((p) => p.classList.remove("active"));
            btn.classList.add("active");
            document.getElementById(tabId).classList.add("active");
        });
    });
}

async function loadHealth() {
    const dot = $("#health-status-indicator");
    const text = $("#health-status-text");
    try {
        const res = await fetch(`${API_BASE}/health`);
        if (!res.ok) throw new Error("HTTP " + res.status);
        const data = await res.json();
        text.textContent = `API: ${data.components?.api ?? "unknown"}, DB: ${data.components?.database ?? "unknown"}, ML: ${data.components?.ml_models ?? "unknown"}`;
        dot.classList.remove("status-dot--ok", "status-dot--error", "status-dot--degraded", "status-dot--unhealthy");
        if (data.status === "healthy") {
            dot.classList.add("status-dot--ok");
        } else if (data.status === "degraded") {
            dot.classList.add("status-dot--degraded");
        } else {
            dot.classList.add("status-dot--unhealthy");
        }
    } catch (err) {
        console.error(err);
        text.textContent = "Не удалось получить статус API";
        dot.classList.add("status-dot--error");
    }
}

function getPredictPayloadFromForm() {
    function num(id) {
        const v = document.getElementById(id).value;
        return v === "" ? null : Number(v);
    }
    const clientIdRaw = $("#client_id").value.trim();
    return {
        amount: num("amount"),
        client_id: clientIdRaw || null,
        os_ver_count_30d: num("os_ver_count_30d"),
        phone_model_count_30d: num("phone_model_count_30d"),
        logins_7d: num("logins_7d"),
        logins_30d: num("logins_30d"),
        logins_per_day_7: num("logins_per_day_7"),
        logins_per_day_30: num("logins_per_day_30"),
        rel_change_7_vs_30: num("rel_change_7_vs_30"),
        share_7_of_30: num("share_7_of_30"),
        mean_interval_30d: num("mean_interval_30d"),
        std_interval_30d: num("std_interval_30d"),
        var_interval_30d: num("var_interval_30d"),
        ewm_interval_7d: num("ewm_interval_7d"),
        burstiness: num("burstiness"),
        fano_factor: num("fano_factor"),
        z_score_7d_vs_30d: num("z_score_7_vs_30d")
    };
}

async function submitPredictForm(ev) {
    ev.preventDefault();
    const btn = $("#predict-submit");
    const loader = $("#predict-loading");
    const errorBox = $("#predict-error");
    const resultEmpty = $("#predict-result-empty");
    const resultContainer = $("#predict-result");
    errorBox.classList.add("hidden");
    resultContainer.classList.add("hidden");
    btn.disabled = true;
    loader.classList.remove("hidden");
    try {
        const payload = getPredictPayloadFromForm();
        const res = await fetch(`${API_BASE}/api/v1/fraud/predict`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (!res.ok) {
            const errText = await res.text();
            throw new Error(errText || "Ошибка запроса");
        }
        const data = await res.json();
        resultEmpty.classList.add("hidden");
        resultContainer.classList.remove("hidden");
        setText($("#result-transaction-id"), data.transaction_id);
        setRiskChip($("#result-risk-level"), data.risk_level);
        const proba = data.fraud_probability;
        setText($("#result-fraud-proba"), formatPercent(proba));
        const bar = $("#result-fraud-bar");
        if (bar) {
            const p = Math.max(0, Math.min(1, proba || 0));
            bar.style.width = (p * 100).toFixed(1) + "%";
        }
        setText($("#result-is-fraud"), data.is_fraud ? "Да" : "Нет");
        setText($("#result-model-version"), data.model_version || "unknown");
        setText($("#result-timestamp"), data.timestamp);
        const reasons = data.reasons || [];
        const ul = $("#result-reasons");
        ul.innerHTML = "";
        if (reasons.length === 0) {
            const li = document.createElement("li");
            li.textContent = "Объяснения от модели отсутствуют.";
            li.classList.add("muted");
            ul.appendChild(li);
        } else {
            reasons.forEach((r) => {
                const li = document.createElement("li");
                li.textContent = r;
                ul.appendChild(li);
            });
        }
    } catch (err) {
        console.error(err);
        errorBox.textContent = "Ошибка скоринга: " + err.message;
        errorBox.classList.remove("hidden");
    } finally {
        btn.disabled = false;
        loader.classList.add("hidden");
    }
}

async function loadTransactions() {
    const limit = Number($("#filter-limit").value || 50);
    const risk = $("#filter-risk").value;
    const isFraudValue = $("#filter-is-fraud").value;
    const params = new URLSearchParams();
    params.set("skip", "0");
    params.set("limit", String(limit));
    if (risk) params.set("risk_level", risk);
    if (isFraudValue) params.set("is_fraud", isFraudValue === "true" ? "true" : "false");
    const tbody = $("#transactions-tbody");
    const errorBox = $("#transactions-error");
    errorBox.classList.add("hidden");
    tbody.innerHTML = `<tr><td colspan="7" class="muted">Загрузка...</td></tr>`;
    try {
        const res = await fetch(`${API_BASE}/api/v1/transactions/?${params.toString()}`);
        if (!res.ok) throw new Error("HTTP " + res.status);
        const data = await res.json();
        if (!Array.isArray(data) || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="muted">Записей не найдено.</td></tr>`;
            return;
        }
        tbody.innerHTML = "";
        data.forEach((t) => {
            const tr = document.createElement("tr");
            const created = t.created_at ? new Date(t.created_at).toLocaleString() : "-";
            const isFraud = t.is_fraud ? "Да" : "Нет";
            const proba = t.fraud_probability != null ? (t.fraud_probability * 100).toFixed(1) + "%" : "-";
            tr.innerHTML = `
                <td>${created}</td>
                <td>${t.transaction_id || "-"}</td>
                <td>${t.client_id || "-"}</td>
                <td>${formatTenge(t.amount || 0)}</td>
                <td>${proba}</td>
                <td>${t.risk_level || "-"}</td>
                <td>${isFraud}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
        errorBox.textContent = "Ошибка загрузки транзакций: " + err.message;
        errorBox.classList.remove("hidden");
        tbody.innerHTML = `<tr><td colspan="7" class="muted">Не удалось загрузить данные.</td></tr>`;
    }
}

async function loadTransactionsSummary() {
    const days = Number($("#filter-days").value || 7);
    const summaryBox = $("#transactions-summary");
    const errorBox = $("#transactions-error");
    errorBox.classList.add("hidden");
    summaryBox.classList.add("hidden");
    summaryBox.innerHTML = "";
    try {
        const res = await fetch(`${API_BASE}/api/v1/transactions/stats/summary?days=${encodeURIComponent(days)}`);
        if (!res.ok) throw new Error("HTTP " + res.status);
        const data = await res.json();
        summaryBox.innerHTML = `
            <span>Всего транзакций: <strong>${data.total_transactions}</strong></span>
            <span>Fraud детект: <strong>${data.fraud_detected}</strong></span>
            <span>Fraud rate: <strong>${(data.fraud_rate * 100).toFixed(2)}%</strong></span>
            <span>Avg fraud amount: <strong>${formatTenge(data.avg_fraud_amount)}</strong></span>
        `;
        summaryBox.classList.remove("hidden");
    } catch (err) {
        console.error(err);
        errorBox.textContent = "Ошибка получения summary: " + err.message;
        errorBox.classList.remove("hidden");
    }
}

async function loadDashboardStats() {
    const days = Number($("#analytics-days").value || 7);
    const container = $("#dashboard-content");
    const errorBox = $("#dashboard-error");
    errorBox.classList.add("hidden");
    container.innerHTML = `<p class="muted">Загрузка...</p>`;
    try {
        const res = await fetch(`${API_BASE}/api/v1/analytics/dashboard?days=${encodeURIComponent(days)}`);
        if (!res.ok) throw new Error("HTTP " + res.status);
        const data = await res.json();
        container.innerHTML = "";
        const cards = [
            {
                label: "Всего транзакций",
                value: data.total_transactions,
                sub: `за ${data.period_days} дней`
            },
            {
                label: "Fraud детект",
                value: data.fraud_detected,
                sub: `rate ${(data.fraud_rate * 100).toFixed(2)}%`
            },
            {
                label: "Средняя сумма fraud",
                value: formatTenge(data.avg_fraud_amount),
                sub: ""
            },
            {
                label: "Период",
                value: `${new Date(data.period_start).toLocaleDateString()} — ${new Date(data.period_end).toLocaleDateString()}`,
                sub: ""
            }
        ];
        cards.forEach((c) => {
            const div = document.createElement("div");
            div.className = "dashboard-card";
            div.innerHTML = `
                <div class="dashboard-label">${c.label}</div>
                <div class="dashboard-value">${c.value}</div>
                ${c.sub ? `<div class="dashboard-sub">${c.sub}</div>` : ""}
            `;
            container.appendChild(div);
        });
    } catch (err) {
        console.error(err);
        errorBox.textContent = "Ошибка загрузки дашборда: " + err.message;
        errorBox.classList.remove("hidden");
    }
}

async function loadRiskPatterns() {
    const list = $("#risk-patterns-list");
    const errorBox = $("#risk-patterns-error");
    errorBox.classList.add("hidden");
    list.innerHTML = `<li class="muted">Загрузка...</li>`;
    try {
        const res = await fetch(`${API_BASE}/api/v1/analytics/risk-patterns?limit=10`);
        if (!res.ok) throw new Error("HTTP " + res.status);
        const data = await res.json();
        if (!Array.isArray(data) || data.length === 0) {
            list.innerHTML = `<li class="muted">Паттерны не найдены.</li>`;
            return;
        }
        list.innerHTML = "";
        data.forEach((p) => {
            const li = document.createElement("li");
            li.className = "pattern-item";
            li.innerHTML = `
                <div class="pattern-title">${p.pattern}</div>
                <div>${p.description}</div>
                <div class="pattern-meta">prevalence ${(p.prevalence * 100).toFixed(1)}%</div>
            `;
            list.appendChild(li);
        });
    } catch (err) {
        console.error(err);
        errorBox.textContent = "Ошибка загрузки паттернов: " + err.message;
        errorBox.classList.remove("hidden");
    }
}

async function loadFeatureImportance() {
    const tbody = $("#feature-importance-tbody");
    const errorBox = $("#feature-importance-error");
    errorBox.classList.add("hidden");
    tbody.innerHTML = `<tr><td colspan="2" class="muted">Загрузка...</td></tr>`;
    try {
        const res = await fetch(`${API_BASE}/api/v1/analytics/feature-importance`);
        if (!res.ok) throw new Error("HTTP " + res.status);
        const data = await res.json();
        if (data.error) {
            tbody.innerHTML = `<tr><td colspan="2" class="muted">${data.error}</td></tr>`;
            return;
        }
        const feats = data.features || [];
        if (feats.length === 0) {
            tbody.innerHTML = `<tr><td colspan="2" class="muted">Нет данных по важности признаков.</td></tr>`;
            return;
        }
        tbody.innerHTML = "";
        feats.forEach((f) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${f.feature}</td>
                <td>${f.importance.toFixed(4)}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
        errorBox.textContent = "Ошибка загрузки важности признаков: " + err.message;
        errorBox.classList.remove("hidden");
        tbody.innerHTML = `<tr><td colspan="2" class="muted">Не удалось загрузить данные.</td></tr>`;
    }
}

async function submitSimulateGenerate(ev) {
    ev.preventDefault();
    const btn = $("#btn-sim-generate");
    const loader = $("#sim-generate-loading");
    const errorBox = $("#sim-generate-error");
    const resultBox = $("#sim-generate-result");
    const tbody = $("#sim-transactions-tbody");
    errorBox.classList.add("hidden");
    resultBox.classList.add("hidden");
    btn.disabled = true;
    loader.classList.remove("hidden");
    try {
        const count = Number($("#sim-count").value || 10);
        const type = $("#sim-type").value || "mixed";
        const ratio = Number($("#sim-fraud-ratio").value || 0.15);
        const payload = {
            count: count,
            transaction_type: type,
            fraud_ratio: ratio
        };
        const res = await fetch(`${API_BASE}/api/v1/simulation/generate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (!res.ok) {
            const text = await res.text();
            throw new Error(text || "Ошибка запроса");
        }
        const data = await res.json();
        setText($("#sim-total"), data.total_generated);
        setText($("#sim-fraud-count"), data.fraud_detected);
        setText($("#sim-fraud-rate"), (data.fraud_rate * 100).toFixed(2) + "%");
        setText($("#sim-generated-at"), data.generated_at);
        resultBox.classList.remove("hidden");
        const txList = data.transactions || [];
        if (txList.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="muted">Нет транзакций.</td></tr>`;
        } else {
            tbody.innerHTML = "";
            txList.slice(0, 20).forEach((t) => {
                const tr = document.createElement("tr");
                const risk = t.fraud_probability >= 0.9
                    ? "CRITICAL"
                    : t.fraud_probability >= 0.7
                        ? "HIGH"
                        : t.fraud_probability >= 0.4
                            ? "MEDIUM"
                            : "LOW";
                tr.innerHTML = `
                    <td>${risk}</td>
                    <td>${formatTenge(t.amount)}</td>
                    <td>${formatPercent(t.fraud_probability)}</td>
                    <td>${t.is_fraud ? "Да" : "Нет"}</td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (err) {
        console.error(err);
        errorBox.textContent = "Ошибка генерации: " + err.message;
        errorBox.classList.remove("hidden");
    } finally {
        btn.disabled = false;
        loader.classList.add("hidden");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    loadHealth();
    const predictForm = $("#predict-form");
    if (predictForm) {
        predictForm.addEventListener("submit", submitPredictForm);
    }
    const btnLoadTransactions = $("#btn-load-transactions");
    if (btnLoadTransactions) {
        btnLoadTransactions.addEventListener("click", loadTransactions);
    }
    const btnLoadSummary = $("#btn-load-summary");
    if (btnLoadSummary) {
        btnLoadSummary.addEventListener("click", loadTransactionsSummary);
    }
    const btnLoadDashboard = $("#btn-load-dashboard");
    if (btnLoadDashboard) {
        btnLoadDashboard.addEventListener("click", (e) => {
            e.preventDefault();
            loadDashboardStats();
        });
    }
    const btnLoadRiskPatterns = $("#btn-load-risk-patterns");
    if (btnLoadRiskPatterns) {
        btnLoadRiskPatterns.addEventListener("click", (e) => {
            e.preventDefault();
            loadRiskPatterns();
        });
    }
    const btnLoadFeatureImportance = $("#btn-load-feature-importance");
    if (btnLoadFeatureImportance) {
        btnLoadFeatureImportance.addEventListener("click", (e) => {
            e.preventDefault();
            loadFeatureImportance();
        });
    }
    const simGenerateForm = $("#simulate-generate-form");
    if (simGenerateForm) {
        simGenerateForm.addEventListener("submit", submitSimulateGenerate);
    }
    loadTransactions();
    loadTransactionsSummary();
    loadDashboardStats();
    loadRiskPatterns();
    loadFeatureImportance();
});
