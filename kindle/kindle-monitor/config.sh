# kindle-monitor settings (sourced by loop.sh). Plain POSIX sh.
SERVER="100.64.0.1:8765"   # atheron on the tailnet; the Kindle reaches it through the Tailscale SOCKS5 proxy
INTERVAL=1                   # seconds between updates (server answers from a pre-rendered cache in ~10 ms; fetch+draw ~0.3 s)
FULL_EVERY=600               # every N updates do a full flash refresh (~10 min at 1 s; clears e-ink ghosting)
FAIL_NOTICE_AFTER=3          # consecutive failures before drawing "sem dados" at the bottom
FIRST_DELAY=12            # seconds to wait before the first draw: the Kindle returns to the library after the scriptlet exits and repaints its UI
LOCK_TOUCH=buttons        # buttons = only the on-screen buttons answer (touch panel grabbed); 1 = touch fully off; 0 = no lock
ARM_SECONDS=6             # a command button stays armed this long waiting for the confirming second tap
STOP_GUI=1                # 1 = stop the Kindle UI (lab126_gui) while the monitor runs, so nothing repaints over it; it comes back on exit
