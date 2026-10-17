/**
 * Docs Microservice — Sidebar Navigation JS
 */

document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebarToggle');
    const sectionTitles = document.querySelectorAll('.nav-section-title');

    // --- Mobile sidebar toggle ---
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });

        // Close sidebar on outside click (mobile)
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 900 && sidebar.classList.contains('open')) {
                if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
                    sidebar.classList.remove('open');
                }
            }
        });
    }

    // --- Section collapse/expand ---
    sectionTitles.forEach(title => {
        const sectionKey = title.dataset.section;
        const subsection = title.nextElementSibling;

        // Restore state from localStorage
        const collapsed = localStorage.getItem(`toc_${sectionKey}`) === 'true';
        if (collapsed) {
            subsection.classList.add('collapsed');
            title.querySelector('.section-chevron').style.transform = 'rotate(-90deg)';
        }

        title.addEventListener('click', () => {
            const isCollapsed = subsection.classList.toggle('collapsed');
            title.querySelector('.section-chevron').style.transform =
                isCollapsed ? 'rotate(-90deg)' : 'rotate(0deg)';
            localStorage.setItem(`toc_${sectionKey}`, isCollapsed);
        });
    });

    // --- Keyboard shortcut: Ctrl+B to toggle sidebar ---
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
            e.preventDefault();
            if (sidebar) sidebar.classList.toggle('open');
        }
    });
});
