from __future__ import annotations

import struct

from Crypto.Cipher import Salsa20

from revlabs_probe.gt7 import KEY, MAGIC, decrypt_packet, parse_packet


def make_packet(
    *,
    size: int = 296,
    packet_id: int = 1,
    speed_mps: float = 50.0,
    rpm: float = 7000.0,
    gear: int = 3,
    throttle: int = 200,
    brake: int = 0,
    fuel: float = 30.0,
    car_code: int = 3485,
) -> bytes:
    payload = bytearray(size)
    struct.pack_into("<i", payload, 0x00, MAGIC)
    struct.pack_into("<f", payload, 0x04, 1.0)
    struct.pack_into("<f", payload, 0x08, 2.0)
    struct.pack_into("<f", payload, 0x0C, 3.0)
    struct.pack_into("<f", payload, 0x3C, rpm)
    struct.pack_into("<f", payload, 0x44, fuel)
    struct.pack_into("<f", payload, 0x48, 60.0)
    struct.pack_into("<f", payload, 0x4C, speed_mps)
    struct.pack_into("<i", payload, 0x70, packet_id)
    payload[0x90] = gear | (4 << 4)
    payload[0x91] = throttle
    payload[0x92] = brake
    struct.pack_into("<i", payload, 0x124, car_code)
    iv = (0x11223344).to_bytes(4, "little")
    payload[0x40:0x44] = iv
    nonce = (0x11223344 ^ 0xDEADBEEF).to_bytes(4, "little") + iv
    cipher = Salsa20.new(key=KEY, nonce=nonce)
    encrypted = bytearray(cipher.encrypt(bytes(payload)))
    # The IV field is sent in plaintext; the console encrypts the rest.
    encrypted[0x40:0x44] = iv
    return bytes(encrypted)


def test_decrypt_and_parse_packet() -> None:
    raw = make_packet(packet_id=42, speed_mps=55.5, rpm=7800, gear=4, fuel=22.5)
    decrypted = decrypt_packet(raw)
    assert decrypted is not None
    packet = parse_packet(decrypted)
    assert packet is not None
    assert packet.packet_type == "A"
    assert packet.packet_id == 42
    assert packet.gear == 4
    assert packet.suggested_gear == 4
    assert packet.speed_mps == 55.5
    assert packet.engine_rpm == 7800
    assert packet.fuel_level_l == 22.5
    assert packet.car_code == 3485


def test_invalid_packet_returns_none() -> None:
    assert decrypt_packet(b"\0" * 32) is None
    assert parse_packet(b"\0" * 296) is None
