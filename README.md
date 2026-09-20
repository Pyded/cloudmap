<!-- Файл сгенерирован scripts/generate.py. Не редактируйте его вручную. -->

# cloudmap

Нейтральный каталог соответствий облачных ресурсов между Cloud.ru Evolution, Cloud.ru Advanced и Yandex Cloud.

Источником истины служат отдельные YAML-файлы:

- `resources/` — нейтральные ресурсы и их соответствия у провайдеров;
- `sources/` — официальные страницы документации и API, на которые ссылаются ресурсы.

`README.md` и `catalog.json` генерируются из них детерминированно.

## Проверка и генерация

```bash
python -m pip install -r requirements.txt
python scripts/validate.py
python scripts/validate.py --check-urls
python scripts/generate.py
```

## Каталог

| Resource | Cloud.ru Evolution | Cloud.ru Advanced | Yandex Cloud |
| --- | --- | --- | --- |
| `managed_postgresql` — Управляемая база данных PostgreSQL | — | Relational Database Service for PostgreSQL<br>Relational Database Service for PostgreSQL ([документация](https://cloud.ru/docs/en/usermanual/rds/en-us_topic_dashboard); [API](https://cloud.ru/docs/en/api/rds/en-us_topic_0032347780)) | — |
| `public_ip` — Публичный IP-адрес | Публичный IP<br>Виртуальные машины ([документация](https://cloud.ru/docs/virtual-machines/ug/index.html); [API](https://cloud.ru/docs/api/specs/virtual-machines/ug/_specs/openapi-v3.yaml)) | Elastic IP<br>Elastic IP ([документация](https://cloud.ru/docs/en/usermanual/eip/overview_0001); [API](https://cloud.ru/docs/advanced/overview/advanced-en-api)) | Address<br>Virtual Private Cloud ([документация 1](https://yandex.cloud/ru/docs/vpc/concepts/network), [документация 2](https://yandex.cloud/ru/docs/vpc/concepts/security-groups), [документация 3](https://yandex.cloud/ru/docs/vpc/concepts/address); [API](https://yandex.cloud/ru/docs/vpc/api-ref/)) |
| `security_group` — Группа безопасности | Группа безопасности<br>Виртуальные машины ([документация](https://cloud.ru/docs/virtual-machines/ug/index.html); [API](https://cloud.ru/docs/api/specs/virtual-machines/ug/_specs/openapi-v3.yaml)) | Security Group<br>Virtual Private Cloud ([документация](https://cloud.ru/docs/en/usermanual/vpc/en-us_topic_0013748729); [API](https://cloud.ru/docs/advanced/overview/advanced-en-api)) | Security Group<br>Virtual Private Cloud ([документация 1](https://yandex.cloud/ru/docs/vpc/concepts/network), [документация 2](https://yandex.cloud/ru/docs/vpc/concepts/security-groups), [документация 3](https://yandex.cloud/ru/docs/vpc/concepts/address); [API](https://yandex.cloud/ru/docs/vpc/api-ref/)) |
| `subnet` — Подсеть | Подсеть<br>Виртуальные машины ([документация](https://cloud.ru/docs/virtual-machines/ug/index.html); [API](https://cloud.ru/docs/api/specs/virtual-machines/ug/_specs/openapi-v3.yaml)) | Subnet<br>Virtual Private Cloud ([документация](https://cloud.ru/docs/en/usermanual/vpc/en-us_topic_0013748729); [API](https://cloud.ru/docs/advanced/overview/advanced-en-api)) | Subnet<br>Virtual Private Cloud ([документация 1](https://yandex.cloud/ru/docs/vpc/concepts/network), [документация 2](https://yandex.cloud/ru/docs/vpc/concepts/security-groups), [документация 3](https://yandex.cloud/ru/docs/vpc/concepts/address); [API](https://yandex.cloud/ru/docs/vpc/api-ref/)) |
| `virtual_machine` — Виртуальная машина | Виртуальная машина<br>Виртуальные машины ([документация](https://cloud.ru/docs/virtual-machines/ug/index.html); [API](https://cloud.ru/docs/api/specs/virtual-machines/ug/_specs/openapi-v3.yaml)) | Elastic Cloud Server<br>Elastic Cloud Server ([документация](https://cloud.ru/docs/en/usermanual/ecs/en-us_topic_0013771112); [API](https://cloud.ru/docs/advanced/overview/advanced-en-api)) | Virtual Machine<br>Compute Cloud ([документация](https://yandex.cloud/ru/docs/compute/concepts/vm); [API](https://yandex.cloud/ru/docs/compute/api-ref/)) |
