document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/api/analytics');
        const data = await response.json();

        updateSummary(data);
        renderTrendChart(data.daily_trend);
        renderConsistencyChart(data.habit_performance);
        renderBreakdown(data.habit_performance);

        lucide.createIcons();
    } catch (error) {
        console.error('Failed to load analytics:', error);
        document.querySelector('.analytics-container').innerHTML = `
            <div style="text-align:center; padding: 4rem; color: var(--text-muted);">
                <i data-lucide="alert-triangle" style="width: 48px; height: 48px; margin-bottom: 1rem;"></i>
                <h2>Failed to load analytics data</h2>
                <p>Please try refreshing the page.</p>
            </div>
        `;
        lucide.createIcons();
    }
});

function updateSummary(data) {
    const sum = data.summary;
    // Animate numbers
    animateValue('total-completions', 0, sum.total_completions, 1000);
    animateValue('best-streak', 0, sum.best_streak, 1000);
    animateValue('total-habits', 0, sum.total_habits, 1000);

    // Calculate avg consistency
    let avg = 0;
    if (data.habit_performance.length > 0) {
        const totalRate = data.habit_performance.reduce((acc, h) => acc + h.completion_rate, 0);
        avg = Math.round(totalRate / data.habit_performance.length);
    }
    document.getElementById('completion-rate').textContent = `${avg}%`;
}

function animateValue(id, start, end, duration) {
    const obj = document.getElementById(id);
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = Math.floor(progress * (end - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

function renderTrendChart(trendData) {
    const canvas = document.getElementById('trendChart');
    const ctx = canvas.getContext('2d');

    // Get theme colors safely
    const style = getComputedStyle(document.body);
    let primaryColor = style.getPropertyValue('--primary').trim() || '#4CAF50';
    const gridColor = style.getPropertyValue('--border-color').trim() || '#333';
    const textColor = style.getPropertyValue('--text-muted').trim() || '#888';
    const cardBg = style.getPropertyValue('--bg-card').trim() || '#1e1e1e';
    const mainText = style.getPropertyValue('--text-main').trim() || '#fff';

    // Create Gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, 350);
    // Use primary color but ensure it's valid, otherwise fallback
    gradient.addColorStop(0, primaryColor + '80'); // 50% opacity
    gradient.addColorStop(1, primaryColor + '00'); // 0% opacity

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: trendData.map(d => formatDate(d.date)),
            datasets: [{
                label: 'Completions',
                data: trendData.map(d => d.count),
                borderColor: primaryColor,
                backgroundColor: gradient,
                fill: true,
                tension: 0.4,
                pointRadius: 0, // Clean look, show on hover
                pointHoverRadius: 6,
                pointHitRadius: 20,
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 800,
                easing: 'easeOutQuart'
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: cardBg,
                    titleColor: mainText,
                    bodyColor: mainText,
                    borderColor: gridColor,
                    borderWidth: 1,
                    padding: 10,
                    displayColors: false,
                    callbacks: {
                        label: function (context) {
                            return context.parsed.y + ' completions';
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        color: textColor,
                        maxTicksLimit: 6,
                        font: { family: 'Inter', size: 11 }
                    }
                },
                y: {
                    grid: {
                        color: gridColor,
                        borderDash: [5, 5],
                        drawBorder: false
                    },
                    ticks: {
                        color: textColor,
                        stepSize: 1,
                        precision: 0,
                        font: { family: 'Inter', size: 11 }
                    },
                    beginAtZero: true
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

function renderConsistencyChart(habits) {
    const ctx = document.getElementById('consistencyChart').getContext('2d');

    const style = getComputedStyle(document.body);
    const textColor = style.getPropertyValue('--text-muted').trim() || '#888';

    // Sort top 8 by completion rate
    const topHabits = habits.slice(0, 8);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topHabits.map(h => h.name),
            datasets: [{
                label: 'Consistency %',
                data: topHabits.map(h => h.completion_rate),
                backgroundColor: topHabits.map(h => h.color),
                borderRadius: 6,
                barPercentage: 0.6,
                categoryPercentage: 0.8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            animation: { duration: 800 },
            plugins: {
                legend: { display: false },
                tooltip: {
                    displayColors: false,
                    callbacks: {
                        label: function (context) {
                            return context.parsed.x + '% Consistency';
                        }
                    }
                }
            },
            scales: {
                x: {
                    max: 100,
                    grid: { display: false },
                    ticks: {
                        color: textColor,
                        font: { family: 'Inter', size: 11 }
                    }
                },
                y: {
                    grid: { display: false },
                    ticks: {
                        color: style.getPropertyValue('--text-main').trim(),
                        font: { family: 'Inter', weight: '500', size: 12 }
                    }
                }
            }
        }
    });
}

function renderBreakdown(habits) {
    const list = document.getElementById('habit-breakdown-list');

    if (habits.length === 0) {
        list.innerHTML = '<div class="habit-item" style="justify-content:center;">No habits found.</div>';
        return;
    }

    list.innerHTML = habits.map(h => `
        <div class="habit-item">
            <div class="habit-info">
                <div class="habit-color" style="background-color: ${h.color}"></div>
                <div class="habit-name">${escapeHtml(h.name)}</div>
            </div>
            <div class="habit-metrics">
                <div class="metric">
                    Streak: <span>${h.current_streak}</span>
                </div>
                <div class="metric">
                    Best: <span>${h.best_streak}</span>
                </div>
                <div class="metric">
                    Consistency: <span>${h.completion_rate}%</span>
                </div>
            </div>
        </div>
    `).join('');
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const [y, m, d] = dateStr.split('-').map(Number);
    const date = new Date(y, m - 1, d);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
