import simplepyble
import time

# -----------------------
# UPDATE THESE CONSTANTS:
# -----------------------
TARGET_NAME = "SA_AE108_0000B984"
TARGET_MAC  = "0B03C9C2-9BFC-5E07-4C68-65E6A594E503"
# -----------------------


def find_device(adapter):
    print("[INFO] Scanning for BLE devices...")
    adapter.scan_for(5000)                 # scan 5 seconds
    devices = adapter.scan_get_results()

    if not devices:
        raise RuntimeError("No BLE devices found.")

    print(f"[INFO] Found {len(devices)} devices.\n")

    for d in devices:
        name = d.identifier()
        addr = d.address()
        print(f"  → {name!r}  @  {addr}")

        # Match by MAC first (macOS random UUID form)
        if TARGET_MAC and addr.lower() == TARGET_MAC.lower():
            print("[INFO] Matched target by MAC.")
            return d

        # Match by Name substring
        if TARGET_NAME and name and TARGET_NAME.lower() in name.lower():
            print("[INFO] Matched target by NAME.")
            return d

    raise RuntimeError("Target device not found. Check name and MAC.")


def print_services(peripheral):
    print("\n=== GATT SERVICES & CHARACTERISTICS ===\n")
    for service in peripheral.services():
        print(f"Service: {service.uuid()}")
        for ch in service.characteristics():
            props = []
            if ch.can_read(): props.append("READ")
            if ch.can_write_request(): props.append("WRITE_REQ")
            if ch.can_write_command(): props.append("WRITE_CMD")
            if ch.can_notify(): props.append("NOTIFY")
            if ch.can_indicate(): props.append("INDICATE")
            p = "+".join(props) if props else "-"
            print(f"  Char: {ch.uuid()}    Props={p}")
    print("\n=======================================\n")


def main():
    adapters = simplepyble.Adapter.get_adapters()
    if not adapters:
        raise RuntimeError("No Bluetooth adapter found!")
    adapter = adapters[0]

    print(f"[INFO] Using adapter: {adapter.identifier()}")

    # --- Find device ---
    dev = find_device(adapter)

    # --- Connect ---
    print(f"\n[INFO] Connecting to {dev.identifier()}  @  {dev.address()} ...")
    dev.connect()
    print("[INFO] Connected.\n")

    # --- Print Services (we need this to identify control UUID) ---
    print_services(dev)

    # Disconnect cleanly
    print("[INFO] Disconnecting...")
    dev.disconnect()
    print("[INFO] Done.")


if __name__ == "__main__":
    main()