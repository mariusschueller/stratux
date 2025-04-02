import socket
import struct
import json
import subprocess
import re
import uuid

def read_gdl90(port=4000, buffer_size=1024):
    """Reads GDL90 messages from Stratux over UDP."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", port))  # Listen on all interfaces
    print(f"Listening for GDL90 messages on UDP port {port}...")
    
    try:
        while True:
            data, addr = sock.recvfrom(buffer_size)
            # print(f"Received {len(data)} bytes from {addr}: {data.hex()}")
            messages = data.split(b'\x7E')  # Split on frame markers
            for msg in messages:
                if msg:
                    parse_gdl90(msg)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        sock.close()

def parse_gdl90(data):
    """Parses and identifies key GDL90 messages."""
    if len(data) < 1:
        return
    
    message_type = data[0]
    if message_type == 0x00:
        print("-> Standard GDL90 Heartbeat Message")
    elif message_type == 0xCC:
        print("-> Stratux Heartbeat Message (0xCC)")
    elif message_type == 0x53 and len(data) > 1 and data[1] == 0x58:
        print("-> Stratux Heartbeat Message (0x5358)")
    elif message_type == 0x4C:
        print("-> AHRS Report (0x4C)")
    elif message_type == 0x0A:
        parse_ownship(data)
    else:
        print(f"-> Unknown Message Type")

def parse_ownship(data):
    """
    Parses an Ownship Report message (Message ID 0x0A).
    The Ownship Report is 28 bytes long. Byte 0 is the message ID of 10 so (0x0A),
    and bytes 1-27 contain the report fields as defined in Table 8.
    """
    if len(data) < 28:
        print("Error: Incomplete Ownship Report message. Expected 28 bytes.")
        return

    # Message ID (byte 0) should be 0x0A
    msg_id = data[0]
    if msg_id != 0x0A:
        print(f"Error: Message ID mismatch (got 0x{msg_id:02X}, expected 0x0A).")
        return

    # The remaining 27 bytes contain the Ownship Report payload
    payload = data[1:]

    print(payload)

    # Byte is 8 bits

    # Byte 0: Traffic Alert Status: 1 for yes
    s = (payload[0] >> 4) & 0xF
    # Byte 0: Address Type
    t = payload[0] & 0xF

    # Bytes 1-3: Participant Address (24 bits)
    # big endian encoding
    participant_address = int.from_bytes(payload[1:4], byteorder='big')

    # Bytes 4-6: Latitude (24-bit signed binary fraction)
    # Should be 0 if not found
    lat_int = int.from_bytes(payload[4:7], byteorder='big', signed=True)
    latitude = lat_int * (180.0 / 8388608.0)

    # Bytes 7-9: Longitude (24-bit signed binary fraction)
    # Should be 0 if not found
    lon_int = int.from_bytes(payload[7:10], byteorder='big', signed=True)
    longitude = lon_int * (180.0 / 8388608.0)

    # Bytes 10-11: Altitude (12-bit offset integer), Resolution = 25 ft
    # putting together the last 4 of byte 10 and first 4 of byte 11
    altitude_raw = (payload[10] << 4) | (payload[11] >> 4)
    altitude_ft = altitude_raw * 25 - 1000

    # Miscellaneous indicators (m, 4 bits)
    # Ignored for now
    misc = payload[11] & 0x0F

    # Byte 12: Navigation Integrity Category (NIC)
    nic = (payload[12] >> 4) & 0xF

    # Navigation Accuracy Category for Position (NACp)
    # filtering out first 4 bits (NIC bits)
    nacp = payload[12] & 0xF

    # Bytes 13-15: Horizontal Velocity (12 bits), resolution 1 kt
    # combining the correct bytes. Shifting to the left and then adding in 4 bits
    horiz_vel = (payload[13] << 4) | (payload[14] >> 4)

    # Vertical Velocity (12 bits, signed), integer in 64 fpm
    # FIXME BIG ENDIAN?
    vert_raw = ((payload[14] & 0x0F) << 8) | payload[15]
    if vert_raw & 0x800:  # 12-bit signed, check sign bit to make sure it's positive
        vert_vel = vert_raw - 4096
    else:
        vert_vel = vert_raw
    vert_vel_fpm = vert_vel / 64  # resolution: fpm

    # Byte 16: Track/Heading (tt), resolution = 360/256 degrees.
    track_heading = payload[16] * (360.0 / 256.0)

    # Byte 17: Emitter Category (ee)
    emitter_category = payload[17]

    # Bytes 18-25: Call Sign (8 ASCII characters)
    try:
        call_sign = payload[18:26].decode('ascii')
    except UnicodeDecodeError:
        call_sign = "<non-ASCII data>"

    # Byte 26: Emergency/Priority Code and Spare
    emergency_priority = (payload[26] >> 4) & 0xF
    spare = payload[26] & 0x0F

    # Display the decoded Ownship Report fields
    print("-> Ownship Report:")
    print(f"   Message ID: 0x{msg_id:02X} (Ownship Report)")
    print(f"   Traffic Alert Status (s): {s}")
    print(f"   Address Type (t): {t}")
    print(f"   Participant Address: 0x{participant_address:06X}")
    print(f"   Latitude: {latitude:.6f}°")
    print(f"   Longitude: {longitude:.6f}°")
    print(f"   Altitude: {altitude_ft} ft")
    print(f"   Miscellaneous: 0x{misc:X}")
    print(f"   NIC: {nic}")
    print(f"   NACp: {nacp}")
    print(f"   Horizontal Velocity: {horiz_vel} kt")
    print(f"   Vertical Velocity: {vert_vel_fpm} fpm")
    print(f"   Track/Heading: {track_heading:.2f}°")
    print(f"   Emitter Category: {emitter_category}")
    print(f"   Call Sign: {call_sign}")
    print(f"   Emergency/Priority Code: {emergency_priority}")
    print(f"   Spare: {spare}")

    parsed_data = {
        "latitude": latitude,
        "longitude": longitude,
        "altitude": altitude_ft,
        "horizontal_velocity": horiz_vel,
        "vertical_velocity": vert_vel_fpm,
        "track_heading": track_heading,
        "call_sign": call_sign
    }

    try:
        with open("ownship_data.json", "a") as json_file:
            json_file.write(json.dumps(parsed_data) + "\n")
    except IOError as e:
        print(f"-> Failed to write data to JSON: {e}")

def get_arp_table():
    try:
        process = subprocess.run(['arp', '-a'], capture_output=True, text=True, check=True)
        output = process.stdout
        return output
    except subprocess.CalledProcessError as e:
        print(f"Error executing arp command: {e}")
        return None
    except FileNotFoundError:
         print("arp command not found. Ensure it's available in your system's PATH.")
         return None

if __name__ == "__main__":
    arp_table = get_arp_table()
    hostname = socket.gethostname()
    ipv4_address = socket.gethostbyname(hostname)

    if ipv4_address not in arp_table:
        print("Adding ARP table entry")
        print("ip: ")
        mac_address = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        sub = ["sudo", "arp", "-i", "ap0", "-s", ipv4_address, mac_address]
        result = subprocess.run(sub, capture_output=True, text=True)

    read_gdl90()