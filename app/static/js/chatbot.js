document.addEventListener("DOMContentLoaded", () => {

    const chatMessages = document.getElementById("chatMessages");
    const chatInput = document.getElementById("chatInput");
    const sendMessageBtn = document.getElementById("sendMessageBtn");
    const typingIndicator = document.getElementById("typingIndicator");
    const logoutBtn = document.getElementById("logoutBtn");

    // Add User Message
    function addUserMessage(message) {
        const messageWrapper = document.createElement("div");

        messageWrapper.className = "chat-message user-message";

        messageWrapper.innerHTML = `
            <div class="message-content">
                <div class="message-name">You</div>
                <div class="message-bubble">${escapeHtml(message)}</div>
            </div>
            <div class="message-avatar user-avatar">
                <i class="bi bi-person-fill"></i>
            </div>
        `;

        chatMessages.appendChild(messageWrapper);
        scrollToBottom();
    }

    // Add AI Message
    function addAIMessage(message) {
        const messageWrapper = document.createElement("div");

        messageWrapper.className = "chat-message ai-message";

        messageWrapper.innerHTML = `
            <div class="message-avatar">
                <i class="bi bi-robot"></i>
            </div>
            <div class="message-content">
                <div class="message-name">PennyWise AI</div>
                <div class="message-bubble">${formatAIResponse(message)}</div>
            </div>
        `;

        chatMessages.appendChild(messageWrapper);
        scrollToBottom();
    }

    // Format AI Response
    function formatAIResponse(message) {
        if (!message) {
            return "I couldn't generate a response.";
        }

        return escapeHtml(message)
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\n/g, "<br>");
    }

    // Prevent HTML Injection
    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    // Scroll Chat
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Typing Indicator
    function showTyping() {
        typingIndicator.classList.add("show");
        scrollToBottom();
    }

    function hideTyping() {
        typingIndicator.classList.remove("show");
    }

    // Send Message
    async function sendMessage() {
        const message = chatInput.value.trim();

        if (!message) {
            return;
        }

        addUserMessage(message);
        chatInput.value = "";
        sendMessageBtn.disabled = true;
        showTyping();

        try {
            const response = await fetch("/api/ai/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                credentials: "include",
                body: JSON.stringify({
                    message: message
                })
            });

            const data = await response.json();

            if (!response.ok) {
                if (response.status === 401) {
                    addAIMessage(
                        "Your session has expired. Please log in again."
                    );
                    return;
                }

                throw new Error(
                    data.detail || "Something went wrong."
                );
            }

            addAIMessage(data.response);

        } catch (error) {
            console.error("Chatbot Error:", error);

            addAIMessage(
                "Sorry, I couldn't connect to PennyWise AI right now. Please try again."
            );

        } finally {
            hideTyping();
            sendMessageBtn.disabled = false;
            chatInput.focus();
        }
    }

    // Send Button
    sendMessageBtn.addEventListener("click", sendMessage);

    // Enter Key
    chatInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });

    // Suggested Questions
    document.querySelectorAll(".suggestion-btn").forEach(button => {
        button.addEventListener("click", () => {
            const question = button.dataset.question;

            chatInput.value = question;
            sendMessage();
        });
    });

    // Logout
    if (logoutBtn) {
        logoutBtn.addEventListener("click", async () => {

            try {
                await fetch("/api/auth/logout", {
                    method: "POST",
                    credentials: "include"
                });

            } catch (error) {
                console.error("Logout error:", error);
            }

            window.location.href = "/login";
        });
    }

    // Focus Input
    chatInput.focus();
});