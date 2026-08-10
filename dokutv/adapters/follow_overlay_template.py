"""
Adapter Layer - Follow Overlay HTML Template Renderer.
Provides HTML template rendering for the standalone glassmorphism follow overlay.
"""

import json
from dokutv.domain.overlay import FollowOverlayConfig

HTML_FOLLOW_OVERLAY_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Follow Overlay – DokuTV</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Outfit:wght@600;700;800&display=swap" rel="stylesheet">
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        twitch: '#9146FF',
                        'twitch-dark': '#772CE8',
                    }},
                    fontFamily: {{
                        sans: ['Inter', 'sans-serif'],
                        outfit: ['Outfit', 'sans-serif'],
                    }}
                }}
            }}
        }}
    </script>

    <style>
        /* Standalone Transparent Canvas */
        html, body {{
            margin: 0;
            padding: 0;
            width: 100vw;
            height: 100vh;
            background: transparent !important;
            overflow: hidden;
            user-select: none;
        }}

        /* Dynamic CSS Variables */
        :root {{
            --accent-color: #{color};
            --accent-glow: rgba(145, 70, 255, 0.5);
        }}

        /* Glassmorphism Pill Container */
        .glass-pill-container {{
            background: rgba(15, 17, 26, 0.82);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.45), 0 0 20px var(--accent-glow);
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        /* Gentle Floating Animation */
        @keyframes floatSlow {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-7px); }}
        }}
        .animate-float {{
            animation: floatSlow 4.5s ease-in-out infinite;
        }}

        /* Shimmer / Light Beam Effect across the pill */
        .shine-effect {{
            position: relative;
            overflow: hidden;
        }}
        .shine-effect::after {{
            content: '';
            position: absolute;
            top: -50%;
            left: -70%;
            width: 50%;
            height: 200%;
            background: linear-gradient(
                to right,
                rgba(255, 255, 255, 0) 0%,
                rgba(255, 255, 255, 0.3) 50%,
                rgba(255, 255, 255, 0) 100%
            );
            transform: rotate(25deg);
            animation: shine 5s infinite;
        }}

        @keyframes shine {{
            0% {{ left: -70%; }}
            20% {{ left: 150%; }}
            100% {{ left: 150%; }}
        }}

        /* Heart Pulse Animation inside Button */
        @keyframes heartBeat {{
            0%, 100% {{ transform: scale(1); }}
            15% {{ transform: scale(1.25); }}
            30% {{ transform: scale(1); }}
            45% {{ transform: scale(1.15); }}
        }}
        .animate-heart-beat {{
            animation: heartBeat 2s ease-in-out infinite;
        }}

        /* Canvas Particle Effects on Follow Event */
        #particleCanvas {{
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 99;
        }}
    </style>
