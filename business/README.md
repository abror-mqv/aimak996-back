# Бизнес API для Бексултана: гоп-мануал (KY-RU)

Ассалому алейкум, Бексултан! Смотри сюда, братишка. Это дока по нашему бизнес-API, чтобы ты быстренько наклепал 3 экрана во Flutter и не парился. Можно насиком закинуться — но аккуратно, чтоб код не обиделся.

- Сервер в бою: http://176.126.164.86:8000
- Базовый префикс для этого приложения: `/business/`
- Авторизация не нужна. Вообще. Жми GET и кайфуй.
- Картинки приходят как абсолютные URL — кидай в `Image.network` и не мучайся.
- `pk` у карточки бизнеса — строка из 6 цифр, типа "123456". Это твой ключ к деталям. Как боксы в оптале

---

## Серверы и URL — чё к чему

- Сервер — это тачка, где крутится наш Django. У нас есть разные окружения, но тебе сейчас важно ПРОД:
  - Прод: `http://176.126.164.86:8000`
- Базовый путь приложения — `/business/`. Значит:
  - Список категорий: `http://176.126.164.86:8000/business/categories/`
  - Список карточек: `http://176.126.164.86:8000/business/cards/`
  - Детально по pk: `http://176.126.164.86:8000/business/pk/<pk>/`

---

## Немного про REST (на пальцах)

- Методы:
  - GET — забрать данные (мы пока только его юзаем). Не мутирующий, безопасный.
- Ресурсы:
  - categories — коллекция категорий
  - cards — коллекция карточек бизнеса
  - cards/<pk>/ — конкретная карточка
- Фильтры — это query-параметры, типа `?category_id=3&city_id=1`.
- Ответы — JSON. Если ок — 200. Если нет такого pk — 404. Всё честно, как на базаре.

---

## Экран 1: Все категории

GET `http://176.126.164.86:8000/business/categories/`

Ответ 200 OK (массив):
```json
[
  {
    "id": 1,
    "name_kg": "Тамак",
    "name_ru": "Еда",
    "created_at": "2025-11-19T06:40:10.123456",
    "icon_url": "http://176.126.164.86:8000/media/business/category_icons/food.png",
    "gradient_start": "#000000",
    "gradient_end": "#FFFFFF"
  }
]
```

Поля:
- id — числовой ID категории (для админки пригодится)
- name_kg, name_ru — названия
- icon_url — PNG-иконка (может быть null)
- gradient_start, gradient_end — два HEX-цвета для твоего красивого градиента

Подсказка для Flutter:
- Градиент делай так: `LinearGradient(colors: [Color(0xFF000000), Color(0xFFFFFFFF)])` — переведи HEX в Color
- Кешани список, он не часто меняется

---

## Экран 2: Все карточки одной категории

GET `http://176.126.164.86:8000/business/cards/?category_id=<ID>&city_id=<ID>`

Оба параметра опциональны, но для экрана по категории ставь `category_id` обязательно. Можно ещё сузить по городу: `city_id`.

Примеры:
- `/business/cards/?category_id=3`
- `/business/cards/?category_id=3&city_id=1`

Ответ 200 OK (массив):
```json
[
  {
    "pk": "123456",
    "name": "Coffee House",
    "short_description": "Лучший кофе",
    "profile_photo": "http://176.126.164.86:8000/media/business/profile_photos/coffee.jpg"
  }
]
```

Поля элемента:
- pk — шестизначный ключ (строка) для навигации на детальный экран
- name — имя бизнеса
- short_description — короткое описание (может быть null)
- profile_photo — аватар (может быть null)

Пока пагинации нет — грузим всё разом, не выпендриваемся. Если тормозит — потом придумаем lazy-loading.

---

## Экран 3: Детали карточки

Доступны два URL (оба валят полный объект):
- GET `http://176.126.164.86:8000/business/cards/<pk>/`
- GET `http://176.126.164.86:8000/business/pk/<pk>/`

Пример:
- `/business/cards/123456/`
- `/business/pk/123456/`

Ответ 200 OK:
```json
{
  "pk": "123456",
  "id": "123456",
  "name": "Coffee House",
  "short_description": "Лучший кофе",
  "long_description": "Подробное описание...",
  "profile_photo": "http://176.126.164.86:8000/media/business/profile_photos/coffee.jpg",
  "header_photo": "http://176.126.164.86:8000/media/business/header_photos/header.jpg",
  "theme_color": "#000000",

  "cta_phone": "+996 555 123 456",
  "additional_phone": null,
  "management_phone": null,
  "price_info": "договорная",

  "address_text": "ул. Пушкина, д. 10",
  "latitude": 42.8746,
  "longitude": 74.5698,
  "tags": ["кофе", "завтрак"],

  "city": "Бишкек",
  "city_id": 1,
  "category": "Еда",
  "category_id": 3,

  "created_at": "2025-11-19T06:40:10.123456",
  "updated_at": "2025-11-19T06:55:01.987654",

  "photos": [
    "http://176.126.164.86:8000/media/business/carousel_photos/1.jpg",
    "http://176.126.164.86:8000/media/business/carousel_photos/2.jpg"
  ],

  "catalog_items": [
    {
      "id": 17,
      "name": "Капучино",
      "description": "250 мл",
      "photo": "http://176.126.164.86:8000/media/business/catalog_photos/cappuccino.jpg",
      "price": "150",
      "created_at": "2025-11-19T06:41:22.000000"
    }
  ],

  "schedules": [
    { "day_of_week": 0, "open_time": "09:00:00", "close_time": "20:00:00", "is_closed": false },
    { "day_of_week": 6, "open_time": null,       "close_time": null,       "is_closed": true }
  ]
}
```

Подсказки для UI:
- `theme_color` — покрась заголовок/кнопки, чтобы сочненько было
- `photos` — крути в карусель
- `catalog_items` — просто список, MVP же
- `schedules` — 0=Mon ... 6=Sun; если `is_closed=true`, время может быть `null`

---

## Доп. маршруты (по желанию, для ленивой подгрузки)

- GET `/business/cards/<pk>/photos/` — массив URL картинок
- GET `/business/cards/<pk>/catalog/` — массив позиций каталога

---

## Ошибки (без драмы)

- 404 — не нашли карточку (не тот pk ввёл, братишка)
- 200 — всё чётко

---

## Быстрые примеры (curl), именно ПРОД

Категории:
```bash
curl -X GET "http://176.126.164.86:8000/business/categories/"
```

Карточки по категории 3:
```bash
curl -X GET "http://176.126.164.86:8000/business/cards/?category_id=3"
```

Детали по pk=123456:
```bash
curl -X GET "http://176.126.164.86:8000/business/pk/123456/"
```

---

## Финалочка

- Авторизация не нужна — никаких токенов, никаких секретов. FREE.
- Все даты — ISO 8601 строки, просто показывай.
- Если что-то тупит — пиши, починим. Если скучно — добавим ещё чьих то матерей (шутка, не надо).
- Главное — не забывай подставлять правильный хост `176.126.164.86:8000` и `pk` как 6-значную строку.

Удачи, Бекс! Жду три экрана как девственницы ждут меня
