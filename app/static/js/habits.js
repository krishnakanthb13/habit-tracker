/**
 * Habit Modal — create, edit, delete habits.
 * Note Modal — add/edit notes on entries.
 */
const HabitModal = {
    modal: null,
    form: null,

    init() {
        this.modal = document.getElementById('modal-habit');
        this.form = document.getElementById('form-habit');

        // Close modal handlers
        this.modal.querySelectorAll('[data-close-modal]').forEach(btn => {
            btn.addEventListener('click', () => this.close());
        });
        this.modal.querySelector('.modal-backdrop').addEventListener('click', () => this.close());

        // Form submit
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.save();
        });

        // Delete button (Hard)
        document.getElementById('btn-delete-habit').addEventListener('click', () => this.hardDelete());

        // Archive button (Hide)
        document.getElementById('btn-archive-habit').addEventListener('click', () => this.archive());

        // Goal type change — drives animated show/hide
        document.getElementById('habit-goal-type').addEventListener('change', (e) => {
            this._updateGoalFields(e.target.value);
        });

        // Note: btn-add-habit is inside the calendar table, bound dynamically via onclick
    },

    open() {
        document.getElementById('modal-habit-title').textContent = 'Add Habit';
        this.form.reset();
        document.getElementById('habit-id').value = '';
        document.getElementById('habit-color').value = '#4CAF50';
        document.getElementById('btn-delete-habit').hidden = true;
        document.getElementById('btn-archive-habit').hidden = true;
        this._updateGoalFields('');
        this.modal.hidden = false;
        document.getElementById('habit-name').focus();
    },

    async openEdit(habitId) {
        const habit = App.habitsData?.find(h => h.id === habitId);
        if (!habit) return;

        document.getElementById('modal-habit-title').textContent = 'Edit Habit';
        document.getElementById('habit-id').value = habit.id;
        document.getElementById('habit-name').value = habit.name;
        document.getElementById('habit-description').value = habit.description || '';
        document.getElementById('habit-color').value = habit.color;
        document.getElementById('btn-delete-habit').hidden = false;
        document.getElementById('btn-archive-habit').hidden = false;

        // Load goal
        if (habit.goal) {
            document.getElementById('habit-goal-type').value = habit.goal.goal_type;
            this._updateGoalFields(habit.goal.goal_type);
            document.getElementById('habit-goal-target').value = habit.goal.target;
            if (habit.goal.period_days) {
                document.getElementById('habit-goal-period').value = habit.goal.period_days;
            }
        } else {
            document.getElementById('habit-goal-type').value = '';
            this._updateGoalFields('');
        }

        this.modal.hidden = false;
        document.getElementById('habit-name').focus();
    },

    close() {
        this.modal.hidden = true;
    },

    async save() {
        const id = document.getElementById('habit-id').value;
        const name = document.getElementById('habit-name').value.trim();
        const description = document.getElementById('habit-description').value.trim();
        const color = document.getElementById('habit-color').value;

        if (!name) {
            Toast.show('Habit name is required', 'error');
            return;
        }

        try {
            if (id) {
                await API.put(`/api/habits/${id}`, { name, description, color });
                Toast.show('Habit updated', 'success');
            } else {
                await API.post('/api/habits', { name, description, color });
                Toast.show('Habit created! 🎯', 'success');
            }

            // Save goal
            const goalType = document.getElementById('habit-goal-type').value;
            const habitId = id || (await this._getLatestHabitId());

            if (goalType) {
                await API.post(`/api/habits/${habitId}/goals`, {
                    goal_type: goalType,
                    target: parseInt(document.getElementById('habit-goal-target').value) || 1,
                    period_days: parseInt(document.getElementById('habit-goal-period').value) || 7,
                });
            } else if (id) {
                // Remove goal if cleared
                try { await API.delete(`/api/habits/${habitId}/goals`); } catch (e) { /* ok */ }
            }

            this.close();
            await App.refresh();
        } catch (e) {
            Toast.show('Failed to save: ' + e.message, 'error');
        }
    },

    async archive() {
        const id = document.getElementById('habit-id').value;
        if (!id) return;

        if (!confirm('Hide this habit from the calendar? You can restore it from settings later.')) return;

        try {
            await API.delete(`/api/habits/${id}`); // Our API currently uses DELETE for soft-delete
            Toast.show('Habit hidden 🙈', 'info');
            this.close();
            await App.refresh();
            await Settings.loadArchivedHabits(); // Refresh the list in settings
        } catch (e) {
            Toast.show('Failed to hide: ' + e.message, 'error');
        }
    },

    async hardDelete() {
        const id = document.getElementById('habit-id').value;
        if (!id) return;

        if (!confirm('⚠️ PERMANENT DELETE\n\nAre you sure? This will delete all history and data for this habit forever.')) return;

        try {
            await API.delete(`/api/habits/${id}/hard-delete`);
            Toast.show('Habit permanently deleted', 'error');
            this.close();
            await App.refresh();
        } catch (e) {
            Toast.show('Failed to delete: ' + e.message, 'error');
        }
    },

    async _getLatestHabitId() {
        const habits = await API.get('/api/habits');
        return habits[habits.length - 1]?.id;
    },

    /**
     * Dynamically show/hide goal sub-fields with CSS animation.
     */
    _updateGoalFields(type) {
        const container = document.getElementById('goal-dynamic-fields');
        const targetRow = document.getElementById('goal-target-row');
        const periodRow = document.getElementById('goal-period-row');
        const targetLabel = document.getElementById('goal-target-label');

        if (!type || type === '' || type === 'daily') {
            // Hide all dynamic fields
            container.classList.remove('visible');
            targetRow.style.display = 'none';
            periodRow.style.display = 'none';
        } else if (type === 'weekly') {
            targetRow.style.display = 'flex';
            periodRow.style.display = 'none';
            targetLabel.textContent = 'times per week';
            container.classList.add('visible');
        } else if (type === 'custom') {
            targetRow.style.display = 'flex';
            periodRow.style.display = 'flex';
            targetLabel.textContent = 'times in period';
            container.classList.add('visible');
        }
    }
};


