from __future__ import annotations

import base64
import json
import socket
import threading
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .gt7 import decrypt_packet, packet_type_for_size, parse_packet

HEARTBEAT_PORT = 33739
TELEMETRY_PORT = 33740


class Capture:
    def __init__(
        self,
        ps_ip: str,
        out_dir: Path,
        duration: float = 60.0,
        heartbeat: str = "A",
        heartbeat_interval: float = 1.0,
    ) -> None:
        self.ps_ip = ps_ip
        self.out_dir = out_dir
        self.duration = duration
        self.heartbeat = heartbeat
        self.heartbeat_interval = heartbeat_interval
        self.stop_event = threading.Event()
        self.counts: Counter[str] = Counter()
        self.invalid_packets = 0
        self.decoded_frames: list[dict[str, Any]] = []
        self.speeds: list[float] = []
        self.rpms: list[float] = []
        self.summary: dict[str, Any] = {}

    def _heartbeat_loop(self, sock: socket.socket) -> None:
        payload = self.heartbeat.encode("utf-8")
        while not self.stop_event.is_set():
            try:
                sock.sendto(payload, (self.ps_ip, HEARTBEAT_PORT))
            except OSError:
                pass
            self.stop_event.wait(self.heartbeat_interval)

    def run(self) -> dict[str, Any]:
        raw_dir = self.out_dir / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        raw_path = raw_dir / "packets.jsonl"
        decoded_path = self.out_dir / "decoded.jsonl"

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", TELEMETRY_PORT))
        sock.settimeout(0.5)

        heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            args=(sock,),
            daemon=True,
        )
        heartbeat_thread.start()

        started_at = datetime.now(timezone.utc)
        deadline = time.monotonic() + self.duration
        last_packet_at: str | None = None
        first_packet_at: str | None = None

        try:
            with raw_path.open("w", encoding="utf-8") as raw_file, decoded_path.open(
                "w", encoding="utf-8"
            ) as decoded_file:
                while time.monotonic() < deadline:
                    try:
                        data, address = sock.recvfrom(4096)
                    except TimeoutError:
                        continue

                    received_at = datetime.now(timezone.utc)
                    timestamp = received_at.isoformat()
                    if first_packet_at is None:
                        first_packet_at = timestamp
                    last_packet_at = timestamp

                    packet_type = packet_type_for_size(len(data))
                    self.counts[packet_type or f"unknown:{len(data)}"] += 1

                    raw_file.write(
                        json.dumps(
                            {
                                "ts": timestamp,
                                "address": address[0],
                                "port": address[1],
                                "size": len(data),
                                "packet_type": packet_type,
                                "heartbeat": self.heartbeat,
                                "raw_b64": base64.b64encode(data).decode("ascii"),
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )

                    decrypted = decrypt_packet(data)
                    if decrypted is None:
                        self.invalid_packets += 1
                        continue

                    packet = parse_packet(decrypted)
                    if packet is None:
                        self.invalid_packets += 1
                        continue

                    if packet.speed_mps is not None:
                        self.speeds.append(packet.speed_mps)
                    if packet.engine_rpm is not None:
                        self.rpms.append(packet.engine_rpm)

                    decoded_file.write(
                        json.dumps(
                            {
                                "ts": timestamp,
                                **packet.as_dict(),
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
                    if len(self.decoded_frames) < 300:
                        self.decoded_frames.append(
                            {
                                "ts": timestamp,
                                **packet.as_dict(),
                            }
                        )
        finally:
            self.stop_event.set()
            sock.close()
            heartbeat_thread.join(timeout=2.0)

        self.summary = self._build_summary(
            started_at=started_at,
            first_packet_at=first_packet_at,
            last_packet_at=last_packet_at,
            raw_path=raw_path,
            decoded_path=decoded_path,
        )
        (self.out_dir / "summary.json").write_text(
            json.dumps(self.summary, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        (self.out_dir / "frames_sample.json").write_text(
            json.dumps(self.decoded_frames, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return self.summary

    def _build_summary(
        self,
        started_at: datetime,
        first_packet_at: str | None,
        last_packet_at: str | None,
        raw_path: Path,
        decoded_path: Path,
    ) -> dict[str, Any]:
        speeds = self.speeds
        rpms = self.rpms
        return {
            "started_at": started_at.isoformat(),
            "ps_ip": self.ps_ip,
            "heartbeat": self.heartbeat,
            "duration_s": self.duration,
            "first_packet_at": first_packet_at,
            "last_packet_at": last_packet_at,
            "packet_counts": dict(self.counts),
            "invalid_packets": self.invalid_packets,
            "decoded_frames_sample": len(self.decoded_frames),
            "max_speed_mps": max(speeds) if speeds else None,
            "max_rpm": max(rpms) if rpms else None,
            "raw_file": str(raw_path),
            "decoded_file": str(decoded_path),
            "notes": [
                "GT7 expõe apenas o carro local.",
                "WSL2 pode não receber UDP da LAN; prefira captura nativa.",
                "Pacotes crus são preservados para reprocessamento.",
            ],
        }
