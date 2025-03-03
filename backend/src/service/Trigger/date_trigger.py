import logging
import time
from datetime import datetime
from typing import Optional

from src.service.Trigger.triggers import Trigger, TriggerConfig, TriggerResponse

LOGGER = logging.getLogger(__name__)


class DateTriggerConfig(TriggerConfig):
    """
    Configuration pour le DateTrigger qui utilise une date spécifique.
    """

    target_date: str  # La date cible au format ISO-8601 (ex : "2023-12-31T23:59:59")


class DateTriggerResponse(TriggerResponse):
    """
    Réponse pour le DateTrigger.
    """

    event_time: float


class DateTrigger(Trigger):
    """
    Déclencheur qui s'active à une date spécifique.
    """

    name = "date_action"
    config = DateTriggerConfig

    def __init__(self, config: DateTriggerConfig):
        """
        Initialisation du DateTrigger avec sa configuration spécifique.

        :param config: Objet DateTriggerConfig contenant la date cible.
        """
        super().__init__(config)
        self.target_timestamp = self._parse_date_to_timestamp(config.target_date)

    def _parse_date_to_timestamp(self, date_str: str) -> float:
        """
        Convertit une date ISO-8601 en timestamp.

        :param date_str: Date sous forme de chaîne (ex : "2023-12-31T23:59:59").
        :return: La date sous la forme d'un timestamp UNIX.
        """
        try:
            target_date = datetime.fromisoformat(date_str)
            return target_date.timestamp()
        except ValueError as e:
            LOGGER.error(f"Erreur dans le format de la date : {date_str}. {e}")
            raise ValueError(f"Date invalide: {date_str}. Assurez-vous du format ISO-8601.")

    async def execute(self, *args, **kwargs) -> Optional[DateTriggerResponse]:
        """
        Évalue si le temps actuel correspond ou dépasse la date cible.

        :return: DateTriggerResponse si déclenché, None sinon.
        """
        current_time = time.time()
        LOGGER.info(f"Temps actuel: {current_time}, temps cible: {self.target_timestamp}")
        if current_time >= self.target_timestamp:
            LOGGER.info(f"DateTrigger déclenché à {current_time}.")
            return DateTriggerResponse(
                event_time=current_time,
                triggered_at=current_time,
            )
        return None
