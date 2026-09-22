// Ghost Substrate — Replay ghost that shows JEPA prediction errors

class GhostSubstrate {
    constructor(walker) {
        this.walker = walker;
        this.recording = [];        // current run
        this.ghostPath = [];        // past run replay
        this.maxGhostLength = 500;  // max waypoints
        this.recordingStarted = Date.now();
        this.errorHistory = [];     // JEPA prediction errors
    }

    // Record a position with prediction error
    record(x, y, angle, predictionError) {
        this.recording.push({
            x, y, angle,
            error: predictionError,
            timestamp: Date.now() - this.recordingStarted,
        });

        if (this.recording.length > this.maxGhostLength) {
            this.recording.shift();
        }
    }

    // Promote current recording to ghost
    promoteToGhost() {
        this.ghostPath = [...this.recording];
        this.recording = [];
        this.recordingStarted = Date.now();
        this.errorHistory = [];
    }

    // Get current ghost waypoint (matching player's current step)
    getCurrentGhostWaypoint(currentStep) {
        if (this.ghostPath.length === 0) return null;
        const idx = Math.min(currentStep, this.ghostPath.length - 1);
        return this.ghostPath[idx];
    }

    // Compute prediction error between predicted cell and actual cell
    computePredictionError(predictedHeight, actualHeight) {
        return Math.abs(predictedHeight - actualHeight) / 30; // normalize 0..1
    }

    // Save ghost to localStorage
    saveGhost() {
        try {
            localStorage.setItem('ghost_substrate', JSON.stringify({
                path: this.ghostPath,
                saved_at: Date.now(),
            }));
        } catch (e) {}
    }

    // Load ghost from localStorage
    loadGhost() {
        try {
            const data = JSON.parse(localStorage.getItem('ghost_substrate') || 'null');
            if (data && data.path) {
                this.ghostPath = data.path;
                return true;
            }
        } catch (e) {}
        return false;
    }

    getGhostLength() {
        return this.ghostPath.length;
    }

    getErrorStats() {
        if (this.errorHistory.length === 0) return { avg: 0, max: 0 };
        const avg = this.errorHistory.reduce((a, b) => a + b, 0) / this.errorHistory.length;
        const max = Math.max(...this.errorHistory);
        return { avg, max };
    }
}

// Export to window
window.GhostSubstrate = GhostSubstrate;
