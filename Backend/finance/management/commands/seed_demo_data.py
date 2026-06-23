import base64
import json
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

from expenses.models import Category, Comment, ExpenseLog, Like
from finance.models import FinancialProduct, FinancialProductOption, StockHolding, UserFinancialProduct
from friends.models import Friend
from profiles.models import Profile


PASSWORD = "rkskekfk"
JSON_DEFAULT_PATH = "finance/fixtures/demo_data.json"
MP4_TEMPLATE_B64 = """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"""

DEMO_USERS = [
    {"name": "\uae40\uc885\ubb34", "username": "kjm", "email": "kjm@example.com", "color": (55, 105, 95)},
    {"name": "\ubc15\uc900\ud615", "username": "pjh", "email": "pjh@example.com", "color": (190, 78, 62)},
    {"name": "\uae40\uc601\ube48", "username": "kyb", "email": "kyb@example.com", "color": (210, 154, 50)},
    {"name": "\ubc15\uc9c4\ud601", "username": "pjh2", "email": "pjh2@example.com", "color": (73, 94, 150)},
    {"name": "\uc774\ubd09\ubbfc", "username": "lbm", "email": "lbm@example.com", "color": (105, 132, 75)},
    {"name": "\uae40\uc218\uc6d0", "username": "ksw", "email": "ksw@example.com", "color": (145, 78, 132)},
    {"name": "\uad6c\uc724\uc9c0", "username": "kyj", "email": "kyj@example.com", "color": (54, 132, 154)},
    {"name": "\uc774\uc7ac\uc900", "username": "ljj", "email": "ljj@example.com", "color": (176, 104, 52)},
    {"name": "\uacfd\uc6b0\ube48", "username": "kwb", "email": "kwb@example.com", "color": (84, 86, 92)},
    {"name": "\uc11c\uc720\uc815", "username": "syj", "email": "syj@example.com", "color": (196, 94, 112)},
]

FRIEND_PAIRS = [
    ("kjm", "pjh"), ("kjm", "kyb"), ("kjm", "ksw"),
    ("pjh", "pjh2"), ("pjh", "kyj"),
    ("kyb", "lbm"), ("kyb", "ljj"),
    ("pjh2", "ksw"),
    ("lbm", "kyj"),
    ("ksw", "ljj"),
    ("kyj", "kwb"),
    ("ljj", "syj"),
    ("kwb", "syj"),
]

CATEGORIES = ["\uc2dd\ube44", "\uad50\ud1b5\ube44", "\uc1fc\ud551", "\ubb38\ud654\uc0dd\ud65c", "\uad6c\ub3c5", "\uae30\ud0c0"]
MERCHANTS = ["Flex Diner", "Bean Studio", "Metro Pass", "Market Hall", "Cinema Club", "Cloud Pay", "Daily Store"]
PRODUCT_NAMES = ["Lunch", "Coffee", "Transit", "Sneakers", "Movie", "Subscription", "Notebook"]
COMMENTS = [
    "Nice record!",
    "Great flex log.",
    "This looks useful.",
    "Good spending note.",
    "Saved for later.",
]
STOCKS = [
    ("AAPL", "Apple", "4.0000", "182.30", "196.50"),
    ("NVDA", "NVIDIA", "2.0000", "118.40", "142.10"),
    ("MSFT", "Microsoft", "3.0000", "408.25", "451.70"),
    ("TSLA", "Tesla", "5.0000", "178.60", "205.15"),
    ("GOOGL", "Alphabet", "2.0000", "162.20", "181.35"),
    ("AMZN", "Amazon", "3.0000", "183.10", "201.45"),
    ("005930", "Samsung Electronics", "12.0000", "73400.00", "81200.00"),
    ("000660", "SK hynix", "5.0000", "182000.00", "221500.00"),
    ("035420", "NAVER", "6.0000", "189000.00", "206000.00"),
    ("051910", "LG Chem", "2.0000", "342000.00", "371500.00"),
]


