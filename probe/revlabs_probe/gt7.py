"""GT7 UDP protocol helpers used by the probe."""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import Any

from Crypto.Cipher import Salsa20

KEY = b"Simulator Interface Packet GT7 ver 0.0"[:32]
MAGIC = 0x47375330
IV_XOR_CANDIDATES = (0xDEADBEEF, 0xDEADBEAF, 0x55FABB4F)

PACKET_TYPES = {
    296: "A",
    316: "B",
    344: "~",
    368: "C",
}


@dataclass
class DecodedPacket:
    packet_type: str | None
    size: int
    magic: int | None = None
    packet_id: int | None = None
    position: tuple[float, float, float] | None = None
    velocity: tuple[float, float, float] | None = None
    speed_mps: float | None = None
    engine_rpm: float | None = None
    gear: int | None = None
    suggested_gear: int | None = None
    throttle: int | None = None
    brake: int | None = None
    fuel_level_l: float | None = None
    fuel_capacity_l: float | None = None
    tire_temp_c: tuple[float, float, float, float] | None = None
    suspension: tuple[float, float, float, float] | None = None
    lap_count: int | None = None
    total_laps: int | None = None
    best_lap_ms: int | None = None
    last_lap_ms: int | None = None
    car_code: int | None = None
    flags: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        data = {
            "packet_type": self.packet_type,
            "size": self.size,
            "magic": self.magic,
            "packet_id": self.packet_id,
            "position": self.position,
            "velocity": self.velocity,
            "speed_mps": self.speed_mps,
            "engine_rpm": self.engine_rpm,
            "gear": self.gear,
            "suggested_gear": self.suggested_gear,
            "throttle": self.throttle,
            "brake": self.brake,
            "fuel_level_l": self.fuel_level_l,
            "fuel_capacity_l": self.fuel_capacity_l,
            "tire_temp_c": self.tire_temp_c,
            "suspension": self.suspension,
            "lap_count": self.lap_count,
            "total_laps": self.total_laps,
            "best_lap_ms": self.best_lap_ms,
            "last_lap_ms": self.last_lap_ms,
            "car_code": self.car_code,
            "flags": self.flags,
        }
        if self.extra:
            data["extra"] = self.extra
        return data


def _nonce(data: bytes, xor_value: int) -> bytes:
    iv1 = int.from_bytes(data[0x40:0x44], "little")
    iv2 = iv1 ^ xor_value
    return iv2.to_bytes(4, "little") + iv1.to_bytes(4, "little")


def decrypt_packet(data: bytes) -> bytes | None:
    """Return decrypted packet bytes or None when no known IV variant works."""
    if len(data) < 0x44:
        return None
    for xor_value in IV_XOR_CANDIDATES:
        cipher = Salsa20.new(key=KEY, nonce=_nonce(data, xor_value))
        decrypted = cipher.decrypt(data)
        if len(decrypted) >= 4 and struct.unpack_from("<i", decrypted, 0)[0] == MAGIC:
            return decrypted
    return None


def packet_type_for_size(size: int) -> str | None:
    return PACKET_TYPES.get(size)


def _f32(data: bytes, offset: int) -> float:
    return struct.unpack_from("<f", data, offset)[0]


def _i32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<i", data, offset)[0]


def _i16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<h", data, offset)[0]


def _u8(data: bytes, offset: int) -> int:
    return data[offset]


def _gear(value: int) -> tuple[int, int]:
    # Bits 0-3: current gear, bits 4-7: suggested gear.
    return value & 0x0F, (value >> 4) & 0x0F


def parse_packet(data: bytes) -> DecodedPacket | None:
    """Decode common fields from an already decrypted GT7 packet."""
    if len(data) < 0x128:
        return None
    if _i32(data, 0) != MAGIC:
        return None

    gear, suggested = _gear(_u8(data, 0x90))
    return DecodedPacket(
        packet_type=packet_type_for_size(len(data)),
        size=len(data),
        magic=_i32(data, 0),
        packet_id=_i32(data, 0x70),
        position=(_f32(data, 0x04), _f32(data, 0x08), _f32(data, 0x0C)),
        velocity=(_f32(data, 0x10), _f32(data, 0x14), _f32(data, 0x18)),
        speed_mps=_f32(data, 0x4C),
        engine_rpm=_f32(data, 0x3C),
        gear=gear,
        suggested_gear=suggested,
        throttle=_u8(data, 0x91),
        brake=_u8(data, 0x92),
        fuel_level_l=_f32(data, 0x44),
        fuel_capacity_l=_f32(data, 0x48),
        tire_temp_c=(
            _f32(data, 0x60),
            _f32(data, 0x64),
            _f32(data, 0x68),
            _f32(data, 0x6C),
        ),
        suspension=(
            _f32(data, 0xC4),
            _f32(data, 0xC8),
            _f32(data, 0xCC),
            _f32(data, 0xD0),
        ),
        lap_count=_i16(data, 0x74),
        total_laps=_i16(data, 0x76),
        best_lap_ms=_i32(data, 0x78),
        last_lap_ms=_i32(data, 0x7C),
        car_code=_i32(data, 0x124),
        flags=_i16(data, 0x8E),
    )
