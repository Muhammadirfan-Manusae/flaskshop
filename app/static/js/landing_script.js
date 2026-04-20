/* ============================================================
   AROMDEE CAFE — Scripts
   ============================================================ */
(() => {
  'use strict';

  /* ---------- DOM refs ---------- */
  const loader    = document.getElementById('loader');
  const navbar    = document.getElementById('navbar');
  const navToggle = document.getElementById('navToggle');
  const navLinks  = document.querySelector('.nav-links');
  const heroImg   = document.querySelector('.hero-bg-img');
  const beans     = document.querySelectorAll('.bean');
  const reveals   = document.querySelectorAll('.reveal');
  const tiltCards = document.querySelectorAll('[data-tilt]');
  const sections  = document.querySelectorAll('section[id]');

  /* ============================================================
     1. LOADING SCREEN
     ============================================================ */
  window.addEventListener('load', () => {
    setTimeout(() => {
      loader.classList.add('hidden');
      document.body.style.overflow = '';
    }, 1400);
  });
  // prevent scroll while loading
  document.body.style.overflow = 'hidden';

  /* ============================================================
     2. NAVBAR — scroll glass effect & active link
     ============================================================ */
  function handleNavbar() {
    const scrollY = window.scrollY;

    // Glass effect
    if (scrollY > 60) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }

    // Active section highlight
    let current = '';
    sections.forEach(sec => {
      const top = sec.offsetTop - 200;
      if (scrollY >= top) current = sec.getAttribute('id');
    });
    document.querySelectorAll('.nav-link').forEach(link => {
      link.classList.toggle('active',
        link.getAttribute('href') === `#${current}`
      );
    });
  }

  /* ============================================================
     3. HERO PARALLAX — background zoom + floating beans
     ============================================================ */
  function handleParallax() {
    const scrollY = window.scrollY;
    const vh = window.innerHeight;

    // Background zoom (only while hero is visible)
    if (scrollY < vh && heroImg) {
      const scale = 1 + scrollY * 0.0004;
      heroImg.style.transform = `scale(${scale})`;
    }

    // Floating beans parallax
    beans.forEach((bean, i) => {
      const speed = 0.03 + i * 0.015;
      const y = scrollY * speed;
      const x = Math.sin(scrollY * 0.002 + i) * 12;
      bean.style.transform = `translate(${x}px, ${-y}px)`;
    });
  }

  /* ============================================================
     4. SCROLL REVEAL
     ============================================================ */
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

  reveals.forEach(el => revealObserver.observe(el));

  /* ============================================================
     5. 3D TILT ON MENU CARDS
     ============================================================ */
  tiltCards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const rotateX = ((y - centerY) / centerY) * -8;
      const rotateY = ((x - centerX) / centerX) * 8;

      card.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.03,1.03,1.03)`;

      // Move shine
      const shine = card.querySelector('.card-shine');
      if (shine) {
        shine.style.background = `radial-gradient(circle at ${x}px ${y}px, rgba(255,255,255,.3) 0%, transparent 60%)`;
      }
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(800px) rotateX(0) rotateY(0) scale3d(1,1,1)';
      const shine = card.querySelector('.card-shine');
      if (shine) shine.style.opacity = '0';
    });

    card.addEventListener('mouseenter', () => {
      const shine = card.querySelector('.card-shine');
      if (shine) shine.style.opacity = '1';
    });
  });

  /* ============================================================
     6. MOBILE NAV TOGGLE
     ============================================================ */
  navToggle.addEventListener('click', () => {
    navLinks.classList.toggle('open');
  });

  // Close mobile nav on link click
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
      navLinks.classList.remove('open');
    });
  });

  /* ============================================================
     7. UNIFIED SCROLL HANDLER (throttled with rAF)
     ============================================================ */
  let ticking = false;
  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        handleNavbar();
        handleParallax();
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });

  // Fire once on load
  handleNavbar();
  handleParallax();

})();
