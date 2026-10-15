#!/usr/bin/env python3
"""Monta quatro poses-chave em uma prévia de 4 segundos, com áudio separado."""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saida", type=Path, default=root / "videos/testes/kratos_guarda_animatic_4s.mp4")
    args = parser.parse_args()
    if not shutil.which("ffmpeg"):
        parser.error("FFmpeg não está disponível no PATH.")
    if args.saida.exists():
        parser.error("O destino já existe; escolha outro com --saida.")
    folder = root / "imagens/animacoes/cena_001_kratos_guarda/quadros"
    frames = [folder / f"kratos_guarda_{i:04d}.png" for i in range(1, 5)]
    wind = root / "audios/efeitos_sonoros/vento_midgard.mp3"
    ice = root / "audios/efeitos_sonoros/gelo_despertar.mp3"
    for path in [*frames, wind, ice]:
        if not path.is_file():
            parser.error(f"Arquivo necessário não encontrado: {path}")
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ragnarok-animatic-") as temp:
        concat = Path(temp) / "quadros.ffconcat"
        lines = ["ffconcat version 1.0"]
        for frame, duration in zip(frames, [1.0, 0.75, 0.75, 1.5]):
            quoted = frame.as_posix().replace("'", "'\\''")
            lines.extend([f"file '{quoted}'", f"duration {duration}"])
        quoted = frames[-1].as_posix().replace("'", "'\\''")
        lines.append(f"file '{quoted}'")
        concat.write_text("\n".join(lines) + "\n", encoding="utf-8")
        # Mantém poses inteiras. Não usa morphing ou interpolação de personagem.
        video = "[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24,format=yuv420p[v]"
        audio = "[1:a]volume=0.30,atrim=0:4,afade=t=in:d=0.15,afade=t=out:st=3.6:d=0.4[w];[2:a]volume=0.65,adelay=2500:all=1[i];[w][i]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95,atrim=0:4[a]"
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-n",
            "-f", "concat", "-safe", "0", "-i", str(concat),
            "-i", str(wind), "-i", str(ice),
            "-filter_complex", video + ";" + audio,
            "-map", "[v]", "-map", "[a]", "-t", "4",
            "-c:v", "libx264", "-threads", "2", "-preset", "medium", "-crf", "19",
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(args.saida),
        ], check=True)
    print(f"Prévia criada: {args.saida}")


if __name__ == "__main__":
    main()
