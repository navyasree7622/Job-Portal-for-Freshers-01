/**
 * FirstStep Careers - Job Search & Filtering JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {
  const filterForm = document.getElementById('jobFilterForm');
  const searchInput = document.getElementById('keywordInput');
  const locationInput = document.getElementById('locationInput');
  const categorySelect = document.getElementById('categorySelect');
  const arrangementSelect = document.getElementById('arrangementSelect');
  const jobTypeSelect = document.getElementById('jobTypeSelect');
  const expLevelSelect = document.getElementById('expLevelSelect');
  const minSalarySelect = document.getElementById('minSalarySelect');
  const sortSelect = document.getElementById('sortSelect');
  const clearFiltersBtn = document.getElementById('clearFiltersBtn');

  if (!filterForm) return;

  let debounceTimer;

  function performSearch() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      filterForm.submit();
    }, 450);
  }

  if (searchInput) {
    searchInput.addEventListener('input', performSearch);
  }

  if (locationInput) {
    locationInput.addEventListener('input', performSearch);
  }

  [categorySelect, arrangementSelect, jobTypeSelect, expLevelSelect, minSalarySelect, sortSelect].forEach(el => {
    if (el) {
      el.addEventListener('change', () => filterForm.submit());
    }
  });

  if (clearFiltersBtn) {
    clearFiltersBtn.addEventListener('click', function (e) {
      e.preventDefault();
      window.location.href = '/jobs';
    });
  }
});
