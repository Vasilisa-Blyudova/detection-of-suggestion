document.getElementById("analyze-button").addEventListener("click", async function() {
    const inputText = document.getElementById("input-text").value;
    const response = await fetch("/analyze-text/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
            text: inputText
        })
    });
    if (response.ok) {
        const result = await response.json();
        document.getElementById("output-text").innerHTML = result.result_text;
    } else {
        document.getElementById("output-text").innerHTML = "Error: " + response.statusText;
    }
});

