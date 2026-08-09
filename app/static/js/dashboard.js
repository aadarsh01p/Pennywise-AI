document.addEventListener("DOMContentLoaded", loadDashboard);

let lineChart = null;
let pieChart = null;


// =====================
// Load Dashboard
// =====================

async function loadDashboard() {

    try {

        // Always request fresh dashboard data
        const res = await fetch(`/api/dashboard?_=${Date.now()}`, {
            method: "GET",
            credentials: "include",
            cache: "no-store"
        });

        if (!res.ok) {
            throw new Error(`Dashboard request failed: ${res.status}`);
        }

        const data = await res.json();

        console.log("Fresh dashboard data:", data);


        // =====================
        // Cards
        // =====================

        if (welcomeUser && data.user) {
            welcomeUser.textContent =
                `Hello, ${data.user.full_name || data.user.username}`;
        }

        if (income) {
            income.textContent = `₹${Number(data.income || 0).toLocaleString("en-IN")}`;
        }

        if (expense) {
            expense.textContent = `₹${Number(data.expense || 0).toLocaleString("en-IN")}`;
        }

        if (savings) {
            savings.textContent = `₹${Number(data.savings || 0).toLocaleString("en-IN")}`;
        }

        if (health) {
            health.textContent = `${data.health || 0}/100`;
        }


        // =====================
        // Health Status
        // =====================

        if (healthStatus) {

            const score = Number(data.health || 0);

            healthStatus.textContent =
                score >= 80 ? "Excellent" :
                score >= 60 ? "Good" :
                score >= 40 ? "Average" :
                "Needs Improvement";
        }


        // =====================
        // Monthly Expenses Chart
        // =====================

        if (lineChartCanvas) {

            lineChart?.destroy();

            const monthlyData = Array.isArray(data.monthly)
                ? data.monthly
                : [];

            lineChart = new Chart(lineChartCanvas, {

                type: "line",

                data: {

                    labels: monthlyData.map(item => item.month),

                    datasets: [{

                        label: "Expenses",

                        data: monthlyData.map(item =>
                            Number(item.expense || 0)
                        ),

                        borderColor: "#2563EB",

                        backgroundColor: "rgba(37, 99, 235, 0.15)",

                        fill: true,

                        tension: 0.4,

                        borderWidth: 3,

                        pointRadius: 4,

                        pointHoverRadius: 6
                    }]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {
                            display: true
                        }

                    },

                    scales: {

                        y: {

                            beginAtZero: true,

                            ticks: {

                                callback: function(value) {
                                    return "₹" +
                                        Number(value).toLocaleString("en-IN");
                                }

                            }

                        }

                    }

                }

            });
        }


        // =====================
        // Expense Categories
        // =====================

        if (pieChartCanvas) {

            pieChart?.destroy();

            const categories =
                data.categories &&
                typeof data.categories === "object"
                    ? data.categories
                    : {};

            pieChart = new Chart(pieChartCanvas, {

                type: "pie",

                data: {

                    labels: Object.keys(categories),

                    datasets: [{

                        data: Object.values(categories),

                        backgroundColor: [

                            "#2563EB",
                            "#22C55E",
                            "#F59E0B",
                            "#EF4444",
                            "#8B5CF6",
                            "#14B8A6",
                            "#EC4899",
                            "#F97316"

                        ]

                    }]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {
                            position: "bottom"
                        }

                    }

                }

            });
        }


    } catch (err) {

        console.error("Dashboard loading error:", err);

    }

}


// =====================
// Logout
// =====================

logoutBtn?.addEventListener("click", async () => {

    try {

        await fetch("/auth/logout", {
            method: "POST",
            credentials: "include"
        });

    } catch (err) {

        console.error("Logout error:", err);

    }

    localStorage.removeItem("user");

    location.replace("/login");

});


// =====================
// Upload CSV
// =====================

uploadBtn?.addEventListener("click", () => {

    location.href = "/upload";

});