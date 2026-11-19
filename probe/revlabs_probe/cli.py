from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .capture import Capture


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="revlabs-probe",
        description="Captura amostras de telemetria UDP do Gran Turismo 7.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    probe = subparsers.add_parser("probe", help="Capturar pacotes do GT7")
    probe.add_argument("--ps-ip", required=True, help="IP do PlayStation na LAN")
    probe.add_argument(
        "--out",
        type=Path,
        default=Path("sample"),
        help="Diretório de saída (padrão: sample)",
    )
    probe.add_argument(
        "--duration",
        type=float,
        default=60.0,
        help="Duração da captura em segundos (padrão: 60)",
    )
    probe.add_argument(
        "--heartbeat",
        choices=["A", "B", "~", "C"],
        default="A",
        help="Tipo de pacote solicitado (padrão: A)",
    )
    probe.add_argument(
        "--heartbeat-interval",
        type=float,
        default=1.0,
        help="Intervalo do heartbeat em segundos (padrão: 1.0)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "probe":
        print(f"Escutando UDP {args.ps_ip}:33740 por {args.duration:.0f}s...")
        print("Pressione Ctrl+C para encerrar antes.")
        capture = Capture(
            ps_ip=args.ps_ip,
            out_dir=args.out,
            duration=args.duration,
            heartbeat=args.heartbeat,
            heartbeat_interval=args.heartbeat_interval,
        )
        try:
            summary = capture.run()
        except KeyboardInterrupt:
            print("\nCaptura interrompida.")
            return 130
        print(f"\nCaptura concluída em {args.out}")
        print(f"Pacotes: {summary['packet_counts']}")
        print(f"Decodificados: {summary['decoded_frames_sample']}")
        print(f"Inválidos: {summary['invalid_packets']}")
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
