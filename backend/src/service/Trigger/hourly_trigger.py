import logging
import time
from datetime import datetime, timedelta
from typing import Optional

from src.service.Trigger.triggers import Trigger, TriggerConfig, TriggerResponse

LOGGER = logging.getLogger(__name__)

class HourlyTriggerConfig(TriggerConfig):
    """
    Configuration pour le HourlyTrigger qui s'exécute à une heure spécifique.
    """
    target_time: str  # L'horaire cible au format "HH:mm:ss" (ex : "08:00:00")


class HourlyTriggerResponse(TriggerResponse):
    """
    Réponse pour le HourlyTri gger.
    """
    event_time: float


class HourlyTrigger(Trigger):
    """
    Déclencheur qui s'active à un horaire précis chaque jour.
    """

    name = "time_of_day_action"
    config = HourlyTriggerConfig

    def __init__(self, config: HourlyTriggerConfig):
        """
        Initialisation du HourlyTrigger avec la configuration spécifique.

        :param config: Objet HourlyTriggerConfig contenant l'horaire cible.
        """
        super().__init__(config)
        self.target_time = self._parse_time_to_seconds(config.target_time)
        self.last_run_date = None  # Permet d'éviter de déclencher plusieurs fois le même jour

    def _parse_time_to_seconds(self, time_str: str) -> int:
        """
        Convertit un horaire (HH:mm:ss) en secondes depuis le début de la journée.

        :param time_str: Horaire sous forme de chaîne (ex : "08:00:00").
        :return: Les secondes écoulées depuis minuit à cet horaire.
        """
        try:
            time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
            return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
        except ValueError as e:
            LOGGER.error(f"Erreur dans le format de l'horaire : {time_str}. {e}")
            raise ValueError(f"L'horaire est invalide : {time_str}. Utilisez le format HH:mm:ss.")

    def _get_next_target_timestamp(self) -> float:
        """
        Calcule le prochain timestamp Unix correspondant à l'horaire cible aujourd'hui ou demain.

        :return: Le prochain timestamp Unix de l'horaire cible.
        """
        now = datetime.now()
        today_midnight = datetime.combine(now.date(), datetime.min.time())
        target_time_today = today_midnight + timedelta(seconds=self.target_time)

        if now.timestamp() < target_time_today.timestamp():
            return target_time_today.timestamp()  # Aujourd'hui
        else:
            return target_time_today.timestamp() + 86400  # Demain (86400s = 24h)

    async def execute(self, *args, **kwargs) -> Optional[HourlyTriggerResponse]:
        """
        Évalue si l'heure actuelle correspond ou dépasse l'horaire ciblé.

        :return: HourlyTriggerResponse si déclenché, None sinon.
        """
        current_time = time.time()
        next_target_time = self._get_next_target_timestamp()

        LOGGER.info(f"Temps actuel: {current_time}, prochain horaire cible: {next_target_time}")
        current_date = datetime.now().date()

        if current_time >= next_target_time:
            if self.last_run_date != current_date:
                self.last_run_date = current_date

                LOGGER.info(f"HourlyTrigger déclenché à {current_time}.")
                return HourlyTriggerResponse(
                    event_time=current_time,
                    triggered_at=current_time
                )
        return None
