/* ==========================================================
   THINKERS - Entrepreneur Clubs Interactive Script
   Integrates Lucide Icons, Modals, Tabs, Upvotes, & Toasts
   ========================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide Icons
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // Mobile Navigation Menu Toggle
  const mobileToggle = document.querySelector('.mobile-nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', () => {
      navLinks.classList.toggle('mobile-open');
    });
  }

  // Interactive Tabs
  const tabButtons = document.querySelectorAll('.comic-tab');
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-tab');
      const tabGroup = btn.closest('.comic-tabs-wrapper') || document;
      
      tabGroup.querySelectorAll('.comic-tab').forEach(b => b.classList.remove('active'));
      tabGroup.querySelectorAll('.tab-content-panel').forEach(p => p.classList.add('tab-panel-hidden'));
      
      btn.classList.add('active');
      const targetPanel = tabGroup.querySelector('#' + targetId);
      if (targetPanel) {
        targetPanel.classList.remove('tab-panel-hidden');
        if (window.lucide) {
          window.lucide.createIcons();
        }
      }
    });
  });

  // Filter Chips interactive selection
  const filterChips = document.querySelectorAll('.filter-chip');
  filterChips.forEach(chip => {
    chip.addEventListener('click', (e) => {
      if (!chip.getAttribute('href')) {
        chip.parentElement.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
      }
    });
  });

  // Modal open/close handlers
  window.openModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('open');
      document.body.style.overflow = 'hidden';
      if (window.lucide) {
        window.lucide.createIcons();
      }
    }
  };

  window.closeModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('open');
      document.body.style.overflow = '';
    }
  };

  // Close modal when clicking overlay background
  document.querySelectorAll('.comic-modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        overlay.classList.remove('open');
        document.body.style.overflow = '';
      }
    });
  });

  // Pitch Deck / Upvote comic interaction
  document.querySelectorAll('.comic-upvote-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const countSpan = this.querySelector('.upvote-count');
      if (countSpan) {
        let count = parseInt(countSpan.innerText.replace(',', '')) || 0;
        if (!this.classList.contains('upvoted')) {
          this.classList.add('upvoted');
          countSpan.innerText = (count + 1);
          showComicToast('Upvoted pitch! Founders appreciate your hype!');
        } else {
          this.classList.remove('upvoted');
          countSpan.innerText = (count - 1);
        }
      }
    });
  });

  // Toast notification helper with Lucide icon
  window.showComicToast = function(message) {
    let toast = document.getElementById('comic-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'comic-toast';
      document.body.appendChild(toast);
    }
    toast.innerHTML = `<i data-lucide="sparkles"></i> <span>${message}</span>`;
    if (window.lucide) {
      window.lucide.createIcons();
    }
    toast.classList.add('show');
    
    setTimeout(() => {
      toast.classList.remove('show');
    }, 3200);
  };
});
