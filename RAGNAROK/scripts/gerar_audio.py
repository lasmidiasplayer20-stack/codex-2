#!/usr/bin/env python3
"""Gera voz ou SFX na ElevenLabs. Usa apenas a biblioteca padrão do Python."""
import argparse
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tipo", choices=["voz", "efeito"])
    parser.add_argument("texto")
    parser.add_argument("saida", type=Path)
    parser.add_argument("--voz", help="ID de uma voz disponível na conta")
    parser.add_argument("--segundos", type=float, default=3)
    args = parser.parse_args()
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        parser.error("Defina ELEVENLABS_API_KEY no ambiente; não coloque chaves no código.")
    if args.saida.exists():
        parser.error("O destino já existe; escolha outro nome para preservar o arquivo.")
    if args.tipo == "voz" and not args.voz:
        parser.error("Voz requer --voz com um ID disponível na conta.")
    if args.tipo == "efeito" and not 0.5 <= args.segundos <= 30:
        parser.error("A duração do efeito deve estar entre 0.5 e 30 segundos.")
    if args.tipo == "voz":
        endpoint = f"/v1/text-to-speech/{args.voz}?output_format=mp3_44100_128"
        payload = {"text": args.texto, "model_id": "eleven_multilingual_v2", "language_code": "pt"}
    else:
        endpoint = "/v1/sound-generation"
        payload = {"text": args.texto, "duration_seconds": args.segundos, "prompt_influence": 0.4}
    request = urllib.request.Request(
        "https://api.elevenlabs.io" + endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = response.read()
            mime = response.headers.get("Content-Type", "")
        if "audio" not in mime or len(data) < 1000:
            raise ValueError("A API não retornou um áudio válido.")
    except urllib.error.HTTPError as exc:
        status = None
        try:
            detail = json.loads(exc.read()).get("detail", {})
            if isinstance(detail, dict):
                status = detail.get("status")
        except (ValueError, AttributeError):
            pass
        print(f"Erro ElevenLabs: HTTP {exc.code}; status={status}", file=sys.stderr)
        return 1
    except (urllib.error.URLError, ValueError):
        print("Falha de conexão ou resposta inválida da ElevenLabs.", file=sys.stderr)
        return 1
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with args.saida.open("xb") as output:
        output.write(data)
    print(f"Criado: {args.saida} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
