// Substrate Walker — WebGL + WASM bridge with frontal-cortex integration.

class SubstrateWalker {
    constructor(canvas, wasmUrl = 'walker.wasm') {
        this.canvas = canvas;
        this.wasmUrl = wasmUrl;
        this.engine = null;
        this.memory = null;
        this.exports = null;
        this.gl = null;
        this.program = null;
        this.texture = null;
        this.fontAtlas = null;
        this.lastTime = performance.now();
        this.frameCount = 0;
        this.fps = 0;
        this.fpsAcc = 0;
        this.keys = new Set();
        this.chainValid = false;
        this.cortex = null;
        this.apiKey = null;
    }

    async init() {
        // Load WASM
        const response = await fetch(this.wasmUrl);
        const bytes = await response.arrayBuffer();
        const module = await WebAssembly.compile(bytes);
        const instance = await WebAssembly.instantiate(module, {
            env: {}
        });
        this.exports = instance.exports;
        this.memory = this.exports.memory;

        this.bufferPtr = this.exports.buffer_ptr();
        this.bufferSize = this.exports.buffer_size();

        this.initWebGL();
        this.bindKeys();

        this.chainValid = this.exports.verify_chain();
        console.log('Chain valid:', this.chainValid);
        console.log('Grid cells:', this.exports.cell_count());
        console.log('Grid first hash: 0x' + this.exports.grid_hash_first().toString(16));
        console.log('Grid last hash: 0x' + this.exports.grid_hash_last().toString(16));

        // Set up frontal cortex
        this.cortex = new FrontalCortex(this);
        this.cortex.setApiKey(this.apiKey);

        this.cortex.walker = this; // Wire back-pointer
        this.lastTime = performance.now();

        // Initial district
        const x = this.exports.camera_x();
        const y = this.exports.camera_y();
        const result = await this.cortex.onMove(x, y, 0);
        if (result.fired && result.lore && this.onLore) {
            this.onLore({ kind: result.kind, text: result.lore });
        }

        requestAnimationFrame(this.render.bind(this));
    }

