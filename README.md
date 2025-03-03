# AREA

## Auteurs

* **Dorian Senecot** _alias_ [@doriansenecot](https://github.com/doriansenecot)
* **Lucas Debize** _alias_ [@lucasdebize](https://github.com/lucas-debize)
* **Matéo Lechantre** _alias_ [@eldiste](https://github.com/Eldiste)
* **Barthélémy Villard** _alias_ [@barthosss](https://github.com/barthossss)
* **Lyam Gomes** _alias_ [@1yam](https://github.com/1yam)

# README.md

## Introduction
Ce projet est un système web basé sur FastAPI, Redis, PostgreSQL, Alembic et SQLAlchemy, conçu pour implémenter un système d’Actions, de Réactions et de Triggers (déclencheurs), inspiré du concept "AREA" (similaire à IFTTT/Zapier).

## Fonctionnalités Clés
- **GitHub, Microsoft, Google, Spotify**: Intégration avec des services populaires pour une gestion étendue des Actions et Réactions.
- **FastAPI**: Fournit une API REST pour gérer les ressources, les utilisateurs, les Actions, les Réactions, et les Triggers.
- **PostgreSQL + SQLAlchemy + Alembic**: Gère la persistance des données, la définition des modèles et les migrations de schéma.
- **Redis et Workers**: Redis sert de file d’attente pour les tâches (Actions/Triggers) et les Workers exécutent ces tâches de façon asynchrone.
- **Actions, Réactions, Triggers (AREA)**: Des composants modulaires permettant de définir des flux événementiels (un Trigger déclenche une Action, et une Réaction s'exécute ensuite). Les déclencheurs et les actions prennent désormais en charge des dates et horaires configurables.

## Structure de la Documentation
1. [Architecture](./ARCHITECTURE.md): Vue d’ensemble des composants et de leur interaction.
2. [Interactions de configuration backend/frontend](./INTERACTIONS_ENTRE_FRONT_ET_BACKEND.md): explication du système de config des formulaires.
3. [Actions, Réactions, Triggers](./ACTIONS_REACTIONS_TRIGGERS.md): Documentation détaillée sur ces composants, les nouveaux services ajoutés, et comment en créer de nouveaux.
3. [Backend et Modèles](./MODELS.md): Description des modèles de base de données, de leurs champs et relations.
4. [API Endpoints](./API_ENDPOINTS.md): Liste et description des endpoints FastAPI.
5. [Workers et Workflow](./WORKER_WORKFLOW.md): Explication du fonctionnement du système de tâches asynchrones et de l’orchestration via Redis et les Workers.
6. [Configuration et Déploiement](./CONFIG_DEPLOYMENT.md): Informations sur la configuration de l’application et son déploiement.
7. [Contributions](./CONTRIBUTIONS.md): Guide pour contribuer au projet, configurer l’environnement de développement, exécuter les tests, etc.
9. [Tests et Qualité](./TESTING.md): Comment exécuter et écrire des tests, outils de CI/CD, linting, formatage.

---

# ARCHITECTURE.md

## Vue d’Ensemble
Le projet est structuré autour de plusieurs composants principaux :

- **FastAPI**: Point d’entrée de l’application, gère les requêtes HTTP.
- **Base de Données PostgreSQL**: Stocke les informations sur les utilisateurs, les services, les Actions, les Réactions, les Triggers, et les AREA.
- **SQLAlchemy / Alembic**: Définit les modèles (ORM) et gère les migrations de la base.
- **Redis**: Sert de file d’attente (queue) pour les tâches déclenchées par les Triggers.
- **Workers**: Processus asynchrones qui écoutent la file Redis, exécutent les Actions et déclenchent les Réactions.
- **ACTIONS/REACTIONS/TRIGGERS**: Classes modulaires pour définir le comportement du système.

## Diagramme d’Architecture (Exemple Simplifié)

```plaintext
      ┌─────────────────┐
      │     Clients     │
      └──────∧──────────┘
       config│   │ HTTP
             │   │ create user, create actions reaction and triggers
             │   v
      ┌─────────────────┐
      │     FastAPI     │
      └───┬───────────┬─┘
          │           │
      (ORM)         (Queue)
          │           │
          v           v
  ┌────────────┐  ┌────────┐
  │ PostgreSQL │  │  Redis │
  └──────┬─────┘  └───┬────┘
         │            │
         v            v
   ┌─────────┐   ┌─────────┐
   │ Alembic │   │ Workers │
   └─────────┘   └─────────┘
      
```

# INTERACTIONS_ENTRE_FRONT_ET_BACKEND.md

## Introduction
Le fonctionnement du front-end et du back-end dans ce système s’articule autour d’un flux d’informations standardisé. Le front-end interagit avec le back-end principalement via des endpoints d’API. Parmi ces endpoints, l’un des plus importants pour comprendre la logique AREA est l’endpoint `/config`.

Ce point d’entrée fournit au front-end une description structurée de tous les types de Triggers, d’Actions et de Réactions disponibles dans le système, ainsi que les schémas de configuration qui leur sont associés. Ainsi, le front-end peut afficher dynamiquement des formulaires, des champs et des options en fonction des services et des tâches disponibles, sans nécessiter de mises à jour statiques du code.

## Exemple de Fonctionnement

1. **Le front-end appelle l’endpoint `/config`** :  
   Lorsqu’un utilisateur souhaite créer une nouvelle AREA, le front-end contacte l’endpoint `/config` pour obtenir la liste complète des Triggers, Actions et Réactions disponibles.
   
   L’endpoint renvoie une structure JSON qui détaille, pour chaque type d’élément, son nom, son type, et un `config_schema` décrivant les propriétés nécessaires à sa configuration.

2. **Interprétation du `config_schema` côté front-end** :  
   Le front-end lit le `config_schema`, généralement conforme à JSON Schema, ce qui indique les champs requis, leurs types, les descriptions, etc.  
   
   Par exemple, un Trigger peut exiger un `interval` (entier) et un `channel_id` (chaîne pour l’ID Discord). Le front-end utilise ces informations pour générer un formulaire adapté : champ numérique pour l’intervalle, champ texte pour le channel_id.

3. **Validation et Envoi des Données** :  
   Une fois que l’utilisateur a rempli les champs, le front-end peut valider ces données puis les envoyer au back-end pour créer, par exemple, une nouvelle instance de Trigger au sein d’une AREA.

4. **Traitement côté back-end** :  
   Le back-end, via des modèles Pydantic, valide les données reçues. Les classes (ex. `TriggersServiceConfig`, `ActionServiceConfig`) vérifient que les propriétés correspondent au schéma.  
   
   Par exemple :
   ```python
   class TriggersServiceConfig(BaseModel):
       interval: Optional[int] = Field(..., description="Interval Between Run")

   class ActionServiceConfig(BaseModel):
       filters: Optional[FilterConfig] = Field(None, description="Filters applied to the action data")

   class ReactionServiceConfig(BaseModel):
       custom_action_output: Optional[str] = Field(None, description="Use any data instead of the output")

   class TriggersDiscordMessage(TriggersServiceConfig):
       channel_id: str = Field(..., description="Discord Channel ID")

   class TriggersDiscordGuild(TriggersServiceConfig):
       guild_id: str = Field(..., description="Guild Id")

Ces classes correspondent aux schémas fournis par /config. Si les données ne correspondent pas (type de champ incorrect, champ requis manquant), une erreur est renvoyée au front-end.

Exécution et Retour d’Information :  
Après validation, le back-end crée l’entité (Trigger, Action, Réaction) et l’associe à une AREA. Le front-end peut alors afficher un message de succès, ou mettre à jour l’interface pour refléter la nouvelle configuration.

Exemples de JSON renvoyés par /config  
Exemple de Trigger  
```json
{
  "type": "trigger",
  "name": "new_message_in_channel",
  "config_schema": {
    "properties": {
      "interval": {
        "anyOf": [
          { "type": "integer" },
          { "type": "null" }
        ],
        "description": "Interval Between Run",
        "title": "Interval"
      },
      "channel_id": {
        "description": "Discord Channel ID",
        "title": "Channel Id",
        "type": "string"
      }
    },
    "required": ["interval", "channel_id"],
    "title": "TriggersDiscordMessage",
    "type": "object"
  }}
```

Ici, le schéma indique que le Trigger nécessite un interval et un channel_id. Le front-end peut donc générer un formulaire avec deux champs correspondants.

Exemple d’Action

```json
{
  "type": "action",
  "name": "new_message_in_channel",
  "config_schema": {
    "$defs": {
      "FilterCondition": {
        "description": "Represents a single filtering condition.",
        "properties": {
          "field": {
            "description": "Field to filter on (e.g., message content, channel_id)",
            "title": "Field",
            "type": "string"
          },
          "operator": {
            "description": "Operator for filtering (e.g., 'contains', 'equals')",
            "title": "Operator",
            "type": "string"
          },
          "value": {
            "description": "Value to compare against (e.g., 'urgent', '12345')",
            "title": "Value"
          }
        },
        "required": ["field", "operator", "value"],
        "title": "FilterCondition",
        "type": "object"
      },
      "FilterConfig": {
        "description": "Represents a collection of filtering conditions.",
        "properties": {
          "conditions": {
            "items": { "$ref": "#/$defs/FilterCondition" },
            "title": "Conditions",
            "type": "array"
          },
          "match": {
            "$ref": "#/$defs/MatchLogic",
            "default": "all"
          }
        },
        "required": ["conditions"],
        "title": "FilterConfig",
        "type": "object"
      },
      "MatchLogic": {
        "enum": ["all", "any"],
        "title": "MatchLogic",
        "type": "string"
      }
    },
    "properties": {
      "filters": {
        "anyOf": [
          { "$ref": "#/$defs/FilterConfig" },
          { "type": "null" }
        ],
        "default": null,
        "description": "Filters applied to the action data"
      }
    },
    "title": "ActionServiceConfig",
    "type": "object"
  }
}
```

Cet exemple montre qu’une Action peut avoir une configuration de filtres optionnelle. Le front-end peut donc afficher une interface permettant de créer plusieurs conditions de filtrage, avec un champ field, un operator et une value. Le match peut être "all" ou "any", indiquant si toutes ou au moins une des conditions doivent être remplies.

# Conclusion

## En résumé, le front-end s’adapte dynamiquement aux capacités du back-end grâce à l’endpoint /config :
- De nouveaux services tels que GitHub, Microsoft, Google et Spotify sont désormais disponibles.
- Les déclencheurs et actions prennent en charge des dates et horaires pour des flux événementiels spécifiques.

- Le back-end définit des schémas clairs pour chaque Trigger, Action et Réaction.
- Le front-end génère des formulaires à partir de ces schémas.
- L’utilisateur remplit ces formulaires, et le front-end envoie les données au back-end.
- Le back-end valide et crée les entités configurées, garantissant une interaction cohérente, évolutive et facile à maintenir entre les deux couches.
Copy code


## Introduction
Les Actions, Réactions, et Triggers sont la base de la logique AREA. Un Trigger surveille une condition puis déclenche une Action, et une Réaction s’exécute une fois l’Action terminée.

Trigger: Détermine si une condition est remplie (ex. un intervalle de temps, un événement externe).  
Action: Opération à effectuer lorsque le Trigger est activé (ex. requête HTTP).  
Réaction: Tâche exécutée après l’Action (ex. logguer le résultat, envoyer une notification).

## Classes de Base

### Base Action
python  

```python
from src.service.base import BaseComponent

class Action(BaseComponent):
    name = "base_action"

    async def execute(self, *args, **kwargs):
        raise NotImplementedError("Action subclasses must implement the `execute` method.")
```

### Base Reaction
python  

```python
from src.service.base import BaseComponent

class Reaction(BaseComponent):
    name = "base_reaction"

    async def execute(self, action_result, *args, **kwargs):
        raise NotImplementedError("Reaction subclasses must implement the `execute` method.")
```

### Base Trigger
python  

```python
from src.service.base import BaseComponent

class Trigger(BaseComponent):
    name = "base_trigger"

    def __init__(self, config: dict):
        self.config = config

    async def execute(self, *args, **kwargs) -> bool:
        raise NotImplementedError("Trigger subclasses must implement the `execute` method.")
```

## Exemples

### Action HTTP GET
python  

```python
from src.service.Action.actions import Action
import aiohttp

class HttpGetAction(Action):
    name = "http_get_action"

    async def execute(self, url: str, *args, **kwargs):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()
```

### Reaction Print
python  

```python
from src.service.Reaction.reactions import Reaction

class PrintReaction(Reaction):
    name = "print_reaction"

    async def execute(self, action_result, *args, **kwargs):
        print(f"Reaction executed with result: {action_result}")
```

### Trigger Temporel
python  

```python
from src.service.Trigger.triggers import Trigger
import time

class TimeTrigger(Trigger):
    name = "time_trigger"

    async def execute(self, *args, **kwargs) -> bool:
        last_run = self.config.get("last_run", 0)
        interval = self.config.get("interval", 60)
        current_time = time.time()

        if current_time - last_run >= interval:
            self.config["last_run"] = current_time
            return True
        return False
```

## Ajout d’un Nouveau Composant
Pour ajouter un nouvel élément, il suffit de créer une classe héritant de Action, Reaction ou Trigger, puis de l’enregistrer auprès du Worker:

python  

```python
from src.service.Worker.worker import Worker
from src.service.Action.http_get_action import HttpGetAction
from src.service.Reaction.print_reaction import PrintReaction
from src.service.Trigger.time_trigger import TimeTrigger

worker = Worker(queue_name="task_queue", redis_client=redis_client)
worker.register_action(HttpGetAction)
worker.register_reaction(PrintReaction)
worker.register_trigger(TimeTrigger)
```

# MODELS.md

## Modèles et Relations

### Aperçu

Entité       | Champs
User         | id, username, email, settings, is_active, created_at, updated_at
Area         | id, user_id, action_id, reaction_id, trigger_id, created_at, updated_at, config
Trigger      | id, type, config, area_id, last_run, created_at, updated_at
Action       | id, name, service_id, config, description, created_at, updated_at
Reaction     | id, name, service_id, config, description, created_at, updated_at
ActionConfig | id, action_id, parameters, metadata, created_at, updated_at
ReactionConfig | id, reaction_id, parameters, metadata, created_at, updated_at
Service      | id, name, integration_type, scopes, description, created_at, updated_at
UserService  | id, user_id, service_id, access_token, refresh_token, permissions, expires_at

TriggersDiscord | id, guild_id, channel_id, interval, created_at, updated_at
ActionsWebhook  | id, url, method, payload, created_at, updated_at
ReactionsEmail  | id, to_email, subject, message, created_at, updated_at

### Relations
User → (1-N) → Area  
User ↔ (N-N via UserService) ↔ Service (permissions, tokens added)  
Area → (1-1) → Trigger, Action, Reaction  
Trigger → (N-1) → Area (with specific subtypes: DiscordChannel, Cron)  
Action → (N-1) → Service (subtypes: Webhook, HTTP Request)  
Reaction → (N-1) → Service (with subtypes: Email, Print)  
Service → (1-N) → Trigger, Action, Reaction  
TriggerConfig → (1-1) → Trigger  
ActionConfig → (1-1) → Action  
ReactionConfig → (1-1) → Reaction  

### Migrations
Les migrations sont gérées via Alembic et incluent de nouvelles colonnes telles que `scopes`, `metadata`, `access_token`, et `expires_at` pour les relations Service et UserService. Un exemple de commande :

bash  

```bash
alembic upgrade head   # Applique la dernière migration
alembic revision --autogenerate -m "Description"  # Crée une nouvelle migration
```

# API_ENDPOINTS.md

## Introduction
L’API expose des endpoints pour gérer les entités (User, Area, Action, Reaction, Trigger, Service) et interagir avec la logique AREA.


#a faire ajouter les endpoint 

Chaque endpoint est documenté via OpenAPI/Swagger automatique par FastAPI.

# WORKER_WORKFLOW.md

## Fonctionnement du Worker
Le Worker écoute une file Redis, récupère les tâches, vérifie les Triggers, exécute les Actions, puis les Réactions.

### Étapes
- Écoute de la file: Le worker interroge Redis pour des tâches.
- déclenchement du Trigger: Si la condition est remplie, passer à l’Action.
- Exécution de l’Action: Appel de la méthode `execute` de l’Action.
- Exécution de la Réaction: Traitement post-Action, comme une notification.
- Planification ou Fin: Si la tâche est périodique, replanifiée. Sinon, terminée. le trigger continu de tourner.

### Diagramme Simplifié
plaintext  

```plaintext
[Trigger] -> [Queue Redis] -> [Worker] -> [ Action -> [trigger ?]  Reaction] -> [Résultat]
```

# CONFIG_DEPLOYMENT.md

## Configuration
- Fichiers `.env`: Contiennent les infos sur la DB, Redis, etc.
- Variables d’environnement: Paramètres sensibles (URL, identifiants).
- `pyproject.toml` / `requirements.txt`: Dépendances Python.
- `alembic.ini`: Configuration d’Alembic pour les migrations.

### Déploiement
- Local: Via `uvicorn src.web.controllers.main:app --reload` ou `hatch run run`.
- Conteneurs Docker : Peut être configuré pour exécuter l’application et le worker.
- Production: Un serveur ASGI (Uvicorn, Gunicorn), une base Postgres gérée (ex: RDS), Redis managé, un load balancer, etc.

# CONTRIBUTIONS.md

## Configuration de l’Environnement de Dev

### Cloner le dépôt
bash  

```bash
git clone <repository-url>
cd area
```

### Créer un environnement virtuel:
bash  

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Linux/Mac
.venv\Scripts\activate     # On Windows
```

### Installer les dépendances:
bash  

```bash
pip install -e .
```
ou:
```bash
hatch env create
hatch run run
```

## Respect du Code Style
- Formatage: black, isort
- Typing: mypy
- Linting: flake8, ou via `hatch run linting:all`

## Base de Données
- Configurer `.env`
- Initialiser la DB:
bash  

```bash
alembic upgrade head
```

## Tests
- Lancer les tests:
bash  

```bash
hatch run test
```
- Couverture:
bash  

```bash
hatch run test_cov
```

## Lignes Directrices
- Créer une branche par fonctionnalité
- Couvrir le code par des tests
- Mettre à jour la documentation lorsque vous ajoutez une fonctionnalité

# TESTING.md

## Stratégie de Test
- Tests Unitaires: Vérifient le comportement des fonctions et classes isolées.
- Tests d’Intégration: Vérifient le bon fonctionnement entre la DB, l’API, et les Workers.
- Couverture: Mesurer avec pytest-cov.

## Exécution des Tests
bash  

```bash
hatch run test
```
ou
```bash
pytest
```
si pytest est disponible localement.

## Intégration Continue (CI/CD)
Utilisation d’outils (GitHub Actions, GitLab CI, etc.) pour exécuter les tests et linting à chaque commit/pull request.
