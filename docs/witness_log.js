// Substrate Walker — Witness Log
// Records every meaningful event in the player's journey

class WitnessLog {
    constructor() {
        this.entries = [];
        this.sessionId = `witness-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`;
    }

    record(eventType, data) {
        const entry = {
            id: this.entries.length + 1,
            session: this.sessionId,
            timestamp: new Date().toISOString(),
            event: eventType,
            data: data,
        };

        // Compute prev_hash → this_hash chain (FNV-1a 64-bit)
        if (this.entries.length > 0) {
            const prev = this.entries[this.entries.length - 1];
            entry.prev_hash = prev.this_hash;
        } else {
            entry.prev_hash = '0x' + (0xcbf29ce484222325).toString(16);
        }
        entry.this_hash = this.computeHash(JSON.stringify(entry));

        this.entries.push(entry);
        return entry;
    }

    computeHash(s) {
        let h = 0xcbf29ce484222325n;
        const FNV_PRIME = 0x100000001b3n;
        const MASK = (1n << 64n) - 1n;
        for (let i = 0; i < s.length; i++) {
            h ^= BigInt(s.charCodeAt(i));
            h = (h * FNV_PRIME) & MASK;
        }
        return '0x' + h.toString(16).padStart(16, '0');
    }

    // Get entries by type
    getByType(type) {
        return this.entries.filter(e => e.event === type);
    }

    // Verify chain integrity
    verify() {
        const MASK = (1n << 64n) - 1n;
        const FNV_PRIME = 0x100000001b3n;

        for (let i = 0; i < this.entries.length; i++) {
            const entry = this.entries[i];
            // Recompute hash
            const entryCopy = {...entry};
            delete entryCopy.this_hash;
            const recomputed = this.computeHash(JSON.stringify(entryCopy));

            if (recomputed !== entry.this_hash) {
                return { valid: false, broken_at: i, reason: 'hash mismatch' };
            }

            // Check chain
            if (i > 0 && entry.prev_hash !== this.entries[i-1].this_hash) {
                return { valid: false, broken_at: i, reason: 'prev_hash mismatch' };
            }
        }
        return { valid: true, count: this.entries.length };
    }

    // Save to localStorage
    save(key = 'witness-log-default') {
        localStorage.setItem(key, JSON.stringify(this.entries));
    }

    // Load from localStorage
    load(key = 'witness-log-default') {
        const data = localStorage.getItem(key);
        if (data) {
            this.entries = JSON.parse(data);
            return true;
        }
        return false;
    }

    export() {
        return JSON.stringify(this.entries, null, 2);
    }

    // Stats
    stats() {
        const types = {};
        for (const e of this.entries) {
            types[e.event] = (types[e.event] || 0) + 1;
        }
        return {
            total: this.entries.length,
            session: this.sessionId,
            types,
        };
    }
}

window.WitnessLog = WitnessLog;
