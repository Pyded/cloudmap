<!-- Файл сгенерирован scripts/generate.py. Не редактируйте его вручную. -->

# cloudmap

Минимальный нейтральный каталог соответствий облачных ресурсов между Cloud.ru Evolution, Cloud.ru Advanced и Yandex Cloud.

Источником истины служат YAML-файлы в `catalog/`. `README.md` и `catalog.json` генерируются из них детерминированно.

## Проверка и генерация

```bash
python -m pip install -r requirements.txt
python scripts/validate.py
python scripts/validate.py --check-urls
python scripts/generate.py
```

## Каталог

| Resource | Evolution | Advanced | Yandex |
| --- | --- | --- | --- |
| `virtual_machine` — Виртуальная машина | Виртуальные машины — Виртуальная машина ([документация](https://cloud.ru/docs/virtual-machines/ug/index), [API](https://cloud.ru/docs/virtual-machines/ug/topics/api-ref)) | Elastic Cloud Server — Elastic Cloud Server ([документация](https://cloud.ru/docs/en/usermanual/ecs/en-us_topic_0013771112), [API](https://cloud.ru/docs/advanced/overview/advanced-en-api)) | Compute Cloud — Virtual Machine ([документация](https://yandex.cloud/ru/docs/compute/concepts/vm), [API](https://yandex.cloud/ru/docs/compute/api-ref/)) |
| `vm_image` — Образ виртуальной машины | Образы — Образ ([документация](https://cloud.ru/docs/images/ug/index), [API](https://cloud.ru/docs/virtual-machines/ug/topics/api-ref)) | Image Management Service — Image ([документация](https://cloud.ru/docs/en/usermanual/ims/en-us_topic_0013901609), [API](https://cloud.ru/docs/advanced/overview/advanced-en-api)) | Compute Cloud — Image ([документация](https://yandex.cloud/ru/docs/compute/concepts/image), [API](https://yandex.cloud/ru/docs/compute/api-ref/)) |
| `vm_snapshot` — Снимок виртуальной машины | — | — | — |
| `public_ip` — Публичный IP-адрес | Публичные IP — Публичный IP ([документация](https://cloud.ru/docs/public-ip/ug/index), [API](https://cloud.ru/docs/evolution-vpc/ug/topics/api-ref)) | Elastic IP — EIP ([документация](https://cloud.ru/docs/en/usermanual/eip/overview_0001), [API](https://cloud.ru/docs/advanced/overview/advanced-en-api)) | Virtual Private Cloud — Address ([документация](https://yandex.cloud/ru/docs/vpc/concepts/address), [API](https://yandex.cloud/ru/docs/vpc/api-ref/)) |
| `security_group` — Группа безопасности | Группы безопасности — Группа безопасности ([документация](https://cloud.ru/docs/security-groups/ug/index), [API](https://cloud.ru/docs/evolution-vpc/ug/topics/api-ref)) | Virtual Private Cloud — Security Group ([документация](https://cloud.ru/docs/en/usermanual/vpc/en-us_topic_0013748729), [API](https://cloud.ru/docs/advanced/overview/advanced-en-api)) | Virtual Private Cloud — Security Group ([документация](https://yandex.cloud/ru/docs/vpc/concepts/security-groups), [API](https://yandex.cloud/ru/docs/vpc/api-ref/)) |
| `subnet` — Подсеть | Подсети — Подсеть ([документация](https://cloud.ru/docs/subnets/ug/index), [API](https://cloud.ru/docs/evolution-vpc/ug/topics/api-ref)) | Virtual Private Cloud — Subnet ([документация](https://cloud.ru/docs/en/usermanual/vpc/en-us_topic_0013748729), [API](https://cloud.ru/docs/advanced/overview/advanced-en-api)) | Virtual Private Cloud — Subnet ([документация](https://yandex.cloud/ru/docs/vpc/concepts/network), [API](https://yandex.cloud/ru/docs/vpc/api-ref/)) |
| `vpc` — Виртуальная частная сеть | Evolution VPC — VPC ([документация](https://cloud.ru/docs/evolution-vpc/ug/index), [API](https://cloud.ru/docs/evolution-vpc/ug/topics/api-ref)) | Virtual Private Cloud — VPC ([документация](https://cloud.ru/docs/en/usermanual/vpc/en-us_topic_0013748729), [API](https://cloud.ru/docs/advanced/overview/advanced-en-api)) | Virtual Private Cloud — Network ([документация](https://yandex.cloud/ru/docs/vpc/concepts/network), [API](https://yandex.cloud/ru/docs/vpc/api-ref/)) |
| `block_storage_volume` — Том блочного хранилища | Диски — Диск ([документация](https://cloud.ru/docs/disks/ug/index), [API](https://cloud.ru/docs/virtual-machines/ug/topics/api-ref)) | Elastic Volume Service — Disk ([документация](https://cloud.ru/docs/en/usermanual/evs/en-us_topic_0014580741), [API](https://cloud.ru/docs/advanced/overview/advanced-en-api)) | Compute Cloud — Disk ([документация](https://yandex.cloud/ru/docs/compute/concepts/disk), [API](https://yandex.cloud/ru/docs/compute/api-ref/)) |
| `disk_snapshot` — Снимок диска | — | Elastic Volume Service — Snapshot ([документация](https://cloud.ru/docs/en/usermanual/evs/evs_01_0098), [API](https://cloud.ru/docs/advanced/overview/advanced-en-api)) | Compute Cloud — Snapshot ([документация](https://yandex.cloud/ru/docs/compute/concepts/snapshot), [API](https://yandex.cloud/ru/docs/compute/api-ref/)) |
