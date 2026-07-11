document.addEventListener("DOMContentLoaded", () => {

    loadDashboard();
    loadCharts();
    animateCards();

});

async function loadDashboard() {

    try {

        const response = await fetch("/api/dashboard", {
            credentials: "include"
        });

        if (!response.ok) {
            console.error("Failed to load dashboard");
            return;
        }

        const data = await response.json();

        document.getElementById("welcomeUser").textContent =
            `Hello, ${data.user.full_name || data.user.username}`;

        document.getElementById("income").textContent =
            `₹${data.income}`;

        document.getElementById("expense").textContent =
            `₹${data.expense}`;

        document.getElementById("savings").textContent =
            `₹${data.savings}`;

        document.getElementById("health").textContent =
            `${data.health}/100`;

        const status = document.getElementById("healthStatus");

        if (data.health >= 80)
            status.textContent = "Excellent";
        else if (data.health >= 60)
            status.textContent = "Good";
        else if (data.health >= 40)
            status.textContent = "Average";
        else
            status.textContent = "Needs Improvement";

    } catch (error) {
        console.error(error);
    }

}

// ===============================
// Income vs Expense Chart
// ===============================

function loadCharts() {

    const lineCanvas = document.getElementById("lineChart");

    if (lineCanvas) {

        new Chart(lineCanvas, {

            type: "line",

            data: {
                labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                datasets: [{
                    label: "Expenses",
                    data: [18, 22, 20, 25, 23, 21],
                    borderColor: "#2563EB",
                    backgroundColor: "rgba(37,99,235,.2)",
                    fill: true,
                    tension: 0.4
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: true   
            }

        });

    }

    const pieCanvas = document.getElementById("pieChart");

    if (pieCanvas) {

        new Chart(pieCanvas, {

            type: "pie",

            data: {

                labels: [
                    "Food",
                    "Transport",
                    "Shopping",
                    "Bills",
                    "Entertainment"
                ],

                datasets: [{

                    data: [35, 20, 18, 15, 12],

                    backgroundColor: [
                        "#2563EB",
                        "#22C55E",
                        "#F59E0B",
                        "#EF4444",
                        "#8B5CF6"
                    ]

                }]

            },

            options: {
                responsive: true,
                maintainAspectRatio: false
            }

        });

    }

}

// ===============================
// Card Hover Animation
// ===============================

function animateCards() {

    const cards = document.querySelectorAll(".summary-card");

    cards.forEach(card => {

        card.addEventListener("mouseenter", () => {

            card.style.transform = "translateY(-5px)";

        });

        card.addEventListener("mouseleave", () => {

            card.style.transform = "translateY(0px)";

        });

    });

}

const logoutBtn = document.getElementById("logoutBtn");

logoutBtn?.addEventListener("click", async () => {

    await fetch("/auth/logout", {
        method: "POST",
        credentials: "include"
    });

    localStorage.removeItem("user");

    window.location.replace("/login");

});

const uploadBtn = document.getElementById("uploadBtn");

uploadBtn?.addEventListener("click", () => {
    window.location.href = "/upload";
});