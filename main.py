"""
Main Entry Point for DokuTV (Clean Architecture Implementation).
"""

import sys
sys.dont_write_bytecode = True

import logging
from dokutv.infrastructure import load_env
from dokutv import DokuTVEngine

load_env()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    print("=" * 65)
    print("  DokuTV_EN On-Demand Streaming System (Clean Architecture)")
    print("  Drücken Sie [STRG + C] im Terminal, um das Streaming zu beenden.")
    print("=" * 65)

    # Initialize Engine Composition Root
    engine = DokuTVEngine(channel_name="DokuTV_EN", dry_run=False)

    try:
        # Run endless on-demand streaming loop (duration_limit=120 for 2 min test, set None for full video)
        engine.run_continuous_stream(duration_limit=120)
    except KeyboardInterrupt:
        print("\n[STOPP] Beenden-Signal empfangen. Stoppe Streaming Engine...")
        engine.stop()
        print("[STOPP] DokuTV_EN wurde sauber beendet.")

if __name__ == "__main__":
    main()