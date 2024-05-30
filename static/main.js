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
     const icons = result.icons;
     const tableRows = document.querySelectorAll("tbody tr");
     tableRows.forEach((row, index) => {
         const cell = row.cells[2];
         cell.innerHTML = icons[index];
     });
     const outputScoreElement = document.getElementById("output-score");
     outputScoreElement.innerHTML = `${result.score}<br>${result.result.replace(/ /g, "&nbsp;")}`;
     outputScoreElement.style.display = "flex";
     outputScoreElement.style.flexDirection = "column";
     outputScoreElement.style.justifyContent = "center";
     outputScoreElement.style.alignItems = "center";
 } else {
     document.getElementById("output-text").innerHTML = "Error: " + response.statusText;
 }
});



