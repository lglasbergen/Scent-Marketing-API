# scent_marketing_api.py
import time
import simplepyble
import argparse

# -----------------------
# DEVICE CONSTANTS
# -----------------------
TARGET_NAME = "SA_AE108_0000B984"
TARGET_MAC  = "0B03C9C2-9BFC-5E07-4C68-65E6A594E503"

SERVICE_UUID      = "0000fff0-0000-1000-8000-00805f9b34fb"
CONTROL_CHAR_UUID = "0000fff6-0000-1000-8000-00805f9b34fb"

# -----------------------
# RAW COMMANDS
# -----------------------

CMD_LOGIN = bytes.fromhex("8f38383838")
CMD_PUMP_ON = bytes.fromhex("03110000173b7f0a0a000000000000")
CMD_PUMP_OFF = bytes.fromhex("03010000173b7f0a0a000000000000")
CMD_GET_DEVICE_INFO = bytes.fromhex("86503d11")
CMD_GET_APP_VERSION = bytes.fromhex("88d02119")


class Diffuser:
    def __init__(self, verbose=True):
        self.adapter = None
        self.dev = None
        self.notification_responses = []
        self.verbose = verbose

    def log(self, msg):
        """Print only if verbose mode is on"""
        if self.verbose:
            print(msg)

    # ------------------------------------------------------------------
    # CONNECTION
    # ------------------------------------------------------------------
    def connect(self):
        """Connect to diffuser"""
        adapters = simplepyble.Adapter.get_adapters()
        if not adapters:
            raise RuntimeError("No BLE adapter found.")
        self.adapter = adapters[0]
        
        self.log("[INFO] Scanning for diffuser...")
        self.adapter.scan_for(2000)
        devices = self.adapter.scan_get_results()

        for d in devices:
            name = d.identifier() or ""
            addr = d.address()
            if addr.lower() == TARGET_MAC.lower() or TARGET_NAME.lower() in name.lower():
                self.log(f"[INFO] Found: {name}")
                self.dev = d
                break

        if not self.dev:
            raise RuntimeError("Diffuser not found. Is it on / not connected to phone?")

        self.log("[INFO] Connecting...")
        self.dev.connect()
        self.log("[INFO] Connected.")

    def disconnect(self):
        if self.dev and self.dev.is_connected():
            self.log("[INFO] Disconnecting...")
            self.dev.disconnect()
            self.log("[INFO] Disconnected.")

    # ------------------------------------------------------------------
    # NOTIFICATIONS
    # ------------------------------------------------------------------
    def _notif(self, data: bytes):
        hex_data = data.hex()
        self.notification_responses.append(hex_data)
        
        # Try to decode readable text
        text = ''.join([chr(b) if 32 <= b < 127 else '' for b in data])
        
        if text.strip():
            self.log(f"[NOTIF] {text}")
            
            # Parse version info
            if "OK_V" in text:
                # Skip - this is just an acknowledgment, not the actual version we want
                pass
            elif text.startswith("V") and "." in text[:6]:
                version = text[:10].strip()
                
                # Determine if it's PCB or Equipment version based on format
                # V2.00 (two decimal places) = PCB Version
                # V3.4 (one decimal place) = Equipment Version
                if ".00" in version or len(version.split(".")[-1]) == 2:
                    print(f"PCB Version: {version}")
                else:
                    print(f"Equipment Version: {version}")

    def enable_notifications(self):
        """Subscribe to notifications"""
        self.log("[INFO] Enabling notifications...")
        self.dev.notify(SERVICE_UUID, CONTROL_CHAR_UUID, self._notif)

    # ------------------------------------------------------------------
    # LOW-LEVEL SEND
    # ------------------------------------------------------------------
    def _send(self, payload: bytes, delay: float = 0.0):
        """Send command with optional delay"""
        self.log(f"[TX] {payload.hex()}")
        self.dev.write_command(SERVICE_UUID, CONTROL_CHAR_UUID, payload)
        if delay > 0:
            time.sleep(delay)

    # ------------------------------------------------------------------
    # HIGH-LEVEL COMMANDS
    # ------------------------------------------------------------------
    def login(self):
        """Login to device"""
        self.log("[INFO] Logging in...")
        self._send(CMD_LOGIN, delay=0.3)

    def start_pump(self):
        """Start pump"""
        self.log("[INFO] Starting pump...")
        self._send(CMD_PUMP_ON, delay=0.5)

    def stop_pump(self):
        """Stop pump"""
        self.log("[INFO] Stopping pump...")
        self._send(CMD_PUMP_OFF, delay=1.0)

    def get_versions(self):
        """Query device versions"""
        print("\n" + "="*60)
        print("DEVICE VERSION INFORMATION")
        print("="*60)
        
        self._send(CMD_GET_DEVICE_INFO)
        time.sleep(1.0)
        
        self._send(CMD_GET_APP_VERSION)
        time.sleep(1.0)
        
        print("="*60 + "\n")


# ----------------------------------------------------------------------
# COMMAND LINE INTERFACE
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description='Control SA_AE108 Scent Marketing Diffuser',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scent_marketing_api.py              # Run pump for 2000ms (2 seconds, default)
  python3 scent_marketing_api.py -d 3000      # Run pump for 3000ms (3 seconds)
  python3 scent_marketing_api.py -d 500       # Run pump for 500ms (0.5 seconds)
  python3 scent_marketing_api.py -d 0         # Turn on and immediately off
  python3 scent_marketing_api.py --versions   # Get device versions only
  python3 scent_marketing_api.py -d 1500 -q   # Run 1500ms silently
        """
    )
    
    parser.add_argument(
        '--versions', '-v',
        action='store_true',
        help='Get device version information only'
    )
    
    parser.add_argument(
        '--duration', '-d',
        type=int,
        default=2000,
        help='Pump run duration in milliseconds (0-4000ms, default: 2000ms)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet mode - minimal output'
    )
    
    args = parser.parse_args()
    
    # Validate duration range
    if args.duration < 0 or args.duration > 4000:
        parser.error(f"Duration must be between 0 and 4000 milliseconds (got {args.duration}ms)")
    
    # Create diffuser instance
    diff = Diffuser(verbose=not args.quiet)
    
    try:
        # Connect
        diff.connect()
        diff.enable_notifications()
        diff.login()
        
        if args.versions:
            # VERSION MODE: Just get versions and exit
            diff.get_versions()
        else:
            # PUMP MODE: Run for specified duration
            diff.start_pump()
            
            if args.duration > 0:
                duration_seconds = args.duration / 1000.0
                if not args.quiet:
                    print(f"[INFO] Running pump for {args.duration}ms ({duration_seconds:.2f}s)...")
                time.sleep(duration_seconds)
            
            diff.stop_pump()
            
            if not args.quiet:
                print("[INFO] Pump cycle complete.")
    
    except Exception as e:
        print(f"[ERROR] {e}")
        # Try to stop pump even on error
        try:
            if diff.dev and diff.dev.is_connected():
                diff.stop_pump()
        except:
            pass
    
    finally:
        # Delay before disconnect to ensure stop command completed
        time.sleep(0.5)
        diff.disconnect()


if __name__ == "__main__":
    main()