// Substrate Walker — Lore Cache Loader
// Loads pre-generated lore from the embedded cache for instant results

class LoreCacheLoader {
    constructor() {
        this.cache = new Map(); // cell_key → lore
        this.districtCache = new Map(); // district_key → lore
        this.loaded = false;
    }

    async load(fetchUrl = 'lore_pack.json') {
        try {
            const response = await fetch(fetchUrl);
            const data = await response.json();
            this.cache = new Map(Object.entries(data));
            this.loaded = true;
            console.log(`Lore cache loaded: ${this.cache.size} entries`);
            return true;
        } catch (e) {
            console.warn('Lore cache load failed:', e);
            return false;
        }
    }

    get(seed) {
        if (!this.loaded) return null;
        return this.cache.get(String(seed));
    }

    getRandom() {
        if (!this.loaded || this.cache.size === 0) return null;
        const keys = Array.from(this.cache.keys());
        const key = keys[Math.floor(Math.random() * keys.length)];
        return this.cache.get(key);
    }

    size() {
        return this.cache.size;
    }
}

window.LoreCacheLoader = LoreCacheLoader;
