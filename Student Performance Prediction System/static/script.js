// Student Performance Predictor - Main JavaScript

// Utility Functions
function formatFeatureName(name) {
  return name.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
}

function showError(message) {
  document.getElementById("errorText").textContent = message;
  document.getElementById("error").classList.remove("hidden");
  document.getElementById("result").classList.add("hidden");
  document.getElementById("loading").classList.add("hidden");
}

function showLoading() {
  document.getElementById("loading").classList.remove("hidden");
  document.getElementById("result").classList.add("hidden");
  document.getElementById("error").classList.add("hidden");
}

function hideLoading() {
  document.getElementById("loading").classList.add("hidden");
}

// Input Validation
function validateSingleInput(input) {
  const min =
    parseFloat(input.getAttribute("min")) ||
    parseFloat(input.getAttribute("data-min"));
  const max =
    parseFloat(input.getAttribute("max")) ||
    parseFloat(input.getAttribute("data-max"));
  const value = parseFloat(input.value);

  // Find or create error element
  let errorElement = input.parentElement.querySelector(".input-error");
  if (!errorElement) {
    errorElement = document.createElement("div");
    errorElement.className = "input-error";
    input.parentElement.appendChild(errorElement);
  }

  // Clear previous error
  input.classList.remove("range-highlight");
  errorElement.classList.remove("show");
  errorElement.textContent = "";

  // Validate
  if (input.value === "") {
    return true; // Allow empty for required validation
  }

  if (isNaN(value)) {
    errorElement.textContent = "Please enter a valid number";
    errorElement.classList.add("show");
    input.classList.add("range-highlight");
    return false;
  }

  if (value < min || value > max) {
    errorElement.textContent = `Value must be between ${min} and ${max}`;
    errorElement.classList.add("show");
    input.classList.add("range-highlight");
    return false;
  }

  return true;
}

function validateAllInputs() {
  let allValid = true;
  const inputs = document.querySelectorAll('input[type="number"]');

  inputs.forEach((input) => {
    if (!validateSingleInput(input)) {
      allValid = false;
    }
  });

  return allValid;
}

// Display Functions
function displayResult(data) {
  // Update prediction badge
  const badge = document.getElementById("predictionBadge");
  badge.textContent = data.prediction;
  badge.className = "prediction-badge " + data.prediction.toLowerCase();

  // Update probability chart
  const chart = document.getElementById("probabilityChart");
  chart.innerHTML = "";

  for (const [category, probability] of Object.entries(data.probabilities)) {
    const bar = document.createElement("div");
    bar.className = "probability-bar-container";
    bar.innerHTML = `
            <div class="probability-label">${category}</div>
            <div class="probability-bar">
                <div class="probability-fill ${category.toLowerCase()}" 
                     style="width: ${probability}"></div>
            </div>
            <div class="probability-value">${probability}</div>
        `;
    chart.appendChild(bar);
  }

  // Update feature summary
  const summary = document.getElementById("featureSummary");
  summary.innerHTML = "";

  for (const [feature, value] of Object.entries(data.features_used)) {
    const div = document.createElement("div");
    div.className = "feature-item";
    div.innerHTML = `
            <span class="feature-name">${formatFeatureName(feature)}</span>
            <span class="feature-value">${value}</span>
        `;
    summary.appendChild(div);
  }

  // Show result
  document.getElementById("result").classList.remove("hidden");
}

// API Functions
async function fetchSampleData() {
  try {
    const response = await fetch("/sample");
    return await response.json();
  } catch (error) {
    showError("Failed to load sample data: " + error.message);
    return null;
  }
}

async function fetchRanges() {
  try {
    const response = await fetch("/ranges");
    return await response.json();
  } catch (error) {
    console.error("Failed to load ranges:", error);
    return null;
  }
}

async function fetchClasses() {
  try {
    const response = await fetch("/classes");
    const data = await response.json();
    return data.classes;
  } catch (error) {
    console.error("Failed to load classes:", error);
    return [];
  }
}

