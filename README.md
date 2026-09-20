# evo_crossmap

Минимальный каталог соответствий сервисов Cloud.ru Evolution, Cloud.ru Advanced и Yandex Cloud.

В репозитории только два содержательных файла:

- `catalog.yaml` — плоский список сопоставлений и официальных источников;
- `README.md` — краткое описание проекта.

## Формат

Каждая запись содержит нейтральные `id` и `name`, после которых идут доступные платформы:

- `evolution` описывает один сервис напрямую через `name`, `docs` и `api`;
- `advanced.services` и `yandex.services` содержат списки связанных сервисов;
- `docs` и `api` — списки прямых HTTPS-ссылок на официальные источники;
- `api` можно не указывать, если отдельный подтверждённый API-источник отсутствует.

## Каталог

Таблица ниже автоматически обновляется GitHub Action после изменений в `main`.

<!-- catalog-table:start -->
| Resource | Evolution | Advanced | Yandex |
| --- | --- | --- | --- |
| `virtual_machines` — Виртуальные машины | Виртуальные машины ([документация](https://cloud.ru/docs/virtual-machines/ug/index.html); [API](https://cloud.ru/docs/virtual-machines/ug/topics/api-ref-v3)) | Elastic Cloud Server ([документация](https://cloud.ru/docs/en/usermanual/ecs/en-us_topic_0013771112); [API](https://cloud.ru/docs/advanced/overview/advanced-en-api))<br>Elastic Volume Service ([документация](https://cloud.ru/docs/en/usermanual/evs/en-us_topic_0014580741))<br>Virtual Private Cloud ([документация](https://cloud.ru/docs/en/usermanual/vpc/en-us_topic_0013748729)) | Compute Cloud ([документация](https://yandex.cloud/ru/docs/compute/concepts/vm); [API](https://yandex.cloud/ru/docs/compute/api-ref/))<br>Virtual Private Cloud ([документация](https://yandex.cloud/ru/docs/vpc/concepts/network); [API](https://yandex.cloud/ru/docs/vpc/api-ref/)) |
| `managed_postgresql` — Managed PostgreSQL | Managed PostgreSQL ([документация](https://cloud.ru/docs/paas-postgresql/ug/index); [API](https://cloud.ru/docs/paas-postgresql/ug/topics/api-ref)) | Relational Database Service ([документация](https://cloud.ru/docs/en/usermanual/rds/en-us_topic_dashboard); [API](https://cloud.ru/docs/en/api/rds/en-us_topic_0032347780)) | Managed Service for PostgreSQL ([документация](https://yandex.cloud/ru/docs/managed-postgresql/); [API](https://yandex.cloud/en/docs/managed-postgresql/api-ref/)) |
<!-- catalog-table:end -->
