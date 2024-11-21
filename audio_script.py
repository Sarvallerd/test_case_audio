import argparse
import logging
import json
from enum import Enum
from logging import Logger
from pathlib import Path

import wave
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer


MAIN_PATH = Path(__file__).parent.resolve()


def modify_audio(
    input_path: Path,
    logger: Logger,
    speed: float = 1.0,
    volume: int = 0,
) -> None:
    """Функция для модификации параметров аудио.

    Изменения скорости и громкости аудио файла.

    Parameters
    ----------
    input_path : Path
        Путь до аудио файла
    logger : Logger
        Логгер
    speed : float, optional
        Множитель скорости воспроизведения аудио, by default 1.0
    volume : int, optional
        На сколько в Дб увеличить громкость аудио, by default 0
    """
    audio = AudioSegment.from_wav(input_path)
    audio = audio + volume
    audio = audio.speedup(playback_speed=speed)

    save_path = MAIN_PATH / "results/modified"
    save_path.mkdir(parents=True, exist_ok=True)

    audio.export(save_path / f"{input_path.stem}.wav", format="wav")
    logger.info(f"Модифицированный файл сохранен: {input_path.stem}")


def transcribe_audio(
    input_path: Path,
    model_path: str,
    logger: Logger,
) -> None:
    """Фукнция для ASR.

    Сохраняет транскрибцию аудио.
    При необходимости конвертирует и сохроняет аудио в нужном формате.

    Parameters
    ----------
    input_path : Path
        Путь до аудио файла
    model_path : str
        Путь до модели для ASR
    logger : Logger
        Логгер
    """
    with wave.open(str(input_path), "rb") as wf:
        if (
            wf.getnchannels() != 1
            or wf.getsampwidth() != 2
            or wf.getframerate() not in [8000, 16000]
        ):
            logger.warning(
                "Аудио файл должен быть в формате mono PCM с\
                     частотой дискретизации от 8000 до 16000 Hz."
            )

            converted_file = _convert_to_mono_pcm(input_path=input_path, logger=logger)
            transcribe_audio(
                input_path=converted_file, model_path=model_path, logger=logger
            )
            return

        model = Model(model_path)
        recognizer = KaldiRecognizer(model, wf.getframerate())
        recognizer.SetWords(True)

        transcription = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                res = recognizer.Result()
                transcription.append(json.loads(res))

        res = recognizer.FinalResult()
        transcription.append(json.loads(res))

        save_path = MAIN_PATH / "results/transcriptions/"
        save_path.mkdir(parents=True, exist_ok=True)

        output_file = save_path / f"{input_path.stem}.json"
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(transcription, f, ensure_ascii=False, indent=4)


def main(
    command: str,
    input_path: Path,
    logger: Logger,
    speed: float | None = None,
    volume: int | None = None,
    model_path: str | None = None,
) -> None:
    """Главная функция скрипта.

    В ней происходит вызов функций необходимых пользователю.

    Parameters
    ----------
    command : str
        Тип запуска скрипта
    input_path : Path
        Путь до аудио файла
    logger : Logger
        Логгер
    speed : float | None, optional
        Множитель скорости воспроизведения аудио, by default None
    volume : int | None, optional
        На сколько в Дб увеличить громкость аудио, by default None
    model_path : str | None, optional
        Путь до модели для ASR, by default None
    """
    match command:
        case Commands.MODIFY:
            modify_audio(
                input_path=input_path,
                logger=logger,
                speed=speed,
                volume=volume,
            )
        case Commands.TRANSCRIBE:
            transcribe_audio(
                input_path=input_path, model_path=model_path, logger=logger
            )


def _create_logger() -> Logger:
    """Создает логгер.

    Returns
    -------
    Logger
        Логгер
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("AudioScript logger")
    return logger


def _convert_to_mono_pcm(
    input_path: Path,
    logger: Logger,
    sample_rate: int = 16000,
) -> Path:
    """Конвертер для аудио. Необходимо для транскрибции текста.

    Parameters
    ----------
    input_path : Path
        Путь до аудио файла
    logger : Logger
        Логгер
    sample_rate : int, optional
        Необходимая частота дискретизации для работы модели, by default 16000

    Returns
    -------
    Path
        Путь к аудио в нужном формате
    """
    audio = AudioSegment.from_file(input_path)

    audio = audio.set_channels(1)

    audio = audio.set_frame_rate(sample_rate)

    save_path = MAIN_PATH / "results/temp"
    save_path.mkdir(parents=True, exist_ok=True)
    save_path = save_path / f"{input_path.stem}.wav"

    audio.export(save_path, format="wav")
    logger.info(f"Файл сконвертирован и успешно сохранен {save_path}")
    return save_path


class Commands(Enum):
    """Enum для перечисления вариантов запуска срипта."""

    MODIFY: str = "modify"
    TRANSCRIBE: str = "transcribe"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Приложение для работы с аудиофайлами WAV"
    )

    parser.add_argument(
        "command", help="Тип запуска приложения", choices=["modify", "transcribe"]
    )

    parser.add_argument("input_path", help="Путь к исходному аудиофайлу")

    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Коэффициент скорости воспроизведения (по умолчанию 1.0)",
        required=False,
    )
    parser.add_argument(
        "--volume",
        type=int,
        default=0,
        help="Изменение громкости в децибелах (по умолчанию 0)",
        required=False,
    )

    parser.add_argument(
        "--model_path",
        help="Путь к модели Vosk. В models/ лежат папки с двумя моделями для RU и EN языков.",
        required=False,
    )

    args = parser.parse_args()
    logger = _create_logger()
    main(
        command=Commands(args.command),
        input_path=Path(args.input_path),
        logger=logger,
        speed=args.speed if args.speed is not None else None,
        volume=args.volume if args.volume is not None else None,
        model_path=args.model_path,
    )
