/**
 * FirstStep Careers - Forms Validation & Interactivity
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Password Visibility Toggle
  document.querySelectorAll('.password-toggle-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const targetId = this.getAttribute('data-target');
      const input = document.getElementById(targetId);
      if (!input) return;

      if (input.type === 'password') {
        input.type = 'text';
        this.innerHTML = `
          <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
          </svg>
        `;
      } else {
        input.type = 'password';
        this.innerHTML = `
          <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
        `;
      }
    });
  });

  // 2. Resume File Validation
  const resumeInput = document.getElementById('resumeFileInput');
  const fileFeedback = document.getElementById('fileUploadFeedback');

  if (resumeInput && fileFeedback) {
    resumeInput.addEventListener('change', function () {
      const file = this.files[0];
      if (!file) return;

      const validExtensions = ['pdf', 'doc', 'docx'];
      const fileExt = file.name.split('.').pop().toLowerCase();
      const maxSize = 5 * 1024 * 1024; // 5MB

      if (!validExtensions.includes(fileExt)) {
        fileFeedback.innerHTML = `<span style="color: var(--danger);">Invalid file type. Only .PDF, .DOC, and .DOCX files are allowed.</span>`;
        this.value = '';
        return;
      }

      if (file.size > maxSize) {
        fileFeedback.innerHTML = `<span style="color: var(--danger);">File size exceeds 5MB limit. Please upload a smaller file.</span>`;
        this.value = '';
        return;
      }

      const sizeKb = Math.round(file.size / 1024);
      fileFeedback.innerHTML = `<span style="color: var(--success); font-weight: 600;">Selected: ${file.name} (${sizeKb} KB)</span>`;
    });
  }

  // 3. Dynamic Profile Completion Calculator (on Profile Page)
  const profileForm = document.getElementById('fresherProfileForm');
  if (profileForm) {
    const trackedFields = [
      'phone', 'location', 'education', 'degree',
      'institution', 'graduation_year', 'cgpa',
      'skills', 'bio', 'github_url', 'linkedin_url'
    ];

    function calculateCompletion() {
      let filled = 0;
      trackedFields.forEach(id => {
        const field = document.getElementById(id);
        if (field && field.value.trim().length > 0) {
          filled++;
        }
      });

      // Check if resume exists
      const resumeExists = profileForm.getAttribute('data-has-resume') === 'true' ||
                           (resumeInput && resumeInput.files.length > 0);
      if (resumeExists) filled += 2; // Weight resume higher

      const totalPoints = trackedFields.length + 2;
      const pct = Math.round((filled / totalPoints) * 100);

      const bar = document.getElementById('profileProgressBar');
      const text = document.getElementById('profileProgressPct');

      if (bar) bar.style.width = pct + '%';
      if (text) text.textContent = pct + '%';
    }

    trackedFields.forEach(id => {
      const field = document.getElementById(id);
      if (field) {
        field.addEventListener('input', calculateCompletion);
        field.addEventListener('change', calculateCompletion);
      }
    });

    calculateCompletion();
  }
});