async function submitPrediction(formData) {
  try {
    const response = await fetch("/predict", {
      method: "POST",
      body: new URLSearchParams(formData),
    });

    const data = await response.json();

    if (response.ok) {
      return { success: true, data: data };
    } else {
      return { success: false, error: data.error || "Prediction failed" };
    }
  } catch (error) {
    return { success: false, error: "Network error: " + error.message };
  }
}

// Event Handlers
async function handleFormSubmit(e) {
  e.preventDefault();

  // Validate inputs before submission
  if (!validateAllInputs()) {
    showError("Please fix validation errors before submitting.");
    return;
  }

  showLoading();

  const formData = new FormData(e.target);
  const result = await submitPrediction(formData);

  hideLoading();

  if (result.success) {
    displayResult(result.data);
  } else {
    showError(result.error);
  }
}

async function handleFillSample() {
  const sampleData = await fetchSampleData();
  if (!sampleData) return;

  for (const [key, value] of Object.entries(sampleData)) {
    const element = document.getElementById(key);
    if (element) {
      if (element.tagName === "SELECT") {
        element.value = value.toString();
      } else {
        element.value = value;
      }
      // Trigger validation after setting value
      if (element.type === "number") {
        validateSingleInput(element);
      }
    }
  }
}

function handleValidateInputs() {
  const allValid = validateAllInputs();

  if (allValid) {
    alert("✅ All inputs are within valid ranges!");
  } else {
    alert(
      "⚠️ Some inputs are outside valid ranges. Please check highlighted fields."
    );
  }
}

async function loadRangeSummary() {
  const ranges = await fetchRanges();
  if (!ranges) return;

  const summary = document.getElementById("rangeSummary");
  summary.innerHTML = "";

  for (const [feature, range] of Object.entries(ranges)) {
    const div = document.createElement("div");
    div.className = "range-item";
    div.innerHTML = `
            <strong>${formatFeatureName(feature)}</strong>
            ${range.min} to ${range.max}
        `;
    summary.appendChild(div);
  }
}

// Initialize Event Listeners
function initializeEventListeners() {
  // Form submission
  const form = document.getElementById("predictionForm");
  if (form) {
    form.addEventListener("submit", handleFormSubmit);
  }

  // Sample button
  const fillSampleBtn = document.getElementById("fillSample");
  if (fillSampleBtn) {
    fillSampleBtn.addEventListener("click", handleFillSample);
  }

  // Validate button
  const validateBtn = document.getElementById("validateInputs");
  if (validateBtn) {
    validateBtn.addEventListener("click", handleValidateInputs);
  }

  // Real-time input validation
  document.querySelectorAll('input[type="number"]').forEach((input) => {
    input.addEventListener("input", function () {
      validateSingleInput(this);
    });

    input.addEventListener("blur", function () {
      validateSingleInput(this);
    });
  });

  // Reset button
  const resetBtn = document.querySelector('button[type="reset"]');
  if (resetBtn) {
    resetBtn.addEventListener("click", function () {
      // Clear validation errors
      document.querySelectorAll(".input-error").forEach((el) => {
        el.classList.remove("show");
        el.textContent = "";
      });
      document.querySelectorAll(".range-highlight").forEach((el) => {
        el.classList.remove("range-highlight");
      });
      document.getElementById("result").classList.add("hidden");
      document.getElementById("error").classList.add("hidden");
    });
  }
}

// Initialize the application
async function initializeApp() {
  console.log("Student Performance Predictor initialized");

  // Load range summary
  await loadRangeSummary();

  // Initialize event listeners
  initializeEventListeners();

  // Fetch and log available classes
  const classes = await fetchClasses();
  if (classes.length > 0) {
    console.log("Available prediction classes:", classes);
  }
}

// Start the application when DOM is loaded
document.addEventListener("DOMContentLoaded", initializeApp);
