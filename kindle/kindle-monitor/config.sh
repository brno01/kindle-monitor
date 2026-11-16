# kindle-monitor settings (sourced by loop.sh). Plain POSIX sh.
SERVER="100.64.0.1:8765"   # atheron on the tailnet; the Kindle reaches it through the Tailscale SOCKS5 proxy
INTERVAL=2                   # seconds between updates (the fetch+draw itself takes ~2 s, so this is as fast as it goes)
FULL_EVERY=300               # every N updates do a full flash refresh (~10 min at 2 s; clears e-ink ghosting)
FAIL_NOTICE_AFTER=3          # consecutive failures before drawing "sem dados" at the bottom
FIRST_DELAY=12            # seconds to wait before the first draw: the Kindle returns to the library after the scriptlet exits and repaints its UI
LOCK_TOUCH=buttons        # buttons = only the on-screen buttons answer (touch panel grabbed); 1 = touch fully off; 0 = no lock
ARM_SECONDS=6             # a command button stays armed this long waiting for the confirming second tap
