# kindle-monitor settings (sourced by loop.sh). Plain POSIX sh.
SERVER="100.64.0.1:8765"   # atheron on the tailnet; the Kindle reaches it through the Tailscale SOCKS5 proxy
INTERVAL=15                  # seconds between updates
FULL_EVERY=40                # every N updates do a full flash refresh (40 x 15 s = 10 min; clears e-ink ghosting)
FAIL_NOTICE_AFTER=3          # consecutive failures before drawing "sem dados" at the bottom
FIRST_DELAY=12            # seconds to wait before the first draw: the Kindle returns to the library after the scriptlet exits and repaints its UI
LOCK_TOUCH=1              # 1 = touch screen off while the monitor runs; the power button stops it
