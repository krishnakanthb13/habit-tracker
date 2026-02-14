/**
 * Calendar — renders monthly calendar as a <table> with day-of-week headers,
 * Goal and Achieved columns, and a "+ New Habit" button row.
 * ALL dates (past, today, future) are editable.
 */
const Calendar = {
    currentYear: new Date().getFullYear(),
    currentMonth: new Date().getMonth() + 1,
    data: null,
    sortable: null,

    init() {
        document.getElementById('btn-prev-month').addEventListener('click', () => this.navigate(-1));
        document.getElementById('btn-next-month').addEventListener('click', () => this.navigate(1));

        // Go to Today
        document.getElementById('btn-today').addEventListener('click', () => {
            const now = new Date();
            this.currentYear = now.getFullYear();
            this.currentMonth = now.getMonth() + 1;
            this.load();
        });

        // Month Selection Modal
        document.getElementById('current-month-label').addEventListener('click', () => {
            this._openPicker();
        });

        document.getElementById('btn-apply-picker').addEventListener('click', () => {
            const activeYearBtn = document.querySelector('.year-grid .picker-btn.active');
            const activeMonthBtn = document.querySelector('.month-grid .picker-btn.active');
            if (activeYearBtn && activeMonthBtn) {
                this.currentYear = parseInt(activeYearBtn.dataset.value);
                this.currentMonth = parseInt(activeMonthBtn.dataset.value);
                this.load();
                document.getElementById('modal-picker').hidden = true;
            }
        });

        // Picker Modal Close handlers
        const pickerModal = document.getElementById('modal-picker');
        pickerModal.querySelectorAll('[data-close-modal]').forEach(btn => {
            btn.addEventListener('click', () => pickerModal.hidden = true);
        });
        pickerModal.querySelector('.modal-backdrop').addEventListener('click', () => pickerModal.hidden = true);
    },

    _openPicker() {
        const modal = document.getElementById('modal-picker');
        const yearGrid = document.getElementById('picker-year-grid');
        const monthGrid = document.getElementById('picker-month-grid');

        // Populate years (-5 to +2 from currentYear)
        yearGrid.innerHTML = '';
        const startYear = this.currentYear - 5;
        for (let y = startYear; y <= this.currentYear + 2; y++) {
            const btn = document.createElement('button');
            btn.className = 'picker-btn';
            if (y === this.currentYear) btn.classList.add('active');
            btn.dataset.value = y;
            btn.textContent = y;
            btn.onclick = () => {
                yearGrid.querySelectorAll('.picker-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            };
            yearGrid.appendChild(btn);
        }

        // Setup Month Grid
        monthGrid.querySelectorAll('.picker-btn').forEach(btn => {
            btn.classList.toggle('active', parseInt(btn.dataset.value) === this.currentMonth);
            btn.onclick = () => {
                monthGrid.querySelectorAll('.picker-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            };
        });

        modal.hidden = false;
    },

    navigate(delta) {
        this.currentMonth += delta;
        if (this.currentMonth > 12) {
            this.currentMonth = 1;
            this.currentYear++;
        } else if (this.currentMonth < 1) {
            this.currentMonth = 12;
            this.currentYear--;
        }
        this.load();
    },

    async load() {
        const monthStr = `${this.currentYear}-${String(this.currentMonth).padStart(2, '0')}`;
        document.getElementById('current-month-label').textContent = this._formatMonthLabel();

        try {
            this.data = await API.get(`/api/calendar?month=${monthStr}`);
            this.render();
        } catch (e) {
            Toast.show('Failed to load calendar: ' + e.message, 'error');
        }
    },

    render() {
        const container = document.getElementById('calendar-container');
        const data = this.data;

        if (!data || !data.habits || data.habits.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="emoji">🎯</div>
                    <h3>No habits yet</h3>
                    <p>Click <strong>+ New Habit</strong> to start tracking your first habit.</p>
                    <button class="btn btn-primary" onclick="HabitModal.open()">+ Add Your First Habit</button>
                </div>
            `;
            return;
        }

        const days = data.days_in_month;
        const today = data.today;
        const dayNames = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];

        let html = '<table class="calendar-table">';

        // ---- HEADER ROW 1: Day-of-week names ----
        html += '<thead>';
        html += '<tr>';
        html += '<th class="col-habit" rowspan="2">Habits</th>';
        for (let d = 1; d <= days; d++) {
            const dayOfWeek = new Date(data.year, data.month - 1, d).getDay();
            const dateStr = this._dateStr(data, d);
            const isToday = dateStr === today;
            const isFri = dayOfWeek === 5;
            const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
            let cls = '';
            if (isToday) cls = 'day-today';
            else if (isFri) cls = 'day-fri';
            else if (isWeekend) cls = 'day-weekend';
            html += `<th class="${cls}">${dayNames[dayOfWeek]}</th>`;
        }
        html += '<th class="col-goal" rowspan="2">Goal</th>';
        html += '<th class="col-achieved" rowspan="2">Achieved</th>';
        html += '</tr>';

        // ---- HEADER ROW 2: Day numbers ----
        html += '<tr>';
        for (let d = 1; d <= days; d++) {
            const dateStr = this._dateStr(data, d);
            const isToday = dateStr === today;
            const dayOfWeek = new Date(data.year, data.month - 1, d).getDay();
            const isFri = dayOfWeek === 5;
            const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
            let cls = '';
            if (isToday) cls = 'day-today';
            else if (isFri) cls = 'day-fri';
            else if (isWeekend) cls = 'day-weekend';
            html += `<th class="${cls}">${d}</th>`;
        }
        html += '</tr>';
        html += '</thead>';

        // ---- BODY: Habit rows ----
        html += '<tbody>';
        for (const habit of data.habits) {
            html += this._renderHabitRow(habit, days, data);
        }

        html += '</tbody></table>';

        container.innerHTML = html;
        this._bindCellEvents();
        if (window.lucide) {
            lucide.createIcons({
                root: container
            });
        }
        this._initSortable();
    },

    _renderHabitRow(habit, days, data) {
        const habitData = App.habitsData?.find(h => h.id === habit.id);
        const goal = habitData?.goal;
        const totalDone = habitData?.total_done ?? 0;
        const goalTarget = goal ? goal.target : '';
        const goalCurrent = goal ? goal.current : totalDone;
        const goalMet = goal && goal.met;

        let html = `<tr data-id="${habit.id}">`;

        // Habit name cell
        const description = (habitData?.description || 'No description').replace(/"/g, '&quot;');
        html += `<td class="habit-name-cell" data-habit-id="${habit.id}" onclick="HabitModal.openEdit(${habit.id})">`;
        html += `<span class="habit-name-text" title="${this._escapeHtml(habit.name)}">${this._escapeHtml(habit.name)}</span>`;
        html += `<span class="habit-info-icon" title="${description}"><i data-lucide="info"></i></span>`;
        html += '</td>';

        // Day cells — ALL dates are now editable (no future block)
        for (let d = 1; d <= days; d++) {
            const dateStr = this._dateStr(data, d);
            const entry = habit.entries[dateStr];
            const status = entry?.status || null;
            const hasNote = entry?.note ? true : false;
            const isToday = dateStr === data.today;

            const classes = ['day-cell'];
            if (status) classes.push(`status-${status}`);
            if (isToday && !status) classes.push('day-today');

            let symbol = '';
            if (status === 'done') symbol = '✔';
            else if (status === 'skip') symbol = '➖';
            else if (status === 'miss') symbol = '❌';

            const noteDot = hasNote ? '<span class="note-dot"></span>' : '';

            const habitColor = habitData?.color || 'var(--status-done)';
            const cellStyle = status === 'done' ? `style="background-color: ${habitColor} !important; box-shadow: 0 0 10px ${habitColor}66 !important;"` : '';

            html += `<td class="${classes.join(' ')}"
                         ${cellStyle}
                         data-habit-id="${habit.id}"
                         data-date="${dateStr}"
                         data-status="${status || ''}"
                         title="${dateStr}${hasNote ? ' 📝' : ''}"
                    >${symbol}${noteDot}</td>`;
        }

        // Goal column
        html += `<td class="col-goal-val">${goalTarget}</td>`;

        // Achieved column
        html += `<td class="col-achieved-val ${goalMet ? 'met' : ''}">${goalCurrent}</td>`;

        html += '</tr>';
        return html;
    },

    _bindCellEvents() {
        // ALL day-cells are clickable — no future filter
        document.querySelectorAll('.calendar-table td.day-cell').forEach(cell => {
            // Left click — cycle status
            cell.addEventListener('click', (e) => {
                e.stopPropagation();
                const habitId = parseInt(cell.dataset.habitId);
                const date = cell.dataset.date;
                const currentStatus = cell.dataset.status;
                this._cycleStatus(habitId, date, currentStatus, cell);
            });

            // Right click — add note
            cell.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                const habitId = parseInt(cell.dataset.habitId);
                const date = cell.dataset.date;
                NoteModal.open(habitId, date);
            });
        });
    },

    async _cycleStatus(habitId, date, currentStatus, cell) {
        const skipEnabled = this.data?.skip_enabled !== false;

        // Calculate next status
        let nextStatus;
        if (!currentStatus || currentStatus === 'undefined' || currentStatus === '') {
            nextStatus = 'done';
        } else if (currentStatus === 'done') {
            nextStatus = skipEnabled ? 'skip' : 'miss';
        } else if (currentStatus === 'skip') {
            nextStatus = 'miss';
        } else if (currentStatus === 'miss') {
            nextStatus = ''; // loop back to none
        }

        // --- OPTIMISTIC UI UPDATE ---
        const habitData = App.habitsData?.find(h => h.id === habitId);
        const habitColor = habitData?.color || 'var(--status-done)';
        const row = cell.closest('tr');
        const achievedCell = row.querySelector('.col-achieved-val');
        let achievedCount = parseInt(achievedCell.textContent) || 0;

        // 1. Update Cell Status
        cell.dataset.status = nextStatus || '';
        cell.className = 'day-cell'; // Reset classes
        if (cell.dataset.date === this.data.today && !nextStatus) cell.classList.add('day-today');
        if (nextStatus) cell.classList.add(`status-${nextStatus}`);

        // 2. Update Style (Color/Shadow)
        if (nextStatus === 'done') {
            cell.style.cssText = `background-color: ${habitColor} !important; box-shadow: 0 0 10px ${habitColor}66 !important;`;
        } else {
            cell.style.cssText = '';
        }

        // 3. Update Symbol
        let symbol = '';
        if (nextStatus === 'done') symbol = '✔';
        else if (nextStatus === 'skip') symbol = '➖';
        else if (nextStatus === 'miss') symbol = '❌';

        // Persist Note Dot
        const hasNote = cell.title.includes('📝'); // Simple check based on title
        const noteDot = hasNote ? '<span class="note-dot"></span>' : '';
        cell.innerHTML = symbol + noteDot;

        // 4. Update Achieved Count (Manual Logic)
        // If moving TO done: +1
        // If moving FROM done: -1
        if (nextStatus === 'done') achievedCount++;
        else if (currentStatus === 'done') achievedCount--;

        achievedCell.textContent = achievedCount;

        // Optimistic goal check (simple)
        const goalTarget = parseInt(row.querySelector('.col-goal-val').textContent);
        if (goalTarget && achievedCount >= goalTarget) achievedCell.classList.add('met');
        else achievedCell.classList.remove('met');


        // --- API CALL ---
        try {
            const result = await API.post('/api/entries', {
                habit_id: habitId,
                date: date,
                status: nextStatus,
            });

            if (result.status === 'done') {
                Animations.celebrate(cell);
            }

            // Sync data quietly in background without full rerender
            // We only need to update App.habitsData logic if we rely on it elsewhere immediately
            // For now, doing nothing is fine until page refresh/navigate

        } catch (e) {
            // Revert on failure (simple revert: refresh)
            console.error('Update failed, reverting', e);
            Toast.show('Failed to update: ' + e.message, 'error');
            await this.load(); // Fallback to full reload on error
            this.render();
        }
    },

    _dateStr(data, day) {
        return `${data.year}-${String(data.month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    },

    _formatMonthLabel() {
        const months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];
        return `${months[this.currentMonth - 1]}, ${this.currentYear}`;
    },

    _escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },

    _initSortable() {
        const el = document.querySelector('.calendar-table tbody');
        if (!el || !window.Sortable) return;

        // Clean up old instance if exists
        if (this.sortable) {
            this.sortable.destroy();
            this.sortable = null;
        }

        this.sortable = Sortable.create(el, {
            animation: 150,
            handle: '.habit-name-cell',
            ghostClass: 'sortable-ghost',
            dragClass: 'sortable-drag',
            onEnd: async () => {
                const order = Array.from(el.querySelectorAll('tr')).map(tr => parseInt(tr.dataset.id));
                try {
                    await API.put('/api/habits/reorder', { order });
                } catch (e) {
                    Toast.show('Failed to save order: ' + e.message, 'error');
                }
            }
        });
    }
};
