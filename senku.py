#!/usr/bin/env python3
"""
=============================================================================
                SENKU TECHNOLOGIES // QUANTUM LABS
        Speculative Multiverse Execution & Counterfactual Causality Engine
=============================================================================
"This is ten billion percent exhilarating!" — Senku Ishigami

Official unified CLI for the Senku QuantumFlow ecosystem.
"""

import argparse
import asyncio
import os
import sys
import time

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure package is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from quantumflow import (
    Multiverse,
    CollapseStrategy,
    Timeline,
    TimeTravelEngine,
    ParadoxSentinel,
    CausalityGraph,
    __version__
)


def print_senku_banner():
    banner = f"""
  ╔══════════════════════════════════════════════════════════════════════╗
  ║    ███████╗███████╗███╗   ██╗██╗  ██╗██╗   ██╗                       ║
  ║    ██╔════╝██╔════╝████╗  ██║██║ ██╔╝██║   ██║                       ║
  ║    ███████╗█████╗  ██╔██╗ ██║█████═╝ ██║   ██║  QUANTUM LABS         ║
  ║    ╚════██║██╔══╝  ██║╚██╗██║██╔═██╗ ██║   ██║                       ║
  ║    ███████║███████╗██║ ╚████║██║ ╚██╗╚██████╔╝  v{__version__}               ║
  ║    ╚══════╝╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝                        ║
  ║                                                                      ║
  ║         Q U A N T U M F L O W   E X E C U T I O N   E N G I N E      ║
  ║      "Ten Billion Percent Resilient Multiverse Architecture"         ║
  ╚══════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def cmd_demo(args):
    """Runs the 4-scenario Senku Scientific Showcase."""
    print_senku_banner()
    from run_demo import main as run_master_demo
    asyncio.run(run_master_demo())


def get_local_ip():
    """Attempt to detect local machine IP for LAN access."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def start_public_tunnel(port: int):
    """Launches an SSH tunnel using Windows OpenSSH to expose port to public internet."""
    import subprocess, threading, re
    cmd = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=NUL",
        "-T",
        "-R", f"80:localhost:{port}",
        "nokey@localhost.run"
    ]
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        def _monitor():
            found_url = False
            for line in proc.stdout:
                match = re.search(r"https://[a-zA-Z0-9.\-_]+", line)
                if match:
                    url = match.group(0)
                    if "admin.localhost.run" not in url and "docs" not in url:
                        if not found_url:
                            found_url = True
                            print("\n" + "="*70)
                            print("  [★] LIVE PUBLIC GLOBAL INTERNET URL (Accessible Worldwide!):")
                            print(f"      👉  {url}")
                            print("="*70 + "\n")
        t = threading.Thread(target=_monitor, daemon=True)
        t.start()
        return proc
    except Exception as e:
        print(f"[-] Could not establish public tunnel: {e}")
        return None


def cmd_web(args):
    """Launches the interactive Senku Quantum Labs Web Visualizer."""
    print_senku_banner()
    port = args.port or int(os.environ.get("PORT", 8080))
    host = args.host or os.environ.get("HOST", "0.0.0.0")
    from quantumflow.server.dashboard import DashboardServer

    mv = Multiverse(name="SenkuQuantumLabs")
    mv.set_root_state("brand", "Senku Technologies")
    mv.set_root_state("system_health", "10,000,000,000% Optimal")
    mv.set_root_state("science_level", "Advanced Causality")
    mv.set_root_state("processed_syntheses", 0)

    # Invariant: balance must be non-negative
    mv.register_invariant(
        "NonNegativeEntropy",
        lambda state: state.get("entropy_level", 0) >= 0,
        "Entropy violation detected (decoherence triggered)"
    )

    server = DashboardServer(multiverse=mv, port=port, host=host)
    server.start()

    tunnel_proc = None
    if getattr(args, "public", False):
        print("[*] Initializing instant public global tunnel...")
        tunnel_proc = start_public_tunnel(port)

    local_ip = get_local_ip()
    print(f"\n[🧪] Senku Quantum Labs Visualizer active!")
    print(f"     • Local:        http://localhost:{port}")
    if local_ip != "127.0.0.1":
        print(f"     • LAN / Mobile: http://{local_ip}:{port}")
    print(f"     • Cloud Host:   http://0.0.0.0:{port}")
    print(f"     Interactive Control Deck & Audio Synthesizer: READY")
    print(f"     Press Ctrl+C to terminate.\n")

    from run_dashboard import traffic_simulator
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(traffic_simulator(mv))
    except KeyboardInterrupt:
        print("\n[*] Shutting down Senku Quantum Labs server...")
    finally:
        if tunnel_proc:
            try:
                tunnel_proc.terminate()
            except Exception:
                pass
        server.stop()