    initWebGL() {
        this.gl = this.canvas.getContext('webgl2') || this.canvas.getContext('webgl');
        if (!this.gl) {
            alert('WebGL not supported');
            return;
        }

        const vsSource = `
            attribute vec2 a_pos;
            varying vec2 v_uv;
            void main() {
                v_uv = vec2((a_pos.x + 1.0) * 0.5, 1.0 - (a_pos.y + 1.0) * 0.5);
                gl_Position = vec4(a_pos, 0.0, 1.0);
            }
        `;

        const fsSource = `
            precision mediump float;
            varying vec2 v_uv;
            uniform sampler2D u_buffer;
            uniform sampler2D u_font;
            uniform vec2 u_resolution;
            uniform vec2 u_gridSize;

            void main() {
                vec4 cell = texture2D(u_buffer, v_uv);
                float glyphIdx = cell.r * 255.0;
                vec3 cellColor = cell.gba;
                float cellAlpha = cell.a;

                vec2 cellCoord = floor(v_uv * u_gridSize);
                vec2 localUV = fract(v_uv * u_gridSize);

                float atlasCols = 16.0;
                float atlasX = mod(glyphIdx, atlasCols);
                float atlasY = floor(glyphIdx / atlasCols);

                vec2 atlasUV = (vec2(atlasX, atlasY) + localUV) / atlasCols;
                atlasUV.y = 1.0 - atlasUV.y;

                vec4 glyph = texture2D(u_font, atlasUV);
                vec3 finalColor = cellColor * glyph.r;
                gl_FragColor = vec4(finalColor, cellAlpha * glyph.a);
            }
        `;

        this.program = this.createProgram(vsSource, fsSource);

        const positionBuffer = this.gl.createBuffer();
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, positionBuffer);
        this.gl.bufferData(
            this.gl.ARRAY_BUFFER,
            new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]),
            this.gl.STATIC_DRAW
        );

        const posLoc = this.gl.getAttribLocation(this.program, 'a_pos');
        this.gl.enableVertexAttribArray(posLoc);
        this.gl.vertexAttribPointer(posLoc, 2, this.gl.FLOAT, false, 0, 0);

        this.texture = this.gl.createTexture();
        this.gl.bindTexture(this.gl.TEXTURE_2D, this.texture);
        this.gl.texParameteri(this.gl.TEXTURE_2D, this.gl.TEXTURE_MIN_FILTER, this.gl.NEAREST);
        this.gl.texParameteri(this.gl.TEXTURE_2D, this.gl.TEXTURE_MAG_FILTER, this.gl.NEAREST);
        this.gl.texParameteri(this.gl.TEXTURE_2D, this.gl.TEXTURE_WRAP_S, this.gl.CLAMP_TO_EDGE);
        this.gl.texParameteri(this.gl.TEXTURE_2D, this.gl.TEXTURE_WRAP_T, this.gl.CLAMP_TO_EDGE);

        this.fontAtlas = this.createFontAtlas();
    }

    createFontAtlas() {
        const atlasSize = 256;
        const cellSize = 16;
        const cols = 16;
        const rows = 16;
        const canvas = document.createElement('canvas');
        canvas.width = atlasSize;
        canvas.height = atlasSize;
        const ctx = canvas.getContext('2d');

        ctx.fillStyle = 'rgba(0,0,0,0)';
        ctx.fillRect(0, 0, atlasSize, atlasSize);

        ctx.fillStyle = '#FFFFFF';
        ctx.font = 'bold 14px "Courier New", monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        for (let ascii = 0; ascii < 256; ascii++) {
            const col = ascii % cols;
            const row = Math.floor(ascii / cols);
            if (ascii < 32 || ascii === 127) continue;
            const ch = String.fromCharCode(ascii);
            const x = col * cellSize + cellSize / 2;
            const y = (rows - 1 - row) * cellSize + cellSize / 2;
            ctx.fillText(ch, x, y);
        }

        const tex = this.gl.createTexture();
        this.gl.bindTexture(this.gl.TEXTURE_2D, tex);
        this.gl.texParameteri(this.gl.TEXTURE_2D, this.gl.TEXTURE_MIN_FILTER, this.gl.NEAREST);
        this.gl.texParameteri(this.gl.TEXTURE_2D, this.gl.TEXTURE_MAG_FILTER, this.gl.NEAREST);
        this.gl.texParameteri(this.gl.TEXTURE_2D, this.gl.TEXTURE_WRAP_S, this.gl.CLAMP_TO_EDGE);
        this.gl.texParameteri(this.gl.TEXTURE_2D, this.gl.TEXTURE_WRAP_T, this.gl.CLAMP_TO_EDGE);
        this.gl.texImage2D(
            this.gl.TEXTURE_2D, 0, this.gl.RGBA,
            this.gl.RGBA, this.gl.UNSIGNED_BYTE, canvas
        );
        return tex;
    }

    createProgram(vsSrc, fsSrc) {
        const vs = this.compileShader(this.gl.VERTEX_SHADER, vsSrc);
        const fs = this.compileShader(this.gl.FRAGMENT_SHADER, fsSrc);
        const program = this.gl.createProgram();
        this.gl.attachShader(program, vs);
        this.gl.attachShader(program, fs);
        this.gl.linkProgram(program);

        if (!this.gl.getProgramParameter(program, this.gl.LINK_STATUS)) {
            console.error('Link error:', this.gl.getProgramInfoLog(program));
        }
        return program;
    }

    compileShader(type, source) {
        const shader = this.gl.createShader(type);
        this.gl.shaderSource(shader, source);
        this.gl.compileShader(shader);

        if (!this.gl.getShaderParameter(shader, this.gl.COMPILE_STATUS)) {
            console.error('Shader compile error:', this.gl.getShaderInfoLog(shader));
        }
        return shader;
    }

    bindKeys() {
        const moveSpeed = 0.3;
        const rotSpeed = 0.1;

        const handleMove = async () => {
            if (!this.exports) return;
            const x0 = this.exports.camera_x();
            const y0 = this.exports.camera_y();
            const a0 = this.exports.camera_angle();

            if (this.keys.has('w') || this.keys.has('arrowup')) this.exports.move_forward(moveSpeed);
            if (this.keys.has('s') || this.keys.has('arrowdown')) this.exports.move_forward(-moveSpeed);
            if (this.keys.has('a') || this.keys.has('arrowleft')) this.exports.rotate(rotSpeed);
            if (this.keys.has('d') || this.keys.has('arrowright')) this.exports.rotate(-rotSpeed);
            if (this.keys.has('q')) this.exports.rotate(-rotSpeed);
            if (this.keys.has('e')) this.exports.rotate(rotSpeed);

            const x = this.exports.camera_x();
            const y = this.exports.camera_y();
            const a = this.exports.camera_angle();

            // Critical-moment check
            if (x !== x0 || y !== y0) {
                const result = await this.cortex.onMove(x, y, a);
                if (result.fired && result.lore && this.onLore) {
                    this.onLore({ kind: result.kind, text: result.lore });
                }
            }
        };

        this.moveInterval = setInterval(handleMove, 50);

        document.getElementById('btn-forward').onmousedown = () => this.exports.move_forward(1.0);
        document.getElementById('btn-back').onmousedown = () => this.exports.move_forward(-1.0);
        document.getElementById('btn-left').onmousedown = () => this.exports.rotate(0.5);
        document.getElementById('btn-right').onmousedown = () => this.exports.rotate(-0.5);
        document.getElementById('btn-rotate-l').onmousedown = () => this.exports.rotate(-0.5);
        document.getElementById('btn-rotate-r').onmousedown = () => this.exports.rotate(0.5);
        document.getElementById('btn-reset').onclick = () => {
            this.exports.set_camera(16.0, 16.0, 0.0);
        };
        document.getElementById('btn-screenshot').onclick = () => {
            const link = document.createElement('a');
            link.download = `substrate-walker-${Date.now()}.png`;
            link.href = this.canvas.toDataURL('image/png');
            link.click();
        };
        document.getElementById('btn-examine').onclick = async () => {
            const text = await this.cortex.onExamine();
            if (text && this.onLore) this.onLore({ kind: 'examine', text });
        };

        document.addEventListener('keydown', async (e) => {
            const key = e.key.toLowerCase();
            this.keys.add(key);
            if (key === 'r') {
                this.exports.set_camera(16.0, 16.0, 0.0);
            }
            if (key === 'p') {
                document.getElementById('btn-screenshot').click();
            }
            if (key === 'l' || key === 'e') {
                const text = await this.cortex.onExamine();
                if (text && this.onLore) this.onLore({ kind: 'examine', text });
            }
        });
        document.addEventListener('keyup', (e) => {
            this.keys.delete(e.key.toLowerCase());
        });
    }

    updateHUD() {
        const fpsEl = document.getElementById('fps-counter');
        const frameEl = document.getElementById('frame-counter');
        const chainEl = document.getElementById('chain-status');
        const posEl = document.getElementById('pos-counter');
        const apiEl = document.getElementById('api-counter');

        fpsEl.textContent = `FPS: ${this.fps.toFixed(1)}`;
        frameEl.textContent = `Frame: ${this.frameCount}`;

        if (this.chainValid) {
            chainEl.textContent = 'Chain: ✓';
            chainEl.style.color = '#80FF80';
        } else {
            chainEl.textContent = 'Chain: ✗';
            chainEl.style.color = '#FF0080';
        }

        const x = this.exports.camera_x();
        const y = this.exports.camera_y();
        const angle = this.exports.camera_angle();
        const deg = (angle * 180 / Math.PI).toFixed(0);
        posEl.textContent = `Pos: (${x.toFixed(1)}, ${y.toFixed(1)}) → ${deg}°`;

        if (this.cortex) {
            const stats = this.cortex.getStats();
            apiEl.textContent = `API: ${stats.apiCalls} calls, ${stats.cacheHits} cached, ${stats.districtCache} districts`;
        }
    }

    render(time) {
        if (!this.exports || !this.gl) {
            requestAnimationFrame(this.render.bind(this));
            return;
        }

        this.exports.step();
        this.frameCount++;

        const buffer = new Uint8Array(
            this.memory.buffer,
            this.bufferPtr,
            this.bufferSize
        );

        this.gl.activeTexture(this.gl.TEXTURE0);
        this.gl.bindTexture(this.gl.TEXTURE_2D, this.texture);
        this.gl.texImage2D(
            this.gl.TEXTURE_2D, 0, this.gl.RGBA,
            160, 60, 0,
            this.gl.RGBA, this.gl.UNSIGNED_BYTE, buffer
        );

        this.gl.useProgram(this.program);
        this.gl.activeTexture(this.gl.TEXTURE1);
        this.gl.bindTexture(this.gl.TEXTURE_2D, this.fontAtlas);

        const bufferLoc = this.gl.getUniformLocation(this.program, 'u_buffer');
        const fontLoc = this.gl.getUniformLocation(this.program, 'u_font');
        const resLoc = this.gl.getUniformLocation(this.program, 'u_resolution');
        const gridLoc = this.gl.getUniformLocation(this.program, 'u_gridSize');

        this.gl.uniform1i(bufferLoc, 0);
        this.gl.uniform1i(fontLoc, 1);
        this.gl.uniform2f(resLoc, this.canvas.width, this.canvas.height);
        this.gl.uniform2f(gridLoc, 160, 60);

        this.gl.viewport(0, 0, this.canvas.width, this.canvas.height);
        this.gl.clearColor(0, 0, 0, 1);
        this.gl.clear(this.gl.COLOR_BUFFER_BIT);
        this.gl.drawArrays(this.gl.TRIANGLE_STRIP, 0, 4);

        const dt = time - this.lastTime;
        this.lastTime = time;
        if (dt > 0) {
            this.fpsAcc += (1000 / dt - this.fpsAcc) * 0.1;
            this.fps = this.fpsAcc;
        }

        if (this.frameCount % 30 === 0) {
            this.updateHUD();
        }

        requestAnimationFrame(this.render.bind(this));
    }
}

