document.addEventListener("DOMContentLoaded", function () {

    console.log("PennyWise upload.js loaded");


    /* =========================
       LOGOUT
    ========================= */

    const logoutBtn =
        document.getElementById("logoutBtn");

    if (logoutBtn) {

        logoutBtn.addEventListener(
            "click",
            function () {

                localStorage.removeItem(
                    "access_token"
                );

                localStorage.removeItem(
                    "token"
                );

                window.location.href =
                    "/login";
            }
        );
    }


    /* =========================
       ELEMENTS
    ========================= */

    const form =
        document.getElementById("uploadForm");

    const fileInput =
        document.getElementById("csvFile");

    const uploadButton =
        document.getElementById("uploadBtn");

    const uploadStatus =
        document.getElementById("uploadStatus");

    const csvLoader =
        document.getElementById("csvLoader");

    const coinSymbol =
        document.getElementById("coinSymbol");

    const loaderText =
        document.getElementById("loaderText");


    /* =========================
       CHECK REQUIRED ELEMENTS
    ========================= */

    if (!form) {

        console.error(
            "ERROR: uploadForm was not found."
        );

        return;
    }


    if (!fileInput) {

        console.error(
            "ERROR: csvFile was not found."
        );

        return;
    }


    console.log(
        "Upload form connected successfully."
    );


    /* =========================
       WAIT HELPER
    ========================= */

    function wait(ms) {

        return new Promise(
            resolve =>
                setTimeout(
                    resolve,
                    ms
                )
        );
    }


    /* =========================
       STATUS MESSAGE
    ========================= */

    function showStatus(
        message,
        type
    ) {

        if (!uploadStatus) {
            return;
        }

        uploadStatus.textContent =
            message;

        uploadStatus.className =
            "upload-status " + type;

        uploadStatus.style.display =
            "block";
    }


    /* =========================
       RESET LOADER
    ========================= */

    function resetLoader() {

        if (csvLoader) {

            csvLoader.classList.remove(
                "success"
            );
        }


        if (coinSymbol) {

            coinSymbol.textContent = "₹";
        }


        if (loaderText) {

            loaderText.innerHTML = `
                Processing your statement

                <span class="loading-dots">
                    <span>.</span>
                    <span>.</span>
                    <span>.</span>
                </span>
            `;
        }
    }


    /* =========================
       SHOW LOADER
    ========================= */

    async function showLoader() {

        resetLoader();


        if (csvLoader) {

            csvLoader.classList.add(
                "active"
            );
        }


        /*
         * Give browser time to
         * render loader animation.
         */

        await new Promise(
            resolve =>

                requestAnimationFrame(
                    () =>

                        requestAnimationFrame(
                            resolve
                        )
                )
        );
    }


    /* =========================
       SUCCESS ANIMATION
    ========================= */

    async function showSuccess() {

        /*
         * Stop normal loader animation
         * and activate success styling.
         */

        if (csvLoader) {

            csvLoader.classList.add(
                "success"
            );
        }


        /*
         * Change ₹ to ✓
         */

        if (coinSymbol) {

            coinSymbol.textContent = "✓";
        }


        /*
         * Change loader message
         */

        if (loaderText) {

            loaderText.textContent =
                "Statement uploaded successfully";
        }


        /*
         * Keep success visible
         */

        await wait(1800);
    }


    /* =========================
       HIDE LOADER
    ========================= */

    function hideLoader() {

        if (!csvLoader) {
            return;
        }


        csvLoader.classList.remove(
            "active",
            "success"
        );
    }


    /* =========================
       RESET UPLOAD BUTTON
    ========================= */

    function resetUploadButton() {

        if (!uploadButton) {
            return;
        }


        uploadButton.disabled = false;


        uploadButton.innerHTML = `
            <i class="bi bi-upload"></i>
            Upload CSV
        `;
    }


    /* =========================
       FORM SUBMISSION
    ========================= */

    form.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            event.stopPropagation();


            /* =========================
               GET FILE
            ========================= */

            const file =
                fileInput.files[0];


            /* =========================
               CHECK FILE
            ========================= */

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

            if (
                !file.name
                    .toLowerCase()
                    .endsWith(".csv")
            ) {

                showStatus(
                    "Please select a valid CSV file.",
                    "error"
                );

                return;
            }


            /* =========================
               PREPARE FORM DATA
            ========================= */

            const formData =
                new FormData();


            formData.append(
                "file",
                file
            );


            try {

                /* =========================
                   BUTTON LOADING STATE
                ========================= */

                if (uploadButton) {

                    uploadButton.disabled =
                        true;


                    uploadButton.innerHTML = `
                        <i class="bi bi-arrow-repeat"></i>
                        Uploading...
                    `;
                }


                /* =========================
                   HIDE OLD STATUS
                ========================= */

                if (uploadStatus) {

                    uploadStatus.style.display =
                        "none";
                }


                /* =========================
                   SHOW ₹ LOADER
                ========================= */

                await showLoader();


                const loaderStartTime =
                    Date.now();


                /* =========================
                   SEND CSV TO BACKEND
                ========================= */

                const response =
                    await fetch(
                        "/upload/csv",
                        {
                            method: "POST",

                            credentials:
                                "include",

                            body:
                                formData
                        }
                    );


                /* =========================
                   READ RESPONSE
                ========================= */

                const contentType =
                    response.headers.get(
                        "content-type"
                    ) || "";


                let data = {};


                if (
                    contentType.includes(
                        "application/json"
                    )
                ) {

                    data =
                        await response.json();

                } else {

                    const text =
                        await response.text();


                    throw new Error(

                        text ||

                        "CSV upload failed."

                    );
                }


                console.log(
                    "Upload response:",
                    data
                );


                /* =========================
                   BACKEND ERROR
                ========================= */

                if (!response.ok) {

                    throw new Error(

                        data.detail ||

                        data.message ||

                        "CSV upload failed."

                    );
                }


                /* =========================
                   MINIMUM LOADER TIME
                ========================= */

                const minimumLoaderTime =
                    3000;


                const elapsedTime =

                    Date.now() -

                    loaderStartTime;


                if (
                    elapsedTime <
                    minimumLoaderTime
                ) {

                    await wait(

                        minimumLoaderTime -

                        elapsedTime

                    );
                }


                /* =========================
                   SUCCESS
                   ₹ → ✓
                ========================= */

                await showSuccess();


                /* =========================
                   HIDE LOADER
                ========================= */

                hideLoader();


                /* =========================
                   REDIRECT
                ========================= */

                window.location.replace(
                    "/dashboard"
                );


            } catch (error) {

                console.error(
                    "Upload error:",
                    error
                );


                /* =========================
                   HIDE LOADER
                ========================= */

                hideLoader();


                resetLoader();


                /* =========================
                   SHOW ERROR
                ========================= */

                showStatus(

                    error.message ||

                    "Upload failed. Please try again.",

                    "error"

                );


                /* =========================
                   RESET BUTTON
                ========================= */

                resetUploadButton();

            }

        }
    );

});