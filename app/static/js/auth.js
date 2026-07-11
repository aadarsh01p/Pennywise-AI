const API_URL = "http://127.0.0.1:8000";

// ================= REGISTER =================

const registerForm = document.getElementById("registerForm");

registerForm?.addEventListener("submit", async (e) => {

    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const full_name = document.getElementById("full_name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    if (password !== confirmPassword)
        return alert("Passwords do not match.");

    try {

        const response = await fetch(`${API_URL}/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                username,
                full_name,
                email,
                password
            })
        });

        const data = await response.json();

        if (!response.ok)
            return alert(data.detail);

        alert("Registration Successful!");
        window.location.href = "/login";

    } catch (err) {

        console.log(err);
        alert("Server Error");

    }

});


// ================= LOGIN =================

const loginForm = document.getElementById("loginForm");

loginForm?.addEventListener("submit", async (e) => {

    e.preventDefault();

    const username_or_email =
        document.getElementById("username_or_email").value.trim();

    const password =
        document.getElementById("password").value;

    try {

        const response = await fetch(`${API_URL}/auth/login`, {

            method: "POST",
            credentials: "include",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                username_or_email,
                password
            })

        });

        const data = await response.json();

        if (!response.ok)
            return alert(data.detail);

        localStorage.setItem(
            "user",
            JSON.stringify(data.user)
        );

        alert("Login Successful!");

        window.location.href = "/dashboard";

    } catch (err) {

        console.log(err);
        alert("Server Error");

    }

});


// ================= FORGOT PASSWORD =================

const forgotBtn = document.getElementById("forgotPasswordBtn");
const modal = document.getElementById("forgotModal");
const closeModal = document.getElementById("closeModal");

forgotBtn?.addEventListener("click", e => {

    e.preventDefault();

    modal.style.display = "flex";

});

closeModal?.addEventListener("click", () => {

    modal.style.display = "none";

});

window.onclick = e => {

    if (e.target === modal)
        modal.style.display = "none";

};


// ================= SEND OTP =================

const sendOtpBtn = document.getElementById("sendOtpBtn");

sendOtpBtn?.addEventListener("click", async () => {

    const email = document.getElementById("resetEmail").value;

    const res = await fetch(`${API_URL}/auth/send-otp`, {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({ email })

    });

    const data = await res.json();

    alert(data.message);

    if (!res.ok)
        return;

    document.getElementById("otp").style.display = "block";
    document.getElementById("newPassword").style.display = "block";
    document.getElementById("confirmNewPassword").style.display = "block";
    document.getElementById("resetPasswordBtn").style.display = "block";

    sendOtpBtn.style.display = "none";

});

// ================= RESET PASSWORD =================

const resetBtn = document.getElementById("resetPasswordBtn");

resetBtn?.addEventListener("click", async () => {

    const email = document.getElementById("resetEmail").value;
    const otp = document.getElementById("otp").value;
    const newPassword = document.getElementById("newPassword").value;
    const confirmPassword = document.getElementById("confirmNewPassword").value;

    if (newPassword !== confirmPassword)
        return alert("Passwords do not match.");

    const res = await fetch(`${API_URL}/auth/reset-password`, {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            email,
            otp,
            new_password: newPassword
        })

    });

    const data = await res.json();

    alert(data.message || data.detail);

    if (!res.ok)
        return;

    modal.style.display = "none";

    document.getElementById("resetEmail").value = "";
    document.getElementById("otp").value = "";
    document.getElementById("newPassword").value = "";
    document.getElementById("confirmNewPassword").value = "";

    sendOtpBtn.style.display = "block";

    document.getElementById("otp").style.display = "none";
    document.getElementById("newPassword").style.display = "none";
    document.getElementById("confirmNewPassword").style.display = "none";
    resetBtn.style.display = "none";

});