def cmd_test(args):
    """Executes the full automated unit test suite with Senku verification."""
    print_senku_banner()
    print("[*] Launching Senku Scientific Verification Protocol...")
    import unittest
    suite = unittest.defaultTestLoader.discover(os.path.join(BASE_DIR, "tests"))
    runner = unittest.TextTestRunner(verbosity=2)
    t0 = time.perf_counter()
    result = runner.run(suite)
    elapsed = time.perf_counter() - t0

    print("\n" + "="*70)
    if result.wasSuccessful():
        print(f"  [✓] SENKU VERIFICATION: 10 BILLION PERCENT CERTIFIED SUCCESS!")
        print(f"      Passed:  {result.testsRun} test cases in {elapsed:.3f}s")
        print(f"      Failures: 0 | Errors: 0")
        print("      Status: Multiverse coherence & invariant isolation verified.")
    else:
        print(f"  [✗] SENKU VERIFICATION FAILED: {len(result.failures)} failures, {len(result.errors)} errors.")
    print("="*70 + "\n")


def cmd_status(args):
    """Displays the current status and cryptographic fingerprint."""
    print_senku_banner()
    mv = Multiverse(name="SenkuPrime")
    mv.set_root_state("engine", "QuantumFlow")
    mv.set_root_state("brand", "Senku")
    mv.set_root_state("status", "ACTIVE_COHERENCE")
    
    print("[*] Senku Prime Reality Matrix:")
    for k, v in mv.root_memory.items():
        print(f"    • {k:<20} = {v}")
    print(f"\n[*] Cryptographic State Fingerprint: {mv.root_memory.compute_fingerprint()[:16]}")
    print("[*] Engine Status: Ten Billion Percent Operational\n")


def main():
    parser = argparse.ArgumentParser(
        description="SENKU // QuantumFlow - Speculative Multiverse Execution Runtime"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # demo subcommand
    sub_demo = subparsers.add_parser("demo", help="Run 4-scenario production demo")
    sub_demo.set_defaults(func=cmd_demo)

    # web subcommand
    sub_web = subparsers.add_parser("web", help="Launch real-time HUD visualizer")
    sub_web.add_argument("--port", type=int, default=None, help="Port to bind (default: 8080 or $PORT)")
    sub_web.add_argument("--host", type=str, default=None, help="Host to bind (default: 0.0.0.0 or $HOST)")
    sub_web.add_argument("--public", action="store_true", help="Launch instant public global internet tunnel")
    sub_web.set_defaults(func=cmd_web)

    # test subcommand
    sub_test = subparsers.add_parser("test", help="Run full 18-test verification suite")
    sub_test.set_defaults(func=cmd_test)

    # status subcommand
    sub_status = subparsers.add_parser("status", help="Print Senku reality matrix status")
    sub_status.set_defaults(func=cmd_status)

    args = parser.parse_args()

    if not args.command:
        print_senku_banner()
        print("Usage: python senku.py [command]")
        print("\nCommands:")
        print("  web     Launch the interactive Senku Quantum Labs HUD at http://localhost:8080")
        print("  demo    Run all 4 speculative resilience & causality scenarios")
        print("  test    Execute the 18-test scientific verification suite")
        print("  status  Display current Senku canonical state & cryptographic fingerprint\n")
        return

    args.func(args)


if __name__ == "__main__":
    main()
