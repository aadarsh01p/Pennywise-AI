const goalContainer = document.getElementById("goalContainer");
const goalSummary = document.getElementById("goalSummary");

const goalId = document.getElementById("goalId");
const goalName = document.getElementById("goalName");
const goalAmount = document.getElementById("goalAmount");
const goalTime = document.getElementById("goalTime");
const goalUnit = document.getElementById("goalUnit");
const goalPriority = document.getElementById("goalPriority");

document
    .getElementById("saveGoalBtn")
    .addEventListener("click", saveGoal);

document.addEventListener("DOMContentLoaded", loadGoals);

async function loadGoals() {

    const data = await fetch("/api/goals").then(r => r.json());

    renderSummary(data);

    renderGoals(data.goals);

}

async function saveGoal() {

    if (!goalName.value || !goalAmount.value || !goalTime.value) {

        console.error("Please fill all fields.");

        return;
    }

    const body = {

        goal_name: goalName.value,

        target_amount: Number(goalAmount.value),

        duration_months:
            Number(goalTime.value) *
            (goalUnit.value === "years" ? 12 : 1),

        priority: goalPriority.value

    };

    await fetch(

        goalId.value
            ? `/api/goals/${goalId.value}`
            : "/api/goals",

        {

            method: goalId.value ? "PUT" : "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify(body)

        }

    );

    clearForm();

    loadGoals();

}

async function deleteGoal(id) {

    if (!confirm("Delete this goal?")) return;

    await fetch(`/api/goals/${id}`, {

        method: "DELETE"

    });

    loadGoals();

}

function renderSummary(data) {

    goalSummary.innerHTML = `

    <div class="d-flex justify-content-between">

        <div>

            <h5>Average Monthly Savings</h5>

            <h3>

                ₹${(data.average_monthly_savings ?? 0).toLocaleString()}

            </h3>

        </div>

        <div>

            <h5>Available Savings</h5>

            <h3>

                ₹${(data.available_savings ?? 0).toLocaleString()}

            </h3>

        </div>

        <div>

            <h5>Active Goals</h5>

            <h3>${data.goals.length}</h3>

        </div>

    </div>

    `;

}

const badge = status => ({

    "Completed": "success",

    "On Schedule": "success",

    "Slight Delay": "warning",

    "Delayed": "danger"

}[status] || "secondary");

function renderGoals(goals) {

    if (!goals.length) {

        goalContainer.innerHTML = `

        <div class="col-12">

            <div class="alert alert-info">

                No goals yet.

            </div>

        </div>`;

        return;

    }

    goalContainer.innerHTML = goals.map(goal => `

    <div class="col-lg-6">

        <div class="card p-4 h-100">

            <div class="d-flex justify-content-between">

                <h4>🎯 ${goal.goal_name}</h4>

                <span class="badge bg-secondary">

                    ${goal.priority}

                </span>

            </div>

            <hr>

            <p>

                <strong>Target</strong><br>

                ₹${goal.target_amount.toLocaleString()}

            </p>

            <p>

                <strong>Current Savings</strong><br>

                ₹${(goal.current_saved ?? 0).toLocaleString()}

            </p>

            <div class="progress mb-3">

                <div

                    class="progress-bar bg-${badge(goal.status)}"

                    style="width:${goal.progress}%">

                    ${goal.progress.toFixed(1)}%

                </div>

            </div>

            <div class="row">

                <div class="col-6">

                    <small>Required / Month</small>

                    <h6>

                        ₹${goal.required_per_month.toLocaleString()}

                    </h6>

                </div>

                <div class="col-6">

                    <small>Allocated / Month</small>

                    <h6>

                        ₹${goal.allocated_per_month.toLocaleString()}

                    </h6>

                </div>

            </div>

            <div class="row mt-3">

                <div class="col-6">

                    <small>Estimated Completion</small>

                    <h6>

                        ${goal.estimated_completion ?? "--"} months

                    </h6>

                </div>

                <div class="col-6">

                    <small>Status</small><br>

                    <span class="badge bg-${badge(goal.status)}">

                        ${goal.status}

                    </span>

                </div>

            </div>

            <div class="d-flex gap-2 mt-4">

                <button

                    class="btn btn-outline-primary flex-fill"

                    onclick='editGoal(${JSON.stringify(goal)})'>

                    Edit

                </button>

                <button

                    class="btn btn-outline-danger flex-fill"

                    onclick="deleteGoal(${goal.id})">

                    Delete

                </button>

            </div>

        </div>

    </div>

    `).join("");

}

function clearForm() {

    goalId.value = "";

    goalName.value = "";

    goalAmount.value = "";

    goalTime.value = "";

    goalPriority.value = "Medium";

    goalUnit.value = "months";

}

function editGoal(goal) {

    goalId.value = goal.id;

    goalName.value = goal.goal_name;

    goalAmount.value = goal.target_amount;

    goalPriority.value = goal.priority;

    goalTime.value = goal.duration_months % 12 === 0
        ? goal.duration_months / 12
        : goal.duration_months;

    goalUnit.value = goal.duration_months % 12 === 0
        ? "years"
        : "months";

    window.scrollTo({

        top: 0,

        behavior: "smooth"

    });

}