class Command(BaseCommand):
    help = "Seed Flex-Log demo users, feeds, friends, products, stocks, media, and JSON."

    def add_arguments(self, parser):
        parser.add_argument("--json-path", default=JSON_DEFAULT_PATH)

    @transaction.atomic
    def handle(self, *args, **options):
        self.media_root = Path(settings.MEDIA_ROOT)
        self.media_root.mkdir(parents=True, exist_ok=True)
        User = get_user_model()
        usernames = [item["username"] for item in DEMO_USERS]
        existing_users = list(User.objects.filter(username__in=usernames))

        self._clear_demo_data(existing_users)
        users = self._upsert_users(User)
        categories = self._ensure_categories()
        product_options = self._ensure_product_options()

        friendships = self._create_friendships(users)
        subscriptions = self._create_subscriptions(users, product_options)
        holdings = self._create_stock_holdings(users)
        logs_payload = self._create_feeds(users, categories)

        json_path = Path(options["json_path"])
        if not json_path.is_absolute():
            json_path = Path(settings.BASE_DIR) / json_path
        json_path.parent.mkdir(parents=True, exist_ok=True)
        payload = self._build_payload(users, friendships, subscriptions, holdings, logs_payload)
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(users)} users, {len(logs_payload)} feeds, "
            f"{len(friendships)} friendships, {len(subscriptions)} subscriptions, "
            f"{len(holdings)} stock holdings. JSON: {json_path}"
        ))

    def _clear_demo_data(self, users):
        if not users:
            return
        demo_logs = ExpenseLog.objects.filter(user__in=users)
        Comment.objects.filter(log__in=demo_logs).delete()
        Like.objects.filter(log__in=demo_logs).delete()
        demo_logs.delete()
        UserFinancialProduct.objects.filter(user__in=users).delete()
        StockHolding.objects.filter(user__in=users).delete()
        Friend.objects.filter(Q(user__in=users) | Q(friend__in=users)).delete()

    def _upsert_users(self, User):
        users = {}
        for index, item in enumerate(DEMO_USERS):
            user, _ = User.objects.update_or_create(
                username=item["username"],
                defaults={"email": item["email"], "name": item["name"]},
            )
            user.set_password(PASSWORD)
            user.save(update_fields=("password", "email", "name", "updated_at"))

            avatar_path = self.media_root / "profiles" / "demo" / f"{item['username']}.png"
            avatar_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_avatar(avatar_path, item, index)
            profile, _ = Profile.objects.update_or_create(
                user=user,
                defaults={
                    "nickname": item["name"],
                    "bio": "\ub7ec\ubc84\ud638\uc2a4 \uc2a4\ud0c0\uc77c\uc758 Flex-Log \ub370\ubaa8 \ud504\ub85c\ud544\uc785\ub2c8\ub2e4.",
                },
            )
            profile.image.name = self._media_name(avatar_path)
            profile.save(update_fields=("image", "nickname", "bio", "updated_at"))
            users[item["username"]] = user
        return users

    def _ensure_categories(self):
        return {name: Category.objects.get_or_create(name=name)[0] for name in CATEGORIES}

    def _ensure_product_options(self):
        options = list(
            FinancialProductOption.objects.select_related("product")
            .filter(product__is_active=True)
            .order_by("id")[:40]
        )
        if options:
            return options

        specs = [
            ("deposit", "DEMO_DEP_01", "Demo Bank", "Flex Demo Deposit", 12, "3.1000", "3.4500"),
            ("saving", "DEMO_SAV_01", "Flex Bank", "Flex Demo Saving", 24, "3.4000", "3.9000"),
            ("deposit", "DEMO_DEP_02", "Pocket Bank", "Pocket Plus Deposit", 6, "2.8000", "3.2000"),
            ("saving", "DEMO_SAV_02", "Daily Bank", "Daily Round Saving", 36, "3.6000", "4.1000"),
        ]
        for product_type, code, bank, name, term, rate, max_rate in specs:
            product, _ = FinancialProduct.objects.get_or_create(
                product_type=product_type,
                fin_prdt_cd=code,
                defaults={
                    "dcls_month": "202606",
                    "kor_co_nm": bank,
                    "fin_prdt_nm": name,
                    "join_way": "online",
                    "join_member": "individual",
                    "is_active": True,
                },
            )
            option, _ = FinancialProductOption.objects.get_or_create(
                product=product,
                save_trm=term,
                intr_rate_type="S",
                rsrv_type="",
                defaults={
                    "intr_rate_type_nm": "simple",
                    "intr_rate": Decimal(rate),
                    "intr_rate2": Decimal(max_rate),
                },
            )
            options.append(option)
        return options

    def _create_friendships(self, users):
        created = []
        for username, friend_username in FRIEND_PAIRS:
            friendship = Friend.objects.create(
                user=users[username],
                friend=users[friend_username],
                status=Friend.Status.ACCEPTED,
            )
            created.append(friendship)
        return created

    def _create_subscriptions(self, users, product_options):
        created = []
        ordered_users = [users[item["username"]] for item in DEMO_USERS]
        for user_index, user in enumerate(ordered_users):
            count = 1 + (user_index % 2)
            for offset in range(count):
                option = product_options[(user_index * 2 + offset) % len(product_options)]
                created.append(UserFinancialProduct.objects.create(user=user, option=option))
        return created

    def _create_stock_holdings(self, users):
        created = []
        ordered_users = [users[item["username"]] for item in DEMO_USERS]
        for user_index, user in enumerate(ordered_users):
            count = 2 + (user_index % 2)
            for offset in range(count):
                symbol, name, quantity, average_price, current_price = STOCKS[(user_index + offset * 3) % len(STOCKS)]
                created.append(StockHolding.objects.create(
                    user=user,
                    symbol=symbol,
                    name=name,
                    quantity=Decimal(quantity),
                    average_price=Decimal(average_price),
                    current_price=Decimal(current_price),
                    memo="demo holding",
                ))
        return created

    def _create_feeds(self, users, categories):
        now = timezone.now()
        ordered_users = [users[item["username"]] for item in DEMO_USERS]
        logs_payload = []
        for user_index, item in enumerate(DEMO_USERS):
            user = users[item["username"]]
            feed_count = 30 if item["username"] == "ksw" else 2 + (user_index % 2)
            for feed_index in range(feed_count):
                category_name = CATEGORIES[(user_index + feed_index) % len(CATEGORIES)]
                category = categories[category_name]
                is_video = feed_index == 0 or (item["username"] == "ksw" and feed_index % 7 == 0)
                suffix = "mp4" if is_video else "png"
                media_path = self.media_root / "expenses" / "demo" / f"{item['username']}-{feed_index + 1:02d}.{suffix}"
                media_path.parent.mkdir(parents=True, exist_ok=True)
                if is_video:
                    media_path.write_bytes(base64.b64decode(MP4_TEMPLATE_B64))
                else:
                    self._write_feed_image(media_path, item, feed_index, category_name)

                created_at = now - timedelta(days=(feed_count - feed_index), hours=user_index)
                log = ExpenseLog.objects.create(
                    user=user,
                    category=category,
                    title=f"{item['username'].upper()} flex #{feed_index + 1}",
                    media=self._media_name(media_path),
                    amount=9000 + (user_index * 2300) + (feed_index * 1700),
                    product_name=PRODUCT_NAMES[(user_index + feed_index) % len(PRODUCT_NAMES)],
                    merchant=MERCHANTS[(user_index + feed_index) % len(MERCHANTS)],
                    content=f"Demo feed by {item['username']} #{feed_index + 1}",
                    overlay_text=f"{item['username'].upper()} #{feed_index + 1}",
                    overlay_style={
                        "boxes": [
                            {
                                "id": "demo-title",
                                "text": f"{item['username'].upper()} #{feed_index + 1}",
                                "x": 50,
                                "y": 44,
                                "fontSize": 30,
                                "color": "#fff8e7",
                                "rotate": -2 + (feed_index % 5),
                            }
                        ]
                    },
                    visibility=ExpenseLog.Visibility.PUBLIC if feed_index % 3 else ExpenseLog.Visibility.FRIENDS,
                    expires_at=now + timedelta(days=365),
                    is_visible=True,
                )
                ExpenseLog.objects.filter(pk=log.pk).update(created_at=created_at, updated_at=created_at)
                log.created_at = created_at
                log.updated_at = created_at
                interactions = self._create_interactions(log, ordered_users, user_index, feed_index)
                logs_payload.append({
                    "log": log,
                    "media_type": "video" if is_video else "image",
                    "likes": interactions["likes"],
                    "comments": interactions["comments"],
                })
        return logs_payload

    def _create_interactions(self, log, ordered_users, user_index, feed_index):
        other_users = [user for user in ordered_users if user.id != log.user_id]
        like_count = 2 + (feed_index % 3)
        comment_count = 1 + (feed_index % 2)
        likes = []
        comments = []
        for offset in range(like_count):
            liker = other_users[(user_index + feed_index + offset) % len(other_users)]
            Like.objects.create(user=liker, log=log)
            likes.append(liker.username)
        for offset in range(comment_count):
            commenter = other_users[(user_index + feed_index + offset + 2) % len(other_users)]
            comment = Comment.objects.create(
                user=commenter,
                log=log,
                content=COMMENTS[(feed_index + offset) % len(COMMENTS)],
            )
            comments.append({"username": commenter.username, "content": comment.content})
        return {"likes": likes, "comments": comments}

    def _write_avatar(self, path, item, index):
        ink = (24, 20, 14)
        paper = (255, 248, 231)
        accent = item["color"]
        image = Image.new("RGB", (320, 320), paper)
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((18, 18, 302, 302), radius=38, fill=(248, 239, 216), outline=ink, width=6)
        draw.ellipse((78, 50, 242, 214), fill=(255, 218, 166), outline=ink, width=6)
        draw.pieslice((108, 88, 148, 128), 20, 330, fill=ink)
        draw.pieslice((174, 88, 214, 128), 210, 160, fill=ink)
        draw.arc((116, 120, 204, 178), start=15, end=165, fill=ink, width=5)
        draw.ellipse((92, 188, 228, 282), fill=accent, outline=ink, width=6)
        draw.line((92, 222, 54, 250, 35, 232), fill=ink, width=10, joint="curve")
        draw.line((228, 222, 266, 250, 285, 232), fill=ink, width=10, joint="curve")
        draw.ellipse((20, 210, 68, 252), fill=paper, outline=ink, width=5)
        draw.ellipse((252, 210, 300, 252), fill=paper, outline=ink, width=5)
        draw.line((124, 282, 110, 304), fill=ink, width=8)
        draw.line((196, 282, 210, 304), fill=ink, width=8)
        font = self._font(40)
        initials = item["username"].upper()
        bbox = draw.textbbox((0, 0), initials, font=font)
        draw.text(((320 - (bbox[2] - bbox[0])) / 2, 232), initials, fill=paper, font=font)
        image.save(path, "PNG")

    def _write_feed_image(self, path, item, feed_index, category_name):
        ink = (24, 20, 14)
        paper = (255, 248, 231)
        accent = item["color"]
        image = Image.new("RGB", (720, 540), paper)
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 720, 540), fill=(248, 239, 216))
        draw.rounded_rectangle((38, 36, 682, 504), radius=34, fill=accent, outline=ink, width=7)
        draw.ellipse((92, 88, 280, 276), fill=(255, 218, 166), outline=ink, width=6)
        draw.rectangle((310, 116, 626, 176), fill=paper, outline=ink, width=5)
        draw.rectangle((310, 214, 626, 274), fill=paper, outline=ink, width=5)
        draw.line((126, 300, 84, 384, 128, 430), fill=ink, width=13, joint="curve")
        draw.line((244, 300, 286, 384, 242, 430), fill=ink, width=13, joint="curve")
        draw.ellipse((68, 390, 148, 462), fill=paper, outline=ink, width=5)
        draw.ellipse((222, 390, 302, 462), fill=paper, outline=ink, width=5)
        title_font = self._font(54)
        small_font = self._font(34)
        draw.text((330, 108), f"{item['username'].upper()} #{feed_index + 1}", fill=ink, font=title_font)
        draw.text((330, 214), category_name, fill=ink, font=small_font)
        image.save(path, "PNG")

    def _font(self, size):
        candidates = [
            "C:/Windows/Fonts/malgun.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "arial.ttf",
        ]
        for candidate in candidates:
            try:
                return ImageFont.truetype(candidate, size=size)
            except OSError:
                continue
        return ImageFont.load_default()

    def _media_name(self, path):
        return path.relative_to(self.media_root).as_posix()

    def _build_payload(self, users, friendships, subscriptions, holdings, logs_payload):
        return {
            "generated_at": timezone.now().isoformat(),
            "password": PASSWORD,
            "username_note": "pjh2 is used for Park Jinhyeok because pjh is already used by Park Junhyeong.",
            "users": [
                {
                    "id": users[item["username"]].id,
                    "username": item["username"],
                    "password": PASSWORD,
                    "name": item["name"],
                    "email": item["email"],
                    "profile_image": f"{settings.MEDIA_URL}{users[item['username']].profile.image.name}",
                }
                for item in DEMO_USERS
            ],
            "friendships": [
                {"id": item.id, "user": item.user.username, "friend": item.friend.username, "status": item.status}
                for item in friendships
            ],
            "feeds": [
                {
                    "id": item["log"].id,
                    "username": item["log"].user.username,
                    "title": item["log"].title,
                    "media": f"{settings.MEDIA_URL}{item['log'].media.name}",
                    "media_type": item["media_type"],
                    "amount": item["log"].amount,
                    "category": item["log"].category.name,
                    "likes": item["likes"],
                    "comments": item["comments"],
                }
                for item in logs_payload
            ],
            "joined_products": [
                {
                    "id": item.id,
                    "username": item.user.username,
                    "bank": item.option.product.kor_co_nm,
                    "product": item.option.product.fin_prdt_nm,
                    "term_months": item.option.save_trm,
                    "rate": str(item.option.intr_rate),
                    "max_rate": str(item.option.intr_rate2),
                    "status": item.status,
                }
                for item in subscriptions
            ],
            "stock_holdings": [
                {
                    "id": item.id,
                    "username": item.user.username,
                    "symbol": item.symbol,
                    "name": item.name,
                    "quantity": str(item.quantity),
                    "average_price": str(item.average_price),
                    "current_price": str(item.current_price),
                }
                for item in holdings
            ],
        }
