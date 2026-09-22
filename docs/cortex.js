// Substrate Walker — Frontal Cortex
//
// Like the human frontal cortex, this module only fires at critical moments:
//   1. Player enters a NEW cell (first visit)        → building description
//   2. Player enters a NEW district (8-cell region)  → district name + lore
//   3. Player is IDLE for >2 seconds (looking around) → ambient observation
//   4. Player presses L (look) or E (examine)        → on-demand narration
//
// All routine movement is FREE (no API calls). The agent only intervenes
// when something genuinely new happens.
//
// Strategy:
//   - Use seed-mini (cheap) for building names / district names (ideation)
//   - Use deepseek (better) for narrative threads (one thread per district)
//   - Cache lore on cell metadata; never re-generate

const API_CONFIG = {
    // DeepInfra (cheapest, fast)
    deepinfra_base: 'https://api.deepinfra.com/v1/openai',
    deepseek_model: 'deepseek-ai/DeepSeek-V3',
    seed_mini_model: 'Qwen/Qwen2.5-7B-Instruct', // small + fast

    // Generation params
    seed_max_tokens: 60,    // seed-mini: short, punchy
    deepseek_max_tokens: 150, // deepseek: deeper narrative

    // Critical moments
    idle_threshold_ms: 2000, // 2 seconds idle
    district_size: 8,        // 8x8 districts

    // Cache
    cache_max_entries: 500,
};

class FrontalCortex {
    constructor(walker) {
        this.walker = walker;
        this.apiKey = null; // Set via setApiKey()
        this.loreCache = new Map();   // cell_key → lore
        this.districtCache = new Map(); // district_key → lore
        this.narrativeThread = [];    // accumulated deepseek thread per district
        this.lastMoveTime = performance.now();
        this.lastCellKey = null;
        this.lastDistrictKey = null;
        this.idleTimer = null;
        this.busy = false;

        // Stats
        this.apiCalls = 0;
        this.cacheHits = 0;
    }

    setApiKey(key) {
        this.apiKey = key;
    }

    // Call when the walker moves to a new cell.
    // Returns: { fired: bool, lore?: string, kind?: string }
    async onMove(x, y, angle) {
        const cellKey = `${x},${y}`;
        const districtKey = `${Math.floor(x / API_CONFIG.district_size)},${Math.floor(y / API_CONFIG.district_size)}`;

        const now = performance.now();
        this.lastMoveTime = now;
        if (this.idleTimer) clearTimeout(this.idleTimer);
        this.idleTimer = setTimeout(() => this.onIdle(), API_CONFIG.idle_threshold_ms);

        const fired = { fired: false };

        // Critical moment: new district
        if (districtKey !== this.lastDistrictKey) {
            this.lastDistrictKey = districtKey;
            fired.fired = true;
            fired.kind = 'district';
            if (this.districtCache.has(districtKey)) {
                fired.lore = this.districtCache.get(districtKey);
                this.cacheHits++;
            } else {
                fired.lore = await this.generateDistrictName(districtKey);
                if (fired.lore) {
                    this.districtCache.set(districtKey, fired.lore);
                }
            }
        }

        // Critical moment: new cell with a building
        if (cellKey !== this.lastCellKey) {
            this.lastCellKey = cellKey;
            if (this.loreCache.has(cellKey)) {
                this.cacheHits++;
            } else {
                const cellHeight = this.walker.exports.get_cell_height(x, y);
                if (cellHeight > 0) {
                    fired.fired = true;
                    fired.kind = 'building';
                    fired.lore = await this.generateBuildingName(cellKey, x, y, cellHeight);
                    if (fired.lore) {
                        this.loreCache.set(cellKey, fired.lore);
                    }
                }
            }
        }

        return fired;
    }

    // Player idle — observe surroundings
    async onIdle() {
        const x = this.walker.exports.camera_x();
        const y = this.walker.exports.camera_y();
        const districtKey = `${Math.floor(x / API_CONFIG.district_size)},${Math.floor(y / API_CONFIG.district_size)}`;

        // Add to narrative thread
        const observation = await this.observe(x, y, this.walker.exports.camera_angle());
        if (observation && this.walker.onLore) {
            this.walker.onLore({
                kind: 'perception',
                text: observation,
                district: districtKey,
            });
        }
    }

