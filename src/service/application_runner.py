"""Application runner entry point."""

from __future__ import annotations

import logging

from src.core.config import AppConfig
from src.core.errors import AdapterError, ApplicationError, NormalizationError
from src.core.logging import CORE_LOGGER

from src.command_mapper.interfaces import CommandNormalizer, CommandParser, CommandValidator
from src.service.interfaces import Controller
from src.speech.interfaces import SpeechAdapterInterface
from src.utils.notifications import build_notification_sound_player


class MouseApplicationRunner:
    """Coordinates the speech-to-action pipeline execution loop."""

    def __init__(
        self,
        adapter: SpeechAdapterInterface,
        normalizer: CommandNormalizer,
        parser: CommandParser,
        validator: CommandValidator,
        controller: Controller,
        config: AppConfig,
        logger: logging.Logger = CORE_LOGGER,
    ) -> None:
        self.adapter = adapter
        self.normalizer = normalizer
        self.parser = parser
        self.validator = validator
        self.controller = controller
        self.config = config
        self.notification_sound_player = build_notification_sound_player()
        self.logger = logger

    def listen_and_execute(self) -> str:
        while True:
            try:
                text = self.adapter.next_text()

                if text is None:
                    self.logger.info("adapter_end")
                    break
                if text == "":
                    continue

                normalized = self.normalizer.normalize(text)
                self.logger.debug(f"normalized_text: {normalized}")

                parse_result = self.parser.parse(normalized)
                if parse_result.error is not None:
                    self.logger.error(f"parse_error: {parse_result.error.reason}")
                    self.notification_sound_player.play_parse_error()
                    continue

                validation = self.validator.validate(parse_result.command)
                if validation.error is not None:
                    self.logger.error(f"validation_error: {validation.error.reason}")
                    self.notification_sound_player.play_parse_error()
                    continue

                # Mouse Clicks
                execution = self.controller.execute(
                    validation.command, self.config
                )
                
                if execution.error is not None:
                    self.logger.error(f"execution_error: {execution.error}")

                if execution.stopped:
                    self.logger.info("execution_stopped")
                    break

            except (AdapterError, NormalizationError):
                raise

            except ApplicationError as exc:
                self.logger.error(f"application_error_in_runtime: {exc}")
                continue

    def run(self) -> None:
        try:
            self.logger.info("runner_started")
            self.notification_sound_player.play_runner_started()
            
            self.listen_and_execute()

        except Exception:
            self.notification_sound_player.play_application_error()
            raise

        finally:
            self.adapter.close()

            self.notification_sound_player.play_runner_finished()
            self.logger.info("runner_finished")
