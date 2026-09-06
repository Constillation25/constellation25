console.log("$REPO frontend loaded");

async function fetchHealth() {
    try {
        const response = await fetch("/health");
        const data = await response.json();
        document.getElementById("app").innerHTML = 
            "<pre>" + JSON.stringify(data, null, 2) + "</pre>";
    } catch (error) {
        console.error("Health check failed:", error);
    }
}

fetchHealth();
