# ZerodayTTS

> [Microsoft Azure Cognitive Services API (text-to-speech)](https://azure.microsoft.com/en-us/services/cognitive-services/text-to-speech/#features)를 활용한 TTS 디스코드 봇

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

## Developer Guide

- ### git pre-commit 설정

```sh
cd .git/hooks
touch pre-commit
```

이제 편집기로 pre-commit 에 아래 스크립트를 추가해주세요.

```sh
#!/bin/sh
pip3 install -r requirements-dev.txt
pip3 install -r requirements.txt

sh ./scripts/format.sh
sh ./scripts/lint.sh
```

- ### Run

```sh
export ms_key=<your-api-key>
export ZERODAY_TTS_DISCORD_TOKEN=<your-discord-token>

pip3 install -r requirements.txt

# 처음 실행하는 경우 
python3 configure.py

python3 start.py
```

## License

This source code is distributed under the [**MIT License**](./LICENSE).
