/**
 * Animations — confetti party popper effect.
 */
const Animations = {
    enabled: true,

    init(enabled) {
        this.enabled = enabled !== false;
    },

    /**
     * Fire confetti from a given element position.
     */
    celebrate(element) {
        if (!this.enabled) return;
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

        // Add pulse to the cell
        element.classList.add('cell-complete-animation');
        setTimeout(() => element.classList.remove('cell-complete-animation'), 300);

        // Create confetti
        this._fireConfetti(element);
    },

    _fireConfetti(origin) {
        const container = document.createElement('div');
        container.className = 'confetti-container';
        document.body.appendChild(container);

        const rect = origin.getBoundingClientRect();
        const x = rect.left + rect.width / 2;
        const y = rect.top + rect.height / 2;

        const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'];
        const emojis = ['🎉', '🎊', '✨', '⭐', '🌟', '💫'];

        for (let i = 0; i < 30; i++) {
            const particle = document.createElement('div');
            const isEmoji = Math.random() > 0.7;

            if (isEmoji) {
                particle.textContent = emojis[Math.floor(Math.random() * emojis.length)];
                particle.style.fontSize = `${12 + Math.random() * 8}px`;
            } else {
                particle.style.width = `${4 + Math.random() * 6}px`;
                particle.style.height = particle.style.width;
                particle.style.background = colors[Math.floor(Math.random() * colors.length)];
                particle.style.borderRadius = Math.random() > 0.5 ? '50%' : '2px';
            }

            particle.style.position = 'fixed';
            particle.style.left = `${x}px`;
            particle.style.top = `${y}px`;
            particle.style.pointerEvents = 'none';
            particle.style.zIndex = '10001';

            container.appendChild(particle);

            // Animate with requestAnimationFrame
            const angle = (Math.random() * Math.PI * 2);
            const velocity = 3 + Math.random() * 5;
            const vx = Math.cos(angle) * velocity;
            const vy = Math.sin(angle) * velocity - 3; // Bias upward
            const gravity = 0.15;
            const rotationSpeed = (Math.random() - 0.5) * 10;

            let px = x, py = y, frame = 0;
            let currentVy = vy;
            let rotation = 0;

            const animate = () => {
                frame++;
                px += vx;
                currentVy += gravity;
                py += currentVy;
                rotation += rotationSpeed;

                const opacity = Math.max(0, 1 - frame / 60);
                particle.style.left = `${px}px`;
                particle.style.top = `${py}px`;
                particle.style.opacity = opacity;
                particle.style.transform = `rotate(${rotation}deg)`;

                if (frame < 60 && opacity > 0) {
                    requestAnimationFrame(animate);
                } else {
                    particle.remove();
                }
            };

            // Stagger start
            setTimeout(() => requestAnimationFrame(animate), Math.random() * 100);
        }

        // Clean up container
        setTimeout(() => container.remove(), 2000);
    },

    /**
     * Trigger streak milestone effect on a habit row.
     */
    streakMilestone(element) {
        if (!this.enabled) return;
        element.classList.add('streak-glow');
        setTimeout(() => element.classList.remove('streak-glow'), 600);
    }
};
