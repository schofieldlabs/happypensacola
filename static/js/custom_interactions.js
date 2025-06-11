document.addEventListener("DOMContentLoaded", function () {
  function isMobile() {
    return window.innerWidth < 992;
  }

  // This function highlights navigation items on mouse over/out
  window.highlightNav = function (navItemId) {
    document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('hovered'));
    if (!navItemId) return;
    const navItem = document.getElementById(navItemId);
    if (navItem) {
      const link = navItem.querySelector('.nav-link');
      if (link) link.classList.add('hovered');
    }
  };

  // This function is called by the clickable overlays on your landing page
  window.triggerDropdown = function (navItemId) {
    const navItem = document.getElementById(navItemId);
    
    if (!navItem) {
      console.error("navItem not found for:", navItemId);
      return;
    }

    if (isMobile()) {
      navItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }

    const toggle = navItem.querySelector('[data-bs-toggle="dropdown"]');
    if (toggle) {
      // Ensure Bootstrap's Dropdown is fully initialized before attempting to use it
      if (typeof bootstrap !== 'undefined' && typeof bootstrap.Dropdown !== 'undefined') {

        // Close any other open dropdowns by explicitly hiding them.
        // This is safer than calling clearMenus globally from a custom click.
        document.querySelectorAll('.dropdown-toggle.show').forEach(function(openToggle) {
          const instance = bootstrap.Dropdown.getInstance(openToggle);
          if (instance && openToggle !== toggle) { // Only hide if it's not the one we're about to open
            instance.hide();
          }
        });

        // Open the target dropdown
        const dropdown = bootstrap.Dropdown.getOrCreateInstance(toggle);
        dropdown.show();
      } else {
        console.warn("Bootstrap Dropdown not yet initialized or available when triggerDropdown called.");
      }
    } else {
      console.warn("Dropdown toggle not found within navItem:", navItemId);
    }
  };

  // **IMPORTANT:** REMOVE THE ENTIRE "CLICK OUTSIDE" LISTENER.
  // Bootstrap handles closing dropdowns when clicking outside automatically.
  // If this block is still present, it is likely causing the error.
  /*
  document.addEventListener('click', function (event) {
    if (!event.target.closest('.dropdown-toggle') && !event.target.closest('.position-relative')) {
        if (typeof bootstrap !== 'undefined' && typeof bootstrap.Dropdown !== 'undefined') {
            bootstrap.Dropdown.clearMenus();
        }
    }
  });
  */

  // Self-executing function to ensure Bootstrap is ready (keep this for safety)
  (function () {
    const checkBootstrapReady = setInterval(() => {
      if (typeof bootstrap !== 'undefined' && typeof bootstrap.Dropdown !== 'undefined') {
        clearInterval(checkBootstrapReady);
        console.log("Bootstrap Dropdown is ready.");
      }
    }, 100);
  })();
});