async function boot() {
    const canvas = document.getElementById('ascii-canvas');
    const loading = document.getElementById('loading');

    const walker = new SubstrateWalker(canvas);
    window.walker = walker;

    // Lore display
    const loreEl = document.getElementById('lore-display');
    walker.onLore = (event) => {
        if (!loreEl) return;
        const kindColors = {
            district: '#FFFF80',
            building: '#FF80FF',
            perception: '#80FFFF',
            examine: '#80FF80',
        };
        const color = kindColors[event.kind] || '#FFFFFF';
        loreEl.innerHTML = `<span style="color:${color};text-transform:uppercase">[${event.kind}]</span> ${event.text}`;
        loreEl.style.opacity = '1';
        setTimeout(() => {
            loreEl.style.transition = 'opacity 0.5s';
            loreEl.style.opacity = '0.6';
        }, 100);
    };

    // Try to read API key from localStorage
    let savedKey = null;
    try {
        savedKey = localStorage.getItem('deepinfra_key');
    } catch (e) {}
    if (savedKey) {
        walker.apiKey = savedKey;
    }

    try {
        await walker.init();
        loading.classList.add('hidden');
    } catch (err) {
        console.error('Failed to init:', err);
        loading.innerHTML = `<p style="color:#FF0080">Failed to load: ${err.message}</p>`;
    }
}

boot();

// API key management
const saveKeyBtn = document.getElementById('save-key');
const apiKeyInput = document.getElementById('api-key-input');
if (saveKeyBtn && apiKeyInput) {
    saveKeyBtn.onclick = () => {
        const key = apiKeyInput.value.trim();
        if (key) {
            try { localStorage.setItem('deepinfra_key', key); } catch (e) {}
            if (window.walker) {
                window.walker.apiKey = key;
                if (window.walker.cortex) {
                    window.walker.cortex.setApiKey(key);
                    window.walker.cortex.apiKey = key;
                }
            }
            apiKeyInput.value = '';
            apiKeyInput.placeholder = '✓ Saved';
            setTimeout(() => {
                apiKeyInput.placeholder = 'DeepInfra API key (optional)';
            }, 2000);
        }
    };

    // Load saved key
    try {
        const saved = localStorage.getItem('deepinfra_key');
        if (saved && window.walker) {
            window.walker.apiKey = saved;
        }
    } catch (e) {}
}
