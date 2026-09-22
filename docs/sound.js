// Substrate Walker — Adaptive Soundtrack
// Procedural cyberpunk soundscape that responds to:
// - Player movement (footstep bass)
// - District transitions (atmospheric pad shifts)
// - Building heights (ambient drone)
// - JEPA prediction errors (magenta glitch)

class AdaptiveSoundtrack {
    constructor() {
        this.ctx = null;
        this.masterGain = null;
        this.footstepGain = null;
        this.atmosphereGain = null;
        this.glitchGain = null;
        this.enabled = false;
        this.lastFootstep = 0;
        this.lastDistrict = null;
        this.glitchActive = false;
    }

    async init() {
        try {
            this.ctx = new (window.AudioContext || window.webkitAudioContext)();
            this.masterGain = this.ctx.createGain();
            this.masterGain.gain.value = 0.3;
            this.masterGain.connect(this.ctx.destination);

            // Footstep bass
            this.footstepGain = this.ctx.createGain();
            this.footstepGain.gain.value = 0.0;
            this.footstepGain.connect(this.masterGain);

            // Atmosphere pad
            this.atmosphereGain = this.ctx.createGain();
            this.atmosphereGain.gain.value = 0.0;
            this.atmosphereGain.connect(this.masterGain);

            // Glitch (JEPA errors)
            this.glitchGain = this.ctx.createGain();
            this.glitchGain.gain.value = 0.0;
            this.glitchGain.connect(this.masterGain);

            // Start atmosphere drone
            this.startAtmosphere();
            this.enabled = true;
            return true;
        } catch (e) {
            console.warn("Audio init failed:", e);
            return false;
        }
    }

    startAtmosphere() {
        if (!this.ctx) return;
        // Cyberpunk drone: 3 oscillators at A2, E3, A3
        const freqs = [110, 165, 220];
        const oscs = [];
        for (const f of freqs) {
            const osc = this.ctx.createOscillator();
            osc.type = 'sawtooth';
            osc.frequency.value = f;
            const g = this.ctx.createGain();
            g.gain.value = 0.05;
            osc.connect(g);
            g.connect(this.atmosphereGain);
            osc.start();
            oscs.push({ osc, gain: g });
        }
        this.atmosphereOscs = oscs;
    }

    footstep() {
        if (!this.enabled || !this.ctx) return;
        const now = this.ctx.currentTime;
        if (now - this.lastFootstep < 0.3) return;
        this.lastFootstep = now;

        // Quick bass hit
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(80, now);
        osc.frequency.exponentialRampToValueAtTime(40, now + 0.1);
        gain.gain.setValueAtTime(0.3, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
        osc.connect(gain);
        gain.connect(this.footstepGain);
        osc.start(now);
        osc.stop(now + 0.15);
    }

    setDistrictIntensity(intensity) {
        if (!this.enabled || !this.atmosphereGain) return;
        // intensity 0..1 controls atmosphere volume
        const now = this.ctx.currentTime;
        this.atmosphereGain.gain.linearRampToValueAtTime(intensity * 0.15, now + 0.5);
    }

    glitch(magnitude) {
        if (!this.enabled || !this.ctx) return;
        const now = this.ctx.currentTime;
        if (magnitude < 0.1) return;

        // High-pitched digital glitch
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'square';
        osc.frequency.value = 800 + magnitude * 2000;
        gain.gain.setValueAtTime(0.05 * magnitude, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);
        osc.connect(gain);
        gain.connect(this.glitchGain);
        osc.start(now);
        osc.stop(now + 0.05);
    }

    setEnabled(enabled) {
        this.enabled = enabled;
        if (this.masterGain) {
            this.masterGain.gain.value = enabled ? 0.3 : 0.0;
        }
    }
}

window.AdaptiveSoundtrack = AdaptiveSoundtrack;
