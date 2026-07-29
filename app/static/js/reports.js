document.addEventListener("DOMContentLoaded", () => {
    loadReport();
});

async function loadReport() {

    const res = await fetch("/api/reports/", {
        credentials: "include"
    });

    const data = await res.json();

    // Summary
    document.getElementById("income").textContent = `₹${data.income}`;
    document.getElementById("expense").textContent = `₹${data.expense}`;
    document.getElementById("savings").textContent = `₹${data.savings}`;

    // Category Table
    document.getElementById("categoryTable").innerHTML =
        data.categories.map(c => `
            <tr>
                <td>${c.category}</td>
                <td>₹${c.amount}</td>
            </tr>
        `).join("");

    // Top Expenses
    document.getElementById("expenseTable").innerHTML =
        data.top_expenses.map(t => `
            <tr>
                <td>${t.date}</td>
                <td>${t.description}</td>
                <td>${t.category}</td>
                <td>₹${t.amount}</td>
            </tr>
        `).join("");

    // AI Insights
    document.getElementById("insightsList").innerHTML =
        data.insights.map(i => `<li>${i}</li>`).join("");

    drawLineChart(data.monthly);
    drawPieChart(data.categories);
}

function drawLineChart(monthly) {

    new Chart(document.getElementById("lineChart"), {

        type: "line",

        data: {
            labels: monthly.map(m => m.month),
            datasets: [{
                label: "Expenses",
                data: monthly.map(m => m.amount),
                borderColor: "#2563EB",
                backgroundColor: "rgba(37,99,235,.2)",
                fill: true,
                tension: .4
            }]
        }

    });

}

function drawPieChart(categories) {

    new Chart(document.getElementById("pieChart"), {

        type: "pie",

        data: {

            labels: categories.map(c => c.category),

            datasets: [{

                data: categories.map(c => c.amount)

            }]

        }

    });

}

document.getElementById("downloadBtn")?.addEventListener("click", () => {

    window.location.href = "/api/reports/pdf";

});

document.getElementById("logoutBtn")?.addEventListener("click", async () => {

    await fetch("/auth/logout", {
        method: "POST",
        credentials: "include"
    });

    window.location.replace("/login");

});