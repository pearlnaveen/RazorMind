import React, {
  useEffect,
  useState,
  useCallback
} from "react";

import axios from "axios";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from "recharts";

import "./App.css";


const API = process.env.REACT_APP_API_URL;


// =====================================================
// PIE CHART COLORS
// =====================================================

const PIE_COLORS = [
  "#6366f1",
  "#ef4444",
  "#f59e0b",
  "#22c55e",
  "#06b6d4",
  "#a855f7"
];


// =====================================================
// APP
// =====================================================

function App() {

  // ===================================================
  // STATE
  // ===================================================

  const [controller, setController] = useState(null);

  const [revenueData, setRevenueData] = useState([]);

  const [rootCauseData, setRootCauseData] = useState([]);

  const [question, setQuestion] = useState("");

  const [answer, setAnswer] = useState("");

  const [loading, setLoading] = useState(false);

  const [controllerLoading, setControllerLoading] = useState(true);

  const [controllerError, setControllerError] = useState("");

  const [selectedDays, setSelectedDays] = useState(30);

  const [recoveryData, setRecoveryData] = useState([]);

  // ===================================================
  // LOAD CONTROLLER
  // ===================================================

  const loadController = useCallback(
    async (days) => {

      try {

        setControllerLoading(true);

        setControllerError("");

        const response = await axios.get(
          `${API}/ai/controller`,
          {
            params: {
              days: days
            }
          }
        );

        console.log(
          "Controller response:",
          response.data
        );

        setController(response.data);

      } catch (error) {

        console.error(
          "Controller error:",
          error
        );

        setControllerError(
          "Unable to load RazorMind dashboard."
        );

      } finally {

        setControllerLoading(false);

      }

    },
    []
  );


  // ===================================================
  // LOAD REVENUE
  // ===================================================

  const loadRevenue = useCallback(
    async (days) => {

      try {

        const response = await axios.get(
          `${API}/analytics/revenue`,
          {
            params: {
              days: days
            }
          }
        );

        console.log(
          "Revenue response:",
          response.data
        );


        const data = response.data;


        /*
         * Backend may return:
         *
         * [
         *   { date: "...", revenue: 10000 }
         * ]
         *
         * OR:
         *
         * {
         *   status: "success",
         *   data: [...]
         * }
         *
         * OR:
         *
         * {
         *   revenue: [...]
         * }
         */


        if (Array.isArray(data)) {

          setRevenueData(data);

        }

        else if (
          data &&
          Array.isArray(data.data)
        ) {

          setRevenueData(data.data);

        }

        else if (
          data &&
          Array.isArray(data.revenue)
        ) {

          setRevenueData(data.revenue);

        }

        else {

          console.warn(
            "Unexpected revenue format:",
            data
          );

          setRevenueData([]);

        }

      } catch (error) {

        console.error(
          "Revenue error:",
          error
        );

        setRevenueData([]);

      }

    },
    []
  );


  // ===================================================
  // LOAD ROOT CAUSE
  // ===================================================

  const loadRootCause = useCallback(
    async (days) => {

      try {

        const response = await axios.get(
          `${API}/analytics/root-cause`,
          {
            params: {
              days: days
            }
          }
        );

        console.log(
          "Root cause response:",
          response.data
        );


        const data = response.data;


        /*
         * IMPORTANT
         *
         * Backend response can be:
         *
         * {
         *   status: "success",
         *   root_cause: {
         *      breakdown: [...]
         *   }
         * }
         *
         * Therefore we extract breakdown.
         */


        if (Array.isArray(data)) {

          setRootCauseData(data);

        }

        else if (
          data &&
          data.root_cause &&
          Array.isArray(
            data.root_cause.breakdown
          )
        ) {

          setRootCauseData(
            data.root_cause.breakdown
          );

        }

        else if (
          data &&
          Array.isArray(data.breakdown)
        ) {

          setRootCauseData(
            data.breakdown
          );

        }

        else if (
          data &&
          Array.isArray(data.data)
        ) {

          setRootCauseData(
            data.data
          );

        }

        else {

          console.warn(
            "Unexpected root cause format:",
            data
          );

          setRootCauseData([]);

        }

      } catch (error) {

        console.error(
          "Root cause error:",
          error
        );

        setRootCauseData([]);

      }

    },
    []
  );
    const loadRecovery = useCallback(
  async (days) => {

    try {

      const response = await axios.get(
        `${API}/analytics/recovery-opportunities`,
        {
          params: {
            days: days
          }
        }
      );

      console.log(
        "Recovery response:",
        response.data
      );

      if (
        response.data &&
        Array.isArray(
          response.data.opportunities
        )
      ) {

        setRecoveryData(
          response.data.opportunities
        );

      } else {

        setRecoveryData([]);

      }

    } catch (error) {

      console.error(
        "Recovery error:",
        error
      );

      setRecoveryData([]);

    }

  },
  []
);

  // ===================================================
  // LOAD ALL DASHBOARD DATA
  // ===================================================

  useEffect(() => {

  loadController(selectedDays);

  loadRevenue(selectedDays);

  loadRootCause(selectedDays);

  loadRecovery(selectedDays);

}, [
  selectedDays,
  loadController,
  loadRevenue,
  loadRootCause,
  loadRecovery
]);


  // ===================================================
  // ASK RAZORMIND
  // ===================================================

  const askRazorMind = async () => {

    if (!question.trim()) {
      return;
    }

    setLoading(true);

    setAnswer("");

    try {

      const response = await axios.get(
        `${API}/ai/ask`,
        {
          params: {
            question: question.trim()
          }
        }
      );


      console.log(
        "AI response:",
        response.data
      );


      const data = response.data;


      // -----------------------------------------------
      // NORMAL RESPONSE
      // -----------------------------------------------

      if (
        data &&
        typeof data === "object" &&
        typeof data.answer === "string"
      ) {

        setAnswer(data.answer);

      }

      // -----------------------------------------------
      // OBJECT WITHOUT answer
      // -----------------------------------------------

      else if (
        data &&
        typeof data === "object"
      ) {

        setAnswer(
          JSON.stringify(
            data,
            null,
            2
          )
        );

      }

      // -----------------------------------------------
      // STRING RESPONSE
      // -----------------------------------------------

      else if (
        data !== undefined &&
        data !== null
      ) {

        setAnswer(
          String(data)
        );

      }

      else {

        setAnswer(
          "RazorMind returned an empty response."
        );

      }

    } catch (error) {

      console.error(
        "AI error:",
        error.response?.data ||
        error.message
      );

      setAnswer(
        "Unable to connect to RazorMind AI."
      );

    } finally {

      setLoading(false);

    }

  };


  // ===================================================
  // LOADING SCREEN
  // ===================================================

  if (controllerLoading) {

    return (

      <div className="loading">

        <div className="loading-card">

          <h1>
            RazorMind
          </h1>

          <p>
            Loading AI-powered payment intelligence...
          </p>

        </div>

      </div>

    );

  }


  // ===================================================
  // CONTROLLER ERROR
  // ===================================================

  if (
    controllerError ||
    !controller
  ) {

    return (

      <div className="loading">

        <div className="loading-card">

          <h1>
            RazorMind
          </h1>

          <p>
            {controllerError ||
              "Unable to load dashboard."}
          </p>

          <button
            onClick={() =>
              loadController(selectedDays)
            }
          >
            Retry
          </button>

        </div>

      </div>

    );

  }


  // ===================================================
  // SAFE DASHBOARD DATA
  // ===================================================

  const risk =
    controller.payment_risk || {};

  const recovery =
    controller.recovery || {};

  const forecast =
    controller.forecast || {};


  // ===================================================
  // RENDER
  // ===================================================

  return (

    <div className="app">


      {/* =================================================
          HEADER
      ================================================= */}

      <header>

        <div>

          <h1>
            RazorMind
          </h1>

          <p>
            AI-Powered Payment Intelligence
          </p>

        </div>

        <div className="status">
          ● System Active
        </div>

      </header>


      {/* =================================================
          ANALYSIS PERIOD
      ================================================= */}

      <div className="analysis-controls">

        <label htmlFor="period">
          Analysis Period
        </label>

        <select
          id="period"
          value={selectedDays}
          onChange={(e) => {

            setSelectedDays(
              Number(e.target.value)
            );

          }}
        >

          <option value={7}>
            Last 7 Days
          </option>

          <option value={14}>
            Last 14 Days
          </option>

          <option value={30}>
            Last 30 Days
          </option>

          <option value={60}>
            Last 60 Days
          </option>

          <option value={90}>
            Last 90 Days
          </option>

        </select>

      </div>


      {/* =================================================
          TOP METRICS
      ================================================= */}

      <section className="metrics">


        {/* FAILURE RATE */}

        <div className="card">

          <span>
            Payment Failure Rate
          </span>

          <h2>

            {Number(
              risk.failure_rate || 0
            ).toFixed(2)}

            %

          </h2>

        </div>


        {/* FAILED TRANSACTIONS */}

        <div className="card">

          <span>
            Failed Transactions
          </span>

          <h2>

            {Number(
              risk.failed_transactions || 0
            ).toLocaleString()}

          </h2>

        </div>


        {/* RECOVERY */}

        <div className="card">

          <span>
            Potential Recovery
          </span>

          <h2>

            ₹
            {Number(
              recovery.potential_recovery || 0
            ).toLocaleString()}

          </h2>

        </div>


        {/* FORECAST */}

        <div className="card">

          <span>
            Avg Daily Forecast
          </span>

          <h2>

            ₹
            {Number(
              forecast.average_daily_revenue || 0
            ).toLocaleString()}

          </h2>

        </div>

      </section>


      {/* =================================================
          MAIN GRID
      ================================================= */}

      <section className="grid">


        {/* =================================================
            PAYMENT RISK
        ================================================= */}

        <div className="panel">

          <h2>
            Payment Risk
          </h2>

          <div className="risk-number">

            {Number(
              risk.failure_rate || 0
            ).toFixed(2)}

            %

          </div>

          <p>
            Failure rate
          </p>

          <hr />

          <p>
            Dominant failure reason
          </p>

          <strong>

            {risk.top_failure_reason ||
              "Unknown"}

          </strong>

          <p>

            {Number(
              risk.top_failure_percentage || 0
            ).toFixed(2)}

            % of failed payments

          </p>

        </div>


        {/* =================================================
            REVENUE RECOVERY
        ================================================= */}

        <div className="panel">

          <h2>
            Revenue Recovery
          </h2>

          <div className="risk-number">

            ₹
            {Number(
              recovery.potential_recovery || 0
            ).toLocaleString()}

          </div>

          <p>
            Potential recoverable revenue
          </p>

          <hr />

          <p>
            High-probability opportunities
          </p>

          <strong>

            {Number(
              recovery.opportunities || 0
            ).toLocaleString()}

          </strong>

        </div>


        {/* =================================================
            RECOMMENDATION
        ================================================= */}

        <div className="panel recommendation">

          <div className="priority">

            {controller.priority ||
              "MEDIUM"}

          </div>

          <h2>

            {controller.title ||
              "Monitor payment performance"}

          </h2>

          <p>

            {controller.recommended_action ||
              "Continue monitoring payment performance."}

          </p>

        </div>


        {/* =================================================
            REVENUE FORECAST
        ================================================= */}

        <div className="panel">

          <h2>
            Revenue Forecast
          </h2>

          <div className="risk-number">

            ₹
            {Number(
              forecast.average_daily_revenue || 0
            ).toLocaleString()}

          </div>

          <p>
            Expected average daily revenue
          </p>

          <hr />

          <p>
            Forecast horizon
          </p>

          <strong>
            7 Days
          </strong>

        </div>


        {/* =================================================
            REVENUE TREND
        ================================================= */}

        <div className="panel chart-panel">

          <h2>
            Revenue Trend
          </h2>

          <p>
            Daily successful payment revenue
          </p>

          <div className="chart-container">

            {revenueData.length === 0 ? (

              <div className="chart-empty">
                No revenue data available
              </div>

            ) : (

              <ResponsiveContainer
                width="100%"
                height={300}
              >

                <LineChart
                  data={revenueData}
                  margin={{
                    top: 10,
                    right: 20,
                    left: 10,
                    bottom: 10
                  }}
                >

                  <CartesianGrid
                    strokeDasharray="3 3"
                  />

                  <XAxis
                    dataKey="date"
                  />

                  <YAxis />

                  <Tooltip
                    formatter={(value) =>
                      `₹${Number(
                        value
                      ).toLocaleString()}`
                    }
                  />

                  <Line
                    type="monotone"
                    dataKey="revenue"
                    stroke="#6366f1"
                    strokeWidth={3}
                    dot={{ r: 4 }}
                    activeDot={{ r: 6 }}
                  />

                </LineChart>

              </ResponsiveContainer>

            )}

          </div>

        </div>


        {/* =================================================
            PAYMENT FAILURE REASONS
        ================================================= */}

        <div className="panel chart-panel">

          <h2>
            Payment Failure Reasons
          </h2>

          <p>
            Distribution of failed payment causes
          </p>

          <div className="chart-container">

            {rootCauseData.length === 0 ? (

              <div className="chart-empty">
                No failure data available
              </div>

            ) : (

              <ResponsiveContainer
                width="100%"
                height={300}
              >

                <PieChart>

                  <Pie
                    data={rootCauseData}
                    dataKey="failures"
                    nameKey="failure_reason"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label
                  >

                    {rootCauseData.map(
                      (entry, index) => (

                        <Cell
                          key={`cell-${index}`}
                          fill={
                            PIE_COLORS[
                              index %
                              PIE_COLORS.length
                            ]
                          }
                        />

                      )
                    )}

                  </Pie>

                  <Tooltip />

                  <Legend />

                </PieChart>

              </ResponsiveContainer>

            )}

          </div>

        </div>

      </section>
      {/* =================================================
    RECOVERY OPPORTUNITIES
================================================= */}

<section className="recovery-section">

  <div className="panel">

    <h2>
      Recovery Opportunities
    </h2>

    <p>
      Failed payments with high predicted
      recovery probability.
    </p>


    {recoveryData.length === 0 ? (

      <div className="chart-empty">
        No recovery opportunities available.
      </div>

    ) : (

      <div className="table-container">

        <table>

          <thead>

            <tr>

              <th>
                Transaction
              </th>

              <th>
                Customer
              </th>

              <th>
                Amount
              </th>

              <th>
                Failure Reason
              </th>

              <th>
                Recovery Probability
              </th>

              <th>
                Potential Recovery
              </th>
              <th>
                Priority
              </th>
            </tr>

          </thead>


          <tbody>

            {recoveryData.map(
              (item, index) => (

                <tr key={index}>

                  <td>
                    {item.transaction_id}
                  </td>

                  <td>
                    {item.customer_id}
                  </td>

                  <td>
                    ₹
                    {Number(
                      item.amount || 0
                    ).toLocaleString()}
                  </td>

                  <td>
                    {item.failure_reason ||
                      "Unknown"}
                  </td>

                  <td>

                    <strong>

                      {Number(
                        item.recovery_probability ||
                        0
                      ).toFixed(2)}
                      %

                    </strong>

                  </td>

                  <td>

                    <strong>

                      ₹
                      {Number(
                        item.potential_recovery ||
                        0
                      ).toLocaleString()}

                    </strong>

                  </td>
                  <td>
                  <span
                    className={`priority-badge ${
                      item.priority?.toLowerCase() || "low"
                    }`}
                  >
                    {item.priority || "LOW"}
                  </span>
                </td>

                </tr>

              )
            )}

          </tbody>

        </table>

      </div>

    )}

  </div>

</section>


      {/* =================================================
          ASK RAZORMIND
      ================================================= */}

      <section className="ai-panel">

        <h2>
          Ask RazorMind
        </h2>

        <p>
          Ask questions about your payment
          and revenue performance.
        </p>


        <div className="ask-box">

          <input

            type="text"

            placeholder="How much revenue can we recover?"

            value={question}

            onChange={(e) =>
              setQuestion(
                e.target.value
              )
            }

            onKeyDown={(e) => {

              if (
                e.key === "Enter"
              ) {

                askRazorMind();

              }

            }}

          />


          <button

            onClick={askRazorMind}

            disabled={loading}

          >

            {loading
              ? "Analyzing..."
              : "Ask"}

          </button>

        </div>


        {/* =================================================
            AI ANSWER
        ================================================= */}

        {answer && (

          <div className="answer">

            <pre>
              {answer}
            </pre>

          </div>

        )}

      </section>


    </div>

  );

}


export default App;