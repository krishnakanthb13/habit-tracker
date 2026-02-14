/**
 * Theme Manager — handles theme switching and persistence.
 */
const ThemeManager = {
    currentTheme: 'dark',

    init() {
        // Load theme from API or fallback to localStorage
        const saved = localStorage.getItem('habit-tracker-theme') || 'dark';
        this.apply(saved);
        this.bindEvents();
    },

    apply(theme) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('habit-tracker-theme', theme);

        // Update active state on theme buttons
        document.querySelectorAll('.theme-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.theme === theme);
        });
    },

    async save(theme) {
        this.apply(theme);
        try {
            await API.put('/api/settings', { theme });
        } catch (e) {
            console.warn('Failed to save theme to server:', e);
        }
    },

    bindEvents() {
        document.querySelectorAll('.theme-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.save(btn.dataset.theme);
            });
        });
    },

    async loadFromServer() {
        try {
            const settings = await API.get('/api/settings');
            if (settings.theme) {
                this.apply(settings.theme);
            }
        } catch (e) {
            console.warn('Failed to load theme from server:', e);
        }
    }
};