    // Player pressed L or E
    async onExamine() {
        const x = this.walker.exports.camera_x();
        const y = this.walker.exports.camera_y();
        const angle = this.walker.exports.camera_angle();
        return await this.observe(x, y, angle, true);
    }

    async generateBuildingName(cellKey, x, y, height) {
        if (!this.apiKey) return null;
        if (this.busy) return null;

        this.busy = true;
        try {
            const prompt = `Name a cyberpunk building in 3-6 words. Building #${cellKey} is ${height} stories tall. Return ONLY the name, no punctuation.`;

            const result = await this.callAPI(
                API_CONFIG.seed_mini_model,
                prompt,
                API_CONFIG.seed_max_tokens
            );
            this.apiCalls++;
            return result?.trim() || null;
        } finally {
            this.busy = false;
        }
    }

    async generateDistrictName(districtKey) {
        if (!this.apiKey) return null;
        if (this.busy) return null;

        this.busy = true;
        try {
            const prompt = `Name a cyberpunk district in 2-4 words. District #${districtKey}. Return ONLY the name.`;

            const result = await this.callAPI(
                API_CONFIG.seed_mini_model,
                prompt,
                API_CONFIG.seed_max_tokens
            );
            this.apiCalls++;
            return result?.trim() || null;
        } finally {
            this.busy = false;
        }
    }

    async observe(x, y, angle, detailed = false) {
        if (!this.apiKey) return null;
        if (this.busy) return null;

        this.busy = true;
        try {
            const districtKey = `${Math.floor(x / API_CONFIG.district_size)},${Math.floor(y / API_CONFIG.district_size)}`;
            const district = this.districtCache.get(districtKey) || `District ${districtKey}`;
            const dirName = this.angleToCompass(angle);

            // Build on the narrative thread
            const threadContext = this.narrativeThread.slice(-3).join(' | ');
            const depth = detailed ? 'Describe what you see in one vivid sentence.' : 'One brief observation.';

            const prompt = `Cyberpunk noir. Player is in ${district}, looking ${dirName}. ${depth}
${threadContext ? 'Previous observations: ' + threadContext : ''}
Return ONLY the observation, no preamble.`;

            const result = await this.callAPI(
                API_CONFIG.deepseek_model,
                prompt,
                API_CONFIG.deepseek_max_tokens
            );
            this.apiCalls++;
            if (result) {
                const cleaned = result.trim();
                this.narrativeThread.push(cleaned);
                if (this.narrativeThread.length > 10) {
                    this.narrativeThread.shift();
                }
                return cleaned;
            }
            return null;
        } finally {
            this.busy = false;
        }
    }

    angleToCompass(angle) {
        // Angle 0 = east, π/2 = north
        const deg = (angle * 180 / Math.PI) % 360;
        if (deg < 0) deg += 360;
        const dirs = ['east', 'northeast', 'north', 'northwest', 'west', 'southwest', 'south', 'southeast'];
        return dirs[Math.round(deg / 45) % 8];
    }

    async callAPI(model, prompt, maxTokens) {
        try {
            const response = await fetch(`${API_CONFIG.deepinfra_base}/chat/completions`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    model: model,
                    messages: [{ role: 'user', content: prompt }],
                    max_tokens: maxTokens,
                    temperature: 0.85,
                    stream: false,
                }),
            });

            if (!response.ok) {
                console.warn('API call failed:', response.status);
                return null;
            }

            const data = await response.json();
            return data.choices?.[0]?.message?.content || null;
        } catch (err) {
            console.warn('API error:', err.message);
            return null;
        }
    }

    getStats() {
        return {
            apiCalls: this.apiCalls,
            cacheHits: this.cacheHits,
            cellCache: this.loreCache.size,
            districtCache: this.districtCache.size,
        };
    }
}

// Export to window for the main app
window.FrontalCortex = FrontalCortex;
