# Обновление карусели и порядка элементов

Prod host: http://176.126.164.86:8000
Auth: Authorization: Token <token>
Roles: IsAdminOrModerator

## Формат карусели фото (в детальной карточке и списке фото)
Теперь фото возвращаются как объекты:
```json
[
  { "url": "http://...", "pos_id": 1, "image_id": 3 },
  { "url": "http://...", "pos_id": 2, "image_id": 8 }
]
```
- url — абсолютная ссылка
- pos_id — позиция фото (целое число)
- image_id — pk фото (используется для удаления/замены)

## Эндпоинты фото
- Добавить фото (добавляет в конец):
  - POST /business/mod/cards/<pk>/photos/add/
  - files: images[]=@1.jpg (& images[]=@2.jpg ...)
  - Response: { "created_ids": [..] }

- Удалить фото:
  - DELETE /business/mod/photos/<photo_id>/delete/
  - Response: { "message": "deleted" }

- Заменить фото:
  - PUT /business/mod/photos/<photo_id>/replace/
  - files: image=@new.jpg
  - Response: { "message": "replaced" }

- Изменить порядок фото:
  - POST /business/mod/cards/<pk>/photos/reorder/
  - Body: order — JSON-массив id фото, в нужном порядке (можно строкой в form-data)
    - Пример: [10,7,15]
  - Response: { "message": "reordered", "count": N }

## Формат каталога (порядок)
- Пункты каталога имеют поле position, сортировка по position, затем id.
- В детальных ответах порядок уже учитывается.

## Эндпоинты каталога
- Добавить пункт (добавляет в конец):
  - POST /business/mod/cards/<pk>/catalog/add/
  - form: name (required), description?, price?, photo?

- Обновить пункт:
  - PUT/PATCH /business/mod/catalog/<item_id>/edit/
  - form: name?, description?, price?, photo?, position?

- Удалить пункт:
  - DELETE /business/mod/catalog/<item_id>/delete/

- Изменить порядок пунктов:
  - POST /business/mod/cards/<pk>/catalog/reorder/
  - Body: order — JSON-массив id в целевом порядке, напр. [5,2,9]

## Миграции
Добавлены поля для упорядочивания:
- BusinessPhoto.position (default=0, ordering=[position, id])
- BusinessCatalogItem.position (default=0, ordering=[position, id])

Действия (выполнить на сервере):
```bash
python manage.py makemigrations business
python manage.py migrate
```

Изменения совместимы: поля добавляются с дефолтом и не ломают существующие записи. Сортировка по умолчанию теперь учитывает position.
