import flet as ft
import time
import threading
import os

ONBOARDING_FLAG = os.path.join(os.path.expanduser("~"), ".soilco_onboarding_seen")

def onboarding_seen():
    return os.path.exists(ONBOARDING_FLAG)

def mark_onboarding_seen():
    open(ONBOARDING_FLAG, "w").close()


def main(page: ft.Page):
    page.title = "Soilco"
    page.window.width = 390
    page.window.height = 844
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = ft.Padding(top=0, left=0, right=0, bottom=0)
    page.bgcolor = "#f0f7f0"
    page.fonts = {
        "Inter": "https://fonts.gstatic.com/s/inter/v13/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfAZ9hiJ-Ek-_EeA.woff2"
    }
    page.theme = ft.Theme(font_family="Inter")

    def logo(size=50, light=False, show_text=True):
        controls = [ft.Icon(ft.Icons.GRASS_ROUNDED, color="white" if light else "green700", size=size)]
        if show_text:
            controls += [
                ft.Text("Soilco", size=28, weight="bold", color="white" if light else "green800"),
                ft.Text("Smart Soil Analysis", size=12, color="#c8e6c9" if light else "green600"),
            ]
        return ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6, controls=controls)

    def switch(controls):
        page.controls.clear()
        for c in controls:
            page.controls.append(c)
        page.update()

    def card(content, padding=20, margin=None, radius=20):
        return ft.Container(
            content=content,
            bgcolor="white",
            border_radius=radius,
            padding=padding,
            margin=margin,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.with_opacity(0.08, "green900")),
        )

    def green_btn(label, on_click, width=300, height=50):
        return ft.Button(
            label, on_click=on_click, width=width, height=height,
            style=ft.ButtonStyle(
                bgcolor="green700", color="white",
                shape=ft.RoundedRectangleBorder(radius=15),
                text_style=ft.TextStyle(size=16, weight="bold"),
            ),
        )

    def appbar(title, back_fn=None, actions=None):
        return ft.AppBar(
            title=ft.Text(title, color="white", weight="bold"),
            bgcolor="green700",
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color="white", on_click=back_fn) if back_fn else None,
            automatically_imply_leading=back_fn is not None,
            actions=actions or [],
        )

    def nav_bar(active, email):
        tabs = [
            {"label": "Home",    "icon": ft.Icons.HOME_OUTLINED,       "icon_active": ft.Icons.HOME,       "fn": lambda e: show_home(email)},
            {"label": "Forum",   "icon": ft.Icons.FORUM_OUTLINED,      "icon_active": ft.Icons.FORUM,      "fn": lambda e: show_forum(email)},
            {"label": "Market",  "icon": ft.Icons.STOREFRONT_OUTLINED, "icon_active": ft.Icons.STOREFRONT, "fn": lambda e: show_marketplace(email)},
            {"label": "Profile", "icon": ft.Icons.PERSON_OUTLINE,      "icon_active": ft.Icons.PERSON,     "fn": lambda e: show_profile(email)},
        ]

        def tab_btn(t):
            is_active = t["label"] == active
            return ft.Container(
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=3,
                    controls=[
                        ft.Icon(
                            t["icon_active"] if is_active else t["icon"],
                            color="green700" if is_active else "grey500",
                            size=24,
                        ),
                        ft.Text(
                            t["label"],
                            size=10,
                            color="green700" if is_active else "grey500",
                            weight="bold" if is_active else "normal",
                        ),
                    ],
                ),
                expand=True,
                on_click=t["fn"],
                ink=True,
                padding=ft.Padding(top=8, bottom=8, left=0, right=0),
            )

        return ft.Container(
            content=ft.Row(
                spacing=0,
                controls=[tab_btn(t) for t in tabs],
            ),
            bgcolor="white",
            border_radius=ft.BorderRadius(top_left=20, top_right=20, bottom_left=0, bottom_right=0),
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=16,
                color=ft.Colors.with_opacity(0.1, "green900"),
                offset=ft.Offset(0, -2),
            ),
            padding=ft.Padding(left=8, right=8, top=0, bottom=0),
        )

    # ──────────────────────────────────────────────────────
    # SPLASH SCREEN
    # ──────────────────────────────────────────────────────
    def show_splash():
        switch([
            ft.Container(
                expand=True, bgcolor="green700", alignment=ft.Alignment(0, 0),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=12, controls=[logo(80, light=True)],
                ),
            )
        ])
        def go():
            time.sleep(2)
            if onboarding_seen():
                show_login()
            else:
                show_onboarding()
        threading.Thread(target=go, daemon=True).start()

    # ──────────────────────────────────────────────────────
    # ONBOARDING SCREENS
    # ──────────────────────────────────────────────────────
    def show_onboarding(page_idx=0):
        slides = [
            {"icon": ft.Icons.GRASS_ROUNDED, "title": "Welcome to Soilco",
             "subtitle": "Your smart soil analysis companion for better farming decisions.", "color": "green700"},
            {"icon": ft.Icons.WATER_DROP, "title": "Smart Irrigation",
             "subtitle": "Get AI-powered daily irrigation recommendations based on your crop and local weather.", "color": "blue700"},
            {"icon": ft.Icons.AUTO_AWESOME, "title": "AI Crop Analysis",
             "subtitle": "Enter any crop and receive instant fertilizer, soil type, and growth time analysis.", "color": "orange700"},
        ]
        s = slides[page_idx]
        dots = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=8, controls=[
            ft.Container(width=10 if i==page_idx else 6, height=10 if i==page_idx else 6,
                border_radius=5, bgcolor="green700" if i==page_idx else "green200")
            for i in range(len(slides))
        ])
        is_last = page_idx == len(slides) - 1
        def on_next(e):
            if is_last: mark_onboarding_seen(); show_login()
            else: show_onboarding(page_idx + 1)
        switch([ft.Container(expand=True, bgcolor="#f0f7f0", content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, spacing=0,
            controls=[
                ft.Container(expand=True, alignment=ft.Alignment(0,0), content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, spacing=24,
                    controls=[
                        ft.Container(content=ft.Icon(s["icon"], color="white", size=72), bgcolor=s["color"], border_radius=40, padding=32),
                        ft.Text(s["title"], size=26, weight="bold", color="green900", text_align=ft.TextAlign.CENTER),
                        ft.Text(s["subtitle"], size=15, color="grey600", text_align=ft.TextAlign.CENTER),
                    ])),
                ft.Container(padding=ft.Padding(left=30, right=30, top=0, bottom=40), content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20,
                    controls=[
                        dots,
                        green_btn("Get Started" if is_last else "Next", on_next, height=50),
                        ft.TextButton("Skip", on_click=lambda e: (mark_onboarding_seen(), show_login()),
                            style=ft.ButtonStyle(color="grey500")) if not is_last else ft.Container(height=10),
                    ])),
            ])) ])

    # ──────────────────────────────────────────────────────
    # LOGIN SCREEN
    # ──────────────────────────────────────────────────────
    def show_login():
        email_field = ft.TextField(label="Email", prefix_icon=ft.Icons.EMAIL_OUTLINED, width=300,
            border_radius=15, border_color="green700", focused_border_color="green900",
            keyboard_type=ft.KeyboardType.EMAIL, bgcolor="white")
        password_field = ft.TextField(label="Password", prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True, can_reveal_password=True, width=300,
            border_radius=15, border_color="green700", focused_border_color="green900", bgcolor="white")
        status = ft.Text("", size=14)
        def on_login(e):
            if not email_field.value or not password_field.value:
                status.value = "Please fill in all fields"; status.color = "red"; page.update()
            else: show_home(email_field.value)
        switch([ft.Container(expand=True, bgcolor="#f0f7f0", content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO, spacing=0, controls=[
                ft.Container(content=logo(50), padding=ft.Padding(top=60, bottom=30, left=0, right=0)),
                card(ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16, controls=[
                    ft.Text("Welcome Back", size=22, weight="bold", color="green900"),
                    email_field, password_field,
                    ft.Container(content=ft.TextButton("Forgot Password?", on_click=lambda e: show_forgot(),
                        style=ft.ButtonStyle(color="green700")), alignment=ft.Alignment(1,0), width=300),
                    green_btn("Login", on_login), status, ft.Divider(color="green200"),
                    ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
                        ft.Text("Don't have an account?", color="grey700"),
                        ft.TextButton("Sign Up", on_click=lambda e: show_signup(), style=ft.ButtonStyle(color="green700")),
                    ]),
                ]), radius=25, margin=ft.Margin(left=20, right=20, top=0, bottom=40)),
            ]))])

    # ──────────────────────────────────────────────────────
    # SIGN UP SCREEN
    # ──────────────────────────────────────────────────────
    def show_signup():
        name_field = ft.TextField(label="Full Name", prefix_icon=ft.Icons.PERSON_OUTLINE, width=300,
            border_radius=15, border_color="green700", focused_border_color="green900", bgcolor="white")
        email_field = ft.TextField(label="Email", prefix_icon=ft.Icons.EMAIL_OUTLINED, width=300,
            border_radius=15, border_color="green700", focused_border_color="green900",
            keyboard_type=ft.KeyboardType.EMAIL, bgcolor="white")
        password_field = ft.TextField(label="Password", prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True, can_reveal_password=True, width=300,
            border_radius=15, border_color="green700", focused_border_color="green900", bgcolor="white")
        status = ft.Text("", size=14)
        def on_register(e):
            if not name_field.value or not email_field.value or not password_field.value:
                status.value = "Please fill in all fields"; status.color = "red"; page.update()
            else: show_home(email_field.value)
        switch([appbar("Sign Up", lambda e: show_login()),
            ft.Container(expand=True, bgcolor="#f0f7f0", content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO, spacing=16, controls=[
                    ft.Container(height=10), logo(40),
                    card(ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16, controls=[
                        ft.Text("Create Account", size=20, weight="bold", color="green900"),
                        name_field, email_field, password_field,
                        green_btn("Create Account", on_register), status,
                        ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
                            ft.Text("Already have an account?", color="grey700"),
                            ft.TextButton("Login", on_click=lambda e: show_login(), style=ft.ButtonStyle(color="green700")),
                        ]),
                    ]), radius=25, margin=ft.Margin(left=20, right=20, top=0, bottom=30)),
                ]))])

    # ──────────────────────────────────────────────────────
    # FORGOT PASSWORD SCREEN
    # ──────────────────────────────────────────────────────
    def show_forgot():
        email_field = ft.TextField(label="Enter your email", prefix_icon=ft.Icons.EMAIL_OUTLINED, width=300,
            border_radius=15, border_color="green700", focused_border_color="green900",
            keyboard_type=ft.KeyboardType.EMAIL, bgcolor="white")
        status = ft.Text("", size=14, text_align=ft.TextAlign.CENTER)
        def on_reset(e):
            if not email_field.value: status.value = "Please enter your email"; status.color = "red"
            else: status.value = f"Reset link sent to {email_field.value}"; status.color = "green700"
            page.update()
        switch([appbar("Forgot Password", lambda e: show_login()),
            ft.Container(expand=True, bgcolor="#f0f7f0", padding=20, content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, spacing=20,
                controls=[
                    logo(40), ft.Icon(ft.Icons.LOCK_RESET, color="green700", size=50),
                    ft.Text("Reset Password", size=22, weight="bold", color="green800"),
                    ft.Text("Enter your email and we will send you a reset link", size=13, color="grey600", text_align=ft.TextAlign.CENTER),
                    card(ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16,
                        controls=[email_field, green_btn("Send Reset Link", on_reset), status]),
                        radius=25, margin=ft.Margin(left=20, right=20, top=0, bottom=20)),
                    ft.TextButton("Back to Login", on_click=lambda e: show_login(), style=ft.ButtonStyle(color="green700")),
                ]))])

    # ──────────────────────────────────────────────────────
    # HOME SCREEN
    # ──────────────────────────────────────────────────────
    def show_home(email=""):
        crop_field = ft.TextField(
            label="Enter Crop Name", prefix_icon=ft.Icons.GRASS,
            width=300, border_radius=15, border_color="green700",
            focused_border_color="green900", bgcolor="white",
            hint_text="e.g. Maize, Wheat, Rice",
        )
        status = ft.Text("", size=13, color="red")

        def on_analyze(e):
            if not crop_field.value:
                status.value = "Please enter a crop name"
                page.update()
            else:
                show_analysis(crop_field.value.capitalize(), email)

        previous_crops = [
            {"crop": "Maize",  "date": "Feb 28", "weeks": "12 wks", "status": "Optimal"},
            {"crop": "Wheat",  "date": "Feb 20", "weeks": "8 wks",  "status": "Acidic"},
            {"crop": "Rice",   "date": "Feb 10", "weeks": "16 wks", "status": "Alkaline"},
        ]

        def prev_crop_card(item):
            color = "green700" if item["status"] == "Optimal" else "orange700" if item["status"] == "Acidic" else "blue700"
            return ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(spacing=12, controls=[
                            ft.Container(content=ft.Icon(ft.Icons.GRASS, color="white", size=18),
                                bgcolor="green700", border_radius=10, padding=8),
                            ft.Column(spacing=2, controls=[
                                ft.Text(item["crop"], size=14, weight="bold", color="green900"),
                                ft.Text(item["date"], size=11, color="grey500"),
                            ]),
                        ]),
                        ft.Column(horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2, controls=[
                            ft.Text(item["weeks"], size=13, weight="bold", color="green800"),
                            ft.Container(
                                content=ft.Text(item["status"], size=10, color="white"),
                                bgcolor=color, border_radius=8,
                                padding=ft.Padding(left=8, right=8, top=3, bottom=3),
                            ),
                        ]),
                    ],
                ),
                bgcolor="white", border_radius=14, padding=12,
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=6, color=ft.Colors.with_opacity(0.06, "green900")),
            )

        market_crops = [
            {"name": "Maize",   "price": "0.23", "difficulty": "Easy",   "diff_color": "green600"},
            {"name": "Wheat",   "price": "0.31", "difficulty": "Medium", "diff_color": "orange600"},
            {"name": "Rice",    "price": "0.42", "difficulty": "Hard",   "diff_color": "red600"},
            {"name": "Soybean", "price": "0.55", "difficulty": "Easy",   "diff_color": "green600"},
            {"name": "Cotton",  "price": "0.78", "difficulty": "Hard",   "diff_color": "red600"},
        ]

        def market_row(item):
            return ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(spacing=10, controls=[
                            ft.Container(content=ft.Icon(ft.Icons.GRASS, color="white", size=14),
                                bgcolor="green700", border_radius=8, padding=6),
                            ft.Text(item["name"], size=14, weight="bold", color="green900"),
                        ]),
                        ft.Row(spacing=12, controls=[
                            ft.Column(horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2, controls=[
                                ft.Text(f"${item['price']}/kg", size=13, weight="bold", color="green800"),
                                ft.Container(
                                    content=ft.Text(item["difficulty"], size=10, color="white"),
                                    bgcolor=item["diff_color"], border_radius=6,
                                    padding=ft.Padding(left=6, right=6, top=2, bottom=2),
                                ),
                            ]),
                        ]),
                    ],
                ),
                padding=ft.Padding(left=0, right=0, top=8, bottom=8),
            )

        switch([
            appbar("Soilco", actions=[
                ft.IconButton(icon=ft.Icons.MENU, icon_color="white",
                    on_click=lambda e: show_sidebar(email), tooltip="Menu")
            ]),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=16, bottom=20),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO, spacing=16,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Column(spacing=2, controls=[
                                    ft.Text("Good day,", size=13, color="grey600"),
                                    ft.Text(email.split("@")[0].capitalize() if email else "Farmer",
                                        size=20, weight="bold", color="green900"),
                                ]),
                                ft.Icon(ft.Icons.GRASS_ROUNDED, color="green700", size=36),
                            ],
                        ),
                        ft.Container(
                            content=ft.Column(spacing=12, controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Column(spacing=4, controls=[
                                            ft.Text("Current Weather", size=12, color="#c8e6c9"),
                                            ft.Text("-- °C", size=32, weight="bold", color="white"),
                                            ft.Text("Location not set", size=12, color="#c8e6c9"),
                                        ]),
                                        ft.Column(
                                            horizontal_alignment=ft.CrossAxisAlignment.END, spacing=6,
                                            controls=[
                                                ft.Icon(ft.Icons.WB_SUNNY_OUTLINED, color="white", size=48),
                                                ft.Row(spacing=8, controls=[ft.Row(spacing=2, controls=[
                                                    ft.Icon(ft.Icons.WATER_DROP_OUTLINED, color="#c8e6c9", size=12),
                                                    ft.Text("Hum: --%", size=11, color="#c8e6c9"),
                                                ])]),
                                                ft.Row(spacing=2, controls=[
                                                    ft.Icon(ft.Icons.AIR, color="#c8e6c9", size=12),
                                                    ft.Text("Wind: -- km/h", size=11, color="#c8e6c9"),
                                                ]),
                                            ],
                                        ),
                                    ],
                                ),
                                ft.Container(
                                    content=ft.Row(spacing=8, controls=[
                                        ft.Icon(ft.Icons.WATER_DROP, color="white", size=14),
                                        ft.Text("Daily Irrigation Alert", size=13, color="white", weight="bold"),
                                        ft.Icon(ft.Icons.ARROW_FORWARD_IOS, color="white", size=12),
                                    ]),
                                    bgcolor=ft.Colors.with_opacity(0.2, "white"),
                                    border_radius=10,
                                    padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                                    on_click=lambda e: show_daily_alert("", "0.0", email), ink=True,
                                ),
                            ]),
                            bgcolor="green700", border_radius=20, padding=20,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.with_opacity(0.15, "green900")),
                        ),
                        card(ft.Column(spacing=12, controls=[
                            ft.Text("Crop Analysis", size=16, weight="bold", color="green900"),
                            crop_field,
                            ft.Button("Analyze", on_click=on_analyze, width=300, height=45,
                                style=ft.ButtonStyle(bgcolor="green700", color="white",
                                    shape=ft.RoundedRectangleBorder(radius=12),
                                    text_style=ft.TextStyle(size=15, weight="bold"))),
                            status,
                        ])),
                        ft.Container(
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Row(spacing=12, controls=[
                                        ft.Container(content=ft.Icon(ft.Icons.WATER_DROP, color="white", size=22),
                                            bgcolor="brown400", border_radius=12, padding=10),
                                        ft.Column(spacing=3, controls=[
                                            ft.Text("Soil pH Estimator", size=14, weight="bold", color="green900"),
                                            ft.Text("Check soil suitability for your crop", size=11, color="grey500"),
                                        ]),
                                    ]),
                                    ft.Container(content=ft.Text("Open", size=11, color="white", weight="bold"),
                                        bgcolor="green700", border_radius=10, padding=ft.Padding(left=12, right=12, top=6, bottom=6)),
                                ],
                            ),
                            bgcolor="white", border_radius=20, padding=16,
                            on_click=lambda e: show_ph_estimator(email), ink=True,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.with_opacity(0.08, "green900")),
                        ),
                        card(ft.Column(spacing=0, controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("Crop Market Prices", size=16, weight="bold", color="green900"),
                                    ft.Row(spacing=4, controls=[
                                        ft.Icon(ft.Icons.AUTO_AWESOME, color="green600", size=14),
                                        ft.Text("AI Rated", size=11, color="green600"),
                                    ]),
                                ],
                            ),
                            ft.Container(height=4),
                            ft.Text("Price per kg — Farming difficulty", size=11, color="grey500"),
                            ft.Divider(color="green100"),
                            *[market_row(c) for c in market_crops],
                        ])),
                        ft.Column(spacing=10, controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("Previous Analyses", size=16, weight="bold", color="green900"),
                                    ft.TextButton("View All",
                                        on_click=lambda e: show_all_analyses(email),
                                        style=ft.ButtonStyle(color="green600")),
                                ],
                            ),
                            *[prev_crop_card(c) for c in previous_crops],
                        ]),
                        ft.Container(height=70),
                    ],
                ),
            ),
            nav_bar("Home", email),
        ])

    # ──────────────────────────────────────────────────────
    # VIEW ALL ANALYSES SCREEN
    # ──────────────────────────────────────────────────────
    def show_all_analyses(email=""):
        all_analyses = [
            {"crop": "Maize",    "date": "Feb 28, 2025", "weeks": "12 wks", "irrigation": "4.2 mm/day", "status": "Optimal"},
            {"crop": "Wheat",    "date": "Feb 20, 2025", "weeks": "8 wks",  "irrigation": "2.8 mm/day", "status": "Acidic"},
            {"crop": "Rice",     "date": "Feb 10, 2025", "weeks": "16 wks", "irrigation": "6.0 mm/day", "status": "Alkaline"},
            {"crop": "Soybean",  "date": "Jan 30, 2025", "weeks": "10 wks", "irrigation": "3.1 mm/day", "status": "Optimal"},
            {"crop": "Cotton",   "date": "Jan 15, 2025", "weeks": "20 wks", "irrigation": "5.5 mm/day", "status": "Optimal"},
            {"crop": "Tomato",   "date": "Jan 05, 2025", "weeks": "14 wks", "irrigation": "4.8 mm/day", "status": "Acidic"},
        ]

        def analysis_card(item):
            color = "green700" if item["status"] == "Optimal" else "orange700" if item["status"] == "Acidic" else "blue700"
            return ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(spacing=12, controls=[
                            ft.Container(content=ft.Icon(ft.Icons.GRASS, color="white", size=20),
                                bgcolor="green700", border_radius=12, padding=10),
                            ft.Column(spacing=3, controls=[
                                ft.Text(item["crop"], size=15, weight="bold", color="green900"),
                                ft.Text(item["date"], size=11, color="grey500"),
                                ft.Row(spacing=6, controls=[
                                    ft.Icon(ft.Icons.WATER_DROP, color="blue500", size=12),
                                    ft.Text(item["irrigation"], size=12, color="grey600"),
                                    ft.Text("·", color="grey400"),
                                    ft.Icon(ft.Icons.SCHEDULE, color="green500", size=12),
                                    ft.Text(item["weeks"], size=12, color="grey600"),
                                ]),
                            ]),
                        ]),
                        ft.Container(
                            content=ft.Text(item["status"], size=10, color="white"),
                            bgcolor=color, border_radius=8,
                            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                        ),
                    ],
                ),
                bgcolor="white", border_radius=16, padding=14,
                margin=ft.Margin(left=0, right=0, top=0, bottom=8),
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=6, color=ft.Colors.with_opacity(0.06, "green900")),
                on_click=lambda e, c=item["crop"]: show_analysis(c, email),
                ink=True,
            )

        switch([
            appbar("All Analyses", lambda e: show_home(email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=16, bottom=20),
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO, spacing=0,
                    controls=[
                        ft.Container(
                            content=ft.Row(spacing=8, controls=[
                                ft.Icon(ft.Icons.HISTORY, color="green700", size=18),
                                ft.Text(f"{len(all_analyses)} total analyses", size=13, color="grey600"),
                            ]),
                            padding=ft.Padding(left=0, right=0, top=0, bottom=12),
                        ),
                        *[analysis_card(a) for a in all_analyses],
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # ANALYSIS RESULT SCREEN
    # ──────────────────────────────────────────────────────
    def show_analysis(crop_name, email=""):
        # BACKEND: Call Groq API with prompt including:
        #   crop_name, user lat/lon, soil_ph from ISRIC SoilGrids at user coordinates
        # BACKEND: Groq returns JSON:
        #   {irrigation_mm_per_day, soil_type, growth_weeks,
        #    nitrogen_kg_ha, phosphorus_kg_ha, potassium_kg_ha, farming_difficulty}
        # BACKEND: farming_difficulty is scored dynamically by Groq based on:
        #   - actual soil pH from ISRIC vs crop's optimal pH range
        #   - regional climate suitability for the crop
        #   - returns "Easy", "Medium", or "Hard"
        # BACKEND: INSERT full result into Supabase analyses table

        irrigation_val = ft.Text("4.2 mm/day", size=20, weight="bold", color="green800")
        soil_type_val  = ft.Text("Loamy",      size=20, weight="bold", color="green800")
        growth_val     = ft.Text("12 weeks",   size=20, weight="bold", color="green800")
        nitrogen_val   = ft.Text("45.0 kg/ha", size=15, weight="bold", color="green700")
        phosphorus_val = ft.Text("22.5 kg/ha", size=15, weight="bold", color="green700")
        potassium_val  = ft.Text("30.0 kg/ha", size=15, weight="bold", color="green700")

        # BACKEND: Replace "Medium" with Groq response farming_difficulty field
        difficulty = "Medium"
        diff_color = {"Easy": "green600", "Medium": "orange600", "Hard": "red600"}
        diff_icon  = {
            "Easy":   ft.Icons.CHECK_CIRCLE,
            "Medium": ft.Icons.WARNING_ROUNDED,
            "Hard":   ft.Icons.DANGEROUS,
        }
        diff_description = {
            "Easy":   "Soil pH and climate in your region are well-suited for this crop. Minimal correction needed.",
            "Medium": "Some soil or climate factors may need attention. Check pH and consider amendments before planting.",
            "Hard":   "Significant soil correction or climate management required to grow this crop in your region.",
        }

        def metric_card(title, value_widget, icon, color):
            return ft.Container(
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6,
                    controls=[ft.Icon(icon, color=color, size=26),
                              ft.Text(title, size=11, color="grey600"), value_widget],
                ),
                bgcolor="white", border_radius=20, padding=16, expand=True,
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=10,
                    color=ft.Colors.with_opacity(0.08, "green900")),
            )

        def fert_row(label, val):
            return ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[ft.Text(label, size=14, color="grey700"), val])

        switch([
            appbar(f"{crop_name} Analysis", lambda e: show_home(email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=16, bottom=20),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO, spacing=16,
                    controls=[

                        # Header with crop + difficulty badge
                        card(ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Column(spacing=4, controls=[
                                    ft.Text("Crop", size=12, color="grey600"),
                                    ft.Text(crop_name, size=22, weight="bold", color="green900"),
                                ]),
                                ft.Column(spacing=6,
                                    horizontal_alignment=ft.CrossAxisAlignment.END,
                                    controls=[
                                    ft.Container(
                                        content=ft.Text("Analyzed", size=11, color="white"),
                                        bgcolor="green600", border_radius=8,
                                        padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                                    ),
                                    ft.Container(
                                        content=ft.Row(spacing=5, controls=[
                                            ft.Icon(diff_icon[difficulty], color="white", size=12),
                                            ft.Text(difficulty, size=11, color="white", weight="bold"),
                                        ]),
                                        bgcolor=diff_color[difficulty], border_radius=8,
                                        padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                                    ),
                                ]),
                            ],
                        )),

                        # Irrigation + soil type
                        ft.Row(spacing=12, controls=[
                            metric_card("Irrigation", irrigation_val, ft.Icons.WATER_DROP, "blue700"),
                            metric_card("Soil Type",  soil_type_val,  ft.Icons.LANDSCAPE,  "brown400"),
                        ]),

                        # Growth time
                        ft.Row(spacing=12, controls=[
                            metric_card("Growth Time", growth_val, ft.Icons.SCHEDULE, "green600"),
                        ]),

                        # Dynamic difficulty explanation
                        ft.Container(
                            content=ft.Column(spacing=10, controls=[
                                ft.Row(spacing=10,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                    ft.Icon(diff_icon[difficulty],
                                        color=diff_color[difficulty], size=22),
                                    ft.Text("Growing Difficulty",
                                        size=15, weight="bold", color="green900"),
                                    ft.Container(expand=True),
                                    ft.Container(
                                        content=ft.Text(difficulty, size=11,
                                            color="white", weight="bold"),
                                        bgcolor=diff_color[difficulty], border_radius=8,
                                        padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                                    ),
                                ]),
                                ft.Divider(color="green100"),
                                ft.Text(diff_description[difficulty], size=13, color="grey700"),
                                ft.Container(
                                    content=ft.Row(spacing=8, controls=[
                                        ft.Icon(ft.Icons.INFO_OUTLINE, color="green600", size=14),
                                        ft.Text(
                                            "Scored using your soil pH (ISRIC SoilGrids) "
                                            "and regional suitability via Groq AI",
                                            size=11, color="grey500", expand=True,
                                        ),
                                    ]),
                                    bgcolor="#f0f7f0", border_radius=8,
                                    padding=ft.Padding(left=10, right=10, top=8, bottom=8),
                                ),
                            ]),
                            bgcolor="white", border_radius=16, padding=16,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10,
                                color=ft.Colors.with_opacity(0.08, "green900")),
                        ),

                        # Fertilizer
                        card(ft.Column(spacing=12, controls=[
                            ft.Text("Fertilizer Recommendation",
                                size=16, weight="bold", color="green900"),
                            ft.Divider(color="green100"),
                            fert_row("Nitrogen (N)",   nitrogen_val),
                            fert_row("Phosphorus (P)", phosphorus_val),
                            fert_row("Potassium (K)",  potassium_val),
                        ])),

                        # Irrigation alert banner
                        ft.Container(
                            content=ft.Row(spacing=10, controls=[
                                ft.Icon(ft.Icons.WATER_DROP, color="white", size=18),
                                ft.Column(spacing=1, expand=True, controls=[
                                    ft.Text("Daily Irrigation Alert",
                                        size=14, weight="bold", color="white"),
                                    ft.Text("Tap to view today's water schedule",
                                        size=11, color="#c8e6c9"),
                                ]),
                                ft.Icon(ft.Icons.ARROW_FORWARD_IOS, color="white", size=14),
                            ]),
                            bgcolor="green700", border_radius=16, padding=16,
                            on_click=lambda e: show_daily_alert(crop_name, "4.2", email),
                            ink=True,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10,
                                color=ft.Colors.with_opacity(0.15, "green900")),
                        ),
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # DAILY IRRIGATION ALERT SCREEN
    # ──────────────────────────────────────────────────────
    def show_daily_alert(crop_name="", base_irrigation="4.2", email=""):
        # Placeholder weather values — will be replaced by OpenWeatherMap API
        weather = {
            "temp": "--",
            "humidity": "--",
            "wind": "--",
            "rain_forecast": "--",
            "condition": "Unknown",
        }

        # Irrigation calculation placeholders
        base = float(base_irrigation)
        rain = 0.0       # placeholder — will come from OpenWeatherMap
        adjusted = base  # adjusted = max(0, base - rain) once weather API connected

        def info_row(icon, icon_color, label, value):
            return ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(spacing=8, controls=[
                        ft.Icon(icon, color=icon_color, size=18),
                        ft.Text(label, size=13, color="grey700"),
                    ]),
                    ft.Text(value, size=13, weight="bold", color="green900"),
                ],
            )

        switch([
            appbar("Daily Irrigation Alert", lambda e: show_analysis(crop_name, email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=16, bottom=24),
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO, spacing=16,
                    controls=[

                        # Crop header
                        ft.Container(
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Row(spacing=12, controls=[
                                        ft.Container(
                                            content=ft.Icon(ft.Icons.GRASS, color="white", size=22),
                                            bgcolor="green700", border_radius=12, padding=10,
                                        ),
                                        ft.Column(spacing=2, controls=[
                                            ft.Text("Crop", size=11, color="grey500"),
                                            ft.Text(crop_name, size=18, weight="bold", color="green900"),
                                        ]),
                                    ]),
                                    ft.Container(
                                        content=ft.Text("Active", size=11, color="white"),
                                        bgcolor="green600", border_radius=8,
                                        padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                                    ),
                                ],
                            ),
                            bgcolor="white", border_radius=16, padding=16,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color=ft.Colors.with_opacity(0.07, "green900")),
                        ),

                        # Weather summary card
                        ft.Container(
                            content=ft.Column(spacing=12, controls=[
                                ft.Row(spacing=8, controls=[
                                    ft.Icon(ft.Icons.WB_SUNNY_OUTLINED, color="white", size=20),
                                    ft.Text("Today's Weather", size=14, weight="bold", color="white"),
                                ]),
                                ft.Divider(color=ft.Colors.with_opacity(0.3, "white")),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                    controls=[
                                        ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, controls=[
                                            ft.Icon(ft.Icons.THERMOSTAT, color="white", size=20),
                                            ft.Text(f"{weather['temp']} °C", size=15, weight="bold", color="white"),
                                            ft.Text("Temp", size=10, color="#c8e6c9"),
                                        ]),
                                        ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, controls=[
                                            ft.Icon(ft.Icons.WATER_DROP_OUTLINED, color="white", size=20),
                                            ft.Text(f"{weather['humidity']}%", size=15, weight="bold", color="white"),
                                            ft.Text("Humidity", size=10, color="#c8e6c9"),
                                        ]),
                                        ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, controls=[
                                            ft.Icon(ft.Icons.UMBRELLA, color="white", size=20),
                                            ft.Text(f"{weather['rain_forecast']} mm", size=15, weight="bold", color="white"),
                                            ft.Text("Rain", size=10, color="#c8e6c9"),
                                        ]),
                                        ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, controls=[
                                            ft.Icon(ft.Icons.AIR, color="white", size=20),
                                            ft.Text(f"{weather['wind']} km/h", size=15, weight="bold", color="white"),
                                            ft.Text("Wind", size=10, color="#c8e6c9"),
                                        ]),
                                    ],
                                ),
                            ]),
                            bgcolor="green700", border_radius=20, padding=20,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=12, color=ft.Colors.with_opacity(0.15, "green900")),
                        ),

                        # Irrigation calculation card
                        card(ft.Column(spacing=14, controls=[
                            ft.Text("Water Calculation", size=15, weight="bold", color="green900"),
                            ft.Divider(color="green100"),
                            info_row(ft.Icons.WATER_DROP, "blue700", "Base irrigation for " + crop_name, f"{base} mm/day"),
                            info_row(ft.Icons.UMBRELLA, "blue400", "Expected rainfall today", f"{weather['rain_forecast']} mm"),
                            info_row(ft.Icons.REMOVE_CIRCLE_OUTLINE, "orange600", "Weather adjustment", "-- mm"),
                            ft.Divider(color="green100"),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Text("Recommended today", size=15, weight="bold", color="green900"),
                                    ft.Container(
                                        content=ft.Text(f"{base} mm", size=16, weight="bold", color="white"),
                                        bgcolor="green700", border_radius=10,
                                        padding=ft.Padding(left=14, right=14, top=6, bottom=6),
                                    ),
                                ],
                            ),
                        ])),

                        # Schedule card
                        card(ft.Column(spacing=12, controls=[
                            ft.Text("Suggested Schedule", size=15, weight="bold", color="green900"),
                            ft.Divider(color="green100"),
                            ft.Row(spacing=12, controls=[
                                ft.Container(
                                    content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, controls=[
                                        ft.Icon(ft.Icons.WB_TWILIGHT, color="orange600", size=22),
                                        ft.Text("Morning", size=12, weight="bold", color="green900"),
                                        ft.Text("6:00 AM", size=11, color="grey500"),
                                        ft.Text("-- mm", size=13, weight="bold", color="green700"),
                                    ]),
                                    expand=True, bgcolor="#f0f7f0", border_radius=12, padding=12,
                                    alignment=ft.Alignment(0, 0),
                                ),
                                ft.Container(
                                    content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, controls=[
                                        ft.Icon(ft.Icons.WB_SUNNY, color="yellow700", size=22),
                                        ft.Text("Afternoon", size=12, weight="bold", color="green900"),
                                        ft.Text("2:00 PM", size=11, color="grey500"),
                                        ft.Text("-- mm", size=13, weight="bold", color="green700"),
                                    ]),
                                    expand=True, bgcolor="#f0f7f0", border_radius=12, padding=12,
                                    alignment=ft.Alignment(0, 0),
                                ),
                                ft.Container(
                                    content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, controls=[
                                        ft.Icon(ft.Icons.NIGHTS_STAY, color="blue700", size=22),
                                        ft.Text("Evening", size=12, weight="bold", color="green900"),
                                        ft.Text("6:00 PM", size=11, color="grey500"),
                                        ft.Text("-- mm", size=13, weight="bold", color="green700"),
                                    ]),
                                    expand=True, bgcolor="#f0f7f0", border_radius=12, padding=12,
                                    alignment=ft.Alignment(0, 0),
                                ),
                            ]),
                        ])),

                        ft.Text(
                            "* Live weather data requires OpenWeatherMap API & location to be set in Settings.",
                            size=11, color="grey400", italic=True, text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # SIDEBAR
    # ──────────────────────────────────────────────────────
    def show_sidebar(email=""):
        def menu_item(icon, label, on_click=None):
            return ft.Container(
                content=ft.Row(spacing=16, controls=[
                    ft.Icon(icon, color="green700", size=22),
                    ft.Text(label, size=15, color="grey900"),
                    ft.Container(expand=True),
                    ft.Icon(ft.Icons.ARROW_FORWARD_IOS, color="grey300", size=14),
                ]),
                padding=ft.Padding(left=20, right=16, top=14, bottom=14),
                border_radius=12, on_click=on_click, ink=True,
            )

        def divider():
            return ft.Divider(color="green100", height=1)

        def section_label(text):
            return ft.Container(
                content=ft.Text(text, size=12, color="grey500", weight="bold"),
                padding=ft.Padding(left=20, right=0, top=8, bottom=4),
            )

        def section_card(items):
            return ft.Container(
                content=ft.Column(spacing=0, controls=items),
                bgcolor="white", border_radius=16,
                margin=ft.Margin(left=16, right=16, top=4, bottom=12),
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color=ft.Colors.with_opacity(0.06, "green900")),
            )

        switch([
            appbar("Menu", lambda e: show_home(email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO, spacing=0,
                    controls=[
                        ft.Container(
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8,
                                controls=[
                                    ft.Container(content=ft.Icon(ft.Icons.PERSON, color="white", size=40),
                                        bgcolor="green700", border_radius=40, padding=20),
                                    ft.Text(email.split("@")[0].capitalize() if email else "Farmer",
                                        size=18, weight="bold", color="green900"),
                                    ft.Text(email or "farmer@soilco.app", size=12, color="grey600"),
                                ],
                            ),
                            bgcolor="white",
                            padding=ft.Padding(top=24, bottom=24, left=0, right=0),
                            width=page.window.width,
                        ),
                        ft.Container(height=12),
                        section_label("Account"),
                        section_card([
                            menu_item(ft.Icons.PERSON_OUTLINE, "Edit Profile", lambda e: show_edit_profile(email)),
                            divider(),
                            menu_item(ft.Icons.IMAGE_OUTLINED, "Profile Picture", lambda e: show_profile_picture(email)),
                            divider(),
                            menu_item(ft.Icons.LOCK_OUTLINE, "Change Password", lambda e: show_change_password(email)),
                        ]),
                        section_label("Preferences"),
                        section_card([
                            menu_item(ft.Icons.LOCATION_ON_OUTLINED, "Change Location", lambda e: show_change_location(email)),
                            divider(),
                            menu_item(ft.Icons.LANGUAGE, "Change Region", lambda e: show_change_region(email)),
                            divider(),
                            menu_item(ft.Icons.NOTIFICATIONS, "Notifications", lambda e: show_notifications(email)),
                            divider(),
                            menu_item(ft.Icons.DARK_MODE_OUTLINED, "Appearance", lambda e: show_appearance(email)),
                        ]),
                        section_label("Community"),
                        section_card([
                            menu_item(ft.Icons.FORUM_OUTLINED, "Crop Forum", lambda e: show_forum(email)),
                            divider(),
                            menu_item(ft.Icons.STOREFRONT_OUTLINED, "Marketplace", lambda e: show_marketplace(email)),
                        ]),
                        section_label("Support"),
                        section_card([
                            menu_item(ft.Icons.HELP_OUTLINE, "Help & FAQ", lambda e: show_help_faq(email)),
                            divider(),
                            menu_item(ft.Icons.FEEDBACK_OUTLINED, "Send Feedback", lambda e: show_feedback(email)),
                            divider(),
                            menu_item(ft.Icons.INFO_OUTLINE, "About Soilco", lambda e: show_about(email)),
                        ]),
                        ft.Container(
                            content=ft.Row(spacing=16, controls=[
                                ft.Icon(ft.Icons.LOGOUT, color="red600", size=22),
                                ft.Text("Logout", size=15, color="red600"),
                            ]),
                            padding=ft.Padding(left=20, right=20, top=14, bottom=14),
                            bgcolor="white", border_radius=16,
                            margin=ft.Margin(left=16, right=16, top=4, bottom=80),
                            on_click=lambda e: show_login(), ink=True,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color=ft.Colors.with_opacity(0.06, "green900")),
                        ),
                    ],
                ),
            ),
            nav_bar("Profile", email),
        ])

    # ──────────────────────────────────────────────────────
    # EDIT PROFILE SCREEN
    # ──────────────────────────────────────────────────────
    def show_edit_profile(email=""):
        name_field = ft.TextField(label="Full Name", value=email.split("@")[0].capitalize() if email else "",
            prefix_icon=ft.Icons.PERSON_OUTLINE, width=320, border_radius=15,
            border_color="green700", focused_border_color="green900", bgcolor="white")
        phone_field = ft.TextField(label="Phone Number", value="+27 -- --- ----",
            prefix_icon=ft.Icons.PHONE_OUTLINED, width=320, border_radius=15,
            border_color="green700", focused_border_color="green900", bgcolor="white",
            keyboard_type=ft.KeyboardType.PHONE)
        farm_field = ft.TextField(label="Farm Name", value="My Farm",
            prefix_icon=ft.Icons.AGRICULTURE, width=320, border_radius=15,
            border_color="green700", focused_border_color="green900", bgcolor="white")
        status = ft.Text("", size=14, color="green700", text_align=ft.TextAlign.CENTER)

        def on_save(e):
            status.value = "Profile saved successfully"
            page.update()

        switch([
            appbar("Edit Profile", lambda e: show_sidebar(email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=20, bottom=20),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO, spacing=20,
                    controls=[
                        ft.Container(
                            content=ft.Stack(controls=[
                                ft.Container(content=ft.Icon(ft.Icons.PERSON, color="white", size=48),
                                    bgcolor="green700", border_radius=50, padding=24,
                                    width=96, height=96, alignment=ft.Alignment(0, 0)),
                                ft.Container(
                                    content=ft.Icon(ft.Icons.CAMERA_ALT, color="white", size=14),
                                    bgcolor="green900", border_radius=20, padding=5,
                                    right=0, bottom=0,
                                ),
                            ]),
                            alignment=ft.Alignment(0, 0),
                        ),
                        card(ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16,
                            controls=[
                                ft.Text("Personal Information", size=15, weight="bold", color="green900"),
                                ft.Divider(color="green100"),
                                name_field, phone_field, farm_field,
                            ],
                        )),
                        green_btn("Save Changes", on_save, width=320),
                        status,
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # PROFILE PICTURE SCREEN
    # ──────────────────────────────────────────────────────
    def show_profile_picture(email=""):
        switch([
            appbar("Profile Picture", lambda e: show_sidebar(email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=24, bottom=20),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=24,
                    controls=[
                        ft.Container(
                            content=ft.Icon(ft.Icons.PERSON, color="white", size=72),
                            bgcolor="green700", border_radius=80, padding=36,
                            width=144, height=144, alignment=ft.Alignment(0, 0),
                        ),
                        ft.Text("Current Profile Picture", size=14, color="grey600"),
                        card(ft.Column(spacing=0, controls=[
                            ft.Container(
                                content=ft.Row(spacing=16, controls=[
                                    ft.Icon(ft.Icons.PHOTO_LIBRARY_OUTLINED, color="green700", size=22),
                                    ft.Text("Choose from Library", size=15, color="grey900"),
                                ]),
                                padding=ft.Padding(left=20, right=20, top=16, bottom=16),
                                on_click=lambda e: None, ink=True,
                            ),
                            ft.Divider(color="green100", height=1),
                            ft.Container(
                                content=ft.Row(spacing=16, controls=[
                                    ft.Icon(ft.Icons.CAMERA_ALT_OUTLINED, color="green700", size=22),
                                    ft.Text("Take Photo", size=15, color="grey900"),
                                ]),
                                padding=ft.Padding(left=20, right=20, top=16, bottom=16),
                                on_click=lambda e: None, ink=True,
                            ),
                        ])),
                        ft.Container(
                            content=ft.Row(spacing=16, controls=[
                                ft.Icon(ft.Icons.DELETE_OUTLINE, color="red600", size=22),
                                ft.Text("Remove Photo", size=15, color="red600"),
                            ]),
                            padding=ft.Padding(left=20, right=20, top=14, bottom=14),
                            bgcolor="white", border_radius=16,
                            margin=ft.Margin(left=0, right=0, top=0, bottom=0),
                            on_click=lambda e: None, ink=True,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color=ft.Colors.with_opacity(0.06, "green900")),
                        ),
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # CHANGE PASSWORD SCREEN
    # ──────────────────────────────────────────────────────
    def show_change_password(email=""):
        current = ft.TextField(label="Current Password", prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True, can_reveal_password=True, width=320, border_radius=15,
            border_color="green700", focused_border_color="green900", bgcolor="white")
        new_pass = ft.TextField(label="New Password", prefix_icon=ft.Icons.LOCK_OPEN,
            password=True, can_reveal_password=True, width=320, border_radius=15,
            border_color="green700", focused_border_color="green900", bgcolor="white")
        confirm = ft.TextField(label="Confirm New Password", prefix_icon=ft.Icons.LOCK_OPEN,
            password=True, can_reveal_password=True, width=320, border_radius=15,
            border_color="green700", focused_border_color="green900", bgcolor="white")
        status = ft.Text("", size=14, text_align=ft.TextAlign.CENTER)

        def on_save(e):
            if not current.value or not new_pass.value or not confirm.value:
                status.value = "Please fill in all fields"
                status.color = "red"
            elif new_pass.value != confirm.value:
                status.value = "New passwords do not match"
                status.color = "red"
            elif len(new_pass.value) < 6:
                status.value = "Password must be at least 6 characters"
                status.color = "red"
            else:
                status.value = "Password updated successfully"
                status.color = "green700"
            page.update()

        switch([
            appbar("Change Password", lambda e: show_sidebar(email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=24, bottom=20),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                    controls=[
                        ft.Container(content=ft.Icon(ft.Icons.SECURITY, color="green700", size=60),
                            alignment=ft.Alignment(0, 0)),
                        card(ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16,
                            controls=[
                                ft.Text("Update Password", size=15, weight="bold", color="green900"),
                                ft.Divider(color="green100"),
                                current, new_pass, confirm,
                            ],
                        )),
                        green_btn("Update Password", on_save, width=320),
                        status,
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # CHANGE LOCATION SCREEN
    # ──────────────────────────────────────────────────────
    def show_change_location(email=""):
        location_field = ft.TextField(label="Enter your location", value="Johannesburg, South Africa",
            prefix_icon=ft.Icons.LOCATION_ON_OUTLINED, width=320, border_radius=15,
            border_color="green700", focused_border_color="green900", bgcolor="white")
        status = ft.Text("", size=14, text_align=ft.TextAlign.CENTER)

        def on_save(e):
            status.value = f"Location set to: {location_field.value}"
            status.color = "green700"
            page.update()

        switch([
            appbar("Change Location", lambda e: show_sidebar(email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=24, bottom=20),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                    controls=[
                        ft.Container(content=ft.Icon(ft.Icons.MAP, color="green700", size=60),
                            alignment=ft.Alignment(0, 0)),
                        ft.Text("Set your farm location for accurate\nweather and irrigation data.",
                            size=14, color="grey600", text_align=ft.TextAlign.CENTER),
                        card(ft.Column(spacing=16, controls=[
                            ft.Text("Manual Location Entry", size=14, weight="bold", color="green900"),
                            location_field,
                        ])),
                        ft.Container(
                            content=ft.Row(spacing=12, controls=[
                                ft.Icon(ft.Icons.MY_LOCATION, color="white", size=20),
                                ft.Text("Use My Current Location", size=14, weight="bold", color="white"),
                            ], alignment=ft.MainAxisAlignment.CENTER),
                            bgcolor="green700", border_radius=15, padding=ft.Padding(left=20, right=20, top=14, bottom=14),
                            width=320, on_click=lambda e: None, ink=True,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.with_opacity(0.15, "green900")),
                        ),
                        green_btn("Save Location", on_save, width=320),
                        status,
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # CHANGE REGION SCREEN
    # ──────────────────────────────────────────────────────
    def show_change_region(email=""):
        regions = ["Sub-Saharan Africa", "East Africa", "West Africa", "Southern Africa",
                   "North Africa", "South Asia", "Southeast Asia", "Latin America"]
        selected = ft.Text("Sub-Saharan Africa", size=16, weight="bold", color="green800")
        status = ft.Text("", size=14, color="green700", text_align=ft.TextAlign.CENTER)

        def make_region_tile(r):
            is_sel = r == selected.value
            def on_tap(e, region=r):
                selected.value = region
                status.value = f"Region set to: {region}"
                page.update()
            return ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(r, size=14, color="green900"),
                        ft.Icon(ft.Icons.CHECK_CIRCLE if is_sel else ft.Icons.RADIO_BUTTON_UNCHECKED,
                            color="green700" if is_sel else "grey300", size=20),
                    ],
                ),
                padding=ft.Padding(left=20, right=16, top=14, bottom=14),
                on_click=on_tap, ink=True,
            )

        def divider():
            return ft.Divider(color="green100", height=1)

        tiles = []
        for i, r in enumerate(regions):
            tiles.append(make_region_tile(r))
            if i < len(regions) - 1:
                tiles.append(divider())

        switch([
            appbar("Change Region", lambda e: show_sidebar(email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=20, bottom=20),
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO, spacing=12,
                    controls=[
                        ft.Text("Select your farming region for relevant crop and market data.",
                            size=13, color="grey600"),
                        card(ft.Column(spacing=0, controls=tiles), padding=0),
                        status,
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # NOTIFICATIONS SCREEN
    # ──────────────────────────────────────────────────────
    def show_notifications(email=""):
        daily_alerts = ft.Switch(value=True, active_color="green700")
        market_updates = ft.Switch(value=True, active_color="green700")
        rain_alerts = ft.Switch(value=False, active_color="green700")
        weekly_summary = ft.Switch(value=True, active_color="green700")
        tips = ft.Switch(value=False, active_color="green700")

        def notif_row(label, subtitle, switch_ctrl):
            return ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(spacing=2, controls=[
                            ft.Text(label, size=14, color="grey900"),
                            ft.Text(subtitle, size=11, color="grey500"),
                        ]),
                        switch_ctrl,
                    ],
                ),
                padding=ft.Padding(left=20, right=16, top=12, bottom=12),
            )

        switch([
            appbar("Notifications", lambda e: show_sidebar(email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=20, bottom=20),
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO, spacing=16,
                    controls=[
                        card(ft.Column(spacing=0, controls=[
                            ft.Container(content=ft.Text("Alerts", size=12, color="grey500", weight="bold"),
                                padding=ft.Padding(left=20, right=0, top=12, bottom=4)),
                            notif_row("Daily Irrigation Alert", "Every morning at 7:00 AM", daily_alerts),
                            ft.Divider(color="green100", height=1),
                            notif_row("Rain Alerts", "When heavy rain is forecast", rain_alerts),
                        ]), padding=0),
                        card(ft.Column(spacing=0, controls=[
                            ft.Container(content=ft.Text("Updates", size=12, color="grey500", weight="bold"),
                                padding=ft.Padding(left=20, right=0, top=12, bottom=4)),
                            notif_row("Market Price Updates", "When crop prices change", market_updates),
                            ft.Divider(color="green100", height=1),
                            notif_row("Weekly Summary", "Every Sunday evening", weekly_summary),
                            ft.Divider(color="green100", height=1),
                            notif_row("Farming Tips", "Weekly tips from Soilco AI", tips),
                        ]), padding=0),
                        ft.Text("* Push notifications require the mobile app",
                            size=11, color="grey400", italic=True),
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # APPEARANCE SCREEN
    # ──────────────────────────────────────────────────────
    def show_appearance(email=""):
        switch([
            appbar("Appearance", lambda e: show_sidebar(email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=24, bottom=20),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=16,
                    controls=[
                        ft.Icon(ft.Icons.PALETTE_OUTLINED, color="green700", size=60),
                        ft.Text("Appearance Settings", size=18, weight="bold", color="green900"),
                        ft.Text("Customization options coming soon.",
                            size=14, color="grey500", text_align=ft.TextAlign.CENTER),
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # HELP & FAQ SCREEN
    # ──────────────────────────────────────────────────────
    def show_help_faq(email=""):
        faqs = [
            {
                "q": "How does Soilco analyze my crop?",
                "a": "Soilco uses AI (Groq/Llama 3) to analyze your crop type and location, then generates tailored recommendations for irrigation, fertilizer, and soil health.",
            },
            {
                "q": "Why is my weather showing '--'?",
                "a": "Weather data requires your location to be set and the OpenWeatherMap API to be connected. Go to Settings > Change Location to set your farm location.",
            },
            {
                "q": "How accurate are the irrigation recommendations?",
                "a": "Recommendations are based on crop type, soil type, and weather data. Once weather integration is live, accuracy improves significantly.",
            },
            {
                "q": "Are my analyses saved?",
                "a": "Yes, all analyses are saved to your account via Supabase and are visible under 'Previous Analyses' on your home screen.",
            },
            {
                "q": "Is Soilco free to use?",
                "a": "Yes, Soilco is free during the beta period. Future premium features may be introduced for commercial farms.",
            },
        ]

        expanded = [False] * len(faqs)

        def faq_tile(i, item):
            return ft.Container(
                content=ft.Column(spacing=8, controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(item["q"], size=14, weight="bold", color="green900", expand=True),
                            ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, color="green700", size=20),
                        ],
                    ),
                    ft.Text(item["a"], size=13, color="grey600"),
                ]),
                bgcolor="white", border_radius=14,
                padding=16,
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=6, color=ft.Colors.with_opacity(0.06, "green900")),
            )

        switch([
            appbar("Help & FAQ", lambda e: show_sidebar(email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=16, bottom=20),
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO, spacing=10,
                    controls=[
                        ft.Text("Frequently Asked Questions", size=16, weight="bold", color="green900"),
                        ft.Container(height=4),
                        *[faq_tile(i, f) for i, f in enumerate(faqs)],
                        ft.Container(height=8),
                        card(ft.Column(spacing=8, controls=[
                            ft.Text("Still need help?", size=14, weight="bold", color="green900"),
                            ft.Text("Contact our support team or send us feedback.",
                                size=13, color="grey600"),
                            ft.TextButton("Send Feedback",
                                on_click=lambda e: show_feedback(email),
                                style=ft.ButtonStyle(color="green700")),
                        ])),
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # SEND FEEDBACK SCREEN
    # ──────────────────────────────────────────────────────
    def show_feedback(email=""):
        categories = ["Bug Report", "Feature Request", "General Feedback", "Compliment"]
        selected_cat = {"value": "General Feedback"}

        feedback_field = ft.TextField(
            label="Write your feedback here...", multiline=True, min_lines=5, max_lines=8,
            width=320, border_radius=15, border_color="green700",
            focused_border_color="green900", bgcolor="white",
        )
        status = ft.Text("", size=14, text_align=ft.TextAlign.CENTER)

        def make_cat_chip(c):
            is_sel = c == selected_cat["value"]
            def on_tap(e, cat=c):
                selected_cat["value"] = cat
                show_feedback(email)
            return ft.Container(
                content=ft.Text(c, size=12, color="white" if is_sel else "green700"),
                bgcolor="green700" if is_sel else "white",
                border_radius=20,
                padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                on_click=on_tap, ink=True,
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=4, color=ft.Colors.with_opacity(0.08, "green900")),
            )

        def on_submit(e):
            if not feedback_field.value:
                status.value = "Please write your feedback"
                status.color = "red"
            else:
                status.value = "Thank you! Your feedback has been submitted."
                status.color = "green700"
                feedback_field.value = ""
            page.update()

        switch([
            appbar("Send Feedback", lambda e: show_sidebar(email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=20, bottom=20),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO, spacing=16,
                    controls=[
                        ft.Text("Category", size=14, weight="bold", color="green900"),
                        ft.Row(wrap=True, spacing=8, controls=[make_cat_chip(c) for c in categories]),
                        card(ft.Column(spacing=12, controls=[
                            ft.Text("Your Feedback", size=14, weight="bold", color="green900"),
                            feedback_field,
                        ])),
                        green_btn("Submit Feedback", on_submit, width=320),
                        status,
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # ABOUT SOILCO SCREEN
    # ──────────────────────────────────────────────────────
    def show_about(email=""):
        switch([
            appbar("About Soilco", lambda e: show_sidebar(email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=24, bottom=20),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO, spacing=20,
                    controls=[
                        logo(60),
                        ft.Text("Version 1.0.0 (Beta)", size=13, color="grey500"),
                        card(ft.Column(spacing=12, controls=[
                            ft.Text("About This App", size=15, weight="bold", color="green900"),
                            ft.Text(
                                "Soilco is an AI-powered smart soil analysis application designed to help farmers make better decisions. "
                                "It provides crop-specific irrigation recommendations, fertilizer guidance, and market insights — all in one place.",
                                size=13, color="grey700",
                            ),
                        ])),
                        card(ft.Column(spacing=10, controls=[
                            ft.Text("Technology Stack", size=15, weight="bold", color="green900"),
                            ft.Divider(color="green100"),
                            ft.Row(spacing=8, controls=[
                                ft.Icon(ft.Icons.CODE, color="green700", size=18),
                                ft.Text("Built with Python & Flet", size=13, color="grey700"),
                            ]),
                            ft.Row(spacing=8, controls=[
                                ft.Icon(ft.Icons.AUTO_AWESOME, color="green700", size=18),
                                ft.Text("AI by Groq (Llama 3)", size=13, color="grey700"),
                            ]),
                            ft.Row(spacing=8, controls=[
                                ft.Icon(ft.Icons.STORAGE, color="green700", size=18),
                                ft.Text("Database by Supabase", size=13, color="grey700"),
                            ]),
                            ft.Row(spacing=8, controls=[
                                ft.Icon(ft.Icons.CLOUD, color="green700", size=18),
                                ft.Text("Weather by OpenWeatherMap", size=13, color="grey700"),
                            ]),
                        ])),
                        card(ft.Column(spacing=10, controls=[
                            ft.Text("Academic Project", size=15, weight="bold", color="green900"),
                            ft.Divider(color="green100"),
                            ft.Text(
                                "This application was developed as a Final Year Project. "
                                "All data, analyses, and recommendations are for demonstration and research purposes.",
                                size=13, color="grey700",
                            ),
                            ft.Container(
                                content=ft.Text("Final Year Project — 2025", size=12, color="green700"),
                                bgcolor="#e8f5e9", border_radius=10,
                                padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                                alignment=ft.Alignment(0, 0),
                            ),
                        ])),
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # CROP FORUM SCREEN
    # ──────────────────────────────────────────────────────
    def show_forum(email=""):
        crop_channels = [
            {"crop": "Maize",    "icon": ft.Icons.GRASS,           "members": 1240, "unread": 3},
            {"crop": "Wheat",    "icon": ft.Icons.GRAIN,           "members": 876,  "unread": 0},
            {"crop": "Rice",     "icon": ft.Icons.WATER_DROP,      "members": 2103, "unread": 7},
            {"crop": "Soybean",  "icon": ft.Icons.ECO,             "members": 534,  "unread": 1},
            {"crop": "Cotton",   "icon": ft.Icons.FILTER_VINTAGE,  "members": 389,  "unread": 0},
            {"crop": "Tomato",   "icon": ft.Icons.CIRCLE,          "members": 991,  "unread": 2},
            {"crop": "Cassava",  "icon": ft.Icons.PARK,            "members": 1450, "unread": 0},
            {"crop": "Sorghum",  "icon": ft.Icons.NATURE,          "members": 620,  "unread": 4},
        ]

        def channel_tile(ch):
            return ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(spacing=14, controls=[
                            ft.Container(
                                content=ft.Icon(ch["icon"], color="white", size=20),
                                bgcolor="green700", border_radius=12, padding=10,
                                width=44, height=44,
                            ),
                            ft.Column(spacing=2, controls=[
                                ft.Text(f"# {ch['crop'].lower()}-farmers",
                                    size=14, weight="bold", color="green900"),
                                ft.Text(f"{ch['members']:,} members",
                                    size=11, color="grey500"),
                            ]),
                        ]),
                        ft.Row(spacing=8, controls=[
                            ft.Container(
                                content=ft.Text(str(ch["unread"]), size=10,
                                    color="white", weight="bold"),
                                bgcolor="green600", border_radius=10,
                                padding=ft.Padding(left=7, right=7, top=3, bottom=3),
                                visible=ch["unread"] > 0,
                            ),
                            ft.Icon(ft.Icons.ARROW_FORWARD_IOS, color="grey300", size=14),
                        ]),
                    ],
                ),
                bgcolor="white", border_radius=14, padding=12,
                margin=ft.Margin(left=0, right=0, top=0, bottom=8),
                on_click=lambda e, c=ch["crop"]: show_forum_channel(c, email),
                ink=True,
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=6,
                    color=ft.Colors.with_opacity(0.06, "green900")),
            )

        switch([
            appbar("Crop Forum", lambda e: show_home(email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=16, bottom=20),
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO, spacing=0,
                    controls=[
                        # Header banner
                        ft.Container(
                            content=ft.Column(spacing=6, controls=[
                                ft.Row(spacing=10, controls=[
                                    ft.Icon(ft.Icons.FORUM, color="white", size=28),
                                    ft.Column(spacing=2, controls=[
                                        ft.Text("Crop Forum", size=17, weight="bold", color="white"),
                                        ft.Text("Connect with farmers growing your crop", size=11, color="#c8e6c9"),
                                    ]),
                                ]),
                            ]),
                            bgcolor="green700", border_radius=16, padding=16,
                            margin=ft.Margin(left=0, right=0, top=0, bottom=14),
                        ),
                        ft.Container(
                            content=ft.Row(spacing=10, controls=[
                                ft.Icon(ft.Icons.CAMERA_ALT_OUTLINED, color="green700", size=16),
                                ft.Text(
                                    "Max 2 photos/day per user. Camera photos only — no screenshots.",
                                    size=11, color="grey600", expand=True,
                                ),
                            ]),
                            bgcolor="#e8f5e9", border_radius=12,
                            padding=ft.Padding(left=12, right=12, top=10, bottom=10),
                            margin=ft.Margin(left=0, right=0, top=0, bottom=14),
                        ),
                        ft.Text("Channels", size=13, color="grey500", weight="bold"),
                        ft.Container(height=8),
                        *[channel_tile(ch) for ch in crop_channels],
                        ft.Container(height=70),
                    ],
                ),
            ),
            nav_bar("Forum", email),
        ])

    # ──────────────────────────────────────────────────────
    # FORUM CHANNEL SCREEN
    # ──────────────────────────────────────────────────────
    def show_forum_channel(crop_name, email=""):
        username = email.split("@")[0].capitalize() if email else "Farmer"

        placeholder_posts = [
            {
                "user": "James K.",
                "time": "2h ago",
                "text": f"Anyone else seeing yellowing on their {crop_name} leaves after the last rain? Checked pH and it's around 5.8.",
                "likes": 12,
                "replies": 4,
                "has_photo": True,
            },
            {
                "user": "Amina S.",
                "time": "5h ago",
                "text": f"Applied the fertilizer recommendation from Soilco last week. {crop_name} looking much healthier. N:45 P:22 K:30.",
                "likes": 28,
                "replies": 9,
                "has_photo": False,
            },
            {
                "user": "David O.",
                "time": "1d ago",
                "text": "What irrigation schedule are you all using this season? Getting conflicting advice.",
                "likes": 6,
                "replies": 15,
                "has_photo": True,
            },
        ]

        photos_today = {"count": 0}

        msg_field = ft.TextField(
            hint_text=f"Message #{crop_name.lower()}-farmers...",
            border_radius=20,
            border_color="green200",
            focused_border_color="green700",
            bgcolor="white",
            expand=True,
            min_lines=1,
            max_lines=3,
            content_padding=ft.Padding(left=16, right=16, top=10, bottom=10),
        )

        def post_tile(p):
            return ft.Container(
                content=ft.Column(spacing=8, controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(spacing=8, controls=[
                                ft.Container(
                                    content=ft.Text(p["user"][0], size=13,
                                        color="white", weight="bold"),
                                    bgcolor="green700", border_radius=16,
                                    width=32, height=32,
                                    alignment=ft.Alignment(0, 0),
                                ),
                                ft.Column(spacing=1, controls=[
                                    ft.Text(p["user"], size=13, weight="bold",
                                        color="green900"),
                                    ft.Text(p["time"], size=10, color="grey400"),
                                ]),
                            ]),
                        ],
                    ),
                    ft.Text(p["text"], size=13, color="grey800"),
                    ft.Container(
                        content=ft.Row(spacing=4, controls=[
                            ft.Icon(ft.Icons.IMAGE_OUTLINED, color="green500", size=14),
                            ft.Text("1 photo attached", size=11, color="green600"),
                        ]),
                        visible=p["has_photo"],
                    ),
                    ft.Row(spacing=16, controls=[
                        ft.Row(spacing=4, controls=[
                            ft.Icon(ft.Icons.FAVORITE_BORDER, color="grey400", size=15),
                            ft.Text(str(p["likes"]), size=11, color="grey500"),
                        ]),
                        ft.Row(spacing=4, controls=[
                            ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, color="grey400", size=15),
                            ft.Text(str(p["replies"]), size=11, color="grey500"),
                        ]),
                    ]),
                ]),
                bgcolor="white", border_radius=14, padding=14,
                margin=ft.Margin(left=0, right=0, top=0, bottom=8),
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=6,
                    color=ft.Colors.with_opacity(0.06, "green900")),
            )

        def on_photo(e):
            if photos_today["count"] >= 2:
                dlg = ft.AlertDialog(
                    title=ft.Text("Daily Limit Reached", color="red700", weight="bold"),
                    content=ft.Text(
                        "You can only upload 2 photos per day in the forum. "
                        "This keeps the channel focused and high quality.",
                        size=13, color="grey700",
                    ),
                    actions=[ft.TextButton("OK",
                        on_click=lambda e: (setattr(dlg, "open", False), page.update()),
                        style=ft.ButtonStyle(color="green700"))],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.overlay.append(dlg)
                dlg.open = True
                page.update()
            else:
                dlg = ft.AlertDialog(
                    title=ft.Text("Add Photo", color="green900", weight="bold"),
                    content=ft.Column(tight=True, spacing=12, controls=[
                        ft.Text(
                            "Photos must be taken directly from your device camera. "
                            "Screenshots and downloaded images are not accepted.",
                            size=13, color="grey600",
                        ),
                        ft.Text(
                            f"Photos used today: {photos_today['count']}/2",
                            size=12, color="green700", weight="bold",
                        ),
                    ]),
                    actions=[
                        ft.TextButton("Cancel",
                            on_click=lambda e: (setattr(dlg, "open", False), page.update()),
                            style=ft.ButtonStyle(color="grey500")),
                        ft.TextButton("Open Camera",
                            on_click=lambda e: (
                                photos_today.update({"count": photos_today["count"] + 1}),
                                setattr(dlg, "open", False),
                                page.update()
                            ),
                            style=ft.ButtonStyle(color="green700")),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.overlay.append(dlg)
                dlg.open = True
                page.update()

        photo_badge = ft.Container(
            content=ft.Text(f"{2 - photos_today['count']} photos left today",
                size=10, color="green600"),
            bgcolor="#e8f5e9", border_radius=10,
            padding=ft.Padding(left=8, right=8, top=3, bottom=3),
        )

        switch([
            appbar(f"#{crop_name.lower()}-farmers", lambda e: show_forum(email),
                actions=[
                    ft.IconButton(
                        icon=ft.Icons.EDIT_NOTE,
                        icon_color="white",
                        tooltip="New Post",
                        on_click=lambda e: show_new_post(crop_name, email),
                    )
                ]),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                content=ft.Column(
                    spacing=0,
                    controls=[
                        ft.Container(
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(spacing=6, controls=[
                                        ft.Container(
                                            content=ft.Icon(ft.Icons.CIRCLE,
                                                color="green500", size=8),
                                        ),
                                        ft.Text(f"{crop_name} Farmers Channel",
                                            size=12, color="grey600"),
                                    ]),
                                    photo_badge,
                                ],
                            ),
                            bgcolor="white",
                            padding=ft.Padding(left=16, right=16, top=8, bottom=8),
                            shadow=ft.BoxShadow(spread_radius=0, blur_radius=4,
                                color=ft.Colors.with_opacity(0.05, "green900")),
                        ),
                        ft.Container(
                            expand=True,
                            padding=ft.Padding(left=16, right=16, top=12, bottom=8),
                            content=ft.Column(
                                scroll=ft.ScrollMode.AUTO, spacing=0,
                                controls=[*[post_tile(p) for p in placeholder_posts]],
                            ),
                        ),
                        ft.Container(
                            content=ft.Row(spacing=8, controls=[
                                ft.IconButton(
                                    icon=ft.Icons.ADD_PHOTO_ALTERNATE_OUTLINED,
                                    icon_color="green700", icon_size=22,
                                    tooltip="Add photo (max 2/day)",
                                    on_click=on_photo,
                                ),
                                msg_field,
                                ft.IconButton(
                                    icon=ft.Icons.SEND_ROUNDED,
                                    icon_color="green700", icon_size=22,
                                    on_click=lambda e: None,
                                ),
                            ]),
                            bgcolor="white",
                            padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                            shadow=ft.BoxShadow(spread_radius=0, blur_radius=8,
                                color=ft.Colors.with_opacity(0.08, "green900")),
                        ),
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # MARKETPLACE — BUYER / SELLER DUAL SIDE
    # ──────────────────────────────────────────────────────
    def show_marketplace(email="", active_tab="buyer"):
        # BACKEND PLACEHOLDER: Fetch listings from Supabase `marketplace_listings`
        #   SELECT * FROM marketplace_listings ORDER BY created_at DESC
        # BACKEND PLACEHOLDER: Fetch user's own listings for Seller tab
        #   SELECT * FROM marketplace_listings WHERE user_id = current_user_id

        listings = [
            {"seller": "James K.",  "crop": "Maize",   "qty": "500 kg",   "price": "$0.22/kg", "location": "Accra, Ghana",      "verified": True,  "status": "Available"},
            {"seller": "Amina S.",  "crop": "Rice",    "qty": "1,200 kg", "price": "$0.40/kg", "location": "Kano, Nigeria",     "verified": True,  "status": "Available"},
            {"seller": "David O.",  "crop": "Soybean", "qty": "300 kg",   "price": "$0.50/kg", "location": "Nairobi, Kenya",    "verified": False, "status": "Available"},
            {"seller": "Fatima B.", "crop": "Wheat",   "qty": "800 kg",   "price": "$0.29/kg", "location": "Lahore, Pakistan",  "verified": True,  "status": "Available"},
            {"seller": "Carlos M.", "crop": "Cotton",  "qty": "2,000 kg", "price": "$0.75/kg", "location": "Sao Paulo, Brazil", "verified": False, "status": "Sold Out"},
            {"seller": "Priya N.",  "crop": "Tomato",  "qty": "150 kg",   "price": "$0.35/kg", "location": "Mumbai, India",     "verified": True,  "status": "Available"},
        ]

        # Placeholder seller's own listings
        my_listings = [
            {"crop": "Maize", "qty": "200 kg", "price": "$0.20/kg", "location": "My Farm", "status": "Available",  "inquiries": 3},
            {"crop": "Rice",  "qty": "500 kg", "price": "$0.38/kg", "location": "My Farm", "status": "Sold Out",   "inquiries": 8},
        ]

        def buyer_listing_card(l):
            is_available = l["status"] == "Available"
            return ft.Container(
                content=ft.Column(spacing=10, controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(spacing=10, controls=[
                                ft.Container(
                                    content=ft.Text(l["seller"][0], size=15,
                                        color="white", weight="bold"),
                                    bgcolor="green700", border_radius=20,
                                    width=38, height=38,
                                    alignment=ft.Alignment(0, 0),
                                ),
                                ft.Column(spacing=1, controls=[
                                    ft.Row(spacing=6, controls=[
                                        ft.Text(l["seller"], size=13,
                                            weight="bold", color="green900"),
                                        ft.Container(
                                            content=ft.Row(spacing=3, controls=[
                                                ft.Icon(ft.Icons.VERIFIED,
                                                    color="white", size=10),
                                                ft.Text("Verified", size=9, color="white"),
                                            ]),
                                            bgcolor="green600", border_radius=8,
                                            padding=ft.Padding(left=6, right=6, top=2, bottom=2),
                                            visible=l["verified"],
                                        ),
                                    ]),
                                    ft.Row(spacing=4, controls=[
                                        ft.Icon(ft.Icons.LOCATION_ON, color="grey400", size=12),
                                        ft.Text(l["location"], size=11, color="grey500"),
                                    ]),
                                ]),
                            ]),
                            ft.Column(horizontal_alignment=ft.CrossAxisAlignment.END,
                                spacing=3, controls=[
                                ft.Text(l["price"], size=15, weight="bold", color="green800"),
                                ft.Text(l["qty"], size=11, color="grey500"),
                            ]),
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(spacing=8, controls=[
                                ft.Container(
                                    content=ft.Row(spacing=5, controls=[
                                        ft.Icon(ft.Icons.GRASS, color="green700", size=13),
                                        ft.Text(l["crop"], size=12, color="green800",
                                            weight="bold"),
                                    ]),
                                    bgcolor="#e8f5e9", border_radius=8,
                                    padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                                ),
                                ft.Container(
                                    content=ft.Text(l["status"], size=10,
                                        color="white", weight="bold"),
                                    bgcolor="green600" if is_available else "grey400",
                                    border_radius=8,
                                    padding=ft.Padding(left=8, right=8, top=3, bottom=3),
                                ),
                            ]),
                            ft.Container(
                                content=ft.Row(spacing=6, controls=[
                                    ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE,
                                        color="white", size=13),
                                    ft.Text("Contact", size=12, color="white", weight="bold"),
                                ]),
                                bgcolor="green700" if is_available else "grey400",
                                border_radius=10,
                                padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                                on_click=(lambda e, s=l["seller"]: show_chat(s, email, "buyer"))
                                    if is_available else None,
                                ink=is_available,
                            ),
                        ],
                    ),
                ]),
                bgcolor="white", border_radius=16, padding=14,
                margin=ft.Margin(left=0, right=0, top=0, bottom=10),
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=6,
                    color=ft.Colors.with_opacity(0.06, "green900")),
            )

        def seller_listing_card(l):
            is_available = l["status"] == "Available"
            return ft.Container(
                content=ft.Column(spacing=10, controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(spacing=10, controls=[
                                ft.Container(
                                    content=ft.Icon(ft.Icons.GRASS, color="white", size=20),
                                    bgcolor="green700", border_radius=12, padding=10,
                                ),
                                ft.Column(spacing=2, controls=[
                                    ft.Text(l["crop"], size=14, weight="bold", color="green900"),
                                    ft.Text(f"{l['qty']}  ·  {l['price']}",
                                        size=12, color="grey600"),
                                ]),
                            ]),
                            ft.Container(
                                content=ft.Text(l["status"], size=10,
                                    color="white", weight="bold"),
                                bgcolor="green600" if is_available else "grey400",
                                border_radius=8,
                                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                            ),
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(spacing=6, controls=[
                                ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE,
                                    color="green700", size=14),
                                ft.Text(f"{l['inquiries']} inquiries",
                                    size=12, color="green700", weight="bold"),
                            ]),
                            ft.Row(spacing=8, controls=[
                                ft.Container(
                                    content=ft.Text("Edit", size=11,
                                        color="green700", weight="bold"),
                                    border=ft.border.all(1, "green700"),
                                    border_radius=8,
                                    padding=ft.Padding(left=12, right=12, top=5, bottom=5),
                                    on_click=lambda e: None, ink=True,
                                    # BACKEND PLACEHOLDER: Open edit listing screen
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        "Mark Sold" if is_available else "Relist",
                                        size=11, color="white", weight="bold"),
                                    bgcolor="green700" if is_available else "orange700",
                                    border_radius=8,
                                    padding=ft.Padding(left=12, right=12, top=5, bottom=5),
                                    on_click=lambda e: None, ink=True,
                                    # BACKEND PLACEHOLDER: UPDATE listing status in Supabase
                                ),
                            ]),
                        ],
                    ),
                ]),
                bgcolor="white", border_radius=16, padding=14,
                margin=ft.Margin(left=0, right=0, top=0, bottom=10),
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=6,
                    color=ft.Colors.with_opacity(0.06, "green900")),
            )

        # Tab toggle
        def tab_toggle(label, tab_id):
            is_active = active_tab == tab_id
            return ft.Container(
                content=ft.Text(label, size=13, weight="bold",
                    color="white" if is_active else "green700"),
                bgcolor="green700" if is_active else "white",
                border_radius=12,
                padding=ft.Padding(left=0, right=0, top=10, bottom=10),
                expand=True,
                alignment=ft.Alignment(0, 0),
                on_click=lambda e, t=tab_id: show_marketplace(email, t),
                ink=True,
            )

        buyer_content = ft.Column(
            scroll=ft.ScrollMode.AUTO, spacing=0,
            controls=[
                ft.Container(
                    content=ft.Row(spacing=6, controls=[
                        ft.Icon(ft.Icons.SEARCH, color="green700", size=18),
                        ft.Text("Browse listings and contact farmers directly",
                            size=12, color="grey600"),
                    ]),
                    bgcolor="#e8f5e9", border_radius=12,
                    padding=ft.Padding(left=12, right=12, top=10, bottom=10),
                    margin=ft.Margin(left=0, right=0, top=0, bottom=12),
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(f"{len(listings)} listings available",
                            size=13, color="grey500"),
                        ft.Row(spacing=4, controls=[
                            ft.Icon(ft.Icons.FILTER_LIST, color="green700", size=16),
                            ft.Text("Filter", size=12, color="green700"),
                        ]),
                    ],
                ),
                ft.Container(height=10),
                *[buyer_listing_card(l) for l in listings],
                ft.Container(height=70),
            ],
        )

        seller_content = ft.Column(
            scroll=ft.ScrollMode.AUTO, spacing=0,
            controls=[
                ft.Container(
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Column(spacing=2, controls=[
                                ft.Text("Your Listings", size=14,
                                    weight="bold", color="green900"),
                                ft.Text(f"{len(my_listings)} active listings",
                                    size=11, color="grey500"),
                            ]),
                            ft.Container(
                                content=ft.Row(spacing=6, controls=[
                                    ft.Icon(ft.Icons.ADD, color="white", size=16),
                                    ft.Text("New Listing", size=12,
                                        color="white", weight="bold"),
                                ]),
                                bgcolor="green700", border_radius=10,
                                padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                                on_click=lambda e: show_list_crop(email), ink=True,
                            ),
                        ],
                    ),
                    margin=ft.Margin(left=0, right=0, top=0, bottom=12),
                ),
                *[seller_listing_card(l) for l in my_listings],
                ft.Container(height=14),
                # Inquiries section
                ft.Text("Recent Inquiries", size=13, color="grey500", weight="bold"),
                ft.Container(height=8),
                *[
                    ft.Container(
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Row(spacing=10, controls=[
                                    ft.Container(
                                        content=ft.Text(inq["buyer"][0], size=13,
                                            color="white", weight="bold"),
                                        bgcolor="green700", border_radius=16,
                                        width=32, height=32,
                                        alignment=ft.Alignment(0, 0),
                                    ),
                                    ft.Column(spacing=2, controls=[
                                        ft.Text(inq["buyer"], size=13,
                                            weight="bold", color="green900"),
                                        ft.Text(f"Re: {inq['crop']} · {inq['time']}",
                                            size=11, color="grey500"),
                                    ]),
                                ]),
                                ft.Container(
                                    content=ft.Text("Reply", size=11,
                                        color="white", weight="bold"),
                                    bgcolor="green700", border_radius=8,
                                    padding=ft.Padding(left=12, right=12, top=5, bottom=5),
                                    on_click=lambda e, b=inq["buyer"]: show_chat(b, email, "seller"),
                                    ink=True,
                                ),
                            ],
                        ),
                        bgcolor="white", border_radius=14, padding=12,
                        margin=ft.Margin(left=0, right=0, top=0, bottom=8),
                        shadow=ft.BoxShadow(spread_radius=1, blur_radius=6,
                            color=ft.Colors.with_opacity(0.06, "green900")),
                    )
                    for inq in [
                        {"buyer": "Kwame A.", "crop": "Maize",  "time": "2h ago"},
                        {"buyer": "Sarah M.", "crop": "Maize",  "time": "5h ago"},
                        {"buyer": "Ali H.",   "crop": "Rice",   "time": "1d ago"},
                    ]
                ],
                ft.Container(height=70),
            ],
        )

        switch([
            appbar("Marketplace"),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                content=ft.Column(
                    spacing=0,
                    controls=[
                        # Header banner
                        ft.Container(
                            content=ft.Row(spacing=12, controls=[
                                ft.Icon(ft.Icons.STOREFRONT, color="white", size=26),
                                ft.Column(spacing=2, controls=[
                                    ft.Text("Marketplace", size=17,
                                        weight="bold", color="white"),
                                    ft.Text("Buy and sell crops directly",
                                        size=11, color="#c8e6c9"),
                                ]),
                            ]),
                            bgcolor="green700", border_radius=0,
                            padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                        ),

                        # Buyer / Seller tab toggle
                        ft.Container(
                            content=ft.Row(spacing=0, controls=[
                                tab_toggle("Buyer", "buyer"),
                                tab_toggle("Seller", "seller"),
                            ]),
                            bgcolor="white",
                            border=ft.border.all(1, "green100"),
                            border_radius=14,
                            margin=ft.Padding(left=16, right=16, top=12, bottom=12),
                            padding=4,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=6,
                                color=ft.Colors.with_opacity(0.06, "green900")),
                        ),

                        # Tab content
                        ft.Container(
                            expand=True,
                            padding=ft.Padding(left=16, right=16, top=0, bottom=0),
                            content=buyer_content if active_tab == "buyer" else seller_content,
                        ),
                    ],
                ),
            ),
            nav_bar("Market", email),
        ])

    # ──────────────────────────────────────────────────────
    # P2P CHAT SCREEN
    # ──────────────────────────────────────────────────────
    def show_chat(other_name, email="", role="buyer"):
        # role = "buyer"  → user is buying, other_name is the seller
        # role = "seller" → user is selling, other_name is the buyer
        # BACKEND PLACEHOLDER: Fetch chat history from Supabase `messages` table:
        #   SELECT * FROM messages WHERE
        #   (sender_id=current_user AND receiver_id=other_user)
        #   OR (sender_id=other_user AND receiver_id=current_user)
        #   ORDER BY created_at ASC
        # BACKEND PLACEHOLDER: On send, INSERT message to Supabase and trigger
        #   real-time subscription update

        username = email.split("@")[0].capitalize() if email else "You"
        is_buyer = role == "buyer"

        messages = [
            {"sender": other_name, "text": "Hello! Yes the produce is still available. Freshly harvested.", "time": "10:32 AM"},
            {"sender": username,   "text": "Great! What is the minimum order quantity?", "time": "10:35 AM"},
            {"sender": other_name, "text": "Minimum is 50kg. I can arrange delivery within 50km of my location.", "time": "10:37 AM"},
        ]

        msg_field = ft.TextField(
            hint_text="Type a message...",
            border_radius=20,
            border_color="green200",
            focused_border_color="green700",
            bgcolor="white",
            expand=True,
            min_lines=1,
            max_lines=4,
            content_padding=ft.Padding(left=16, right=16, top=10, bottom=10),
        )

        chat_column = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=8, controls=[])

        def bubble(m):
            is_me = m["sender"] == username
            return ft.Row(
                alignment=ft.MainAxisAlignment.END if is_me else ft.MainAxisAlignment.START,
                controls=[
                    ft.Container(
                        content=ft.Column(spacing=3, controls=[
                            ft.Text(m["sender"], size=10,
                                color="white70" if is_me else "green700",
                                weight="bold", visible=not is_me),
                            ft.Text(m["text"], size=13,
                                color="white" if is_me else "grey900"),
                            ft.Text(m["time"], size=9,
                                color="white70" if is_me else "grey400"),
                        ]),
                        bgcolor="green700" if is_me else "white",
                        border_radius=ft.BorderRadius(
                            top_left=16, top_right=16,
                            bottom_left=4 if is_me else 16,
                            bottom_right=16 if is_me else 4,
                        ),
                        padding=ft.Padding(left=14, right=14, top=10, bottom=8),
                        max_width=260,
                        shadow=ft.BoxShadow(spread_radius=1, blur_radius=4,
                            color=ft.Colors.with_opacity(0.08, "green900")),
                    )
                ],
            )

        for m in messages:
            chat_column.controls.append(bubble(m))

        def on_send(e):
            if msg_field.value and msg_field.value.strip():
                chat_column.controls.append(bubble({
                    "sender": username,
                    "text":   msg_field.value.strip(),
                    "time":   "Just now",
                }))
                msg_field.value = ""
                page.update()

        switch([
            appbar(other_name, lambda e: show_marketplace(email, role)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                content=ft.Column(spacing=0, controls=[

                    # Chat header — shows role context
                    ft.Container(
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Row(spacing=10, controls=[
                                    ft.Container(
                                        content=ft.Text(other_name[0], size=14,
                                            color="white", weight="bold"),
                                        bgcolor="green700", border_radius=20,
                                        width=36, height=36,
                                        alignment=ft.Alignment(0, 0),
                                    ),
                                    ft.Column(spacing=1, controls=[
                                        ft.Text(other_name, size=14,
                                            weight="bold", color="green900"),
                                        ft.Text(
                                            "Seller · Online" if is_buyer else "Buyer · Online",
                                            size=11, color="green600"),
                                    ]),
                                ]),
                                ft.Container(
                                    content=ft.Text(
                                        "You are buying" if is_buyer else "You are selling",
                                        size=10, color="green700", weight="bold"),
                                    bgcolor="#e8f5e9", border_radius=10,
                                    padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                                ),
                            ],
                        ),
                        bgcolor="white",
                        padding=ft.Padding(left=16, right=16, top=10, bottom=10),
                        shadow=ft.BoxShadow(spread_radius=0, blur_radius=4,
                            color=ft.Colors.with_opacity(0.05, "green900")),
                    ),

                    # Messages
                    ft.Container(
                        expand=True,
                        padding=ft.Padding(left=16, right=16, top=12, bottom=8),
                        content=chat_column,
                    ),

                    # Quick reply chips (buyer only)
                    ft.Container(
                        content=ft.Row(
                            scroll=ft.ScrollMode.AUTO,
                            spacing=8,
                            controls=[
                                ft.Container(
                                    content=ft.Text(q, size=11, color="green700"),
                                    bgcolor="#e8f5e9", border_radius=16,
                                    padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                                    on_click=lambda e, q=q: (
                                        setattr(msg_field, "value", q),
                                        page.update()
                                    ),
                                    ink=True,
                                )
                                for q in (
                                    ["Is this available?", "What's the minimum order?",
                                     "Can you deliver?", "Is price negotiable?"]
                                    if is_buyer else
                                    ["Yes, still available", "Minimum 50kg",
                                     "Delivery within 50km", "Price is fixed"]
                                )
                            ],
                        ),
                        bgcolor="white",
                        padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                    ) if True else ft.Container(),

                    # Message input
                    ft.Container(
                        content=ft.Row(spacing=8, controls=[
                            msg_field,
                            ft.IconButton(
                                icon=ft.Icons.SEND_ROUNDED,
                                icon_color="green700", icon_size=22,
                                on_click=on_send,
                            ),
                        ]),
                        bgcolor="white",
                        padding=ft.Padding(left=12, right=8, top=8, bottom=8),
                        shadow=ft.BoxShadow(spread_radius=0, blur_radius=8,
                            color=ft.Colors.with_opacity(0.08, "green900")),
                    ),
                ]),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # SOIL pH ESTIMATOR SCREEN
    # ──────────────────────────────────────────────────────
    def show_ph_estimator(email=""):
        # BACKEND PLACEHOLDER: Replace lat/lon with page.get_location() result
        # BACKEND PLACEHOLDER: Call ISRIC SoilGrids API:
        #   GET https://rest.isric.org/soilgrids/v2.0/properties/query
        #       ?lon={lon}&lat={lat}&property=phh2o&depth=0-5cm&depth=5-15cm
        # BACKEND PLACEHOLDER: Parse response and populate ph_value, suitability, advice

        selected_crop = {"value": "Maize"}
        ph_result     = {"value": None}

        crops = ["Maize", "Wheat", "Rice", "Soybean", "Cotton", "Tomato", "Cassava", "Sorghum"]

        # Optimal pH ranges per crop (used for suitability logic)
        ph_ranges = {
            "Maize":   (5.8, 7.0), "Wheat":   (6.0, 7.5),
            "Rice":    (5.5, 6.5), "Soybean": (6.0, 7.0),
            "Cotton":  (5.8, 8.0), "Tomato":  (5.5, 7.0),
            "Cassava": (5.0, 6.5), "Sorghum": (5.5, 7.5),
        }

        ph_display   = ft.Text("--", size=48, weight="bold", color="green800")
        ph_label     = ft.Text("Tap 'Estimate pH' to analyse your location",
                           size=13, color="grey500", text_align=ft.TextAlign.CENTER)
        suit_badge   = ft.Container(visible=False)
        advice_col   = ft.Column(visible=False, spacing=8)

        lat_field = ft.TextField(
            label="Latitude",  hint_text="e.g. 6.5244",
            prefix_icon=ft.Icons.MY_LOCATION,
            width=148, border_radius=12, border_color="green700",
            focused_border_color="green900", bgcolor="white",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        lon_field = ft.TextField(
            label="Longitude", hint_text="e.g. 3.3792",
            prefix_icon=ft.Icons.EXPLORE,
            width=148, border_radius=12, border_color="green700",
            focused_border_color="green900", bgcolor="white",
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        def make_crop_chip(c):
            is_sel = c == selected_crop["value"]
            def on_tap(e, crop=c):
                selected_crop["value"] = crop
                show_ph_estimator(email)
            return ft.Container(
                content=ft.Text(c, size=12,
                    color="white" if is_sel else "green700", weight="bold" if is_sel else "normal"),
                bgcolor="green700" if is_sel else "white",
                border_radius=20,
                padding=ft.Padding(left=14, right=14, top=7, bottom=7),
                on_click=on_tap, ink=True,
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=4,
                    color=ft.Colors.with_opacity(0.08, "green900")),
            )

        def on_estimate(e):
            # BACKEND PLACEHOLDER: Replace this block with real ISRIC API call
            # For now simulate a result using placeholder value
            if not lat_field.value or not lon_field.value:
                ph_label.value  = "Please enter your coordinates first"
                ph_label.color  = "red"
                page.update()
                return

            # Placeholder simulated pH value — replace with API response
            simulated_ph = 6.2
            ph_result["value"] = simulated_ph
            ph_display.value = str(simulated_ph)

            lo, hi = ph_ranges.get(selected_crop["value"], (6.0, 7.0))
            if lo <= simulated_ph <= hi:
                suit_color, suit_text, suit_icon = "green600", "Suitable", ft.Icons.CHECK_CIRCLE
                advice_text = (
                    f"Your soil pH of {simulated_ph} is within the optimal range "
                    f"({lo}–{hi}) for {selected_crop['value']}. "
                    f"No corrective action needed. Proceed with standard fertilizer recommendations."
                )
            elif simulated_ph < lo:
                suit_color, suit_text, suit_icon = "orange700", "Too Acidic", ft.Icons.WARNING_ROUNDED
                advice_text = (
                    f"Your soil pH of {simulated_ph} is below the optimal range "
                    f"({lo}–{hi}) for {selected_crop['value']}. "
                    f"Apply agricultural lime (calcium carbonate) to raise pH. "
                    f"Recommended: 1–2 tonnes/ha depending on soil texture."
                )
            else:
                suit_color, suit_text, suit_icon = "blue700", "Too Alkaline", ft.Icons.INFO_ROUNDED
                advice_text = (
                    f"Your soil pH of {simulated_ph} is above the optimal range "
                    f"({lo}–{hi}) for {selected_crop['value']}. "
                    f"Apply elemental sulfur to lower pH gradually. "
                    f"Recommended: 0.5–1 tonne/ha. Retest after 3 months."
                )

            ph_display.color = suit_color
            ph_label.value   = f"Soil pH at your location for {selected_crop['value']}"
            ph_label.color   = "grey600"

            suit_badge.content = ft.Row(spacing=8, controls=[
                ft.Icon(suit_icon, color="white", size=16),
                ft.Text(suit_text, size=13, color="white", weight="bold"),
            ])
            suit_badge.bgcolor  = suit_color
            suit_badge.border_radius = 12
            suit_badge.padding  = ft.Padding(left=14, right=14, top=8, bottom=8)
            suit_badge.visible  = True

            advice_col.controls = [
                ft.Text("AI Recommendation", size=14, weight="bold", color="green900"),
                ft.Divider(color="green100"),
                ft.Text(advice_text, size=13, color="grey700"),
                ft.Container(height=4),
                # BACKEND PLACEHOLDER: Depth breakdown from SoilGrids
                ft.Row(spacing=0, controls=[
                    ft.Container(
                        content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=3, controls=[
                                ft.Text("0–5 cm", size=10, color="grey500"),
                                ft.Text(str(simulated_ph), size=16,
                                    weight="bold", color=suit_color),
                            ]),
                        expand=True, bgcolor="#f9f9f9", border_radius=10, padding=10,
                    ),
                    ft.Container(width=8),
                    ft.Container(
                        content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=3, controls=[
                                ft.Text("5–15 cm", size=10, color="grey500"),
                                ft.Text("--", size=16, weight="bold", color="grey400"),
                            ]),
                        expand=True, bgcolor="#f9f9f9", border_radius=10, padding=10,
                    ),
                    ft.Container(width=8),
                    ft.Container(
                        content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=3, controls=[
                                ft.Text("15–30 cm", size=10, color="grey500"),
                                ft.Text("--", size=16, weight="bold", color="grey400"),
                            ]),
                        expand=True, bgcolor="#f9f9f9", border_radius=10, padding=10,
                    ),
                ]),
            ]
            advice_col.visible = True
            page.update()

        switch([
            appbar("Soil pH Estimator", lambda e: show_home(email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=16, bottom=24),
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO, spacing=16,
                    controls=[

                        # Map placeholder
                        ft.Container(
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=10,
                                controls=[
                                    ft.Icon(ft.Icons.MAP, color="green700", size=48),
                                    ft.Text("Interactive Map", size=15,
                                        weight="bold", color="green900"),
                                    ft.Text(
                                        "Tap your farm location on the map\nto auto-fill coordinates",
                                        size=12, color="grey500",
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                    # BACKEND PLACEHOLDER: Replace with flet_map or
                                    # WebView + Leaflet.js showing OpenStreetMap tiles
                                    # with soil pH colour overlay from SoilGrids WMS
                                    ft.Container(
                                        content=ft.Text(
                                            "[ Map loads here — OpenStreetMap + SoilGrids overlay ]",
                                            size=11, color="grey400",
                                            text_align=ft.TextAlign.CENTER,
                                        ),
                                        bgcolor="#e8f5e9", border_radius=10,
                                        padding=ft.Padding(left=16, right=16, top=10, bottom=10),
                                    ),
                                ],
                            ),
                            bgcolor="white", border_radius=20, padding=20, height=200,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10,
                                color=ft.Colors.with_opacity(0.08, "green900")),
                        ),

                        # Coordinate entry
                        card(ft.Column(spacing=14, controls=[
                            ft.Text("Enter Coordinates", size=14,
                                weight="bold", color="green900"),
                            ft.Row(spacing=8, controls=[lat_field, lon_field]),
                            ft.Container(
                                content=ft.Row(spacing=8, controls=[
                                    ft.Icon(ft.Icons.MY_LOCATION, color="white", size=16),
                                    ft.Text("Use My Location", size=13,
                                        color="white", weight="bold"),
                                ], alignment=ft.MainAxisAlignment.CENTER),
                                bgcolor="green700", border_radius=12,
                                padding=ft.Padding(left=16, right=16, top=10, bottom=10),
                                on_click=lambda e: None, ink=True,
                                # BACKEND PLACEHOLDER: Call page.get_location()
                                # and populate lat_field/lon_field
                            ),
                        ])),

                        # Crop selector
                        card(ft.Column(spacing=12, controls=[
                            ft.Text("Select Your Crop", size=14,
                                weight="bold", color="green900"),
                            ft.Row(wrap=True, spacing=8,
                                controls=[make_crop_chip(c) for c in crops]),
                        ])),

                        # Estimate button
                        green_btn("Estimate Soil pH", on_estimate, width=340),

                        # pH result
                        card(ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10,
                            controls=[
                                ft.Text("Soil pH", size=13, color="grey500"),
                                ph_display,
                                ph_label,
                                suit_badge,
                            ],
                        )),

                        # Advice card
                        card(advice_col),
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # NEW FORUM POST SCREEN
    # ──────────────────────────────────────────────────────
    def show_new_post(crop_name, email=""):
        # BACKEND PLACEHOLDER: On submit, INSERT into Supabase `forum_posts` table:
        #   { user_id, crop_channel, text, photo_url (if attached), created_at }
        # BACKEND PLACEHOLDER: Check today's photo count for user before allowing upload
        #   SELECT count(*) FROM forum_posts WHERE user_id=? AND DATE(created_at)=today
        #   AND photo_url IS NOT NULL

        photos_today  = {"count": 0}  # BACKEND PLACEHOLDER: fetch from Supabase
        attached_photo = {"path": None}

        post_field = ft.TextField(
            label=f"Share something with #{crop_name.lower()}-farmers...",
            multiline=True, min_lines=4, max_lines=8,
            border_radius=15, border_color="green700",
            focused_border_color="green900", bgcolor="white",
        )
        photo_status = ft.Text("", size=12, color="green600")
        status_msg   = ft.Text("", size=13, color="red", text_align=ft.TextAlign.CENTER)

        def on_attach_photo(e):
            if photos_today["count"] >= 2:
                photo_status.value = "Daily photo limit reached (2/2)"
                photo_status.color = "red"
                page.update()
                return
            # BACKEND PLACEHOLDER: Open native camera via platform channel
            # Image must be native iOS/Android camera format — enforce MIME type check
            # on upload: only image/jpeg and image/heic accepted
            attached_photo["path"] = "camera_photo_placeholder.jpg"
            photos_today["count"] += 1
            remaining = 2 - photos_today["count"]
            photo_status.value = f"Photo attached  ({remaining} photo{'s' if remaining != 1 else ''} remaining today)"
            photo_status.color = "green600"
            page.update()

        def on_submit(e):
            if not post_field.value or not post_field.value.strip():
                status_msg.value = "Please write something before posting"
                page.update()
                return
            # BACKEND PLACEHOLDER: Upload photo to Supabase Storage if attached
            # BACKEND PLACEHOLDER: INSERT post to forum_posts table
            # BACKEND PLACEHOLDER: Navigate back and refresh channel feed
            status_msg.value = "Post published!"
            status_msg.color = "green700"
            page.update()

        switch([
            appbar(f"New Post · #{crop_name.lower()}-farmers",
                lambda e: show_forum_channel(crop_name, email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=20, bottom=24),
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO, spacing=16,
                    controls=[

                        # User header
                        ft.Row(spacing=12, controls=[
                            ft.Container(
                                content=ft.Text(
                                    email[0].upper() if email else "F",
                                    size=16, color="white", weight="bold"),
                                bgcolor="green700", border_radius=20,
                                width=40, height=40, alignment=ft.Alignment(0, 0),
                            ),
                            ft.Column(spacing=2, controls=[
                                ft.Text(
                                    email.split("@")[0].capitalize() if email else "Farmer",
                                    size=14, weight="bold", color="green900"),
                                ft.Row(spacing=4, controls=[
                                    ft.Icon(ft.Icons.LOCK_OPEN, color="green600", size=12),
                                    ft.Text(f"Posting to #{crop_name.lower()}-farmers",
                                        size=11, color="green600"),
                                ]),
                            ]),
                        ]),

                        # Post text field
                        card(ft.Column(spacing=10, controls=[
                            post_field,
                            ft.Divider(color="green100"),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Container(
                                        content=ft.Row(spacing=8, controls=[
                                            ft.Icon(ft.Icons.ADD_PHOTO_ALTERNATE_OUTLINED,
                                                color="green700", size=20),
                                            ft.Text("Attach Photo", size=13,
                                                color="green700"),
                                        ]),
                                        on_click=on_attach_photo, ink=True,
                                        border_radius=8,
                                        padding=ft.Padding(left=8, right=8, top=6, bottom=6),
                                    ),
                                    ft.Text(
                                        f"{2 - photos_today['count']}/2 photos left today",
                                        size=11, color="grey400"),
                                ],
                            ),
                            photo_status,
                        ])),

                        # Rules card
                        ft.Container(
                            content=ft.Column(spacing=6, controls=[
                                ft.Row(spacing=6, controls=[
                                    ft.Icon(ft.Icons.INFO_OUTLINE,
                                        color="green700", size=15),
                                    ft.Text("Posting Rules", size=12,
                                        weight="bold", color="green900"),
                                ]),
                                ft.Text(
                                    "• Maximum 2 photos per day\n"
                                    "• Photos must be taken from your device camera\n"
                                    "• Screenshots and downloaded images are rejected\n"
                                    "• Keep posts relevant to your crop channel",
                                    size=11, color="grey600",
                                ),
                            ]),
                            bgcolor="#e8f5e9", border_radius=14, padding=14,
                        ),

                        green_btn("Publish Post", on_submit, width=340),
                        status_msg,
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # LIST YOUR CROP SCREEN
    # ──────────────────────────────────────────────────────
    def show_list_crop(email=""):
        # BACKEND PLACEHOLDER: On submit, INSERT into Supabase `marketplace_listings` table:
        #   { user_id, crop, quantity_kg, price_per_kg, location, description,
        #     contact_number, verified (false by default), created_at }
        # BACKEND PLACEHOLDER: After insert, navigate back to marketplace and refresh listings

        crop_field = ft.TextField(
            label="Crop Name", hint_text="e.g. Maize, Rice, Wheat",
            prefix_icon=ft.Icons.GRASS,
            border_radius=15, border_color="green700",
            focused_border_color="green900", bgcolor="white",
        )
        qty_field = ft.TextField(
            label="Quantity Available (kg)", hint_text="e.g. 500",
            prefix_icon=ft.Icons.SCALE,
            border_radius=15, border_color="green700",
            focused_border_color="green900", bgcolor="white",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        price_field = ft.TextField(
            label="Price per kg (USD)", hint_text="e.g. 0.25",
            prefix_icon=ft.Icons.ATTACH_MONEY,
            border_radius=15, border_color="green700",
            focused_border_color="green900", bgcolor="white",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        location_field = ft.TextField(
            label="Your Location", hint_text="e.g. Accra, Ghana",
            prefix_icon=ft.Icons.LOCATION_ON_OUTLINED,
            border_radius=15, border_color="green700",
            focused_border_color="green900", bgcolor="white",
        )
        phone_field = ft.TextField(
            label="Contact Number", hint_text="e.g. +234 800 000 0000",
            prefix_icon=ft.Icons.PHONE_OUTLINED,
            border_radius=15, border_color="green700",
            focused_border_color="green900", bgcolor="white",
            keyboard_type=ft.KeyboardType.PHONE,
        )
        desc_field = ft.TextField(
            label="Description (optional)",
            hint_text="Harvested recently, good quality...",
            multiline=True, min_lines=3, max_lines=5,
            border_radius=15, border_color="green700",
            focused_border_color="green900", bgcolor="white",
        )
        status_msg = ft.Text("", size=13, text_align=ft.TextAlign.CENTER)

        def on_submit(e):
            if not crop_field.value or not qty_field.value or \
               not price_field.value or not location_field.value or \
               not phone_field.value:
                status_msg.value  = "Please fill in all required fields"
                status_msg.color  = "red"
                page.update()
                return
            # BACKEND PLACEHOLDER: Validate price and qty are valid numbers
            # BACKEND PLACEHOLDER: INSERT listing to Supabase marketplace_listings table
            # BACKEND PLACEHOLDER: Navigate back to marketplace
            status_msg.value = "Listing published successfully!"
            status_msg.color = "green700"
            page.update()

        switch([
            appbar("List Your Crop", lambda e: show_marketplace(email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=20, bottom=24),
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO, spacing=16,
                    controls=[

                        # Header
                        ft.Container(
                            content=ft.Row(spacing=12, controls=[
                                ft.Container(
                                    content=ft.Icon(ft.Icons.STOREFRONT,
                                        color="white", size=26),
                                    bgcolor="green700", border_radius=14, padding=12,
                                ),
                                ft.Column(spacing=2, controls=[
                                    ft.Text("New Listing", size=16,
                                        weight="bold", color="green900"),
                                    ft.Text("Buyers will be able to contact you directly",
                                        size=11, color="grey500"),
                                ]),
                            ]),
                            bgcolor="white", border_radius=16, padding=14,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=8,
                                color=ft.Colors.with_opacity(0.06, "green900")),
                        ),

                        # Form
                        card(ft.Column(spacing=14, controls=[
                            ft.Text("Crop Details", size=14,
                                weight="bold", color="green900"),
                            ft.Divider(color="green100"),
                            crop_field, qty_field, price_field,
                        ])),

                        card(ft.Column(spacing=14, controls=[
                            ft.Text("Contact & Location", size=14,
                                weight="bold", color="green900"),
                            ft.Divider(color="green100"),
                            location_field, phone_field,
                        ])),

                        card(ft.Column(spacing=14, controls=[
                            ft.Text("Additional Info", size=14,
                                weight="bold", color="green900"),
                            ft.Divider(color="green100"),
                            desc_field,
                        ])),

                        green_btn("Publish Listing", on_submit, width=340),
                        status_msg,
                        ft.Container(height=10),
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # PROFILE PAGE (full page — not just sidebar menu)
    # ──────────────────────────────────────────────────────
    def show_profile(email=""):
        # BACKEND PLACEHOLDER: Fetch user profile from Supabase `users` table:
        #   SELECT full_name, avatar_url, location, region, created_at FROM users
        #   WHERE id = current_user_id
        # BACKEND PLACEHOLDER: Fetch user's analysis count:
        #   SELECT count(*) FROM analyses WHERE user_id = current_user_id
        # BACKEND PLACEHOLDER: Fetch user's forum post count:
        #   SELECT count(*) FROM forum_posts WHERE user_id = current_user_id
        # BACKEND PLACEHOLDER: Fetch user's active marketplace listings:
        #   SELECT count(*) FROM marketplace_listings WHERE user_id = current_user_id

        username  = email.split("@")[0].capitalize() if email else "Farmer"
        user_email = email or "farmer@soilco.app"

        def stat_box(value, label):
            return ft.Container(
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=3,
                    controls=[
                        ft.Text(value, size=22, weight="bold", color="green800"),
                        ft.Text(label, size=10, color="grey500"),
                    ],
                ),
                expand=True, bgcolor="white", border_radius=14, padding=14,
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=6,
                    color=ft.Colors.with_opacity(0.06, "green900")),
            )

        def setting_row(icon, label, on_tap):
            return ft.Container(
                content=ft.Row(spacing=16, controls=[
                    ft.Icon(icon, color="green700", size=20),
                    ft.Text(label, size=14, color="grey900", expand=True),
                    ft.Icon(ft.Icons.ARROW_FORWARD_IOS, color="grey300", size=13),
                ]),
                padding=ft.Padding(left=16, right=16, top=14, bottom=14),
                on_click=on_tap, ink=True,
            )

        switch([
            appbar("Profile", actions=[
                ft.IconButton(
                    icon=ft.Icons.EDIT_OUTLINED, icon_color="white",
                    on_click=lambda e: show_edit_profile(email),
                    tooltip="Edit Profile",
                )
            ]),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO, spacing=0,
                    controls=[

                        # Profile hero
                        ft.Container(
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=10,
                                controls=[
                                    ft.Stack(controls=[
                                        ft.Container(
                                            content=ft.Icon(ft.Icons.PERSON,
                                                color="white", size=52),
                                            bgcolor="green700", border_radius=50,
                                            width=100, height=100,
                                            alignment=ft.Alignment(0, 0),
                                            # BACKEND PLACEHOLDER: Replace with
                                            # ft.Image(src=avatar_url) when Supabase
                                            # Storage is connected
                                        ),
                                        ft.Container(
                                            content=ft.Icon(ft.Icons.CAMERA_ALT,
                                                color="white", size=14),
                                            bgcolor="green900", border_radius=12,
                                            padding=5, right=0, bottom=0,
                                            on_click=lambda e: show_profile_picture(email),
                                            ink=True,
                                        ),
                                    ]),
                                    ft.Text(username, size=20,
                                        weight="bold", color="green900"),
                                    ft.Text(user_email, size=12, color="grey600"),
                                    ft.Row(spacing=6,
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        controls=[
                                            ft.Icon(ft.Icons.LOCATION_ON,
                                                color="green600", size=14),
                                            ft.Text("Location not set",
                                                size=12, color="grey500"),
                                            # BACKEND PLACEHOLDER: Replace with
                                            # user.location from Supabase
                                        ]),
                                ],
                            ),
                            bgcolor="white",
                            padding=ft.Padding(top=28, bottom=24, left=0, right=0),
                            width=page.window.width,
                        ),

                        # Stats row
                        ft.Container(
                            content=ft.Row(spacing=10, controls=[
                                stat_box("0", "Analyses"),
                                # BACKEND PLACEHOLDER: Replace "0" with real counts
                                stat_box("0", "Forum Posts"),
                                stat_box("0", "Listings"),
                            ]),
                            padding=ft.Padding(left=16, right=16, top=14, bottom=14),
                        ),

                        # Recent activity
                        ft.Container(
                            content=ft.Text("Recent Activity", size=13,
                                color="grey500", weight="bold"),
                            padding=ft.Padding(left=16, right=0, top=4, bottom=6),
                        ),
                        ft.Container(
                            content=ft.Column(spacing=0, controls=[
                                ft.Container(
                                    content=ft.Row(spacing=12,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Container(
                                                content=ft.Icon(ft.Icons.GRASS,
                                                    color="white", size=16),
                                                bgcolor="green700", border_radius=10,
                                                padding=8,
                                            ),
                                            ft.Column(spacing=2, controls=[
                                                ft.Text("Analysed Maize",
                                                    size=13, color="green900"),
                                                ft.Text("Feb 28 · pH 6.5 · Optimal",
                                                    size=11, color="grey500"),
                                                # BACKEND PLACEHOLDER: Replace with
                                                # latest analyses from Supabase
                                            ]),
                                        ]),
                                    padding=ft.Padding(left=16, right=16,
                                        top=12, bottom=12),
                                ),
                                ft.Divider(color="green100", height=1),
                                ft.Container(
                                    content=ft.Row(spacing=12,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Container(
                                                content=ft.Icon(ft.Icons.FORUM,
                                                    color="white", size=16),
                                                bgcolor="green600", border_radius=10,
                                                padding=8,
                                            ),
                                            ft.Column(spacing=2, controls=[
                                                ft.Text("Posted in #rice-farmers",
                                                    size=13, color="green900"),
                                                ft.Text("5h ago",
                                                    size=11, color="grey500"),
                                            ]),
                                        ]),
                                    padding=ft.Padding(left=16, right=16,
                                        top=12, bottom=12),
                                ),
                            ]),
                            bgcolor="white", border_radius=16,
                            margin=ft.Margin(left=16, right=16, top=0, bottom=14),
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=8,
                                color=ft.Colors.with_opacity(0.06, "green900")),
                        ),

                        # Settings
                        ft.Container(
                            content=ft.Text("Account Settings", size=13,
                                color="grey500", weight="bold"),
                            padding=ft.Padding(left=16, right=0, top=4, bottom=6),
                        ),
                        ft.Container(
                            content=ft.Column(spacing=0, controls=[
                                setting_row(ft.Icons.PERSON_OUTLINE, "Edit Profile",
                                    lambda e: show_edit_profile(email)),
                                ft.Divider(color="green100", height=1),
                                setting_row(ft.Icons.IMAGE_OUTLINED, "Profile Picture",
                                    lambda e: show_profile_picture(email)),
                                ft.Divider(color="green100", height=1),
                                setting_row(ft.Icons.LOCK_OUTLINE, "Change Password",
                                    lambda e: show_change_password(email)),
                                ft.Divider(color="green100", height=1),
                                setting_row(ft.Icons.LOCATION_ON_OUTLINED, "Change Location",
                                    lambda e: show_change_location(email)),
                                ft.Divider(color="green100", height=1),
                                setting_row(ft.Icons.NOTIFICATIONS, "Notifications",
                                    lambda e: show_notifications(email)),
                                ft.Divider(color="green100", height=1),
                                setting_row(ft.Icons.HELP_OUTLINE, "Help & FAQ",
                                    lambda e: show_help_faq(email)),
                            ]),
                            bgcolor="white", border_radius=16,
                            margin=ft.Margin(left=16, right=16, top=0, bottom=14),
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=8,
                                color=ft.Colors.with_opacity(0.06, "green900")),
                        ),

                        # Logout
                        ft.Container(
                            content=ft.Row(spacing=12,
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(ft.Icons.LOGOUT, color="red600", size=20),
                                    ft.Text("Logout", size=14, color="red600",
                                        weight="bold"),
                                ]),
                            bgcolor="white", border_radius=16,
                            margin=ft.Margin(left=16, right=16, top=0, bottom=80),
                            padding=ft.Padding(left=20, right=20, top=14, bottom=14),
                            on_click=lambda e: show_login(), ink=True,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=8,
                                color=ft.Colors.with_opacity(0.06, "green900")),
                        ),
                    ],
                ),
            ),
            nav_bar("Profile", email),
        ])

    # ──────────────────────────────────────────────────────
    # START
    # ──────────────────────────────────────────────────────
    show_splash()


if __name__ == "__main__":
    ft.run(main)