/**
 * Note Modal — add/edit notes on calendar entries.
 */
const NoteModal = {
    modal: null,

    init() {
        this.modal = document.getElementById('modal-note');

        this.modal.querySelectorAll('[data-close-modal]').forEach(btn => {
            btn.addEventListener('click', () => this.close());
        });
        this.modal.querySelector('.modal-backdrop').addEventListener('click', () => this.close());

        document.getElementById('btn-save-note').addEventListener('click', () => this.save());
        document.getElementById('btn-clear-note').addEventListener('click', () => this.clear());
    },

    open(habitId, date) {
        document.getElementById('note-habit-id').value = habitId;
        document.getElementById('note-date').value = date;

        // Load existing note
        const habit = Calendar.data?.habits?.find(h => h.id === habitId);
        const entry = habit?.entries?.[date];
        document.getElementById('note-text').value = entry?.note || '';

        this.modal.hidden = false;
        document.getElementById('note-text').focus();
    },

    close() {
        this.modal.hidden = true;
    },

    async save() {
        const habitId = document.getElementById('note-habit-id').value;
        const date = document.getElementById('note-date').value;
        const note = document.getElementById('note-text').value.trim();

        try {
            await API.put('/api/entries/note', {
                habit_id: parseInt(habitId),
                date: date,
                note: note,
            });
            Toast.show('Note saved 📝', 'success');
            this.close();
            await App.refresh();
        } catch (e) {
            Toast.show('Failed to save note: ' + e.message, 'error');
        }
    },

    async clear() {
        if (!confirm('Are you sure you want to clear this note?')) return;
        document.getElementById('note-text').value = '';
        await this.save();
    }
};
