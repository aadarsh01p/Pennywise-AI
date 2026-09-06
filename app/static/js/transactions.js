console.log("transactions.js loaded");
const API_URL = "http://127.0.0.1:8000";

// =========================
// Load Transactions
// =========================
async function loadTransactions() {
    console.log("Loading transactions...");
    try {

        const response = await fetch(`${API_URL}/api/transactions/`);

        const transactions = await response.json();
        console.log(transactions);
        const table = document.getElementById("transactionTable");

        table.innerHTML = "";

        transactions.forEach(transaction => {

            table.innerHTML += `
                <tr>
                    <td>${transaction.date}</td>
                    <td>${transaction.description}</td>
                    <td>${transaction.category}</td>
                    <td>₹${transaction.amount}</td>
                    <td>
                        <button onclick="deleteTransaction(${transaction.id})">
                            Delete
                        </button>
                    </td>
                </tr>
            `;

        });

    } catch (error) {

        console.error(error);

    }

}

// =========================
// Open Modal
// =========================
function openModal() {

    document.getElementById("transactionModal").style.display = "flex";

}

// =========================
// Close Modal
// =========================
function closeModal() {

    document.getElementById("transactionModal").style.display = "none";

}

// =========================
// Add Transaction
// =========================
const form = document.getElementById("transactionForm");

if (form) {

    form.addEventListener("submit", async function (e) {

        e.preventDefault();

        const transaction = {

            date: document.getElementById("date").value,

            description: document.getElementById("description").value,

            amount: Number(document.getElementById("amount").value),

            transaction_type: document.getElementById("transaction_type").value,

        };

        try {

            const response = await fetch(`${API_URL}/api/transactions/`, {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(transaction)

            });

            if (response.ok) {

                closeModal();

                form.reset();

                loadTransactions();

            }

            else {

    const error = await response.text();

    console.error(error);

}

        }

        catch (error) {

            console.error(error);

        }

    });

}

// =========================
// Delete Transaction
// =========================
async function deleteTransaction(id) {

    if (!confirm("Delete this transaction?")) return;

    await fetch(`${API_URL}/api/transactions/${id}`, {

        method: "DELETE"

    });

    loadTransactions();

}

// =========================
// Load on Page Start
// =========================
window.onload = loadTransactions;