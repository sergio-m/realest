// Custom JavaScript for Real Estate Analyzer

document.addEventListener("DOMContentLoaded", () => {
  console.log("Real Estate Analyzer frontend loaded ✅");

  // Example: highlight investment score cells
  document.querySelectorAll("td").forEach(td => {
    if (td.innerText.includes("/100")) {
      let val = parseFloat(td.innerText);
      if (val >= 70) td.classList.add("score-high");
      else if (val >= 50) td.classList.add("score-medium");
      else td.classList.add("score-low");
    }
  });
});