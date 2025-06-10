from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from ads.models import Ad, City
from django.utils.timezone import now
from datetime import timedelta
from users.models import ModeratorActivityStat
from django.utils import timezone


User = get_user_model()


class CreateModeratorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Доступ запрещён"}, status=403)

        phone = request.data.get("phone")
        password = request.data.get("password")
        full_name = request.data.get("full_name")
        print(phone, full_name, password)
        if not all([phone, password, full_name]):
            return Response({"error": "Все поля обязательны"}, status=400)

        if User.objects.filter(phone=phone).exists():
            return Response({"error": "Пользователь с таким номером уже существует"}, status=400)

        user = User.objects.create(
            phone=phone,
            name=full_name,
            is_staff=True,
            raw_password=password  # 👈 сохраняем в открытом виде
        )
        user.set_password(password)  # 👈 безопасная установка
        user.save()

        return Response({
            "message": "Модератор создан",
            "id": user.id,
            "phone": user.phone,
            "full_name": user.name,
            "raw_password": user.raw_password  # 👈 возвращаем сырой пароль
        }, status=201)


class ListModeratorsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Доступ запрещён"}, status=403)

        moderators = User.objects.filter(is_staff=True, is_superuser=False)

        data = []
        for mod in moderators:
            data.append({
                "id": mod.id,
                "phone": mod.phone,
                "full_name": mod.name,
                "is_active": mod.is_active,
                "raw_password": mod.raw_password  # 👈 показываем сырой пароль
            })

        return Response(data)
    

class RegisterView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        password = request.data.get("password")

        if not phone or not password:
            return Response({"error": "Phone and password required"}, status=400)

        if User.objects.filter(phone=phone).exists():
            return Response({"error": "User already exists"}, status=400)

        user = User.objects.create_user(phone=phone, password=password)
        token, _ = Token.objects.get_or_create(user=user)

        return Response({"token": token.key}, status=201)


class LoginView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        password = request.data.get("password")
        print(phone, password)

        user = authenticate(request, phone=phone, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=401)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "name": user.name,
            "phone": user.phone,
            "role": user.role,
        })
    

class DeleteModeratorView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, moderator_id):
        if not request.user.is_superuser:
            return Response({"error": "Доступ запрещён"}, status=403)

        try:
            user = User.objects.get(id=moderator_id, is_staff=True, is_superuser=False)
        except User.DoesNotExist:
            return Response({"error": "Модератор не найден"}, status=404)

        user.delete()
        return Response({"message": "Модератор удалён"}, status=200)
    

class UpdateModeratorView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, moderator_id):
        if not request.user.is_superuser:
            return Response({"error": "Доступ запрещён"}, status=403)

        try:
            moderator = User.objects.get(id=moderator_id, is_staff=True, is_superuser=False)
        except User.DoesNotExist:
            return Response({"error": "Модератор не найден"}, status=404)

        phone = request.data.get("phone")
        full_name = request.data.get("full_name")

        if phone:
            moderator.phone = phone
        if full_name:
            moderator.name = full_name

        moderator.save()

        return Response({
            "message": "Модератор обновлён",
            "id": moderator.id,
            "phone": moderator.phone,
            "full_name": moderator.name
        }, status=200)






def get_stats_since(start_date):
    moderators = User.objects.filter(is_staff=True)
    all_cities = City.objects.all()

    stats = []
    city_totals = {city.id: {"city_name": city.name, "ads_count": 0} for city in all_cities}
    total_ads_count = 0

    for moderator in moderators:
        ads = Ad.objects.filter(
            author=moderator,
            created_at__gte=start_date
        ).prefetch_related('cities')

        city_counter = {city.id: {"city_name": city.name, "ads_count": 0} for city in all_cities}

        for ad in ads:
            for city in ad.cities.all():
                city_counter[city.id]["ads_count"] += 1
                city_totals[city.id]["ads_count"] += 1
                total_ads_count += 1

        city_stats = [
            {"city_id": city_id, **data}
            for city_id, data in city_counter.items()
        ]

        city_stats.insert(0, {
            "city_id": 0,
            "city_name": "В общем",
            "ads_count": sum(item["ads_count"] for item in city_stats)
        })

        stats.append({
            "moderator_id": moderator.id,
            "moderator_name": moderator.name or moderator.phone,
            "city_stats": city_stats
        })

    # Общие суммы по городам
    total_city_stats = [
        {"city_id": city_id, **data}
        for city_id, data in city_totals.items()
    ]
    total_city_stats.insert(0, {
        "city_id": 0,
        "city_name": "В общем",
        "ads_count": total_ads_count
    })

    stats.append({
        "moderator_id": 0,
        "moderator_name": f"Всего по всем модераторам ({total_ads_count})",
        "city_stats": total_city_stats
    })

    return stats







class StatsTodayView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Доступ запрещён"}, status=403)

        today = now().date()
        data = get_stats_since(today)
        return Response(data)
    
class StatsWeekView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Доступ запрещён"}, status=403)

        today = now().date()
        monday = today - timedelta(days=today.weekday())  # Понедельник этой недели
        data = get_stats_since(monday)
        return Response(data)


class StatsMonthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Доступ запрещён"}, status=403)

        today = now().date()
        month_start = today.replace(day=1)
        data = get_stats_since(month_start)
        return Response(data)










class ModeratorActivityStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        three_days_ago = today - timedelta(days=2)  # включительно 3 дня: today, -1, -2

        stats = ModeratorActivityStat.objects.filter(date__gte=three_days_ago)
        users = User.objects.filter(id__in=stats.values_list("user_id", flat=True).distinct())

        response_data = {}

        for user in users:
            user_stats = stats.filter(user=user)
            user_data = {}

            for stat in user_stats:
                date_str = stat.date.isoformat()
                if date_str not in user_data:
                    user_data[date_str] = {}
                user_data[date_str][str(stat.hour)] = stat.ad_count

            response_data[user.name] = user_data

        return Response(response_data)
    

class SingleModeratorStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        today = timezone.now().date()
        three_days = [today - timedelta(days=i) for i in range(2, -1, -1)] 
        user = get_object_or_404(User, id=user_id)
        stats = ModeratorActivityStat.objects.filter(user=user, date__in=three_days)

        # Собираем в словарь: { (date, hour): count }
        stats_map = {(s.date, s.hour): s.ad_count for s in stats}

        user_data = {}

        for date in three_days:
            date_str = date.isoformat()
            user_data[date_str] = {}

            for hour in range(24):
                user_data[date_str][str(hour)] = stats_map.get((date, hour), 0)

        return Response({
            "user": user.name,
            "data": user_data
        })