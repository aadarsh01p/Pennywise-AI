document.addEventListener("DOMContentLoaded", () => {
    loadBudget();

    document
        .getElementById("generateBtn")
        ?.addEventListener("click", generateBudget);

    document
        .getElementById("saveBtn")
        ?.addEventListener("click", saveBudget);

    document
        .getElementById("logoutBtn")
        ?.addEventListener("click", logout);
});

async function loadBudget() {

    const res = await fetch("/api/budget/", {
        credentials: "include"
    });

    const data = await res.json();

    const tbody = document.getElementById("budgetTable");

    tbody.innerHTML = "";

    if (!data.categories.length) {

        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-muted py-4">
                    No budget generated yet.
                </td>
            </tr>
        `;

    } else {

        data.categories.forEach(category => {

            tbody.innerHTML += `
                <tr>

                    <td>${category.category}</td>

                    <td>₹${category.average_spend.toFixed(0)}</td>

                    <td>
                        <input
                            class="form-control budget-input"
                            data-category="${category.category}"
                            value="${category.budget.toFixed(0)}">
                    </td>

                    <td>${formatDifference(category.difference)}</td>

                    <td>${statusBadge(category.status)}</td>

                </tr>
            `;

        });

    }

    const button = document.getElementById("generateBtn");

    button.innerHTML = data.has_budget
        ? `<i class="bi bi-arrow-repeat"></i> Regenerate AI Budget`
        : `<i class="bi bi-stars"></i> Generate AI Budget`;
}

function statusBadge(status) {

    switch (status) {

        case "Good":
            return `<span class="badge bg-success">Good</span>`;

        case "On Track":
            return `<span class="badge bg-warning text-dark">On Track</span>`;

        case "Reduce":
            return `<span class="badge bg-danger">Reduce</span>`;

        default:
            return `<span class="badge bg-secondary">Fixed</span>`;
    }

}

function formatDifference(value) {

    if (value > 0)
        return `<span class="text-success">+₹${value.toFixed(0)}</span>`;

    if (value < 0)
        return `<span class="text-danger">-₹${Math.abs(value).toFixed(0)}</span>`;

    return "₹0";
}

async function generateBudget() {

    const button = document.getElementById("generateBtn");

    button.disabled = true;

    button.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2"></span>
        Generating...
    `;

    await fetch("/api/budget/generate", {
        method: "POST",
        credentials: "include"
    });

    button.disabled = false;

    loadBudget();
}

async function saveBudget() {

    const rows = document.querySelectorAll(".budget-input");

    for (const row of rows) {

        await fetch("/api/budget/", {

            method: "PUT",

            credentials: "include",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                category: row.dataset.category,

                budget_amount: Number(row.value)

            })

        });

    }

    loadBudget();
}

async function logout() {

    await fetch("/auth/logout", {

        method: "POST",

        credentials: "include"

    });

    window.location.replace("/login");
}