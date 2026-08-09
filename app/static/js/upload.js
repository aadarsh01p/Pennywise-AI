document.addEventListener("DOMContentLoaded", function () {

    console.log("PennyWise upload.js loaded");

    /* =========================
    LOGOUT
    ========================= */

    const logoutBtn = document.getElementById("logoutBtn");

    if (logoutBtn) {

        logoutBtn.addEventListener("click", function () {

            localStorage.removeItem("access_token");
            localStorage.removeItem("token");

            window.location.href = "/login";

        });

    }
    const form = document.getElementById("uploadForm");
    const fileInput = document.getElementById("csvFile");
    const uploadButton = document.getElementById("uploadBtn");
    const uploadStatus = document.getElementById("uploadStatus");


    /* =========================
       CHECK REQUIRED ELEMENTS
    ========================= */

    if (!form) {
        console.error("ERROR: uploadForm was not found.");
        return;
    }

    if (!fileInput) {
        console.error("ERROR: csvFile was not found.");
        return;
    }

    console.log("Upload form connected successfully.");


    /* =========================
       STATUS MESSAGE
    ========================= */

    function showStatus(message, type) {

        if (!uploadStatus) {
            return;
        }

        uploadStatus.textContent = message;

        uploadStatus.className =
            "upload-status " + type;

        uploadStatus.style.display = "block";
    }


    /* =========================
       FORM SUBMISSION
    ========================= */

    form.addEventListener("submit", async function (event) {

        event.preventDefault();
        event.stopPropagation();


        /* =========================
           CHECK FILE
        ========================= */

        const file = fileInput.files[0];

        if (!file) {

            showStatus(
                "Please select a CSV file.",
                "error"
            );

            return;
        }


        /* =========================
           CHECK FILE TYPE
        ========================= */

        if (!file.name.toLowerCase().endsWith(".csv")) {

            showStatus(
                "Please select a CSV file.",
                "error"
            );

            return;
        }


        /* =========================
           PREPARE FORM DATA
        ========================= */

        const formData = new FormData();

        formData.append("file", file);


        try {

            /* =========================
               LOADING STATE
            ========================= */

            if (uploadButton) {

                uploadButton.disabled = true;

                uploadButton.innerHTML =
                    '<i class="bi bi-arrow-repeat"></i> Uploading...';
            }

            showStatus(
                "Uploading CSV...",
                "loading"
            );


            /* =========================
               SEND CSV TO BACKEND
            ========================= */

            const response = await fetch(
                "/upload/csv",
                {
                    method: "POST",
                    credentials: "include",
                    body: formData
                }
            );


            /* =========================
               READ RESPONSE
            ========================= */

            const contentType =
                response.headers.get("content-type") || "";

            let data = {};

            if (contentType.includes("application/json")) {

                data = await response.json();

            } else {

                const text = await response.text();

                throw new Error(
                    text || "CSV upload failed."
                );
            }


            console.log(
                "Upload response:",
                data
            );


            /* =========================
               HANDLE BACKEND ERROR
            ========================= */

            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "CSV upload failed."
                );
            }


            /* =========================
               SUCCESS
            ========================= */

            showStatus(
                "CSV uploaded successfully",
                "success"
            );


            /* =========================
               SUCCESS BUTTON STATE
            ========================= */

            if (uploadButton) {

                uploadButton.innerHTML =
                    '<i class="bi bi-check-circle"></i> Uploaded';

            }


            /* =========================
               GO TO DASHBOARD
            ========================= */

            setTimeout(() => {

                window.location.replace(
                    "/dashboard"
                );

            }, 1000);


        } catch (error) {

            console.error(
                "Upload error:",
                error
            );


            /* =========================
               ERROR MESSAGE
            ========================= */

            showStatus(
                error.message ||
                "Upload failed. Please try again.",
                "error"
            );


            /* =========================
               RESET BUTTON
            ========================= */

            if (uploadButton) {

                uploadButton.disabled = false;

                uploadButton.innerHTML =
                    '<i class="bi bi-upload"></i> Upload CSV';
            }

        }

    });

});