// CrimeSense Main JavaScript

// Import Bootstrap
import bootstrap from "bootstrap"

document.addEventListener("DOMContentLoaded", () => {
  // Initialize tooltips
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  var tooltipList = tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl))

  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault()
      const target = document.querySelector(this.getAttribute("href"))
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        })
      }
    })
  })

  // Form validation and submission
  const contactForm = document.querySelector("#contact form")
  if (contactForm) {
    contactForm.addEventListener("submit", function (e) {
      const submitBtn = this.querySelector('button[type="submit"]')
      const originalText = submitBtn.innerHTML

      // Show loading state
      submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Sending...'
      submitBtn.disabled = true

      // Reset after 3 seconds (form will redirect anyway)
      setTimeout(() => {
        submitBtn.innerHTML = originalText
        submitBtn.disabled = false
      }, 3000)
    })
  }

  // Auto-hide alerts after 5 seconds
  const alerts = document.querySelectorAll(".alert")
  alerts.forEach((alert) => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert)
      bsAlert.close()
    }, 5000)
  })

  // Carousel auto-play control
  const carousel = document.querySelector("#heroCarousel")
  if (carousel) {
    const bsCarousel = new bootstrap.Carousel(carousel, {
      interval: 5000,
      wrap: true,
    })

    // Pause on hover
    carousel.addEventListener("mouseenter", () => {
      bsCarousel.pause()
    })

    carousel.addEventListener("mouseleave", () => {
      bsCarousel.cycle()
    })
  }

  // Add fade-in animation to cards when they come into view
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("fade-in")
      }
    })
  }, observerOptions)

  // Observe all cards
  document.querySelectorAll(".card").forEach((card) => {
    observer.observe(card)
  })
})

// Download tracking (for analytics)
function trackDownload(platform) {
  console.log(`Download initiated for ${platform}`)
  // Add your analytics tracking code here
  // Example: gtag('event', 'download', { 'platform': platform });
}

// Add click tracking to download buttons
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('a[href*="download"]').forEach((link) => {
    link.addEventListener("click", function () {
      const platform = this.href.includes("ios") ? "iOS" : "Android"
      trackDownload(platform)
    })
  })
})
