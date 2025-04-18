document.addEventListener("DOMContentLoaded", () => {
  // Track wizard progress
  function updateProgress() {
    const totalSections = document.querySelectorAll('.section-list input[type="checkbox"]').length
    const completedSections = document.querySelectorAll('.section-list input[type="checkbox"]:checked').length
    const progressPercentage = (completedSections / totalSections) * 100

    document.getElementById("wizard-progress").style.width = `${progressPercentage}%`
  }

  // Initialize progress
  updateProgress()

  // Update progress when sections are checked/unchecked
  document.querySelectorAll('.section-list input[type="checkbox"]').forEach((checkbox) => {
    checkbox.addEventListener("change", updateProgress)
  })

  // Handle placeholder highlighting
  function setupPlaceholderHighlighting() {
    document.querySelectorAll(".placeholder").forEach((placeholder) => {
      placeholder.addEventListener("click", function () {
        const field = this.getAttribute("data-field")
        const input = document.getElementById(field)

        if (input) {
          input.focus()
          // Scroll to the input field
          input.scrollIntoView({ behavior: "smooth", block: "center" })
        }
      })
    })
  }

  // Setup placeholder highlighting when a section is loaded
  document.addEventListener("htmx:afterSwap", (event) => {
    if (event.detail.target.id === "section-editor") {
      setupPlaceholderHighlighting()
    }
  })

  // Handle form submission
  document.getElementById("sow-form").addEventListener("htmx:beforeRequest", function (event) {
    // Collect all form data to pass to the preview
    const formData = new FormData(this)

    // Add all checked sections
    document.querySelectorAll('.section-list input[type="checkbox"]:checked').forEach((checkbox) => {
      formData.append("included_sections", checkbox.value)
    })

    // Replace the original request data with our enhanced data
    event.detail.requestConfig.parameters = formData
  })

  // Handle preview rendering
  document.addEventListener("htmx:afterSwap", (event) => {
    if (event.detail.target.id === "preview-container") {
      // Scroll to preview
      document.getElementById("preview-container").scrollIntoView({ behavior: "smooth" })
    }
  })
})
