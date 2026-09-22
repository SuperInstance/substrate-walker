// Test the frontal cortex cache logic without hitting the API

class MockFrontalCortex {
    constructor() {
        this.loreCache = new Map();
        this.districtCache = new Map();
        this.apiCalls = 0;
        this.cacheHits = 0;
    }

    async onMove(x, y, lastCellKey, lastDistrictKey) {
        const cellKey = `${x},${y}`;
        const districtKey = `${Math.floor(x / 8)},${Math.floor(y / 8)}`;
        const fired = [];

        if (districtKey !== lastDistrictKey) {
            lastDistrictKey = districtKey;
            if (this.districtCache.has(districtKey)) {
                fired.push({ kind: 'district', lore: this.districtCache.get(districtKey), cached: true });
                this.cacheHits++;
            } else {
                this.apiCalls++;
                const name = `District ${districtKey}`;
                this.districtCache.set(districtKey, name);
                fired.push({ kind: 'district', lore: name, cached: false });
            }
        }

        if (cellKey !== lastCellKey) {
            lastCellKey = cellKey;
            if (this.loreCache.has(cellKey)) {
                this.cacheHits++;
            } else {
                this.apiCalls++;
                const name = `Building ${cellKey}`;
                this.loreCache.set(cellKey, name);
                fired.push({ kind: 'building', lore: name, cached: false });
            }
        }

        return { fired, lastCellKey, lastDistrictKey };
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

async function simulate() {
    console.log("Frontal Cortex Cache Test\n");
    const cortex = new MockFrontalCortex();
    let lastCellKey = null;
    let lastDistrictKey = null;

    // Simulate walking a long path through the city
    const path = [];
    for (let x = 0; x < 32; x++) {
        for (let y = 0; y < 32; y++) {
            path.push([x, y]);
        }
    }

    console.log(`Simulating ${path.length} steps through 32x32 grid...\n`);

    for (const [x, y] of path) {
        const result = await cortex.onMove(x, y, lastCellKey, lastDistrictKey);
        lastCellKey = result.lastCellKey;
        lastDistrictKey = result.lastDistrictKey;

        if (result.fired.length > 0) {
            for (const f of result.fired) {
                const tag = f.cached ? '💾' : '🔥';
                console.log(`${tag} ${f.kind}: ${f.lore}`);
            }
        }
    }

    // Re-walk same path - should all be cache hits
    console.log(`\nRe-walking same path (all cache hits)...\n`);
    lastCellKey = null;
    lastDistrictKey = null;
    for (const [x, y] of path) {
        const result = await cortex.onMove(x, y, lastCellKey, lastDistrictKey);
        lastCellKey = result.lastCellKey;
        lastDistrictKey = result.lastDistrictKey;
    }

    const stats = cortex.getStats();
    console.log(`\n=== Final Stats ===`);
    console.log(`Total steps: ${path.length * 2}`);
    console.log(`API calls: ${stats.apiCalls}`);
    console.log(`Cache hits: ${stats.cacheHits}`);
    console.log(`Cell cache: ${stats.cellCache} entries`);
    console.log(`District cache: ${stats.districtCache} entries`);
    console.log(`Cache hit rate: ${(100 * stats.cacheHits / (path.length * 2)).toFixed(1)}%`);
    console.log(`API reduction: ${(100 * (1 - stats.apiCalls / (path.length * 2))).toFixed(1)}%`);
}

simulate().catch(console.error);
