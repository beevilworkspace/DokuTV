"""
Main Entry Point for DokuTV (Clean Architecture Implementation).
"""

import time
import logging
import json
from dokutv.infrastructure import load_env
from dokutv import DokuTVEngine

load_env()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("DokuTV_Main")

def main():
    print("=" * 65)
    print("  DokuTV_EN 24/7 Streaming System (Clean Architecture)")
    print("  Drücken Sie [STRG + C] im Terminal, um das Streaming zu beenden.")
    print("=" * 65)

    # Initialize Engine Composition Root
    engine = DokuTVEngine(channel_name="DokuTV_EN", dry_run=False)
    
    # 1. Discover Content & Plan 30-Day Schedule via Application Use Cases
    init_res = engine.initialize()
    logger.info(f"Initialization Result: {init_res}")

    # 2. Start Streaming & Twitch Title Sync via Application Use Cases
    run_status = engine.start()
    logger.info(f"Streaming Active: {run_status['is_running']}")

    # 3. Output Status Diagnostic
    status = engine.get_status()
    print("\n--- Current System Status ---")
    print(json.dumps(status, indent=2, ensure_ascii=False))
    print("=" * 65)

    print("\n[LIVE] DokuTV_EN läuft... Drücken Sie STRG+C zum Stoppen.")
    
    try:
        while engine.is_running:
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n[STOPP] Beenden-Signal empfangen. Stoppe Streaming Engine...")
        engine.stop()
        print("[STOPP] DokuTV_EN wurde sauber beendet.")

if __name__ == "__main__":
    main()
