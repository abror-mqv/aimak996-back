# Деталка для фронта админки (сchedules, photos, catalog)

Base: PROD http://176.126.164.86:8000
Auth: Authorization: Token <token>
Role: IsAdminOrModerator

Карточка бизнеса идентифицируется по строковому `pk` (6 цифр), например `"123456"`.

---

## 1) График работы бизнеса (Schedules)

Задача: полностью заменить (set) весь график карточки на присланный массив.

- Endpoint: POST /business/mod/cards/<pk>/schedules/set/
- Body param: `schedules` — JSON-массив или JSON-строка в form-data
- Элемент массива:
  ```json
  {
    "day_of_week": 0,         // 0=Mon ... 6=Sun
    "open_time": "09:00:00", // может быть null
    "close_time": "20:00:00",// может быть null
    "is_closed": false        // true => выходной
  }
  ```
- Поведение: старые записи удаляются, создаются новые (bulk_create)

Пример (curl):
```bash
curl -X POST \
  -H "Authorization: Token $TOKEN" \
  -F schedules='[
    {"day_of_week":0,"open_time":"09:00:00","close_time":"20:00:00","is_closed":false},
    {"day_of_week":6,"open_time":null,"close_time":null,"is_closed":true}
  ]' \
  http://176.126.164.86:8000/business/mod/cards/123456/schedules/set/
```

UI подсказки:
- Редактировать массивом за один сабмит.
- Валидировать диапазон day_of_week (0-6).
- Если `is_closed=true`, показывать `open_time/close_time` как disabled/null.

---

## 2) Карусель изображений (Carousel Photos)

Добавление фото в карусель карточки:
- Endpoint: POST /business/mod/cards/<pk>/photos/add/
- Files: `images[]=@1.jpg&images[]=@2.jpg` (или одиночное `image`)
- Response: `{ "created_ids": [3,4,5] }`

Удаление отдельного фото:
- Endpoint: DELETE /business/mod/photos/<photo_id>/delete/
- Response: `{ "message": "deleted" }`

Пример (curl):
```bash
curl -X POST \
  -H "Authorization: Token $TOKEN" \
  -F images[]=@1.jpg -F images[]=@2.jpg \
  http://176.126.164.86:8000/business/mod/cards/123456/photos/add/
```

UI подсказки:
- После загрузки перезапрашивать детальную карточку (`/business/pk/<pk>/`) — массив `photos` уже содержит абсолютные URL.
- Дать пользователю удаление по одной фотке, подтверждение перед DELETE.

---

## 3) Бизнес-каталог (Catalog Items)

Создать пункт каталога:
- Endpoint: POST /business/mod/cards/<pk>/catalog/add/
- Form data:
  - name (required)
  - description (optional)
  - price (optional)
  - photo (file, optional)
- Response: `{ "id": 42 }`

Обновить пункт каталога:
- Endpoint: PUT/PATCH /business/mod/catalog/<item_id>/edit/
- Form data: любой из `name`, `description`, `price`; `photo` (file) — перезапишет
- Response: `{ "message": "updated" }`

Удалить пункт каталога:
- Endpoint: DELETE /business/mod/catalog/<item_id>/delete/
- Response: `{ "message": "deleted" }`

Пример (curl):
```bash
curl -X POST \
  -H "Authorization: Token $TOKEN" \
  -F name="Капучино" -F price=150 -F photo=@cappuccino.jpg \
  http://176.126.164.86:8000/business/mod/cards/123456/catalog/add/
```

UI подсказки:
- Для списка используйте данные из детальной карточки (`catalog_items`).
- При редактировании/удалении — обновляйте локальный стейт и/или рефетчите деталь.
- Загрузка фото — multipart/form-data; покажите предпросмотр.
