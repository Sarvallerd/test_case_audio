# Тестовое задание

## Описание

В проекте предсталвен скрипт с реализацией необходимых функций.

1. Модификация аудиофайла
    Для увелечения/уменьшения громкости, скорости аудио необходимо передать соотвествующие аргументы и путь для файла.
    Модифицированный файл появится в папке results/modified/{название_вашего_файла}.wav

2. Расшифровка аудио в текст
    В папке models/ скачаны и разархивированы 2 модели для RU и EN языков. Для расшифорки необходимо передать путь до аудио файла и модели для соотвествующего языка.
    При необходимости аудио файл будет сконвертирован с нужный формат и появится в папке results/temp.
    Расшифровка в формте json будет находится в results/transcriptions/{название_вашего_файла}.json

## Начало работы

### Предусловия

* Для установки окружения с помощью poetry использовался python 3.11.9

### Установка

Для установки зависимостей необходимо выполнить следующие команды в директории проекта:

1. С помощью pip

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. С помощью poetry

```
poetry install
```

## Использование

Примеры запуска скрипта:

* Расшифровка аудио

```
poetry run python audio_script.py transcribe en.wav --model_path  models/vosk-model-small-en-us-0.15 
poetry run python audio_script.py transcribe ru.wav --model_path  models/vosk-model-small-ru-0.22
```

* Модификация аудио

```
poetry run python audio_script.py modify  en.wav --speed 1.5 --volume 20
poetry run python audio_script.py modify  ru.wav --speed 2.0 --volume 10
```
