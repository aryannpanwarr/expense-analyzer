const { useEffect, useMemo, useRef, useState } = React;

const currency = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

const categories = [
  "Food",
  "Travel",
  "Shopping",
  "Bills",
  "Education",
  "Health",
  "Entertainment",
  "Other",
];

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return "";
}

async function apiFetch(url, options = {}) {
  const headers = {
    "X-CSRFToken": getCookie("csrftoken"),
    ...(options.headers || {}),
  };
  const response = await fetch(url, { ...options, headers });
  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error(`Server error (${response.status})`);
  }
  if (!response.ok) {
    throw new Error((data.errors || [data.error || "Request failed"]).join(" "));
  }
  return data;
}

function ChartCanvas({ type, labels, values, label }) {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current) return;
    if (chartRef.current) chartRef.current.destroy();

    chartRef.current = new Chart(canvasRef.current, {
      type,
      data: {
        labels,
        datasets: [
          {
            label,
            data: values,
            backgroundColor: [
              "#0f766e",
              "#2563eb",
              "#f59e0b",
              "#dc2626",
              "#7c3aed",
              "#0891b2",
              "#65a30d",
              "#475569",
            ],
            borderColor: "#ffffff",
            borderWidth: type === "doughnut" ? 2 : 0,
            borderRadius: type === "bar" ? 6 : 0,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: type === "doughnut", position: "bottom" },
        },
        scales: type === "bar" ? { y: { beginAtZero: true } } : {},
      },
    });

    return () => {
      if (chartRef.current) chartRef.current.destroy();
    };
  }, [type, labels.join("|"), values.join("|"), label]);

  return <canvas ref={canvasRef} aria-label={label}></canvas>;
}

