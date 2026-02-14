/**
 * Toast — simple toast notification system.
 */
const Toast = {
    show(message, type = 'info', duration = 3000) {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'toastOut 0.3s ease forwards';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
};


/**
 * App — main orchestrator, initializes everything.
 */
const App = {
    habitsData: [],

    async init() {
        // Initialize modules
        ThemeManager.init();
        Calendar.init();
        HabitModal.init();
        NoteModal.init();
        Settings.init();
        if (window.lucide) {
            lucide.createIcons();
        }

        // Load settings first (applies theme, toggles)
        await Settings.loadSettings();

        // Load data
        await this.refresh();

        // Help button
        document.getElementById('btn-help').addEventListener('click', () => {
            window.location.href = '/help';
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                document.getElementById('modal-habit').hidden = true;
                document.getElementById('modal-note').hidden = true;
                Settings.close();
            }
            // Ctrl+N = new habit
            if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
                e.preventDefault();
                HabitModal.open();
            }
        });
    },

    async loadHabits() {
        try {
            this.habitsData = await API.get('/api/habits');
        } catch (e) {
            Toast.show('Failed to load habits: ' + e.message, 'error');
        }
    },

    async refresh() {
        await this.loadHabits();
        await Calendar.load();
    }
};


// Boot
document.addEventListener('DOMContentLoaded', () => App.init());
