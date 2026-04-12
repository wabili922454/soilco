import flet as ft
import time
import threading
import os

ONBOARDING_FLAG = os.path.join(os.path.expanduser("~"), ".soilco_onboarding_seen")

CROPS = [
    "Maize", "Wheat", "Rice", "Beans", "Soybean",
    "Tomato", "Potato", "Sorghum", "Cassava", "Cotton",
    "Sunflower", "Groundnut", "Barley", "Millet", "Sugarcane",
    "Onion", "Cabbage", "Spinach", "Pepper", "Sweet Potato",
]

SOIL_TYPES = [
    "Loamy", "Sandy", "Clay", "Silty", "Peaty",
    "Chalky", "Sandy Loam", "Clay Loam", "Silt Loam", "Loamy Sand",
]

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

    # ──────────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────────
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
        # Instagram-style: Home | [+Analyze center] | Forum | Profile
        def tab_btn(label, icon, icon_active, fn):
            is_active = label == active
            return ft.Container(
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=3,
                    controls=[
                        ft.Icon(icon_active if is_active else icon,
                            color="green700" if is_active else "grey500", size=24),
                        ft.Text(label, size=10,
                            color="green700" if is_active else "grey500",
                            weight="bold" if is_active else "normal"),
                    ],
                ),
                expand=True, on_click=fn, ink=True,
                padding=ft.Padding(top=8, bottom=8, left=0, right=0),
            )

        analyze_btn = ft.Container(
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=3,
                controls=[
                    ft.Container(
                        content=ft.Icon(ft.Icons.ADD, color="white", size=26),
                        bgcolor="green700",
                        border_radius=18,
                        width=52, height=36,
                        alignment=ft.Alignment(0, 0),
                        shadow=ft.BoxShadow(spread_radius=1, blur_radius=8,
                            color=ft.Colors.with_opacity(0.25, "green900")),
                    ),
                    ft.Text("Analyze", size=10, color="green700", weight="bold"),
                ],
            ),
            expand=True,
            on_click=lambda e: show_crop_selector(email),
            ink=True,
            padding=ft.Padding(top=6, bottom=8, left=0, right=0),
        )

        return ft.Container(
            content=ft.Row(spacing=0, controls=[
                tab_btn("Home", ft.Icons.HOME_OUTLINED, ft.Icons.HOME, lambda e: show_home(email)),
                analyze_btn,
                tab_btn("Forum", ft.Icons.FORUM_OUTLINED, ft.Icons.FORUM, lambda e: show_forum(email)),
                tab_btn("Profile", ft.Icons.PERSON_OUTLINE, ft.Icons.PERSON, lambda e: show_profile(email)),
            ]),
            bgcolor="white",
            border_radius=ft.BorderRadius(top_left=20, top_right=20, bottom_left=0, bottom_right=0),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=16,
                color=ft.Colors.with_opacity(0.1, "green900"), offset=ft.Offset(0, -2)),
            padding=ft.Padding(left=8, right=8, top=0, bottom=0),
        )

    # ──────────────────────────────────────────────────────
    # SPLASH
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
    # ONBOARDING
    # ──────────────────────────────────────────────────────
    def show_onboarding(page_idx=0):
        slides = [
            {"icon": ft.Icons.GRASS_ROUNDED, "title": "Welcome to Soilco",
             "subtitle": "Your smart soil analysis companion for better farming decisions.", "color": "green700"},
            {"icon": ft.Icons.WATER_DROP, "title": "Smart Irrigation",
             "subtitle": "Get AI-powered daily irrigation recommendations based on your crop and local weather.", "color": "blue700"},
            {"icon": ft.Icons.AUTO_AWESOME, "title": "AI Crop Analysis",
             "subtitle": "Pick a crop and receive instant fertilizer, soil type, and growth time analysis.", "color": "orange700"},
        ]
        s = slides[page_idx]
        dots = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=8, controls=[
            ft.Container(width=10 if i == page_idx else 6, height=10 if i == page_idx else 6,
                border_radius=5, bgcolor="green700" if i == page_idx else "green200")
            for i in range(len(slides))
        ])
        is_last = page_idx == len(slides) - 1

        def on_next(e):
            if is_last:
                mark_onboarding_seen()
                show_login()
            else:
                show_onboarding(page_idx + 1)

        switch([ft.Container(expand=True, bgcolor="#f0f7f0", content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER, spacing=0,
            controls=[
                ft.Container(expand=True, alignment=ft.Alignment(0, 0), content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER, spacing=24,
                    controls=[
                        ft.Container(content=ft.Icon(s["icon"], color="white", size=72),
                            bgcolor=s["color"], border_radius=40, padding=32),
                        ft.Text(s["title"], size=26, weight="bold", color="green900",
                            text_align=ft.TextAlign.CENTER),
                        ft.Text(s["subtitle"], size=15, color="grey600",
                            text_align=ft.TextAlign.CENTER),
                    ])),
                ft.Container(padding=ft.Padding(left=30, right=30, top=0, bottom=40),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20,
                        controls=[
                            dots,
                            green_btn("Get Started" if is_last else "Next", on_next, height=50),
                            ft.TextButton("Skip",
                                on_click=lambda e: (mark_onboarding_seen(), show_login()),
                                style=ft.ButtonStyle(color="grey500")) if not is_last else ft.Container(height=10),
                        ])),
            ]))])

    # ──────────────────────────────────────────────────────
    # LOGIN
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
                status.value = "Please fill in all fields"
                status.color = "red"
                page.update()
            else:
                # BACKEND: supabase.auth.sign_in_with_password(email, password)
                show_home(email_field.value)

        switch([ft.Container(expand=True, bgcolor="#f0f7f0", content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO, spacing=0,
            controls=[
                ft.Container(content=logo(50), padding=ft.Padding(top=60, bottom=30, left=0, right=0)),
                card(ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16, controls=[
                    ft.Text("Welcome Back", size=22, weight="bold", color="green900"),
                    email_field, password_field,
                    ft.Container(
                        content=ft.TextButton("Forgot Password?",
                            on_click=lambda e: show_forgot(),
                            style=ft.ButtonStyle(color="green700")),
                        alignment=ft.Alignment(1, 0), width=300),
                    green_btn("Login", on_login),
                    status,
                    ft.Divider(color="green200"),
                    ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
                        ft.Text("Don't have an account?", color="grey700"),
                        ft.TextButton("Sign Up", on_click=lambda e: show_signup(),
                            style=ft.ButtonStyle(color="green700")),
                    ]),
                ]), radius=25, margin=ft.Margin(left=20, right=20, top=0, bottom=40)),
            ]))])

    # ──────────────────────────────────────────────────────
    # SIGN UP
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
                status.value = "Please fill in all fields"
                status.color = "red"
                page.update()
            else:
                # BACKEND: supabase.auth.sign_up(email, password) + INSERT into users
                show_home(email_field.value)

        switch([
            appbar("Sign Up", lambda e: show_login()),
            ft.Container(expand=True, bgcolor="#f0f7f0", content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO, spacing=16,
                controls=[
                    ft.Container(height=10), logo(40),
                    card(ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16, controls=[
                        ft.Text("Create Account", size=20, weight="bold", color="green900"),
                        name_field, email_field, password_field,
                        green_btn("Create Account", on_register),
                        status,
                        ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
                            ft.Text("Already have an account?", color="grey700"),
                            ft.TextButton("Login", on_click=lambda e: show_login(),
                                style=ft.ButtonStyle(color="green700")),
                        ]),
                    ]), radius=25, margin=ft.Margin(left=20, right=20, top=0, bottom=30)),
                ])),
        ])

    # ──────────────────────────────────────────────────────
    # FORGOT PASSWORD
    # ──────────────────────────────────────────────────────
    def show_forgot():
        email_field = ft.TextField(label="Enter your email", prefix_icon=ft.Icons.EMAIL_OUTLINED,
            width=300, border_radius=15, border_color="green700", focused_border_color="green900",
            keyboard_type=ft.KeyboardType.EMAIL, bgcolor="white")
        status = ft.Text("", size=14, text_align=ft.TextAlign.CENTER)

        def on_reset(e):
            if not email_field.value:
                status.value = "Please enter your email"
                status.color = "red"
            else:
                # BACKEND: supabase.auth.reset_password_email(email)
                status.value = f"Reset link sent to {email_field.value}"
                status.color = "green700"
            page.update()

        switch([
            appbar("Forgot Password", lambda e: show_login()),
            ft.Container(expand=True, bgcolor="#f0f7f0", padding=20, content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER, spacing=20,
                controls=[
                    logo(40),
                    ft.Icon(ft.Icons.LOCK_RESET, color="green700", size=50),
                    ft.Text("Reset Password", size=22, weight="bold", color="green800"),
                    ft.Text("Enter your email and we will send you a reset link",
                        size=13, color="grey600", text_align=ft.TextAlign.CENTER),
                    card(ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16,
                        controls=[email_field, green_btn("Send Reset Link", on_reset), status]),
                        radius=25, margin=ft.Margin(left=20, right=20, top=0, bottom=20)),
                    ft.TextButton("Back to Login", on_click=lambda e: show_login(),
                        style=ft.ButtonStyle(color="green700")),
                ])),
        ])

    # ──────────────────────────────────────────────────────
    # HOME
    # ──────────────────────────────────────────────────────
    def show_home(email=""):
        previous_crops = [
            # BACKEND: SELECT * FROM soil_analyses WHERE user_id=? ORDER BY analyzed_at DESC LIMIT 3
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
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=6,
                    color=ft.Colors.with_opacity(0.06, "green900")),
                on_click=lambda e, c=item["crop"]: show_analysis(c, email),
                ink=True,
            )

        switch([
            ft.Container(
                expand=True, bgcolor="white",
                padding=ft.Padding(left=16, right=16, top=50, bottom=20),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO, spacing=16,
                    controls=[
                        # Greeting
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Column(spacing=2, controls=[
                                    ft.Text("Good day,", size=13, color="grey500"),
                                    ft.Text(
                                        email.split("@")[0].capitalize() if email else "Farmer",
                                        size=22, weight="bold", color="green900"),
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
                                            # BACKEND: GET /weather?lat=&lon=&appid=&units=metric
                                        ]),
                                        ft.Column(horizontal_alignment=ft.CrossAxisAlignment.END, spacing=6,
                                            controls=[
                                                ft.Icon(ft.Icons.WB_SUNNY_OUTLINED, color="white", size=48),
                                                ft.Row(spacing=2, controls=[
                                                    ft.Icon(ft.Icons.WATER_DROP_OUTLINED, color="#c8e6c9", size=12),
                                                    ft.Text("Hum: --%", size=11, color="#c8e6c9"),
                                                ]),
                                                ft.Row(spacing=2, controls=[
                                                    ft.Icon(ft.Icons.AIR, color="#c8e6c9", size=12),
                                                    ft.Text("Wind: -- km/h", size=11, color="#c8e6c9"),
                                                ]),
                                            ]),
                                    ],
                                ),
                            ]),
                            bgcolor="green700", border_radius=20, padding=20,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10,
                                color=ft.Colors.with_opacity(0.15, "green900")),
                        ),

                        # Quick analyze card — clean white
                        ft.Container(
                            content=ft.Row(spacing=12,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Container(
                                        content=ft.Icon(ft.Icons.AUTO_AWESOME, color="green700", size=20),
                                        bgcolor="#e8f5e9", border_radius=10, padding=8),
                                    ft.Column(spacing=2, expand=True, controls=[
                                        ft.Text("Start Crop Analysis", size=14, weight="bold", color="green900"),
                                        ft.Text("Tap + below to get started", size=11, color="grey500"),
                                    ]),
                                    ft.Icon(ft.Icons.ARROW_FORWARD_IOS, color="grey400", size=14),
                                ]),
                            bgcolor="white", border_radius=16, padding=16,
                            border=ft.border.all(1, "#e0e0e0"),
                            on_click=lambda e: show_crop_selector(email), ink=True,
                        ),

                        # Previous analyses
                        ft.Column(spacing=10, controls=[
                            ft.Text("Previous Analyses", size=16, weight="bold", color="green900"),
                            # BACKEND: Replace with real analyses from Supabase
                            *[prev_crop_card(c) for c in previous_crops],
                        ]),

                        ft.Container(height=70),
                    ],
                ),
            ),
            nav_bar("Home", email),
        ])

    # ──────────────────────────────────────────────────────
    # CROP ENTRY
    # ──────────────────────────────────────────────────────
    def show_crop_selector(email=""):

        crop_field = ft.TextField(
            label="Enter crop name",
            prefix_icon=ft.Icons.GRASS,
            hint_text="e.g. Maize, Tomato, Wheat...",
            border_radius=15,
            border_color="green700",
            focused_border_color="green900",
            bgcolor="white",
            width=320,
        )

        status = ft.Text("", size=13, color="red", text_align=ft.TextAlign.CENTER)

        def on_analyze(e):
            if not crop_field.value or not crop_field.value.strip():
                status.value = "Please enter a crop name"
                page.update()
                return
            show_analysis(crop_field.value.strip().capitalize(), email)

        switch([
            appbar("Analyze Crop", lambda e: show_home(email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=20, right=20, top=30, bottom=24),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO, spacing=20,
                    controls=[
                        ft.Column(spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(ft.Icons.GRASS_ROUNDED, color="green700", size=40),
                                ft.Text("What are you growing?",
                                    size=20, weight="bold", color="green900",
                                    text_align=ft.TextAlign.CENTER),
                                ft.Text("Type in your crop and we'll handle the rest",
                                    size=13, color="grey500", text_align=ft.TextAlign.CENTER),
                            ]),
                        crop_field,
                        status,
                        green_btn("Analyze", on_analyze, width=320, height=52),
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # ANALYSIS RESULT
    # ──────────────────────────────────────────────────────
    def show_analysis(crop_name, email=""):
        # BACKEND: POST to Groq API:
        #   prompt: crop_name, user lat/lon, soil_ph from ISRIC SoilGrids
        #   returns JSON: {irrigation_mm_per_day, soil_type, growth_weeks,
        #                  nitrogen_kg_ha, phosphorus_kg_ha, potassium_kg_ha, farming_difficulty}
        # BACKEND: INSERT result into Supabase soil_analyses table

        irrigation_val = ft.Text("4.2 mm/day", size=20, weight="bold", color="green800")
        soil_type_val  = ft.Text("Loamy",      size=20, weight="bold", color="green800")
        growth_val     = ft.Text("12 weeks",   size=20, weight="bold", color="green800")
        nitrogen_val   = ft.Text("45.0 kg/ha", size=15, weight="bold", color="green700")
        phosphorus_val = ft.Text("22.5 kg/ha", size=15, weight="bold", color="green700")
        potassium_val  = ft.Text("30.0 kg/ha", size=15, weight="bold", color="green700")

        # BACKEND: Replace "Medium" with Groq farming_difficulty response
        difficulty = "Medium"
        diff_color = {"Easy": "green600", "Medium": "orange600", "Hard": "red600"}
        diff_icon  = {
            "Easy":   ft.Icons.CHECK_CIRCLE,
            "Medium": ft.Icons.WARNING_ROUNDED,
            "Hard":   ft.Icons.DANGEROUS,
        }
        diff_description = {
            "Easy":   "Soil pH and climate in your region are well-suited for this crop.",
            "Medium": "Some soil or climate factors may need attention before planting.",
            "Hard":   "Significant soil correction required to grow this crop in your region.",
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

                        # Header
                        card(ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Column(spacing=4, controls=[
                                    ft.Text("Crop", size=12, color="grey600"),
                                    ft.Text(crop_name, size=22, weight="bold", color="green900"),
                                ]),
                                ft.Column(spacing=6, horizontal_alignment=ft.CrossAxisAlignment.END,
                                    controls=[
                                        ft.Container(
                                            content=ft.Text("Analyzed", size=11, color="white"),
                                            bgcolor="green600", border_radius=8,
                                            padding=ft.Padding(left=10, right=10, top=4, bottom=4)),
                                        ft.Container(
                                            content=ft.Row(spacing=5, controls=[
                                                ft.Icon(diff_icon[difficulty], color="white", size=12),
                                                ft.Text(difficulty, size=11, color="white", weight="bold"),
                                            ]),
                                            bgcolor=diff_color[difficulty], border_radius=8,
                                            padding=ft.Padding(left=8, right=8, top=4, bottom=4)),
                                    ]),
                            ],
                        )),

                        # Metrics
                        ft.Row(spacing=12, controls=[
                            metric_card("Irrigation", irrigation_val, ft.Icons.WATER_DROP, "blue700"),
                            metric_card("Soil Type",  soil_type_val,  ft.Icons.LANDSCAPE,  "brown400"),
                        ]),
                        ft.Row(spacing=12, controls=[
                            metric_card("Growth Time", growth_val, ft.Icons.SCHEDULE, "green600"),
                        ]),

                        # Difficulty card
                        ft.Container(
                            content=ft.Column(spacing=10, controls=[
                                ft.Row(spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Icon(diff_icon[difficulty], color=diff_color[difficulty], size=22),
                                        ft.Text("Growing Difficulty", size=15, weight="bold", color="green900"),
                                        ft.Container(expand=True),
                                        ft.Container(
                                            content=ft.Text(difficulty, size=11, color="white", weight="bold"),
                                            bgcolor=diff_color[difficulty], border_radius=8,
                                            padding=ft.Padding(left=10, right=10, top=4, bottom=4)),
                                    ]),
                                ft.Divider(color="green100"),
                                ft.Text(diff_description[difficulty], size=13, color="grey700"),
                                ft.Container(
                                    content=ft.Row(spacing=8, controls=[
                                        ft.Icon(ft.Icons.INFO_OUTLINE, color="green600", size=14),
                                        ft.Text("Scored using soil pH and regional climate via Groq AI",
                                            size=11, color="grey500", expand=True),
                                    ]),
                                    bgcolor="#f0f7f0", border_radius=8,
                                    padding=ft.Padding(left=10, right=10, top=8, bottom=8)),
                            ]),
                            bgcolor="white", border_radius=16, padding=16,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10,
                                color=ft.Colors.with_opacity(0.08, "green900"))),

                        # Fertilizer
                        card(ft.Column(spacing=12, controls=[
                            ft.Text("Fertilizer Recommendation", size=16, weight="bold", color="green900"),
                            ft.Divider(color="green100"),
                            fert_row("Nitrogen (N)",   nitrogen_val),
                            fert_row("Phosphorus (P)", phosphorus_val),
                            fert_row("Potassium (K)",  potassium_val),
                        ])),

                        # Go to irrigation alert
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
                            on_click=lambda e: show_daily_alert(crop_name, "4.2", email),
                            ink=True,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10,
                                color=ft.Colors.with_opacity(0.15, "green900"))),
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # DAILY IRRIGATION ALERT
    # ──────────────────────────────────────────────────────
    def show_daily_alert(crop_name="", base_irrigation="4.2", email=""):
        # BACKEND: GET /weather?lat=&lon=&appid=&units=metric (OpenWeatherMap)
        weather = {"temp": "--", "humidity": "--", "wind": "--", "rain_forecast": "--"}
        base = float(base_irrigation)
        # BACKEND: adjusted = max(0, base - rain_mm)

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
                                        ft.Container(content=ft.Icon(ft.Icons.GRASS, color="white", size=22),
                                            bgcolor="green700", border_radius=12, padding=10),
                                        ft.Column(spacing=2, controls=[
                                            ft.Text("Crop", size=11, color="grey500"),
                                            ft.Text(crop_name, size=18, weight="bold", color="green900"),
                                        ]),
                                    ]),
                                ],
                            ),
                            bgcolor="white", border_radius=16, padding=16,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=8,
                                color=ft.Colors.with_opacity(0.07, "green900"))),

                        # Weather summary
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
                                        ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4,
                                            controls=[
                                                ft.Icon(ft.Icons.THERMOSTAT, color="white", size=20),
                                                ft.Text(f"{weather['temp']} °C", size=15, weight="bold", color="white"),
                                                ft.Text("Temp", size=10, color="#c8e6c9"),
                                            ]),
                                        ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4,
                                            controls=[
                                                ft.Icon(ft.Icons.WATER_DROP_OUTLINED, color="white", size=20),
                                                ft.Text(f"{weather['humidity']}%", size=15, weight="bold", color="white"),
                                                ft.Text("Humidity", size=10, color="#c8e6c9"),
                                            ]),
                                        ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4,
                                            controls=[
                                                ft.Icon(ft.Icons.UMBRELLA, color="white", size=20),
                                                ft.Text(f"{weather['rain_forecast']} mm", size=15, weight="bold", color="white"),
                                                ft.Text("Rain", size=10, color="#c8e6c9"),
                                            ]),
                                        ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4,
                                            controls=[
                                                ft.Icon(ft.Icons.AIR, color="white", size=20),
                                                ft.Text(f"{weather['wind']} km/h", size=15, weight="bold", color="white"),
                                                ft.Text("Wind", size=10, color="#c8e6c9"),
                                            ]),
                                    ],
                                ),
                            ]),
                            bgcolor="green700", border_radius=20, padding=20,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=12,
                                color=ft.Colors.with_opacity(0.15, "green900"))),

                        # Calculation
                        card(ft.Column(spacing=14, controls=[
                            ft.Text("Water Calculation", size=15, weight="bold", color="green900"),
                            ft.Divider(color="green100"),
                            info_row(ft.Icons.WATER_DROP, "blue700", f"Base irrigation for {crop_name}", f"{base} mm/day"),
                            info_row(ft.Icons.UMBRELLA, "blue400", "Expected rainfall today", f"{weather['rain_forecast']} mm"),
                            ft.Divider(color="green100"),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Text("Recommended today", size=15, weight="bold", color="green900"),
                                    ft.Container(
                                        content=ft.Text(f"{base} mm", size=16, weight="bold", color="white"),
                                        bgcolor="green700", border_radius=10,
                                        padding=ft.Padding(left=14, right=14, top=6, bottom=6)),
                                ]),
                        ])),

                        # Schedule
                        card(ft.Column(spacing=12, controls=[
                            ft.Text("Suggested Schedule", size=15, weight="bold", color="green900"),
                            ft.Divider(color="green100"),
                            ft.Row(spacing=12, controls=[
                                ft.Container(
                                    content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4,
                                        controls=[
                                            ft.Icon(ft.Icons.WB_TWILIGHT, color="orange600", size=22),
                                            ft.Text("Morning", size=12, weight="bold", color="green900"),
                                            ft.Text("6:00 AM", size=11, color="grey500"),
                                            ft.Text("-- mm", size=13, weight="bold", color="green700"),
                                        ]),
                                    expand=True, bgcolor="#f0f7f0", border_radius=12,
                                    padding=12, alignment=ft.Alignment(0, 0)),
                                ft.Container(
                                    content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4,
                                        controls=[
                                            ft.Icon(ft.Icons.WB_SUNNY, color="yellow700", size=22),
                                            ft.Text("Afternoon", size=12, weight="bold", color="green900"),
                                            ft.Text("2:00 PM", size=11, color="grey500"),
                                            ft.Text("-- mm", size=13, weight="bold", color="green700"),
                                        ]),
                                    expand=True, bgcolor="#f0f7f0", border_radius=12,
                                    padding=12, alignment=ft.Alignment(0, 0)),
                                ft.Container(
                                    content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4,
                                        controls=[
                                            ft.Icon(ft.Icons.NIGHTS_STAY, color="blue700", size=22),
                                            ft.Text("Evening", size=12, weight="bold", color="green900"),
                                            ft.Text("6:00 PM", size=11, color="grey500"),
                                            ft.Text("-- mm", size=13, weight="bold", color="green700"),
                                        ]),
                                    expand=True, bgcolor="#f0f7f0", border_radius=12,
                                    padding=12, alignment=ft.Alignment(0, 0)),
                            ]),
                        ])),

                        ft.Text("* Live weather data requires OpenWeatherMap API and location to be set.",
                            size=11, color="grey400", italic=True, text_align=ft.TextAlign.CENTER),
                    ],
                ),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # FORUM — single WhatsApp-style group
    # ──────────────────────────────────────────────────────
    def show_forum(email=""):
        username = email.split("@")[0].capitalize() if email else "Farmer"

        # BACKEND: SELECT * FROM forum_posts ORDER BY created_at DESC
        posts = [
            {"author": "Alice", "text": "Best time to plant maize in Nairobi?", "time": "2h ago"},
            {"author": "Bob",   "text": "Anyone tried SRI method for rice? Great results!", "time": "5h ago"},
            {"author": "Carol", "text": "My beans are yellowing — could be nitrogen deficiency?", "time": "1d ago"},
        ]

        msg_field = ft.TextField(
            hint_text="Write something...",
            border_radius=20,
            border_color="green200",
            focused_border_color="green700",
            bgcolor="white",
            expand=True,
            min_lines=1,
            max_lines=4,
            content_padding=ft.Padding(left=16, right=16, top=10, bottom=10),
        )

        posts_column = ft.Column(spacing=10, controls=[])

        def post_card(p):
            def on_reply(e, author=p["author"]):
                msg_field.value = f"@{author} "
                page.update()

            return ft.Container(
                content=ft.Column(spacing=8, controls=[
                    ft.Row(spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                content=ft.Text(p["author"][0], size=13, color="white", weight="bold"),
                                bgcolor="green700", border_radius=16,
                                width=32, height=32, alignment=ft.Alignment(0, 0)),
                            ft.Column(spacing=1, controls=[
                                ft.Text(p["author"], size=13, weight="bold", color="green900"),
                                ft.Text(p["time"], size=10, color="grey400"),
                            ]),
                        ]),
                    ft.Text(p["text"], size=13, color="grey800"),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        controls=[
                            ft.Container(
                                content=ft.Row(spacing=4, controls=[
                                    ft.Icon(ft.Icons.REPLY, color="green700", size=13),
                                    ft.Text("Reply", size=11, color="green700", weight="bold"),
                                ]),
                                bgcolor="#e8f5e9", border_radius=12,
                                padding=ft.Padding(left=10, right=10, top=5, bottom=5),
                                on_click=on_reply, ink=True,
                            ),
                        ]),
                ]),
                bgcolor="white", border_radius=16, padding=14,
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=6,
                    color=ft.Colors.with_opacity(0.06, "green900")),
            )

        for p in posts:
            posts_column.controls.append(post_card(p))

        def on_send(e):
            if msg_field.value and msg_field.value.strip():
                # BACKEND: INSERT into forum_posts (user_id, content, created_at)
                posts_column.controls.insert(0, post_card({
                    "author": username,
                    "text": msg_field.value.strip(),
                    "time": "Just now",
                }))
                msg_field.value = ""
                page.update()

        switch([
            appbar("Farmers Group"),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                content=ft.Column(spacing=0, controls=[

                    # Group header
                    ft.Container(
                        content=ft.Row(spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    content=ft.Icon(ft.Icons.GRASS_ROUNDED, color="white", size=20),
                                    bgcolor="green700", border_radius=20,
                                    width=40, height=40, alignment=ft.Alignment(0, 0)),
                                ft.Column(spacing=2, controls=[
                                    ft.Text("Soilco Farmers", size=14, weight="bold", color="green900"),
                                    ft.Text("Open community group", size=11, color="grey500"),
                                ]),
                            ]),
                        bgcolor="white", padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                        shadow=ft.BoxShadow(spread_radius=0, blur_radius=4,
                            color=ft.Colors.with_opacity(0.05, "green900"))),

                    # Posts list
                    ft.Container(
                        expand=True,
                        padding=ft.Padding(left=16, right=16, top=12, bottom=8),
                        content=ft.Column(scroll=ft.ScrollMode.AUTO, spacing=0,
                            controls=[posts_column, ft.Container(height=70)])),

                    # Message input bar
                    ft.Container(
                        content=ft.Row(spacing=10, controls=[
                            msg_field,
                            ft.Container(
                                content=ft.Icon(ft.Icons.SEND, color="white", size=18),
                                bgcolor="green700", border_radius=20,
                                width=44, height=44, alignment=ft.Alignment(0, 0),
                                on_click=on_send, ink=True),
                        ]),
                        bgcolor="white",
                        padding=ft.Padding(left=12, right=12, top=10, bottom=10),
                        shadow=ft.BoxShadow(spread_radius=0, blur_radius=8,
                            color=ft.Colors.with_opacity(0.08, "green900"),
                            offset=ft.Offset(0, -2))),
                ]),
            ),
            nav_bar("Forum", email),
        ])

    # ──────────────────────────────────────────────────────
    # NOTIFICATIONS
    # ──────────────────────────────────────────────────────
    def show_notifications(email=""):
        daily_alerts   = ft.Switch(value=True,  active_color="green700")
        rain_alerts    = ft.Switch(value=False, active_color="green700")
        weekly_summary = ft.Switch(value=True,  active_color="green700")
        tips           = ft.Switch(value=False, active_color="green700")

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
            appbar("Notifications", lambda e: show_profile(email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=20, bottom=20),
                content=ft.Column(scroll=ft.ScrollMode.AUTO, spacing=16, controls=[
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
                        notif_row("Weekly Summary", "Every Sunday evening", weekly_summary),
                        ft.Divider(color="green100", height=1),
                        notif_row("Farming Tips", "Weekly tips from Soilco AI", tips),
                    ]), padding=0),
                    ft.Text("* Push notifications require the mobile app",
                        size=11, color="grey400", italic=True),
                ]),
            ),
        ])



    # ──────────────────────────────────────────────────────
    # EDIT PROFILE
    # ──────────────────────────────────────────────────────
    def show_edit_profile(email=""):
        name_field = ft.TextField(label="Full Name", prefix_icon=ft.Icons.PERSON_OUTLINE,
            border_radius=15, border_color="green700", focused_border_color="green900", bgcolor="white")
        phone_field = ft.TextField(label="Phone Number", prefix_icon=ft.Icons.PHONE_OUTLINED,
            border_radius=15, border_color="green700", focused_border_color="green900",
            keyboard_type=ft.KeyboardType.PHONE, bgcolor="white")
        farm_field = ft.TextField(label="Farm Name", prefix_icon=ft.Icons.GRASS,
            border_radius=15, border_color="green700", focused_border_color="green900", bgcolor="white")
        location_field = ft.TextField(label="Location", prefix_icon=ft.Icons.LOCATION_ON_OUTLINED,
            border_radius=15, border_color="green700", focused_border_color="green900", bgcolor="white")
        status = ft.Text("", size=13, text_align=ft.TextAlign.CENTER)

        def on_save(e):
            # BACKEND: UPDATE users SET full_name, phone, farm_name, location WHERE id=?
            status.value = "Profile updated successfully"
            status.color = "green700"
            page.update()

        switch([
            appbar("Edit Profile", lambda e: show_profile(email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=20, bottom=20),
                content=ft.Column(scroll=ft.ScrollMode.AUTO, spacing=16,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        card(ft.Column(spacing=14, controls=[
                            ft.Text("Personal Info", size=14, weight="bold", color="green900"),
                            ft.Divider(color="green100"),
                            name_field, phone_field, farm_field, location_field,
                        ])),
                        green_btn("Save Changes", on_save, width=320),
                        status,
                    ]),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # CHANGE PASSWORD
    # ──────────────────────────────────────────────────────
    def show_change_password(email=""):
        current_field = ft.TextField(label="Current Password", prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True, can_reveal_password=True,
            border_radius=15, border_color="green700", focused_border_color="green900", bgcolor="white")
        new_field = ft.TextField(label="New Password", prefix_icon=ft.Icons.LOCK_OPEN,
            password=True, can_reveal_password=True,
            border_radius=15, border_color="green700", focused_border_color="green900", bgcolor="white")
        confirm_field = ft.TextField(label="Confirm New Password", prefix_icon=ft.Icons.LOCK_OPEN,
            password=True, can_reveal_password=True,
            border_radius=15, border_color="green700", focused_border_color="green900", bgcolor="white")
        status = ft.Text("", size=13, text_align=ft.TextAlign.CENTER)

        def on_save(e):
            if not current_field.value or not new_field.value or not confirm_field.value:
                status.value = "Please fill in all fields"
                status.color = "red"
            elif new_field.value != confirm_field.value:
                status.value = "New passwords do not match"
                status.color = "red"
            else:
                # BACKEND: supabase.auth.update_user({"password": new_field.value})
                status.value = "Password updated successfully"
                status.color = "green700"
            page.update()

        switch([
            appbar("Change Password", lambda e: show_profile(email)),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=20, bottom=20),
                content=ft.Column(scroll=ft.ScrollMode.AUTO, spacing=16,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        card(ft.Column(spacing=14, controls=[
                            ft.Text("Update Password", size=14, weight="bold", color="green900"),
                            ft.Divider(color="green100"),
                            current_field, new_field, confirm_field,
                        ])),
                        green_btn("Save Password", on_save, width=320),
                        status,
                    ]),
            ),
        ])

    # ──────────────────────────────────────────────────────
    # PROFILE
    # ──────────────────────────────────────────────────────
    def show_profile(email=""):
        username   = email.split("@")[0].capitalize() if email else "Farmer"
        user_email = email or "farmer@soilco.app"

        def stat_box(value, label):
            return ft.Container(
                content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3,
                    controls=[
                        ft.Text(value, size=22, weight="bold", color="green800"),
                        ft.Text(label, size=10, color="grey500"),
                    ]),
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
            appbar("Profile"),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                content=ft.Column(scroll=ft.ScrollMode.AUTO, spacing=0, controls=[

                    # Profile hero — no profile picture
                    ft.Container(
                        content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10,
                            controls=[
                                ft.Container(
                                    content=ft.Icon(ft.Icons.PERSON, color="white", size=52),
                                    bgcolor="green700", border_radius=50,
                                    width=100, height=100, alignment=ft.Alignment(0, 0)),
                                ft.Text(username, size=20, weight="bold", color="green900"),
                                ft.Text(user_email, size=12, color="grey600"),
                                ft.Row(spacing=6, alignment=ft.MainAxisAlignment.CENTER, controls=[
                                    ft.Icon(ft.Icons.LOCATION_ON, color="green600", size=14),
                                    ft.Text("Location not set", size=12, color="grey500"),
                                    # BACKEND: Replace with user.location from Supabase
                                ]),
                            ]),
                        bgcolor="white",
                        padding=ft.Padding(top=28, bottom=24, left=0, right=0),
                        width=page.window.width),

                    # Settings
                    ft.Container(
                        content=ft.Text("Account Settings", size=13, color="grey500", weight="bold"),
                        padding=ft.Padding(left=16, right=0, top=4, bottom=6)),
                    ft.Container(
                        content=ft.Column(spacing=0, controls=[
                            setting_row(ft.Icons.PERSON_OUTLINE, "Edit Profile",
                                lambda e: show_edit_profile(email)),
                            ft.Divider(color="green100", height=1),
                            setting_row(ft.Icons.LOCK_OUTLINE, "Change Password",
                                lambda e: show_change_password(email)),
                            ft.Divider(color="green100", height=1),
                            setting_row(ft.Icons.NOTIFICATIONS, "Notifications",
                                lambda e: show_notifications(email)),
                        ]),
                        bgcolor="white", border_radius=16,
                        margin=ft.Margin(left=16, right=16, top=0, bottom=14),
                        shadow=ft.BoxShadow(spread_radius=1, blur_radius=8,
                            color=ft.Colors.with_opacity(0.06, "green900"))),

                    # Logout
                    ft.Container(
                        content=ft.Row(spacing=12, alignment=ft.MainAxisAlignment.CENTER, controls=[
                            ft.Icon(ft.Icons.LOGOUT, color="red600", size=20),
                            ft.Text("Logout", size=14, color="red600", weight="bold"),
                        ]),
                        bgcolor="white", border_radius=16,
                        margin=ft.Margin(left=16, right=16, top=0, bottom=80),
                        padding=ft.Padding(left=20, right=20, top=14, bottom=14),
                        on_click=lambda e: show_login(), ink=True,
                        shadow=ft.BoxShadow(spread_radius=1, blur_radius=8,
                            color=ft.Colors.with_opacity(0.06, "green900"))),
                ]),
            ),
            nav_bar("Profile", email),
        ])

    # ──────────────────────────────────────────────────────
    # START
    # ──────────────────────────────────────────────────────
    show_splash()


if __name__ == "__main__":
    ft.run(main)