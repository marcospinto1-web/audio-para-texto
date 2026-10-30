# Áudio para Texto

Aplicativo gratuito para macOS e Windows que transcreve áudios do WhatsApp e
outros arquivos de voz **localmente**. Nenhum áudio é enviado para servidores.

## Como usar

1. No WhatsApp Web, baixe a mensagem de áudio.
2. Abra o **Áudio para Texto**.
3. Arraste o arquivo para a janela ou clique em **Escolher áudio**.
4. Clique em **Transcrever**.
5. Copie ou salve o texto.

O modelo gratuito de reconhecimento de voz já vem dentro do instalador. A
transcrição funciona sem internet desde o primeiro uso.

## Privacidade

- O processamento acontece no próprio computador.
- O aplicativo não possui conta, anúncios, telemetria ou cobrança.
- Não precisa enviar nem baixar dados durante o uso.
- Os áudios não são guardados pelo aplicativo.

## Instalação para amigos

Baixe o arquivo da página **Releases** do projeto:

- macOS Apple Silicon: `Audio-para-Texto-macOS-arm64.dmg`
- Windows 64 bits: `Audio-para-Texto-Windows-x64.zip`

No Windows, extraia o ZIP e abra `Audio para Texto.exe`. No macOS, abra o DMG e
arraste o aplicativo para a pasta Aplicativos.

Como o aplicativo ainda não possui certificados pagos da Apple e Microsoft, o
sistema pode exibir um aviso de desenvolvedor desconhecido. O código-fonte está
todo disponível para auditoria.

## Desenvolvimento

Requer Python 3.11 ou 3.12.

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python -m pip install -e .[dev]
audio-para-texto
```

Para executar os testes:

```bash
pytest
```

## Gerar instaladores

O workflow em `.github/workflows/build.yml` gera automaticamente pacotes para
Mac e Windows. Ao criar uma tag como `v1.0.0`, os arquivos também são publicados
em uma Release do GitHub.

## Licença

MIT. Você pode usar, compartilhar e modificar gratuitamente.

