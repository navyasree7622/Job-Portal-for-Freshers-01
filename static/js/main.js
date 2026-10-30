/**
 * FirstStep Careers - Main Global JavaScript
 * Navigation, Dropdowns, Flash Messages, Modals, Dynamic Bookmarking
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Mobile Menu Toggle
  const mobileToggle = document.getElementById('mobileNavToggle');
  const navMenu = document.getElementById('mainNavMenu');

  if (mobileToggle && navMenu) {
    mobileToggle.addEventListener('click', function () {
      navMenu.classList.toggle('open');
      const isExpanded = navMenu.classList.contains('open');
      mobileToggle.setAttribute('aria-expanded', isExpanded);
    });
  }

  // 2. User Avatar Dropdown
  const userProfileBtn = document.getElementById('userProfileBtn');
  const userDropdownMenu = document.getElementById('userDropdownMenu');

  if (userProfileBtn && userDropdownMenu) {
    userProfileBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      userDropdownMenu.classList.toggle('show');
    });

    // Close dropdown on outside click
    document.addEventListener('click', function (e) {
      if (!userProfileBtn.contains(e.target) && !userDropdownMenu.contains(e.target)) {
        userDropdownMenu.classList.remove('show');
      }
    });
  }

  // 3. Flash Alert Dismissal
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(function (alert) {
    const closeBtn = alert.querySelector('.alert-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', function () {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 250);
      });
    }

    // Auto dismiss after 6 seconds
    setTimeout(function () {
      if (alert && alert.parentElement) {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 250);
      }
    }, 6000);
  });

  // 4. Modal Helpers
  window.openModal = function (modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('show');
      document.body.style.overflow = 'hidden';
    }
  };

  window.closeModal = function (modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('show');
      document.body.style.overflow = '';
    }
  };

  // Close modals when clicking overlay background
  document.querySelectorAll('.modal-overlay').forEach(function (overlay) {
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) {
        overlay.classList.remove('show');
        document.body.style.overflow = '';
      }
    });
  });

  // 5. Dynamic Job Bookmark Toggler
  document.querySelectorAll('.bookmark-btn').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();

      const jobId = this.getAttribute('data-job-id');
      if (!jobId) return;

      const button = this;

      fetch(`/api/jobs/${jobId}/bookmark`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'unauthorized') {
          window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
          return;
        }

        if (data.status === 'saved') {
          button.classList.add('saved');
          button.title = 'Remove from Saved Jobs';
          showToast('Job saved to your bookmarks!', 'success');
        } else if (data.status === 'removed') {
          button.classList.remove('saved');
          button.title = 'Save Job';
          showToast('Job removed from saved jobs.', 'info');
          // If on saved jobs page, remove card smoothly
          const card = button.closest('.saved-job-card');
          if (card) {
            card.style.opacity = '0';
            setTimeout(() => card.remove(), 250);
          }
        }
      })
      .catch(err => {
        console.error('Bookmark error:', err);
      });
    });
  });

  // 6. Toast Notification Generator
  window.showToast = function (message, type = 'info') {
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.id = 'toastContainer';
      toastContainer.style.position = 'fixed';
      toastContainer.style.bottom = '24px';
      toastContainer.style.right = '24px';
      toastContainer.style.zIndex = '3000';
      toastContainer.style.display = 'flex';
      toastContainer.style.flexDirection = 'column';
      toastContainer.style.gap = '10px';
      document.body.appendChild(toastContainer);
    }

    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.style.boxShadow = '0 8px 20px rgba(0,0,0,0.15)';
    toast.style.margin = '0';
    toast.style.minWidth = '280px';
    toast.innerHTML = `
      <span>${message}</span>
      <button class="alert-close" onclick="this.parentElement.remove()">&times;</button>
    `;

    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 250);
    }, 4500);
  };
});

