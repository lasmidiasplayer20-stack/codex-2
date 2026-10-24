# AiTrends e Stick Animator para Codex

[Instruções de uso](README-CODEX.md) · [Pacote ZIP](animation-plugins-codex.zip)

## Demonstrações

Os MP4s abaixo foram renderizados pelo Codex neste ambiente. **Não vieram prontos nos arquivos `.plugin`.** O conteúdo foi fornecido pelos próprios plugins: cenas e roteiro do exemplo `reaction-time` no aiTrends; roteiro, personagens e cenas construídos pelo `selftest.py` original no Stick Animator. Não são histórias ou cenas novas criadas pelo Codex. A adaptação, instalação e execução foram feitas aqui.

- [aiTrends — MP4 de 3 segundos, sem áudio](aitrends-demo.mp4)
- [Stick Animator — MP4 de 7,6 segundos, com áudio](stick-demo.mp4)
- [Quadros aiTrends](aitrends-sheet.png)
- [Quadro Stick Animator](stick-frame.png)

## Executar

```bash
cd /workspace/codex-2/AiTrends
python3 studio.py doctor
```

Fontes, assets e demonstrações estão nesta pasta. O ambiente virtual e os caches locais ficam ignorados pelo Git; em outra máquina execute `python3 studio.py setup`. O pacote ZIP contém fontes e demonstrações, sem dependências binárias.

Para a origem de cada arquivo, os comandos de reprodução e o fluxo de um vídeo novo, consulte as [instruções específicas](README-CODEX.md).