</head>
<body class="font-sans text-slate-100 antialiased">

    <!-- Particle Burst Canvas for Alert Triggers -->
    <canvas id="particleCanvas"></canvas>

    <!-- Overlay Stage: Outer position wrapper -->
    <div id="positionWrapper" class="fixed inset-0 p-8 pointer-events-none flex flex-col justify-end items-start transition-all duration-300">

        <!-- Minimalist Glass Pill Element -->
        <div id="glassPill" class="pointer-events-auto animate-float transition-all duration-300">
            <div class="glass-pill-container px-5 py-3.5 rounded-2xl flex items-center gap-4 border-l-4 shine-effect" style="border-left-color: var(--accent-color)">
                
                <!-- Avatar / Twitch Icon with Pulse Indicator -->
                <div class="relative flex items-center justify-center shrink-0">
                    <div id="iconBox" class="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-600 flex items-center justify-center text-white font-bold shadow-md shadow-purple-500/30">
                        <i class="fa-brands fa-twitch text-xl"></i>
                    </div>
                    <!-- Live online dot -->
                    <span class="absolute -top-1 -right-1 w-3.5 h-3.5 bg-emerald-400 border-2 border-slate-900 rounded-full animate-pulse"></span>
                </div>

                <!-- Text Area: Username & Call-to-Action -->
                <div class="flex flex-col pr-1">
                    <div class="flex items-center gap-1.5">
                        <span id="txtUser" class="text-[11px] font-black uppercase tracking-widest text-slate-300"></span>
                    </div>
                    <p id="txtCta" class="text-sm font-bold text-white tracking-tight"></p>
                </div>

                <!-- Interactive Call-To-Action Button Badge -->
                <div id="btnBadge" class="ml-1 px-4 py-2 rounded-xl text-xs font-bold text-white shadow-lg flex items-center gap-2 transition-all duration-300 hover:scale-105 shrink-0"
                    style="background: linear-gradient(135deg, var(--accent-color), #4F46E5); box-shadow: 0 4px 15px var(--accent-glow)">
                    <i class="fa-solid fa-heart text-red-300 text-xs animate-heart-beat"></i>
                    <span id="txtBtn"></span>
                </div>

            </div>
        </div>

    </div>

    <script>
        // Server-injected Configuration
        const SERVER_CONFIG = {config_json};

        // Configuration Settings
        const config = {{
            user: SERVER_CONFIG.user || 'DeinKanalName',
            cta: SERVER_CONFIG.cta || '',
            btn: SERVER_CONFIG.btn || '',
            color: SERVER_CONFIG.color || '9146FF',
            pos: SERVER_CONFIG.pos || 'bottom-left',
            scale: SERVER_CONFIG.scale || 100,
            lang: SERVER_CONFIG.lang || 'de'
        }};

        // Initialize and parse optional URL parameters (URL params override backend defaults)
        window.addEventListener('DOMContentLoaded', () => {{
            parseUrlParameters();
            applyConfiguration();
        }});

        function parseUrlParameters() {{
            const params = new URLSearchParams(window.location.search);
            if (params.has('user')) config.user = params.get('user');
            if (params.has('cta')) config.cta = params.get('cta');
            if (params.has('btn')) config.btn = params.get('btn');
            if (params.has('color')) config.color = params.get('color').replace('#', '');
            if (params.has('pos')) config.pos = params.get('pos');
            if (params.has('scale')) config.scale = parseInt(params.get('scale')) || config.scale;
        }}

        function applyConfiguration() {{
            // Text values
            document.getElementById('txtUser').textContent = config.user.startsWith('@') ? config.user : '@' + config.user;
            document.getElementById('txtCta').textContent = config.cta;
            document.getElementById('txtBtn').textContent = config.btn;

            // Accent Colors
            const colorHex = '#' + config.color;
            document.documentElement.style.setProperty('--accent-color', colorHex);
            const rgb = hexToRgb(colorHex);
            if (rgb) {{
                document.documentElement.style.setProperty('--accent-glow', `rgba(${{rgb.r}}, ${{rgb.g}}, ${{rgb.b}}, 0.5)`);
            }}

            // Position on Stage
            const wrapper = document.getElementById('positionWrapper');
            wrapper.className = "fixed inset-0 p-8 pointer-events-none flex flex-col transition-all duration-300 ";

            switch(config.pos) {{
                case 'bottom-center':
                    wrapper.className += "justify-end items-center";
                    break;
                case 'bottom-right':
                    wrapper.className += "justify-end items-end";
                    break;
                case 'top-left':
                    wrapper.className += "justify-start items-start";
                    break;
                case 'top-right':
                    wrapper.className += "justify-start items-end";
                    break;
                case 'top-center':
                    wrapper.className += "justify-start items-center";
                    break;
                case 'bottom-left':
                default:
                    wrapper.className += "justify-end items-start";
                    break;
            }}

            // Scale multiplier
            if (config.scale !== 100) {{
                document.getElementById('glassPill').style.transform = `scale(${{config.scale / 100}})`;
            }}
        }}

        function hexToRgb(hex) {{
            const result = /^#?([a-f\d]{{2}})([a-f\d]{{2}})([a-f\d]{{2}})$/i.exec(hex);
            return result ? {{
                r: parseInt(result[1], 16),
                g: parseInt(result[2], 16),
                b: parseInt(result[3], 16)
            }} : null;
        }}

        // Click on the glass pill inside browser to trigger test alert
        document.getElementById('glassPill').addEventListener('click', () => {{
            triggerFollowAlert();
        }});

        // Trigger Follow Chime + Confetti Particles
        function triggerFollowAlert() {{
            playChimeSound();
            spawnParticles();

            // Bounce animation on pill
            const pill = document.getElementById('glassPill');
            pill.style.transform = `scale(${{(config.scale / 100) * 1.1}})`;
            setTimeout(() => {{
                pill.style.transform = `scale(${{config.scale / 100}})`;
            }}, 300);
        }}

        // Web Audio Synthesizer Chime
        function playChimeSound() {{
            try {{
                const AudioCtx = window.AudioContext || window.webkitAudioContext;
                if (!AudioCtx) return;
                const ctx = new AudioCtx();
                const now = ctx.currentTime;

                const notes = [523.25, 659.25, 1046.50]; // C5, E5, C6
                notes.forEach((freq, idx) => {{
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.type = 'sine';
                    osc.frequency.setValueAtTime(freq, now + idx * 0.1);
                    gain.gain.setValueAtTime(0.18, now + idx * 0.1);
                    gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.1 + 0.5);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start(now + idx * 0.1);
                    osc.stop(now + idx * 0.1 + 0.5);
                }});
            }} catch (e) {{
                console.log('Audio disabled/not supported');
            }}
        }}

        // Particle Burst System
        function spawnParticles() {{
            const canvas = document.getElementById('particleCanvas');
            const ctx = canvas.getContext('2d');
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;

            const pillRect = document.getElementById('glassPill').getBoundingClientRect();
            const startX = pillRect.left + pillRect.width / 2;
            const startY = pillRect.top + pillRect.height / 2;

            const particles = [];
            const colors = ['#' + config.color, '#00F0FF', '#00FF88', '#FF0055', '#FFFFFF'];

            for (let i = 0; i < 50; i++) {{
                particles.push({{
                    x: startX,
                    y: startY,
                    vx: (Math.random() - 0.5) * 12,
                    vy: (Math.random() - 0.5) * 12 - 2,
                    size: Math.random() * 6 + 3,
                    color: colors[Math.floor(Math.random() * colors.length)],
                    alpha: 1,
                    decay: Math.random() * 0.02 + 0.015
                }});
            }}

            function animate() {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                let active = false;

                particles.forEach(p => {{
                    if (p.alpha > 0) {{
                        active = true;
                        p.x += p.vx;
                        p.y += p.vy;
                        p.vy += 0.15;
                        p.alpha -= p.decay;

                        ctx.globalAlpha = Math.max(0, p.alpha);
                        ctx.fillStyle = p.color;
                        ctx.beginPath();
                        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                        ctx.fill();
                    }}
                }});

                if (active) {{
                    requestAnimationFrame(animate);
                }} else {{
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                }}
            }}

            animate();
        }}
    </script>
</body>
</html>
"""


def render_follow_overlay(config: FollowOverlayConfig) -> str:
    """Render full HTML string for Follow Overlay with injected dynamic config."""
    config_dict = config.to_dict()
    config_json = json.dumps(config_dict, ensure_ascii=False)
    return HTML_FOLLOW_OVERLAY_TEMPLATE.format(
        lang=config.lang,
        color=config.color,
        config_json=config_json,
    )
