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
            {
                "icon": ft.Icons.GRASS_ROUNDED,
                "title": "Welcome to Soilco",
                "subtitle": "Your smart soil analysis companion for better farming decisions.",
                "color": "green700",
            },
            {
                "icon": ft.Icons.WATER_DROP,
                "title": "Smart Irrigation",
                "subtitle": "Get AI-powered daily irrigation recommendations based on your crop and local weather.",
                "color": "blue700",
            },
            {
                "icon": ft.Icons.AUTO_AWESOME,
                "title": "AI Crop Analysis",
                "subtitle": "Enter any crop and receive instant fertilizer, soil type, and growth time analysis.",
                "color": "orange700",
            },
        ]
        s = slides[page_idx]
        dots = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Container(
                    width=10 if i == page_idx else 6,
                    height=10 if i == page_idx else 6,
                    border_radius=5,
                    bgcolor="green700" if i == page_idx else "green200",
                )
                for i in range(len(slides))
            ],
        )
        is_last = page_idx == len(slides) - 1

        def on_next(e):
            if is_last:
                mark_onboarding_seen()
                show_login()
            else:
                show_onboarding(page_idx + 1)

        switch([
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=0,
                    controls=[
                        ft.Container(
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=24,
                                controls=[
                                    ft.Container(
                                        content=ft.Icon(s["icon"], color="white", size=72),
                                        bgcolor=s["color"],
                                        border_radius=40,
                                        padding=32,
                                    ),
                                    ft.Text(s["title"], size=26, weight="bold", color="green900",
                                            text_align=ft.TextAlign.CENTER),
                                    ft.Text(s["subtitle"], size=15, color="grey600",
                                            text_align=ft.TextAlign.CENTER),
                                ],
                            ),
                            expand=True,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Container(
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=20,
                                controls=[
                                    dots,
                                    green_btn("Get Started" if is_last else "Next", on_next, height=50),
                                    ft.TextButton(
                                        "Skip" if not is_last else "",
                                        on_click=lambda e: (mark_onboarding_seen(), show_login()),
                                        style=ft.ButtonStyle(color="grey500"),
                                    ) if not is_last else ft.Container(height=10),
                                ],
                            ),
                            padding=ft.Padding(left=30, right=30, top=0, bottom=40),
                        ),
                    ],
                ),
            )
        ])

    # ──────────────────────────────────────────────────────
    # LOGIN SCREEN
    # ──────────────────────────────────────────────────────
    def show_login():
        email_field = ft.TextField(
            label="Email", prefix_icon=ft.Icons.EMAIL_OUTLINED,
            width=300, border_radius=15, border_color="green700",
            focused_border_color="green900", keyboard_type=ft.KeyboardType.EMAIL, bgcolor="white",
        )
        password_field = ft.TextField(
            label="Password", prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True, can_reveal_password=True, width=300,
            border_radius=15, border_color="green700", focused_border_color="green900", bgcolor="white",
        )
        status = ft.Text("", size=14)

        def on_login(e):
            if not email_field.value or not password_field.value:
                status.value = "Please fill in all fields"
                status.color = "red"
                page.update()
            else:
                show_home(email_field.value)

        switch([
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO, spacing=0,
                    controls=[
                        ft.Container(content=logo(50), padding=ft.Padding(top=60, bottom=30, left=0, right=0)),
                        card(
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16,
                                controls=[
                                    ft.Text("Welcome Back", size=22, weight="bold", color="green900"),
                                    email_field, password_field,
                                    ft.Container(
                                        content=ft.TextButton("Forgot Password?",
                                            on_click=lambda e: show_forgot(),
                                            style=ft.ButtonStyle(color="green700")),
                                        alignment=ft.Alignment(1, 0), width=300,
                                    ),
                                    green_btn("Login", on_login),
                                    status,
                                    ft.Divider(color="green200"),
                                    ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
                                        ft.Text("Don't have an account?", color="grey700"),
                                        ft.TextButton("Sign Up", on_click=lambda e: show_signup(),
                                            style=ft.ButtonStyle(color="green700")),
                                    ]),
                                ],
                            ),
                            radius=25,
                            margin=ft.Margin(left=20, right=20, top=0, bottom=40),
                        ),
                    ],
                ),
            )
        ])

    # ──────────────────────────────────────────────────────
    # SIGN UP SCREEN
    # ──────────────────────────────────────────────────────
    def show_signup():
        name_field = ft.TextField(label="Full Name", prefix_icon=ft.Icons.PERSON_OUTLINE,
            width=300, border_radius=15, border_color="green700", focused_border_color="green900", bgcolor="white")
        email_field = ft.TextField(label="Email", prefix_icon=ft.Icons.EMAIL_OUTLINED,
            width=300, border_radius=15, border_color="green700",
            focused_border_color="green900", keyboard_type=ft.KeyboardType.EMAIL, bgcolor="white")
        password_field = ft.TextField(label="Password", prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True, can_reveal_password=True, width=300,
            border_radius=15, border_color="green700", focused_border_color="green900", bgcolor="white")
        status = ft.Text("", size=14)

        def on_register(e):
            if not name_field.value or not email_field.value or not password_field.value:
                status.value = "Please fill in all fields"
                status.color = "red"
                page.update()
            else:
                show_home(email_field.value)

        switch([
            appbar("Sign Up", lambda e: show_login()),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO, spacing=16,
                    controls=[
                        ft.Container(height=10), logo(40),
                        card(
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16,
                                controls=[
                                    ft.Text("Create Account", size=20, weight="bold", color="green900"),
                                    name_field, email_field, password_field,
                                    green_btn("Create Account", on_register),
                                    status,
                                    ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
                                        ft.Text("Already have an account?", color="grey700"),
                                        ft.TextButton("Login", on_click=lambda e: show_login(),
                                            style=ft.ButtonStyle(color="green700")),
                                    ]),
                                ],
                            ),
                            radius=25,
                            margin=ft.Margin(left=20, right=20, top=0, bottom=30),
                        ),
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # FORGOT PASSWORD SCREEN
    # ──────────────────────────────────────────────────────
    def show_forgot():
        email_field = ft.TextField(label="Enter your email", prefix_icon=ft.Icons.EMAIL_OUTLINED,
            width=300, border_radius=15, border_color="green700",
            focused_border_color="green900", keyboard_type=ft.KeyboardType.EMAIL, bgcolor="white")
        status = ft.Text("", size=14, text_align=ft.TextAlign.CENTER)

        def on_reset(e):
            if not email_field.value:
                status.value = "Please enter your email"
                status.color = "red"
            else:
                status.value = f"Reset link sent to {email_field.value}"
                status.color = "green700"
            page.update()

        switch([
            appbar("Forgot Password", lambda e: show_login()),
            ft.Container(
                expand=True, bgcolor="#f0f7f0", padding=20,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER, spacing=20,
                    controls=[
                        logo(40),
                        ft.Icon(ft.Icons.LOCK_RESET, color="green700", size=50),
                        ft.Text("Reset Password", size=22, weight="bold", color="green800"),
                        ft.Text("Enter your email and we will send you a reset link",
                            size=13, color="grey600", text_align=ft.TextAlign.CENTER),
                        card(
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16,
                                controls=[email_field, green_btn("Send Reset Link", on_reset), status],
                            ),
                            radius=25,
                            margin=ft.Margin(left=20, right=20, top=0, bottom=20),
                        ),
                        ft.TextButton("Back to Login", on_click=lambda e: show_login(),
                            style=ft.ButtonStyle(color="green700")),
                    ],
                ),
            ),
        ])

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

                        # Weather widget
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
                                                ft.Row(spacing=8, controls=[
                                                    ft.Row(spacing=2, controls=[
                                                        ft.Icon(ft.Icons.WATER_DROP_OUTLINED, color="#c8e6c9", size=12),
                                                        ft.Text("Hum: --%", size=11, color="#c8e6c9"),
                                                    ]),
                                                ]),
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

                        # Crop analysis card
                        card(ft.Column(spacing=12, controls=[
                            ft.Text("Crop Analysis", size=16, weight="bold", color="green900"),
                            crop_field,
                            ft.Button("Analyze", on_click=on_analyze, width=300, height=45,
                                style=ft.ButtonStyle(bgcolor="green700", color="white",
                                    shape=ft.RoundedRectangleBorder(radius=12),
                                    text_style=ft.TextStyle(size=15, weight="bold"))),
                            status,
                        ])),

                        # Market prices
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

                        # Previous analyses
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

                        # Community section
                        ft.Text("Community", size=16, weight="bold", color="green900"),
                        ft.Row(spacing=12, controls=[
                            ft.Container(
                                content=ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=10,
                                    controls=[
                                        ft.Container(
                                            content=ft.Icon(ft.Icons.FORUM_OUTLINED, color="white", size=28),
                                            bgcolor="green700", border_radius=16, padding=14,
                                        ),
                                        ft.Text("Crop Forum", size=13, weight="bold", color="green900"),
                                        ft.Text("Chat with farmers\ngrowing your crop", size=10,
                                            color="grey500", text_align=ft.TextAlign.CENTER),
                                        ft.Container(
                                            content=ft.Text("Open", size=11, color="white", weight="bold"),
                                            bgcolor="green700", border_radius=10,
                                            padding=ft.Padding(left=16, right=16, top=6, bottom=6),
                                        ),
                                    ],
                                ),
                                bgcolor="white", border_radius=20, padding=16,
                                expand=True, on_click=lambda e: show_forum(email), ink=True,
                                shadow=ft.BoxShadow(spread_radius=1, blur_radius=10,
                                    color=ft.Colors.with_opacity(0.08, "green900")),
                            ),
                            ft.Container(
                                content=ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=10,
                                    controls=[
                                        ft.Container(
                                            content=ft.Icon(ft.Icons.STOREFRONT_OUTLINED, color="white", size=28),
                                            bgcolor="green700", border_radius=16, padding=14,
                                        ),
                                        ft.Text("Marketplace", size=13, weight="bold", color="green900"),
                                        ft.Text("Buy & sell crops\ndirectly with farmers", size=10,
                                            color="grey500", text_align=ft.TextAlign.CENTER),
                                        ft.Container(
                                            content=ft.Text("Open", size=11, color="white", weight="bold"),
                                            bgcolor="green700", border_radius=10,
                                            padding=ft.Padding(left=16, right=16, top=6, bottom=6),
                                        ),
                                    ],
                                ),
                                bgcolor="white", border_radius=20, padding=16,
                                expand=True, on_click=lambda e: show_marketplace(email), ink=True,
                                shadow=ft.BoxShadow(spread_radius=1, blur_radius=10,
                                    color=ft.Colors.with_opacity(0.08, "green900")),
                            ),
                        ]),
                        ft.Container(height=8),
                    ],
                ),
            ),
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
        irrigation_val = ft.Text("4.2 mm/day", size=20, weight="bold", color="green800")
        soil_type_val = ft.Text("Loamy", size=20, weight="bold", color="green800")
        growth_val = ft.Text("12 weeks", size=20, weight="bold", color="green800")
        nitrogen_val = ft.Text("45.0 kg/ha", size=15, weight="bold", color="green700")
        phosphorus_val = ft.Text("22.5 kg/ha", size=15, weight="bold", color="green700")
        potassium_val = ft.Text("30.0 kg/ha", size=15, weight="bold", color="green700")

        def metric_card(title, value_widget, icon, color):
            return ft.Container(
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6,
                    controls=[ft.Icon(icon, color=color, size=26), ft.Text(title, size=11, color="grey600"), value_widget],
                ),
                bgcolor="white", border_radius=20, padding=16, expand=True,
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.with_opacity(0.08, "green900")),
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
                        card(ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Column(spacing=2, controls=[
                                    ft.Text("Crop", size=12, color="grey600"),
                                    ft.Text(crop_name, size=22, weight="bold", color="green900"),
                                ]),
                                ft.Container(
                                    content=ft.Text("Analyzed", size=11, color="white"),
                                    bgcolor="green600", border_radius=8,
                                    padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                                ),
                            ],
                        )),
                        ft.Row(spacing=12, controls=[
                            metric_card("Irrigation", irrigation_val, ft.Icons.WATER_DROP, "blue700"),
                            metric_card("Soil Type", soil_type_val, ft.Icons.LANDSCAPE, "brown400"),
                        ]),
                        ft.Row(spacing=12, controls=[
                            metric_card("Growth Time", growth_val, ft.Icons.SCHEDULE, "green600"),
                        ]),
                        card(ft.Column(spacing=12, controls=[
                            ft.Text("Fertilizer Recommendation", size=16, weight="bold", color="green900"),
                            ft.Divider(color="green100"),
                            fert_row("Nitrogen (N)", nitrogen_val),
                            fert_row("Phosphorus (P)", phosphorus_val),
                            fert_row("Potassium (K)", potassium_val),
                        ])),
                        ft.Container(
                            content=ft.Row(spacing=10, controls=[
                                ft.Icon(ft.Icons.WATER_DROP, color="white", size=18),
                                ft.Column(spacing=1, expand=True, controls=[
                                    ft.Text("Daily Irrigation Alert", size=14, weight="bold", color="white"),
                                    ft.Text("Tap to view today's water schedule", size=11, color="#c8e6c9"),
                                ]),
                                ft.Icon(ft.Icons.ARROW_FORWARD_IOS, color="white", size=14),
                            ]),
                            bgcolor="green700", border_radius=16, padding=16,
                            on_click=lambda e: show_daily_alert(crop_name, "4.2", email), ink=True,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.with_opacity(0.15, "green900")),
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
                            menu_item(ft.Icons.NOTIFICATIONS_OUTLINED, "Notifications", lambda e: show_notifications(email)),
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
                            margin=ft.Margin(left=16, right=16, top=4, bottom=30),
                            on_click=lambda e: show_login(), ink=True,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color=ft.Colors.with_opacity(0.06, "green900")),
                        ),
                    ],
                ),
            ),
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
                    ],
                ),
            ),
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
            appbar(f"#{crop_name.lower()}-farmers", lambda e: show_forum(email)),
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
    # MARKETPLACE SCREEN
    # ──────────────────────────────────────────────────────
    def show_marketplace(email=""):
        listings = [
            {"seller": "James K.",    "crop": "Maize",   "qty": "500 kg",  "price": "$0.22/kg", "location": "Accra, Ghana",        "verified": True},
            {"seller": "Amina S.",    "crop": "Rice",    "qty": "1,200 kg","price": "$0.40/kg", "location": "Kano, Nigeria",       "verified": True},
            {"seller": "David O.",    "crop": "Soybean", "qty": "300 kg",  "price": "$0.50/kg", "location": "Nairobi, Kenya",      "verified": False},
            {"seller": "Fatima B.",   "crop": "Wheat",   "qty": "800 kg",  "price": "$0.29/kg", "location": "Lahore, Pakistan",    "verified": True},
            {"seller": "Carlos M.",   "crop": "Cotton",  "qty": "2,000 kg","price": "$0.75/kg", "location": "Sao Paulo, Brazil",   "verified": False},
            {"seller": "Priya N.",    "crop": "Tomato",  "qty": "150 kg",  "price": "$0.35/kg", "location": "Mumbai, India",       "verified": True},
        ]

        def listing_card(l):
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
                                                ft.Text("Verified", size=9,
                                                    color="white"),
                                            ]),
                                            bgcolor="green600", border_radius=8,
                                            padding=ft.Padding(left=6, right=6,
                                                top=2, bottom=2),
                                            visible=l["verified"],
                                        ),
                                    ]),
                                    ft.Row(spacing=4, controls=[
                                        ft.Icon(ft.Icons.LOCATION_ON,
                                            color="grey400", size=12),
                                        ft.Text(l["location"], size=11,
                                            color="grey500"),
                                    ]),
                                ]),
                            ]),
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                spacing=2,
                                controls=[
                                    ft.Text(l["price"], size=14, weight="bold",
                                        color="green800"),
                                    ft.Text(l["qty"], size=11, color="grey500"),
                                ],
                            ),
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                content=ft.Row(spacing=6, controls=[
                                    ft.Icon(ft.Icons.GRASS, color="green700", size=14),
                                    ft.Text(l["crop"], size=12, color="green800",
                                        weight="bold"),
                                ]),
                                bgcolor="#e8f5e9", border_radius=8,
                                padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                            ),
                            ft.Container(
                                content=ft.Row(spacing=6, controls=[
                                    ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE,
                                        color="white", size=14),
                                    ft.Text("Contact Seller", size=12,
                                        color="white", weight="bold"),
                                ]),
                                bgcolor="green700", border_radius=10,
                                padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                                on_click=lambda e, s=l["seller"]: show_chat(s, email),
                                ink=True,
                            ),
                        ],
                    ),
                ]),
                bgcolor="white", border_radius=16, padding=14,
                margin=ft.Margin(left=0, right=0, top=0, bottom=10),
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=6,
                    color=ft.Colors.with_opacity(0.06, "green900")),
            )

        switch([
            appbar("Marketplace", lambda e: show_home(email)),
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
                                    ft.Icon(ft.Icons.STOREFRONT, color="white", size=28),
                                    ft.Column(spacing=2, controls=[
                                        ft.Text("Marketplace", size=17, weight="bold", color="white"),
                                        ft.Text("Buy and sell crops directly with farmers", size=11, color="#c8e6c9"),
                                    ]),
                                ]),
                            ]),
                            bgcolor="green700", border_radius=16, padding=16,
                            margin=ft.Margin(left=0, right=0, top=0, bottom=14),
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text("Available Listings", size=15,
                                    weight="bold", color="green900"),
                                ft.Container(
                                    content=ft.Row(spacing=6, controls=[
                                        ft.Icon(ft.Icons.ADD, color="white", size=16),
                                        ft.Text("List Crop", size=12, color="white", weight="bold"),
                                    ]),
                                    bgcolor="green700", border_radius=10,
                                    padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                                    on_click=lambda e: None, ink=True,
                                ),
                            ],
                        ),
                        ft.Container(height=10),
                        *[listing_card(l) for l in listings],
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # P2P CHAT SCREEN
    # ──────────────────────────────────────────────────────
    def show_chat(seller_name, email=""):
        username = email.split("@")[0].capitalize() if email else "You"

        messages = [
            {"sender": seller_name, "text": "Hello! Yes the maize is still available. Harvested last week.", "time": "10:32 AM"},
            {"sender": username,    "text": "Great! What is the minimum order quantity?", "time": "10:35 AM"},
            {"sender": seller_name, "text": "Minimum is 50kg. I can arrange delivery within 50km.", "time": "10:37 AM"},
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

        chat_column = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=8,
            controls=[],
        )

        def bubble(m):
            is_me = m["sender"] == username
            return ft.Row(
                alignment=ft.MainAxisAlignment.END if is_me
                    else ft.MainAxisAlignment.START,
                controls=[
                    ft.Container(
                        content=ft.Column(spacing=3, controls=[
                            ft.Text(m["sender"], size=10,
                                color="green700" if not is_me else "white70",
                                weight="bold",
                                visible=not is_me,
                            ),
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
                new_msg = {
                    "sender": username,
                    "text": msg_field.value.strip(),
                    "time": "Just now",
                }
                chat_column.controls.append(bubble(new_msg))
                msg_field.value = ""
                page.update()

        switch([
            appbar(seller_name, lambda e: show_marketplace(email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                content=ft.Column(
                    spacing=0,
                    controls=[
                        ft.Container(
                            content=ft.Row(spacing=10, controls=[
                                ft.Container(
                                    content=ft.Text(seller_name[0], size=14,
                                        color="white", weight="bold"),
                                    bgcolor="green700", border_radius=20,
                                    width=36, height=36,
                                    alignment=ft.Alignment(0, 0),
                                ),
                                ft.Column(spacing=1, controls=[
                                    ft.Text(seller_name, size=14,
                                        weight="bold", color="green900"),
                                    ft.Text("Farmer · Online", size=11,
                                        color="green600"),
                                ]),
                            ]),
                            bgcolor="white",
                            padding=ft.Padding(left=16, right=16, top=10, bottom=10),
                            shadow=ft.BoxShadow(spread_radius=0, blur_radius=4,
                                color=ft.Colors.with_opacity(0.05, "green900")),
                        ),
                        ft.Container(
                            expand=True,
                            padding=ft.Padding(left=16, right=16, top=12, bottom=8),
                            content=chat_column,
                        ),
                        ft.Container(
                            content=ft.Row(spacing=8, controls=[
                                msg_field,
                                ft.IconButton(
                                    icon=ft.Icons.SEND_ROUNDED,
                                    icon_color="green700",
                                    icon_size=22,
                                    on_click=on_send,
                                ),
                            ]),
                            bgcolor="white",
                            padding=ft.Padding(left=12, right=8, top=8, bottom=8),
                            shadow=ft.BoxShadow(spread_radius=0, blur_radius=8,
                                color=ft.Colors.with_opacity(0.08, "green900")),
                        ),
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # START
    # ──────────────────────────────────────────────────────
    show_splash()


if __name__ == "__main__":
    ft.run(main)