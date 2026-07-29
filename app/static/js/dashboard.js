document.addEventListener("DOMContentLoaded", loadDashboard);

let lineChart, pieChart;

async function loadDashboard() {

    try {

        const res = await fetch("/api/dashboard", {
            credentials: "include"
        });

        const data = await res.json();

        // =====================
        // Cards
        // =====================

        welcomeUser.textContent =
            `Hello, ${data.user.full_name || data.user.username}`;

        income.textContent = `₹${data.income}`;
        expense.textContent = `₹${data.expense}`;
        savings.textContent = `₹${data.savings}`;
        health.textContent = `${data.health}/100`;

        healthStatus.textContent =
            data.health >= 80 ? "Excellent" :
            data.health >= 60 ? "Good" :
            data.health >= 40 ? "Average" :
            "Needs Improvement";

        // =====================
        // Monthly Chart
        // =====================

        lineChart?.destroy();

        lineChart = new Chart(lineChartCanvas, {

            type: "line",

            data: {

                labels: data.monthly.map(m => m.month),

                datasets: [{

                    label: "Expenses",

                    data: data.monthly.map(m => m.expense),

                    borderColor: "#2563EB",

                    backgroundColor: "rgba(37,99,235,.15)",

                    fill: true,

                    tension: .4

                }]

            }

        });

        // =====================
        // Pie Chart
        // =====================

        pieChart?.destroy();

        pieChart = new Chart(pieChartCanvas, {

            type: "pie",

            data: {

                labels: Object.keys(data.categories),

                datasets: [{

                    data: Object.values(data.categories),

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

            }

        });

    }

    catch (err) {

        console.error(err);

    }

}

// =====================
// Logout
// =====================

logoutBtn?.addEventListener("click", async () => {

    await fetch("/auth/logout", {
        method: "POST",
        credentials: "include"
    });

    localStorage.removeItem("user");

    location.replace("/login");

});

// =====================
// Upload
// =====================

uploadBtn?.addEventListener("click", () => {

    location.href = "/upload";

});
