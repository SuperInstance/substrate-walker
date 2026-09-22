// Substrate Walker — Streaming Lore
// Shows lore tokens as they arrive (character-by-character reveal)

class StreamingLore {
    constructor(loreElement) {
        this.element = loreElement;
        this.queue = [];
        this.typing = false;
        this.charDelay = 25; // ms per char
    }

    setElement(el) {
        this.element = el;
    }

    stream(text) {
        if (!this.element) return;
        this.queue.push(text);
        if (!this.typing) {
            this._processQueue();
        }
    }

    async _processQueue() {
        this.typing = true;
        while (this.queue.length > 0) {
            const text = this.queue.shift();
            // First clear with fade
            this.element.style.transition = 'opacity 0.15s';
            this.element.style.opacity = '0';

            await new Promise(r => setTimeout(r, 150));
            this.element.style.opacity = '1';

            // Type each character
            this.element.textContent = '';
            for (let i = 0; i < text.length; i++) {
                this.element.textContent += text[i];
                await new Promise(r => setTimeout(r, this.charDelay));
            }

            // Pause between lores
            await new Promise(r => setTimeout(r, 500));
        }
        this.typing = false;
    }

    clear() {
        this.queue = [];
        this.typing = false;
        if (this.element) {
            this.element.textContent = '';
        }
    }
}

window.StreamingLore = StreamingLore;
