/* ==========================================================
   THINKERS - Entrepreneur Clubs Interactive Script
   Integrates Lucide Icons, Modals, Tabs, Upvotes, & Toasts
   ========================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide Icons
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // Mobile Navigation Toggle
  const mobileToggleBtn = document.getElementById('mobileNavToggleBtn');
  const navbarLinks = document.getElementById('navbarLinks');

  if (mobileToggleBtn && navbarLinks) {
    mobileToggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      navbarLinks.classList.toggle('show');
    });
  }

  // Notification Dropdown Toggle
  const notificationBtn = document.getElementById('notificationToggleBtn');
  const notificationMenu = document.getElementById('notificationDropdownMenu');
  const notificationCloseBtn = document.getElementById('notificationCloseBtn');

  function openNotifications() {
    if (!notificationMenu || !notificationBtn) return;
    notificationMenu.classList.add('show');
    notificationMenu.style.display = 'block';
    notificationBtn.setAttribute('aria-expanded', 'true');
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }

  function closeNotifications() {
    if (!notificationMenu || !notificationBtn) return;
    notificationMenu.classList.remove('show');
    notificationMenu.style.display = 'none';
    notificationBtn.setAttribute('aria-expanded', 'false');
  }

  if (notificationBtn && notificationMenu) {
    notificationBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = notificationMenu.classList.contains('show') || notificationMenu.style.display === 'block';
      if (isOpen) {
        closeNotifications();
      } else {
        openNotifications();
      }
    });

    if (notificationCloseBtn) {
      notificationCloseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        closeNotifications();
      });
    }

    notificationMenu.addEventListener('click', (e) => {
      if (!e.target.closest('a')) {
        e.stopPropagation();
      }
    });
  }

  // Global click outside to close dropdowns / mobile menus
  document.addEventListener('click', (e) => {
    if (notificationMenu && notificationBtn) {
      if (!notificationMenu.contains(e.target) && !notificationBtn.contains(e.target)) {
        closeNotifications();
      }
    }
    if (navbarLinks && mobileToggleBtn) {
      if (!navbarLinks.contains(e.target) && !mobileToggleBtn.contains(e.target)) {
        navbarLinks.classList.remove('show');
      }
    }
  });

  // Global Escape key handler
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeNotifications();
      if (navbarLinks && navbarLinks.classList.contains('show')) {
        navbarLinks.classList.remove('show');
      }
    }
  });

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

  // Pitch Deck / Upvote comic interaction with AJAX persistence
  document.querySelectorAll('.comic-upvote-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const countSpan = this.querySelector('.upvote-count');
      const url = this.getAttribute('data-url');
      if (countSpan) {
        let count = parseInt(countSpan.innerText.replace(',', '')) || 0;
        if (!this.classList.contains('upvoted')) {
          this.classList.add('upvoted');
          countSpan.innerText = (count + 1);
          showComicToast('Upvoted! Founders appreciate your hype!');
          if (url) {
            fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
              .then(res => res.json())
              .then(data => {
                if (data && data.upvotes !== undefined) {
                  countSpan.innerText = data.upvotes;
                }
              })
              .catch(err => console.log('Upvote registered locally:', err));
          }
        } else {
          this.classList.remove('upvoted');
          countSpan.innerText = Math.max(0, count - 1);
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

  // Live polling for navbar unread messages count
  const chatBadge = document.getElementById('chatUnreadCountBadge');
  if (chatBadge) {
    setInterval(() => {
      fetch('/chat/api/unread-count/')
        .then(res => res.json())
        .then(data => {
          if (data && typeof data.unread_count === 'number') {
            if (data.unread_count > 0) {
              chatBadge.innerText = data.unread_count;
              chatBadge.style.display = 'flex';
            } else {
              chatBadge.style.display = 'none';
            }
          }
        })
        .catch(() => {});
    }, 15000);
  }
});
