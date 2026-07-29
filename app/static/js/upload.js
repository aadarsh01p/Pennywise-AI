const form = document.getElementById("uploadForm");

form?.addEventListener("submit", async (e) => {

    e.preventDefault();

    const file = document.getElementById("csvFile").files[0];

    if (!file) {
        alert("Please select a CSV file.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {

        const response = await fetch("/upload/csv", {
            method: "POST",
            credentials: "include",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail);
            return;
        }

        alert(data.message);

        window.location.href = "/dashboard";

    } catch (err) {

        console.log(err);
        alert("Upload Failed");

    }

});