function App() {
  const [summary, setSummary] = useState(null);
  const [form, setForm] = useState({
    date: new Date().toISOString().slice(0, 10),
    category: "Food",
    description: "",
    amount: "",
  });
  const [question, setQuestion] = useState("Where am I spending most and how can I reduce expenses?");
  const [insight, setInsight] = useState("");
  const [message, setMessage] = useState("");
  const [loadingInsight, setLoadingInsight] = useState(false);

  const loadSummary = async () => {
    const data = await apiFetch("/api/expenses/");
    setSummary(data);
  };

  useEffect(() => {
    loadSummary().catch((error) => setMessage(error.message));
  }, []);

  const categoryChart = useMemo(() => {
    const rows = summary?.categories || [];
    return {
      labels: rows.map((row) => row.category),
      values: rows.map((row) => row.total),
    };
  }, [summary]);

  const monthlyChart = useMemo(() => {
    const rows = summary?.monthly || [];
    return {
      labels: rows.map((row) => row.month),
      values: rows.map((row) => row.total),
    };
  }, [summary]);

  const addExpense = async (event) => {
    event.preventDefault();
    setMessage("");
    try {
      const data = await apiFetch("/api/expenses/add/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      setSummary(data.summary);
      setForm({ ...form, description: "", amount: "" });
      setMessage("Expense added successfully.");
    } catch (error) {
      setMessage(error.message);
    }
  };

  const uploadCsv = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const payload = new FormData();
    payload.append("file", file);
    setMessage("");
    try {
      const data = await apiFetch("/api/expenses/upload/", {
        method: "POST",
        body: payload,
      });
      setSummary(data.summary);
      const skipped = data.skipped.length ? ` Skipped: ${data.skipped.join(" ")}` : "";
      setMessage(`Imported ${data.created} expense rows.${skipped}`);
      event.target.value = "";
    } catch (error) {
      setMessage(error.message);
    }
  };

  const deleteExpense = async (id) => {
    setMessage("");
    try {
      const data = await apiFetch(`/api/expenses/${id}/delete/`, { method: "POST" });
      setSummary(data.summary);
      setMessage("Expense deleted.");
    } catch (error) {
      setMessage(error.message);
    }
  };

  const askGemini = async () => {
    setLoadingInsight(true);
    setInsight("");
    setMessage("");
    try {
      const data = await apiFetch("/api/expenses/insights/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const sourceLabel = data.source === "gemini"
        ? "Gemini API"
        : data.source === "fallback"
          ? "Gemini error fallback"
          : "Local fallback";
      setInsight(`${sourceLabel}\n\n${data.insight}`);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoadingInsight(false);
    }
  };

  const topCategory = summary?.topCategory?.category || "No data";

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="container py-3 d-flex align-items-center justify-content-between gap-3">
          <div className="d-flex align-items-center gap-3">
            <div className="brand-mark">EA</div>
            <div>
              <h1 className="h4 mb-0 fw-bold">Expense Data Analyzer</h1>
              <div className="text-secondary small">Track, analyze, and improve spending habits</div>
            </div>
          </div>
          <label className="btn btn-outline-primary mb-0">
            Upload CSV
            <input type="file" accept=".csv" className="d-none" onChange={uploadCsv} />
          </label>
        </div>
      </header>

      <section className="page-band">
        <div className="container">
          {message && <div className="alert alert-info">{message}</div>}

          <div className="row g-3 mb-3">
            <div className="col-md-4">
              <div className="metric">
                <div className="metric-label">Total spending</div>
                <div className="metric-value">{currency.format(summary?.total || 0)}</div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="metric">
                <div className="metric-label">Expenses recorded</div>
                <div className="metric-value">{summary?.count || 0}</div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="metric">
                <div className="metric-label">Highest category</div>
                <div className="metric-value">{topCategory}</div>
              </div>
            </div>
          </div>

          <div className="row g-3">
            <div className="col-lg-4">
              <div className="panel h-100">
                <div className="panel-title">Add Expense</div>
                <form onSubmit={addExpense} className="vstack gap-3">
                  <input className="form-control" type="date" value={form.date} onChange={(event) => setForm({ ...form, date: event.target.value })} required />
                  <select className="form-select" value={form.category} onChange={(event) => setForm({ ...form, category: event.target.value })}>
                    {categories.map((category) => <option key={category}>{category}</option>)}
                  </select>
                  <input className="form-control" placeholder="Description" value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} required />
                  <input className="form-control" type="number" min="1" step="0.01" placeholder="Amount" value={form.amount} onChange={(event) => setForm({ ...form, amount: event.target.value })} required />
                  <button className="btn btn-primary" type="submit">Add Expense</button>
                </form>
              </div>
            </div>

            <div className="col-lg-8">
              <div className="panel h-100">
                <div className="panel-title">Gemini Savings Suggestions</div>
                <div className="input-group mb-3">
                  <input className="form-control" value={question} onChange={(event) => setQuestion(event.target.value)} />
                  <button className="btn btn-primary" onClick={askGemini} disabled={loadingInsight}>
                    {loadingInsight ? "Analyzing..." : "Ask"}
                  </button>
                </div>
                <div className="insight-box">
                  {insight || "Ask Gemini where your money is going and how to reduce expenses. If the API key is not set, the app shows a local analysis fallback."}
                </div>
              </div>
            </div>
          </div>

          <div className="row g-3 mt-1">
            <div className="col-lg-6">
              <div className="panel">
                <div className="panel-title">Category-wise Expenses</div>
                <div className="chart-box">
                  {categoryChart.labels.length ? (
                    <ChartCanvas type="doughnut" labels={categoryChart.labels} values={categoryChart.values} label="Category spending" />
                  ) : (
                    <div className="empty-state">Add expenses to see category analysis.</div>
                  )}
                </div>
              </div>
            </div>
            <div className="col-lg-6">
              <div className="panel">
                <div className="panel-title">Monthly Spending</div>
                <div className="chart-box">
                  {monthlyChart.labels.length ? (
                    <ChartCanvas type="bar" labels={monthlyChart.labels} values={monthlyChart.values} label="Monthly spending" />
                  ) : (
                    <div className="empty-state">Add expenses to see monthly trends.</div>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="panel mt-3">
            <div className="panel-title">Recent Expenses</div>
            <div className="table-responsive">
              <table className="table table-hover mb-0">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Category</th>
                    <th>Description</th>
                    <th className="text-end">Amount</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {(summary?.recent || []).map((expense) => (
                    <tr key={expense.id}>
                      <td>{expense.date}</td>
                      <td>{expense.category}</td>
                      <td>{expense.description}</td>
                      <td className="text-end amount">{currency.format(expense.amount)}</td>
                      <td className="text-end">
                        <button className="btn btn-sm btn-outline-danger" onClick={() => deleteExpense(expense.id)}>Delete</button>
                      </td>
                    </tr>
                  ))}
                  {!(summary?.recent || []).length && (
                    <tr>
                      <td colSpan="5" className="empty-state">No expenses yet.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
