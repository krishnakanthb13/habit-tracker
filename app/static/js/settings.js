/**
 * Settings panel — toggles, import/export, database health.
 */
const Settings = {
    panel: null,

    init() {
        this.panel = document.getElementById('settings-panel');

        // Open/close
        document.getElementById('btn-settings').addEventListener('click', () => this.toggle());
        document.getElementById('btn-close-settings').addEventListener('click', () => this.close());

        // Day extension toggle
        document.getElementById('toggle-day-extension').addEventListener('change', (e) => {
            this._saveSetting('day_extension', e.target.checked ? 'true' : 'false');
            document.getElementById('day-ext-hour-control').hidden = !e.target.checked;
        });

        // Day extension hour slider
        document.getElementById('day-ext-hour').addEventListener('input', (e) => {
            document.getElementById('day-ext-hour-value').textContent = e.target.value;
            document.getElementById('day-ext-hour-display').textContent = e.target.value;
        });
        document.getElementById('day-ext-hour').addEventListener('change', (e) => {
            this._saveSetting('day_extension_hour', e.target.value);
        });

        // Skip toggle
        document.getElementById('toggle-skip').addEventListener('change', (e) => {
            this._saveSetting('skip_enabled', e.target.checked ? 'true' : 'false');
        });

        // Animation toggle
        document.getElementById('toggle-animations').addEventListener('change', (e) => {
            const enabled = e.target.checked;
            this._saveSetting('animations_enabled', enabled ? 'true' : 'false');
            Animations.init(enabled);
        });

        // Export
        document.getElementById('btn-export').addEventListener('click', () => this._export());

        // Import
        document.getElementById('import-file').addEventListener('change', (e) => this._import(e));

        // Health check
        document.getElementById('btn-health-check').addEventListener('click', () => this._healthCheck());

        // Backup
        document.getElementById('btn-backup').addEventListener('click', () => this._backup());

        // Repair
        document.getElementById('btn-repair').addEventListener('click', () => this._repair());

        // Backdrop click to close
        document.getElementById('settings-backdrop').addEventListener('click', () => this.close());
    },

    toggle() {
        const isHidden = this.panel.hidden;
        if (isHidden) {
            this.open();
        } else {
            this.close();
        }
    },

    open() {
        this.panel.hidden = false;
        document.getElementById('settings-backdrop').hidden = false;
    },

    close() {
        this.panel.hidden = true;
        document.getElementById('settings-backdrop').hidden = true;
    },

    async loadSettings() {
        try {
            const settings = await API.get('/api/settings');

            // Apply theme
            if (settings.theme) {
                ThemeManager.apply(settings.theme);
            }

            // Day extension
            const dayExt = settings.day_extension === 'true';
            document.getElementById('toggle-day-extension').checked = dayExt;
            document.getElementById('day-ext-hour-control').hidden = !dayExt;
            const hour = settings.day_extension_hour || '3';
            document.getElementById('day-ext-hour').value = hour;
            document.getElementById('day-ext-hour-value').textContent = hour;
            document.getElementById('day-ext-hour-display').textContent = hour;

            // Skip
            document.getElementById('toggle-skip').checked = settings.skip_enabled !== 'false';

            // Animations
            const animEnabled = settings.animations_enabled !== 'false';
            document.getElementById('toggle-animations').checked = animEnabled;
            Animations.init(animEnabled);

            // Load archived habits in background
            this.loadArchivedHabits();

        } catch (e) {
            console.warn('Failed to load settings:', e);
        }
    },

    async _saveSetting(key, value) {
        try {
            await API.put('/api/settings', { [key]: value });
            // Refresh calendar if date-affecting settings changed
            if (key === 'day_extension' || key === 'day_extension_hour' || key === 'skip_enabled') {
                await App.refresh();
            }
        } catch (e) {
            Toast.show('Failed to save setting: ' + e.message, 'error');
        }
    },

    async _export() {
        try {
            Toast.show('Preparing export...', 'info');
            const result = await API.get('/api/export');
            Toast.show(`Exported to: ${result.filename} 📤`, 'success');
        } catch (e) {
            Toast.show('Export failed: ' + e.message, 'error');
        }
    },

    async _import(event) {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            // Preview first
            const preview = await API.upload('/api/import/preview', formData);

            if (!preview.valid) {
                Toast.show('Invalid file: ' + preview.errors.join(', '), 'error');
                return;
            }

            const msg = `Import ${preview.row_count} rows into "${preview.table}" table?`;
            if (!confirm(msg)) return;

            // Do the actual import
            const importForm = new FormData();
            importForm.append('file', file);
            importForm.append('table_name', preview.table);

            const result = await API.upload('/api/import', importForm);
            Toast.show(`Imported ${result.imported} rows! 📥`, 'success');

            if (result.errors?.length > 0) {
                Toast.show(`${result.errors.length} errors during import`, 'error');
            }

            await App.refresh();
        } catch (e) {
            Toast.show('Import failed: ' + e.message, 'error');
        }

        // Reset file input
        event.target.value = '';
    },

    async _healthCheck() {
        const resultDiv = document.getElementById('health-result');
        resultDiv.hidden = false;
        resultDiv.textContent = 'Running integrity check...';
        resultDiv.className = 'health-result';

        try {
            const result = await API.get('/api/health');
            if (result.ok) {
                resultDiv.className = 'health-result ok';
                resultDiv.textContent = '✅ Database integrity check passed!';
            } else {
                resultDiv.className = 'health-result error';
                resultDiv.textContent = '❌ Issues found:\n' + result.details.join('\n');
            }
        } catch (e) {
            resultDiv.className = 'health-result error';
            resultDiv.textContent = '❌ Check failed: ' + e.message;
        }
    },

    async _backup() {
        try {
            const result = await API.post('/api/health/backup', {});
            Toast.show('Backup created! 💾', 'success');
        } catch (e) {
            Toast.show('Backup failed: ' + e.message, 'error');
        }
    },

    async _repair() {
        if (!confirm('⚠️ This will attempt to repair the database. A backup will be created first. Continue?')) return;

        const resultDiv = document.getElementById('health-result');
        resultDiv.hidden = false;
        resultDiv.className = 'health-result';
        resultDiv.textContent = 'Repairing database...';

        try {
            const result = await API.post('/api/health/repair', {});
            if (result.success) {
                resultDiv.className = 'health-result ok';
                resultDiv.textContent = '✅ Repair successful!\n' + result.details.join('\n');
                Toast.show('Database repaired! 🔧', 'success');
            } else {
                resultDiv.className = 'health-result error';
                resultDiv.textContent = '❌ Repair issues:\n' + result.details.join('\n');
            }
            await App.refresh();
        } catch (e) {
            resultDiv.className = 'health-result error';
            resultDiv.textContent = '❌ Repair failed: ' + e.message;
        }
    },

    async loadArchivedHabits() {
        const listContainer = document.getElementById('archived-habits-list');
        try {
            const habits = await API.get('/api/habits/archived');
            if (habits.length === 0) {
                listContainer.innerHTML = '<p class="text-muted" style="font-size: 0.8rem;">No hidden habits.</p>';
                return;
            }

            listContainer.innerHTML = habits.map(h => `
                <div class="archived-item">
                    <div class="archived-info">
                        <span class="archived-color" style="background-color: ${h.color}"></span>
                        <span>${h.name}</span>
                    </div>
                    <button class="btn btn-secondary btn-sm" onclick="Settings.unarchiveHabit(${h.id})">Unhide</button>
                </div>
            `).join('');

        } catch (e) {
            console.error('Failed to load archived habits:', e);
        }
    },

    async unarchiveHabit(id) {
        // Optimistic UI update
        const listContainer = document.getElementById('archived-habits-list');
        // Find the button with this ID onclick
        // Simple search: iterate children or query selector
        const buttons = listContainer.querySelectorAll('button');
        let removed = false;
        buttons.forEach(btn => {
            if (btn.getAttribute('onclick')?.includes(`(${id})`)) {
                btn.closest('.archived-item').remove();
                removed = true;
            }
        });

        if (removed && listContainer.children.length === 0) {
            listContainer.innerHTML = '<p class="text-muted" style="font-size: 0.8rem;">No hidden habits.</p>';
        }

        try {
            await API.post(`/api/habits/${id}/unarchive`, {});
            Toast.show('Habit restored! 👀', 'success');
            // Background refresh to update calendar
            App.refresh();
        } catch (e) {
            console.error(e);
            Toast.show('Failed to restore habit: ' + e.message, 'error');
            // Revert UI on error
            this.loadArchivedHabits();
        }
    }
};
