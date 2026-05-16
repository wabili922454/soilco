import sys
import os

# Dynamically inject both the root folder and src folder into Python's memory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import flet as ft
import time
import threading
from datetime import datetime

# Safe import wrapper: Try both styles so it NEVER crashes your app window
try:
    from backend.weather_service import get_weather, calculate_irrigation_advice
except ModuleNotFoundError:
    try:
        from src.backend.weather_service import get_weather, calculate_irrigation_advice
    except ModuleNotFoundError:
        # Fallbacks to prevent application rendering breaks
        def get_weather(lat, lon): return None
        def calculate_irrigation_advice(t, h): return {"status": "Normal", "advice": "Standard schedule", "icon": "info"}
try:
    from backend.supabase_client import get_recent_analyses, save_analysis, update_user_preferences
except ModuleNotFoundError:
    try:
        from src.backend.supabase_client import get_recent_analyses, save_analysis, update_user_preferences
    except ModuleNotFoundError:
        # Fallback to prevent app execution crashes
        def update_user_preferences(user_id, irrigation, weekly): return False
try:
    from backend.forum_service import get_forum_posts, post_to_forum
except ModuleNotFoundError:
    try:
        from src.backend.forum_service import get_forum_posts, post_to_forum
    except ModuleNotFoundError:
        # Fallbacks to prevent application crashes
        def get_forum_posts(limit=50): return []
        def post_to_forum(user_id, author_name, content): return False


welcome_flag = os.path.join(os.path.expanduser("~"), ".soilco_onboarding_seen")

crops = [
    "Maize", "Wheat", "Rice", "Beans", "Soybean",
    "Tomato", "Potato", "Sorghum", "Cassava", "Cotton",
    "Sunflower", "Groundnut", "Barley", "Millet", "Sugarcane",
    "Onion", "Cabbage", "Spinach", "Pepper", "Sweet Potato",
]

soil_types = [
    "Loamy", "Sandy", "Clay", "Silty", "Peaty",
    "Chalky", "Sandy Loam", "Clay Loam", "Silt Loam", "Loamy Sand",
]

diff_color = {"Easy": ft.Colors.GREEN_600, "Medium": ft.Colors.ORANGE_600, "Hard": ft.Colors.RED_600}
DIFF_ICON  = {
    "Easy":   ft.Icons.CHECK_CIRCLE,
    "Medium": ft.Icons.WARNING_ROUNDED,
    "Hard":   ft.Icons.DANGEROUS,
}
DIFF_DESCRIPTION = {
    "Easy":   "Soil pH and climate in your region are well-suited for this crop.",
    "Medium": "Some soil or climate factors may need attention before planting.",
    "Hard":   "Significant soil correction required to grow this crop in your region.",
}




def main(page: ft.Page):
    page.title        = "Soilco"
    page.window.width  = 390
    page.window.height = 844
    page.theme_mode   = ft.ThemeMode.LIGHT
    page.padding      = ft.Padding(top=0, left=0, right=0, bottom=0)
    page.bgcolor      = "#f0f7f0"
    page.fonts        = {
        "Inter": "https://fonts.gstatic.com/s/inter/v13/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfAZ9hiJ-Ek-_EeA.woff2"
    }
    page.theme = ft.Theme(font_family="Inter")

    def logo(size=50, light=False, show_text=True):
        icon_color = "white" if light else ft.Colors.GREEN_700
        text_color = ft.Colors.WHITE if light else ft.Colors.GREEN_900
        sub_color  = "#c8e6c9" if light else  ft.Colors.GREEN_600
        controls = [ft.Icon(ft.Icons.GRASS_ROUNDED, color=icon_color, size=size)]
        if show_text:
            controls += [
                ft.Text("Soilco",              size=28, weight="bold", color=text_color),
                ft.Text("Smart Soil Analysis", size=12,               color=sub_color),
            ]
        return ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6, controls=controls)

    def switch_pages(controls):
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
                bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=15),
                text_style=ft.TextStyle(size=16, weight="bold"),
            ),
        )

    def appbar(title, back_bttn=None, actions=None):
        back_button = ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE, on_click=back_bttn) if back_bttn else None
        return ft.AppBar(
            title=ft.Text(title, color=ft.Colors.WHITE, weight="bold"),
            bgcolor=ft.Colors.GREEN_700,
            leading=back_button,
            automatically_imply_leading=back_bttn is not None,
            actions=actions or [],
        )

    def status_badge(text, color):
        return ft.Container(
            content=ft.Text(text, size=11, color=ft.Colors.WHITE),
            bgcolor=color,
            border_radius=8,
            padding=ft.Padding(left=10, right=10, top=4, bottom=4),
        )

    def nav_bar(active, email):

        def go_home(e):
            home_page(email)

        def go_analyze(e):
            analyzer_page(email)

        def go_forum(e):
            forum_page(email)

        def go_profile(e):
            profile_page(email)

        def tab_btn(label, icon, icon_pressed, on_click_func):
            is_active  = label == active
            tab_color  = ft.Colors.GREEN_700 if is_active else ft.Colors.GREY_700
            tab_weight = "bold" if is_active else "normal"
            return ft.Container(
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=3,
                    controls=[
                        ft.Icon(icon_pressed if is_active else icon, color=tab_color, size=24),
                        ft.Text(label, size=10, color=tab_color, weight=tab_weight),
                    ],
                ),
                expand=True, on_click=on_click_func, ink=True,
                padding=ft.Padding(top=8, bottom=8, left=0, right=0),
            )

        analyze_btn = ft.Container(
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=3,
                controls=[
                    ft.Container(
                        content=ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE, size=26),
                        bgcolor=ft.Colors.GREEN_700, border_radius=20, width=50, height=35,
                        alignment=ft.Alignment(0, 0),
                        shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color=ft.Colors.with_opacity(0.25, "green900")),
                    ),
                    ft.Text("Analyze", size=10, color=ft.Colors.GREEN_700, weight="bold"),
                ],
            ),
            expand=True, on_click=go_analyze, ink=True,
            padding=ft.Padding(top=6, bottom=8, left=0, right=0),
        )

        return ft.Container(
            content=ft.Row(spacing=0, controls=[
                tab_btn("Home",    ft.Icons.HOME_OUTLINED,  ft.Icons.HOME,   go_home),
                analyze_btn,
                tab_btn("Forum",   ft.Icons.FORUM_OUTLINED, ft.Icons.FORUM,  go_forum),
                tab_btn("Profile", ft.Icons.PERSON_OUTLINE, ft.Icons.PERSON, go_profile),
            ]),
            bgcolor="white",
            border_radius=ft.BorderRadius(top_left=20, top_right=20, bottom_left=0, bottom_right=0),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=16, color=ft.Colors.with_opacity(0.1, "green900"), offset=ft.Offset(0, -2)),
            padding=ft.Padding(left=8, right=8, top=0, bottom=0),
        )

    # splashscreen
    def login_page():
        switch_pages([
            ft.Container(
                expand=True, bgcolor=ft.Colors.GREEN_700, alignment=ft.Alignment(0, 0),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=12, controls=[logo(80, light=True)],
                ),
            )
        ])
        def after_splash():
            time.sleep(2)
           
            login_page()
        threading.Thread(target=after_splash, daemon=True).start()

    #login
    def login_page():
        email_field = ft.TextField(label="Email", prefix_icon=ft.Icons.EMAIL_OUTLINED, width=300,
            border_radius=15, border_color="green700", 
            keyboard_type=ft.KeyboardType.EMAIL, bgcolor="white")
        password_field = ft.TextField(label="Password", prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True, can_reveal_password=True, width=300,
            border_radius=15, border_color=ft.Colors.GREEN_700,  bgcolor="white")
        status = ft.Text("", size=14)

        def login_pressed(e):
            if not email_field.value or not password_field.value:
                status.value = " fill in all fields"
                status.color = "red"
                page.update()
            else:
                
                home_page(email_field.value)

        def go_forgot(e):
            forgotPasswordPage()

        def go_signup(e):
            signUp_page()

        forgot_btn = ft.Container(
            content=ft.TextButton("Forgot Password?", on_click=go_forgot, style=ft.ButtonStyle(color="green700")),
            alignment=ft.Alignment(1, 0), width=300,
        )
        signup_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text("Don't have an account?", color="grey700"),
                ft.TextButton("Sign Up", on_click=go_signup, style=ft.ButtonStyle(color= ft.Colors.GREEN_700)),
            ],
        )

        switch_pages([
            ft.Container(expand=True, bgcolor="#f0f7f0", content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO, spacing=0,
                controls=[
                    ft.Container(content=logo(50), padding=ft.Padding(top=60, bottom=30, left=0, right=0)),
                    card(ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16, controls=[
                        ft.Text("Welcome Back", size=22, weight="bold", color="green900"),
                        email_field, password_field, forgot_btn,
                        green_btn("Login", login_pressed), status,
                        ft.Divider(color="green200"), signup_row,
                    ]), radius=25, margin=ft.Margin(left=20, right=20, top=0, bottom=40)),
                ]))
        ])

    # signUp
    def signUp_page():
        name_field = ft.TextField(label="Full Name", prefix_icon=ft.Icons.PERSON_OUTLINE, width=300,
            border_radius=15, border_color= ft.Colors.GREEN_700, focused_border_color=ft.Colors.GREEN_900, bgcolor="white")
        email_field = ft.TextField(label="Email", prefix_icon=ft.Icons.EMAIL_OUTLINED, width=300,
            border_radius=15, border_color=ft.Colors.GREEN_700, focused_border_color=ft.Colors.GREEN_900,
            keyboard_type=ft.KeyboardType.EMAIL, bgcolor="white")
        password_field = ft.TextField(label="Password", prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True, can_reveal_password=True, width=300,
            border_radius=15, border_color= ft.Colors.GREEN_700, focused_border_color=ft.Colors.GREEN_900, bgcolor="white")
        status = ft.Text("", size=14)

        def CreateAcctPressed(e):
            if not name_field.value or not email_field.value or not password_field.value:
                status.value = "fill in all fields"
                status.color = "red"
                page.update()
            else:
                
                home_page(email_field.value)

        def go_login(e):
            login_page()

        login_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text("Already have an account?", color="grey700"),
                ft.TextButton("Login", on_click=go_login, style=ft.ButtonStyle(color="green700")),
            ],
        )

        switch_pages([
            appbar("Sign Up", back_bttn=go_login),
            ft.Container(expand=True, bgcolor="#f0f7f0", content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO, spacing=16,
                controls=[
                    ft.Container(height=10), logo(40),
                    card(ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16, controls=[
                        ft.Text("Create Account", size=20, weight="bold", color="green900"),
                        name_field, email_field, password_field,
                        green_btn("Create Account", CreateAcctPressed), status, login_row,
                    ]), radius=25, margin=ft.Margin(left=20, right=20, top=0, bottom=30)),
                ])),
        ])

    # forgot password 
    def forgotPasswordPage():
        email_field = ft.TextField(label="Enter your email", prefix_icon=ft.Icons.EMAIL_OUTLINED,
            width=300, border_radius=15, border_color="green700", focused_border_color="green900",
            keyboard_type=ft.KeyboardType.EMAIL, bgcolor="white")
        status = ft.Text("", size=14, text_align=ft.TextAlign.CENTER)

        def resetBtnPressed(e):
            if not email_field.value:
                status.value = "Please enter your email"
                status.color = "red"
            else:
               
               
                status.value = f"Reset link sent to {email_field.value}"
                status.color = "green700"
            page.update()

        def go_login(e):
            login_page()

        switch_pages([
            appbar("Forgot Password", back_bttn=go_login),
            ft.Container(expand=True, bgcolor="#f0f7f0", padding=20, content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER, spacing=20,
                controls=[
                    logo(40),
                    ft.Icon(ft.Icons.LOCK_RESET, color="green700", size=50),
                    ft.Text("Reset Password", size=22, weight="bold", color="green800"),
                    ft.Text("Enter your email and we will send you a reset link", size=13, color="grey600", text_align=ft.TextAlign.CENTER),
                    card(ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16,
                        controls=[email_field, green_btn("Send Reset Link", resetBtnPressed), status]),
                        radius=25, margin=ft.Margin(left=20, right=20, top=0, bottom=20)),
                    ft.TextButton("Back to Login", on_click=go_login, style=ft.ButtonStyle(color="green700")),
                ])),
        ])

    # home
    def home_page(email=""):
        # 1. Fetch weather data right when the screen opens
        # (Using test coordinates until Person 1 connects real database user profiles)
        test_lat = 48.8566
        test_lon = 2.3522
        weather_data = get_weather(test_lat, test_lon)

        # 2. Extract metrics safely using Rule 5 (Option A: fallback if None)
        if weather_data is not None:
            temp_str = f"{weather_data['temp']} °C"
            humidity_str = f"Hum: {weather_data['humidity']}%"
            wind_str = f"Wind: {weather_data['wind']} m/s"
            location_str = "Paris, FR (Test)"
        else:
            temp_str = "-- °C"
            humidity_str = "Hum: --%"
            wind_str = "Wind: -- m/s"
            location_str = "Weather Unavailable"

        db_records = get_recent_analyses(user_id=email, limit=3)
        
        previous_crops = []
        if db_records:
            for record in db_records:
                raw_date = record.get("created_at", "")
                try:
                    parsed_date = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                    formatted_date = parsed_date.strftime("%b %d")
                except Exception:
                    formatted_date = "Recent"

                payload = record.get("analysis_data", {})
                
                previous_crops.append({
                    "crop": record.get("crop_name", "Unknown Crop"),
                    "date": formatted_date,
                    "weeks": payload.get("growth_stage", "N/A"),
                    "status": payload.get("soil_status", "Optimal")
                })
        else:
            previous_crops = [
                {"crop": "No analysis yet", "date": "-", "weeks": "-", "status": "Optimal"}
            ]
        status_colors = {"Optimal": "green700", "Acidic": "orange700", "Alkaline": "blue700"}

        def open_analysis(crop_name):
            def handler(e):
                show_analysis(crop_name, email)
            return handler

        def prev_crop_card(item):
            badge_color = status_colors.get(item["status"], "grey500")
            return ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(spacing=12, controls=[
                            ft.Container(content=ft.Icon(ft.Icons.GRASS, color="white", size=18), bgcolor="green700", border_radius=10, padding=8),
                            ft.Column(spacing=2, controls=[
                                ft.Text(item["crop"], size=14, weight="bold", color= ft.Colors.GREEN_900),
                                ft.Text(item["date"], size=11,               color="grey500"),
                            ]),
                        ]),
                        ft.Column(horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2, controls=[
                            ft.Text(item["weeks"], size=13, weight="bold", color="green800"),
                            ft.Container(content=ft.Text(item["status"], size=10, color="white"),
                                bgcolor=badge_color, border_radius=8, padding=ft.Padding(left=8, right=8, top=3, bottom=3)),
                        ]),
                    ],
                ),
                bgcolor="white", border_radius=14, padding=12,
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=6, color=ft.Colors.with_opacity(0.06, "green900")),
                on_click=open_analysis(item["crop"]),
                ink=True,
            )

        farmer_name = email.split("@")[0].capitalize() if email else "Farmer"

        greeting_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(spacing=2, controls=[
                    ft.Text("Good day,",  size=13, color="grey500"),
                    ft.Text(farmer_name, size=22, weight="bold", color="green900"),
                ]),
                ft.Icon(ft.Icons.GRASS_ROUNDED, color="green700", size=36),
            ],
        )

        # 3. Use the updated dynamic text variables right here!
        weather_widget = ft.Container(
            content=ft.Column(spacing=12, controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(spacing=4, controls=[
                            ft.Text("Current Weather", size=12, color="#c8e6c9"),
                            ft.Text(temp_str,            size=32, weight="bold", color="white"),
                            ft.Text(location_str, size=12,               color="#c8e6c9"),
                        ]),
                        ft.Column(horizontal_alignment=ft.CrossAxisAlignment.END, spacing=6, controls=[
                            ft.Icon(ft.Icons.WB_SUNNY_OUTLINED, color="white", size=48),
                            ft.Row(spacing=2, controls=[
                                ft.Icon(ft.Icons.WATER_DROP_OUTLINED, color="#c8e6c9", size=12),
                                ft.Text(humidity_str, size=11, color="#c8e6c9"),
                            ]),
                            ft.Row(spacing=2, controls=[
                                ft.Icon(ft.Icons.AIR, color="#c8e6c9", size=12),
                                ft.Text(wind_str, size=11, color="#c8e6c9"),
                            ]),
                        ]),
                    ],
                ),
            ]),
            bgcolor="green700", border_radius=20, padding=20,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.with_opacity(0.15, "green900")),
        )

        analyses_section = ft.Column(
            spacing=10,
            controls=[
                ft.Text("Previous Analyses", size=16, weight="bold", color="green900"),
               
                *[prev_crop_card(c) for c in previous_crops],
            ],
        )

        switch_pages([
            ft.Container(
                expand=True, bgcolor="white",
                padding=ft.Padding(left=16, right=16, top=50, bottom=20),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO, spacing=16,
                    controls=[greeting_row, weather_widget, analyses_section, ft.Container(height=70)],
                ),
            ),
            nav_bar("Home", email),
        ])

    # ── CROP ENTRY ──────────────────────────────────────
    def analyzer_page(email=""):
        crop_field = ft.TextField(
            label="Enter crop name", prefix_icon=ft.Icons.GRASS,
            hint_text="e.g. Maize, Tomato, Wheat...",
            border_radius=15, border_color="green700", focused_border_color="green900",
            bgcolor="white", width=320,
        )
        status = ft.Text("", size=13, color="red", text_align=ft.TextAlign.CENTER)

        def on_analyze(e):
            crop_typed = crop_field.value.strip() if crop_field.value else ""
            if not crop_typed:
                status.value = "Please enter a crop name"
                page.update()
                return
            show_analysis(crop_typed.capitalize(), email)

        def go_back(e):
            home_page(email)

        switch_pages([
            appbar("Analyze Crop", back_bttn=go_back),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=20, right=20, top=30, bottom=24),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO, spacing=20,
                    controls=[
                        ft.Column(spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                            ft.Icon(ft.Icons.GRASS_ROUNDED, color="green700", size=40),
                            ft.Text("What are you growing?", size=20, weight="bold", color="green900", text_align=ft.TextAlign.CENTER),
                            ft.Text("Type in your crop and we'll handle the rest", size=13, color="grey500", text_align=ft.TextAlign.CENTER),
                        ]),
                        crop_field, status,
                        green_btn("Analyze", on_analyze, width=320, height=52),
                    ],
                ),
            ),
        ])

    # ── ANALYSIS RESULT ─────────────────────────────────
    def show_analysis(crop_name, email):
        # BACKEND: POST to Groq API — crop_name, user lat/lon, soil_ph from ISRIC SoilGrids
        # BACKEND: Returns JSON: {irrigation_mm_per_day, soil_type, growth_weeks,
        #                         nitrogen_kg_ha, phosphorus_kg_ha, potassium_kg_ha, farming_difficulty}
        # BACKEND: INSERT result into Supabase soil_analyses table

        # Placeholder values — replaced by Groq response in Sprint 2
        irrigation_val = ft.Text("4.2 mm/day",size=20,weight="bold", color="green800")
        soil_type_val  = ft.Text("Loamy",size=20,weight="bold",color="green800")
        growth_val  = ft.Text("12 weeks", size=20, weight="bold", color="green800")
        nitrogen_val  = ft.Text("45.0 kg/ha",size=15, weight="bold",color="green700")
        phosphorus_val = ft.Text("22.5 kg/ha",size=15, weight="bold", color="green700")
        potassium_val  = ft.Text("30.0 kg/ha", size=15, weight="bold", color="green700")
        difficulty  = "Medium"  # BACKEND: Replace with Groq farming_difficulty field

        def go_home(e):
            home_page(email)

        def go_irrigation(e):
            show_daily_alert(crop_name, "4.2", email)

        def metric_card(title, value_widget, icon, color):
            return ft.Container(
                content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6,
                    controls=[ft.Icon(icon, color=color, size=26), ft.Text(title, size=11, color="grey600"), value_widget]),
                bgcolor="white", border_radius=20, padding=16, expand=True,
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.with_opacity(0.08, "green900")),
            )

        def fert_row(label, val):
            return ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[ft.Text(label, size=14, color="grey700"), val])

        header_card = card(ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(spacing=4, controls=[
                    ft.Text("Crop",    size=12, color="grey600"),
                    ft.Text(crop_name, size=22, weight="bold", color="green900"),
                ]),
                ft.Column(spacing=6, horizontal_alignment=ft.CrossAxisAlignment.END, controls=[
                    status_badge("Analyzed", ft.Colors.GREEN_700),
                    ft.Container(
                        content=ft.Row(spacing=5, controls=[
                            ft.Icon(DIFF_ICON[difficulty], color="white", size=12),
                            ft.Text(difficulty, size=11, color="white", weight="bold"),
                        ]),
                        bgcolor=diff_color[difficulty], border_radius=8,
                        padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                    ),
                ]),
            ],
        ))

        difficulty_card = ft.Container(
            content=ft.Column(spacing=10, controls=[
                ft.Row(spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                    ft.Icon(DIFF_ICON[difficulty], color=diff_color[difficulty], size=22),
                    ft.Text("Growing Difficulty", size=15, weight="bold", color="green900"),
                    status_badge(difficulty, diff_color[difficulty]),
                ]),
                ft.Divider(color="green100"),
                ft.Text(DIFF_DESCRIPTION[difficulty], size=13, color="grey700"),
                ft.Container(
                    content=ft.Row(spacing=8, controls=[
                        ft.Icon(ft.Icons.INFO_OUTLINE, color="green600", size=14),
                        ft.Text("Scored using soil pH and regional climate via Groq AI", size=11, color="grey500", expand=True),
                    ]),
                    bgcolor="#f0f7f0", border_radius=8, padding=ft.Padding(left=10, right=10, top=8, bottom=8)),
            ]),
            bgcolor="white", border_radius=16, padding=16,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.with_opacity(0.08, "green900")),
        )

        irrigation_banner = ft.Container(
            content=ft.Row(spacing=10, controls=[
                ft.Icon(ft.Icons.WATER_DROP, color="white", size=18),
                ft.Column(spacing=1, expand=True, controls=[
                    ft.Text("Daily Irrigation Alert",           size=14, weight="bold", color="white"),
                    ft.Text("Tap to view today's water schedule", size=11,              color="#c8e6c9"),
                ]),
                ft.Icon(ft.Icons.ARROW_FORWARD_IOS, color="white", size=14),
            ]),
            bgcolor="green700", border_radius=16, padding=16,
            on_click=go_irrigation, ink=True,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.with_opacity(0.15, "green900")),
        )

        switch_pages([
            appbar(f"{crop_name} Analysis", back_bttn=go_home),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=16, bottom=20),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO, spacing=16,
                    controls=[
                        header_card,
                        ft.Row(spacing=12, controls=[
                            metric_card("Irrigation", irrigation_val, ft.Icons.WATER_DROP, "blue700"),
                            metric_card("Soil Type",  soil_type_val,  ft.Icons.LANDSCAPE,  "brown400"),
                        ]),
                        ft.Row(spacing=12, controls=[
                            metric_card("Growth Time", growth_val, ft.Icons.SCHEDULE, "green600"),
                        ]),
                        difficulty_card,
                        card(ft.Column(spacing=12, controls=[
                            ft.Text("Fertilizer Recommendation", size=16, weight="bold", color="green900"),
                            ft.Divider(color="green100"),
                            fert_row("Nitrogen (N)",   nitrogen_val),
                            fert_row("Phosphorus (P)", phosphorus_val),
                            fert_row("Potassium (K)",  potassium_val),
                        ])),
                        irrigation_banner,
                    ],
                ),
            ),
        ])

    # ── DAILY IRRIGATION ALERT ───────────────────────────
    def show_daily_alert(crop_name, base_irrigation, email):
        # 1. Initialize safe fallback dictionary to prevent crashes
        weather = {"temp": "--", "humidity": "--", "wind": "--", "rain_forecast": "0.0"}
        base_mm = 0.0
        try:
            base_mm = float(base_irrigation)
        except ValueError:
            pass

        # 2. Fetch live atmospheric data from your backend engine
        try:
            test_lat, test_lon = 48.8566, 2.3522  # Standard test coordinates
            weather_data = get_weather(test_lat, test_lon)
            if weather_data:
                weather["temp"] = str(weather_data.get("temp", "--"))
                weather["humidity"] = str(weather_data.get("humidity", "--"))
                weather["wind"] = str(weather_data.get("wind", "--"))
                # Use a fallback value if your API plan doesn't include pop/rain data fields
                weather["rain_forecast"] = str(weather_data.get("rain", 0.0))
        except Exception as weather_err:
            print(f"⚠️ Daily Alert screen weather fallback triggered: {weather_err}")

        # 3. Apply the Smart Irrigation offset calculation math safely
        try:
            rain_mm = float(weather["rain_forecast"])
        except ValueError:
            rain_mm = 0.0

        # Dynamic watering calculation: subtract the natural rain from the baseline needed
        recommended_mm = max(0.0, base_mm - rain_mm)
        
        # Split recommended volume into 3 clean scheduling intervals
        interval_split = round(recommended_mm / 3, 1)

        def go_back(e):
            show_analysis(crop_name, email)

        def info_row(icon, icon_color, label, value):
            return ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(spacing=8, controls=[ft.Icon(icon, color=icon_color, size=18), ft.Text(label, size=13, color="grey700")]),
                    ft.Text(value, size=13, weight="bold", color="green900"),
                ],
            )

        def schedule_box(icon, icon_color, label, time_str):
            return ft.Container(
                content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, controls=[
                    ft.Icon(icon, color=icon_color, size=22),
                    ft.Text(label,    size=12, weight="bold", color="green900"),
                    ft.Text(time_str, size=11,               color="grey500"),
                    ft.Text(f"{interval_split} mm",  size=13, weight="bold", color="green700"),
                ]),
                expand=True, bgcolor="#f0f7f0", border_radius=12, padding=12, alignment=ft.Alignment(0, 0),
            )

        switch_pages([
            appbar("Daily Irrigation Alert", back_bttn=go_back),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=16, bottom=24),
                content=ft.Column(scroll=ft.ScrollMode.AUTO, spacing=16, controls=[

                    ft.Container(
                        content=ft.Row(spacing=12, controls=[
                            ft.Container(content=ft.Icon(ft.Icons.GRASS, color="white", size=22), bgcolor="green700", border_radius=12, padding=10),
                            ft.Column(spacing=2, controls=[
                                ft.Text("Crop",    size=11, color="grey500"),
                                ft.Text(crop_name, size=18, weight="bold", color="green900"),
                            ]),
                        ]),
                        bgcolor="white", border_radius=16, padding=16,
                        shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color=ft.Colors.with_opacity(0.07, "green900"))),

                    ft.Container(
                        content=ft.Column(spacing=12, controls=[
                            ft.Row(spacing=8, controls=[
                                ft.Icon(ft.Icons.WB_SUNNY_OUTLINED, color="white", size=20),
                                ft.Text("Today's Weather", size=14, weight="bold", color="white"),
                            ]),
                            ft.Divider(color=ft.Colors.with_opacity(0.3, "white")),
                            ft.Row(alignment=ft.MainAxisAlignment.SPACE_AROUND, controls=[
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
                            ]),
                        ]),
                        bgcolor="green700", border_radius=20, padding=20,
                        shadow=ft.BoxShadow(spread_radius=1, blur_radius=12, color=ft.Colors.with_opacity(0.15, "green900"))),

                    card(ft.Column(spacing=14, controls=[
                        ft.Text("Water Calculation", size=15, weight="bold", color="green900"),
                        ft.Divider(color="green100"),
                        info_row(ft.Icons.WATER_DROP, "blue700", f"Base irrigation for {crop_name}", f"{base_mm} mm/day"),
                        info_row(ft.Icons.UMBRELLA,   "blue400", "Expected rainfall today",           f"{weather['rain_forecast']} mm"),
                        ft.Divider(color="green100"),
                        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                            ft.Text("Recommended today", size=15, weight="bold", color="green900"),
                            ft.Container(content=ft.Text(f"{recommended_mm} mm", size=16, weight="bold", color="white"),
                                bgcolor="green700", border_radius=10, padding=ft.Padding(left=14, right=14, top=6, bottom=6)),
                        ]),
                    ])),

                    card(ft.Column(spacing=12, controls=[
                        ft.Text("Suggested Schedule", size=15, weight="bold", color="green900"),
                        ft.Divider(color="green100"),
                        ft.Row(spacing=12, controls=[
                            schedule_box(ft.Icons.WB_TWILIGHT, "orange600", "Morning",   "6:00 AM"),
                            schedule_box(ft.Icons.WB_SUNNY,    "yellow700", "Afternoon", "2:00 PM"),
                            schedule_box(ft.Icons.NIGHTS_STAY, "blue700",   "Evening",   "6:00 PM"),
                        ]),
                    ])),

                    ft.Text("* Live weather data requires OpenWeatherMap API and location to be set.",
                        size=11, color="grey400", italic=True, text_align=ft.TextAlign.CENTER),
                ]),
            ),
        ])

    # ── FORUM ───────────────────────────────────────────
    def forum_page(email=""):
        # 1. Fetch live community posts from your backend engine
        db_posts = get_forum_posts(limit=50)
        
        # Format database rows into UI-ready dictionaries
        posts = []
        for p in db_posts:
            # Clean up author display handles
            display_name = p.get("author_name", "Anonymous Farmer")
            if not display_name or display_name == "Anonymous Farmer":
                raw_uid = p.get("user_id", "")
                if "@" in raw_uid:
                    display_name = raw_uid.split("@")[0].capitalize()

            posts.append({
                "author": display_name,
                "time": "Recent",
                "text": p.get("content", ""),
                "likes": "0",
                "replies": "0"
            })

        # Fallback card if the global message timeline is completely empty
        if not posts:
            posts = [{"author": "System", "time": "Now", "text": "Welcome to the Soilco Community Forum! Start the conversation below.", "likes": "0", "replies": "0"}]

        def post_card(item):
            return ft.Container(
                content=ft.Column(spacing=8, controls=[
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                        ft.Row(spacing=8, controls=[
                            ft.CircleAvatar(content=ft.Text(item["author"][0].upper() if item["author"] else "?", color="white", size=12, weight="bold"), bgcolor="green700", radius=16),
                            ft.Column(spacing=1, controls=[
                                ft.Text(item["author"], size=13, weight="bold", color="green900"),
                                ft.Text(item["time"],   size=10,               color="grey500"),
                            ]),
                        ]),
                        ft.Icon(ft.Icons.MORE_VERT, color="grey400", size=18),
                    ]),
                    ft.Text(item["text"], size=13, color="grey800"),
                    ft.Divider(height=1, color="grey100"),
                    ft.Row(alignment=ft.MainAxisAlignment.START, spacing=16, controls=[
                        ft.Row(spacing=4, controls=[ft.Icon(ft.Icons.THUMB_UP_OUTLINED, size=14, color="grey500"), ft.Text(item["likes"], size=11, color="grey500")]),
                        ft.Row(spacing=4, controls=[ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, size=14, color="grey500"), ft.Text(item["replies"], size=11, color="grey500")]),
                    ]),
                ]),
                bgcolor="white", border_radius=14, padding=14,
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=6, color=ft.Colors.with_opacity(0.04, "green900")),
            )

        # Text Controller to capture typing input from the keyboard
        post_input = ft.TextField(
            hint_text="Share an update or ask a farming question...",
            hint_style=ft.TextStyle(size=13, color="grey400"),
            border=ft.InputBorder.NONE, multiline=True, min_lines=1, max_lines=3,
            text_style=ft.TextStyle(size=13, color="green900"),
        )

        # 2. This function fires when the user clicks the "Post" button
        def handle_submit_post(e):
            text_to_save = post_input.value.strip()
            if not text_to_save:
                return # Ignore empty submission attempts

            # Extract author handle name based on user's identity email
            farmer_author = email.split("@")[0].capitalize() if email else "Farmer"
            
            # Save directly into your Supabase public table row
            success = post_to_forum(user_id=email, author_name=farmer_author, content=text_to_save)
            
            if success:
                post_input.value = "" # Empty out input box
                forum_page(email)     # Refresh timeline views to display it instantly

        input_container = ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(content=post_input, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.SEND_ROUNDED, 
                        icon_color="white", 
                        bgcolor="green700",
                        icon_size=18,
                        on_click=handle_submit_post  # Connect click handler
                    ),
                ],
            ),
            bgcolor="white", border_radius=24, padding=ft.Padding(left=16, right=8, top=4, bottom=4),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color=ft.Colors.with_opacity(0.06, "green900")),
        )

        switch_pages([
            ft.Container(
                expand=True, bgcolor="#f5f7f5",
                padding=ft.Padding(left=16, right=16, top=50, bottom=20),
                content=ft.Column(
                    spacing=14,
                    controls=[
                        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                            ft.Text("Community Forum", size=20, weight="bold", color="green900"),
                            ft.Icon(ft.Icons.PEOPLE_ROUNDED, color="green700", size=24),
                        ]),
                        input_container,

                        ft.ListView(
                             controls=locals().get('timeline_posts', []),
                             expand=True,
                             spacing=10,
                        )
                    ],
                ),
            ),
            nav_bar("Forum", email),
        ])

    # ── FORUM ───────────────────────────────────────────
    def forum_page(email=""):
        # 1. Fetch live community posts from your backend engine
        db_posts = get_forum_posts(limit=50)
        
        # Format database rows into UI-ready dictionaries
        posts = []
        for p in db_posts:
            # Clean up author display handles
            display_name = p.get("author_name", "Anonymous Farmer")
            if not display_name or display_name == "Anonymous Farmer":
                raw_uid = p.get("user_id", "")
                if "@" in raw_uid:
                    display_name = raw_uid.split("@")[0].capitalize()

            posts.append({
                "author": display_name,
                "time": "Recent",
                "text": p.get("content", ""),
                "likes": "0",
                "replies": "0"
            })

        # Fallback card if the global message timeline is completely empty
        if not posts:
            posts = [{"author": "System", "time": "Now", "text": "Welcome to the Soilco Community Forum! Start the conversation below.", "likes": "0", "replies": "0"}]

        def post_card(item):
            return ft.Container(
                content=ft.Column(spacing=8, controls=[
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                        ft.Row(spacing=8, controls=[
                            ft.CircleAvatar(content=ft.Text(item["author"][0].upper() if item["author"] else "?", color="white", size=12, weight="bold"), bgcolor="green700", radius=16),
                            ft.Column(spacing=1, controls=[
                                ft.Text(item["author"], size=13, weight="bold", color="green900"),
                                ft.Text(item["time"],   size=10,               color="grey500"),
                            ]),
                        ]),
                        ft.Icon(ft.Icons.MORE_VERT, color="grey400", size=18),
                    ]),
                    ft.Text(item["text"], size=13, color="grey800"),
                    ft.Divider(height=1, color="grey100"),
                    ft.Row(alignment=ft.MainAxisAlignment.START, spacing=16, controls=[
                        ft.Row(spacing=4, controls=[ft.Icon(ft.Icons.THUMB_UP_OUTLINED, size=14, color="grey500"), ft.Text(item["likes"], size=11, color="grey500")]),
                        ft.Row(spacing=4, controls=[ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, size=14, color="grey500"), ft.Text(item["replies"], size=11, color="grey500")]),
                    ]),
                ]),
                bgcolor="white", border_radius=14, padding=14,
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=6, color=ft.Colors.with_opacity(0.04, "green900")),
            )

        # Map our raw post data into live Flet post_card UI controls
        timeline_items = [post_card(item) for item in posts]

        # Text Controller to capture typing input from the keyboard
        post_input = ft.TextField(
            hint_text="Share an update or ask a farming question...",
            hint_style=ft.TextStyle(size=13, color="grey400"),
            border=ft.InputBorder.NONE, multiline=True, min_lines=1, max_lines=3,
            text_style=ft.TextStyle(size=13, color="green900"),
        )

        # 2. This function fires when the user clicks the "Post" button
        def handle_submit_post(e):
            text_to_save = post_input.value.strip()
            if not text_to_save:
                return # Ignore empty submission attempts

            # Extract author handle name based on user's identity email
            farmer_author = email.split("@")[0].capitalize() if email else "Farmer"
            
            # Save directly into your Supabase public table row
            success = post_to_forum(user_id=email, author_name=farmer_author, content=text_to_save)
            
            if success:
                post_input.value = "" # Empty out input box
                forum_page(email)     # Refresh timeline views to display it instantly

        input_container = ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(content=post_input, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.SEND_ROUNDED, 
                        icon_color="white", 
                        bgcolor="green700",
                        icon_size=18,
                        on_click=handle_submit_post  # Connect click handler
                    ),
                ],
            ),
            bgcolor="white", border_radius=24, padding=ft.Padding(left=16, right=8, top=4, bottom=4),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color=ft.Colors.with_opacity(0.06, "green900")),
        )

        switch_pages([
            ft.Container(
                expand=True, bgcolor="#f5f7f5",
                padding=ft.Padding(left=16, right=16, top=50, bottom=20),
                content=ft.Column(
                    spacing=14,
                    controls=[
                        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                            ft.Text("Community Forum", size=20, weight="bold", color="green900"),
                            ft.Icon(ft.Icons.PEOPLE_ROUNDED, color="green700", size=24),
                        ]),
                        input_container,

                        ft.ListView(
                             controls=timeline_items,
                             expand=True,
                             spacing=10,
                        )
                    ],
                ),
            ),
            nav_bar("Forum", email),
        ])

    # ── PROFILE ──────────────────────────────────────────
    def profile_page(email=""):
        farmer_name = email.split("@")[0].capitalize() if email else "Farmer"

        # This function fires automatically every time a switch is flipped
        def save_settings(e):
            # Safe database update execution
            update_user_preferences(
                user_id=email,
                irrigation_alerts=irrigation_switch.value,
                weekly_reports=reports_switch.value
            )

        # UI Toggles equipped with state event listeners
        irrigation_switch = ft.Switch(value=True, active_color="green700", on_change=save_settings)
        reports_switch = ft.Switch(value=False, active_color="green700", on_change=save_settings)

        def settings_row(icon, title, subtitle, control):
            return ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(spacing=12, controls=[
                            ft.Container(content=ft.Icon(icon, color="green700", size=20), bgcolor="#e8f5e9", border_radius=10, padding=8),
                            ft.Column(spacing=2, controls=[
                                ft.Text(title, size=14, weight="bold", color="green900"),
                                ft.Text(subtitle, size=11, color="grey500"),
                            ]),
                        ]),
                        control,
                    ],
                ),
                bgcolor="white", border_radius=14, padding=12,
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=6, color=ft.Colors.with_opacity(0.04, "green900")),
            )

        switch_pages([
            ft.Container(
                expand=True, bgcolor="#f5f7f5",
                padding=ft.Padding(left=16, right=16, top=50, bottom=20),
                content=ft.Column(
                    spacing=20,
                    controls=[
                        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                            ft.Text("Profile Settings", size=20, weight="bold", color="green900"),
                            ft.Icon(ft.Icons.SETTINGS_ROUNDED, color="green700", size=24),
                        ]),
                        # User Identity Badge Card
                        ft.Container(
                            content=ft.Row(spacing=16, controls=[
                                ft.CircleAvatar(content=ft.Text(farmer_name[0].upper() if farmer_name else "U", color="white", size=18, weight="bold"), bgcolor="green700", radius=28),
                                ft.Column(spacing=4, controls=[
                                    ft.Text(farmer_name, size=18, weight="bold", color="green900"),
                                    ft.Text(email if email else "farmer@soilco.com", size=12, color="grey500"),
                                ]),
                            ]),
                            bgcolor="white", border_radius=16, padding=16,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color=ft.Colors.with_opacity(0.04, "green900")),
                        ),
                        # Notifications Section
                        ft.Column(spacing=10, controls=[
                            ft.Text("Notification Preferences", size=14, weight="bold", color="green800"),
                            settings_row(ft.Icons.WATER_DROP_ROUNDED, "Irrigation Alerts", "Smart watering recommendation warnings", irrigation_switch),
                            settings_row(ft.Icons.ASSESSMENT_ROUNDED, "Weekly Health Reports", "Summary of historical soil performance metrics", reports_switch),
                        ]),
                        # Danger Zone / Logout Section
                        ft.Column(spacing=10, controls=[
                            ft.Text("Account Actions", size=14, weight="bold", color="green800"),
                            ft.Container(
                                content=ft.Row(spacing=12, controls=[
                                    ft.Icon(ft.Icons.LOGOUT_ROUNDED, color="red400", size=20),
                                    ft.Text("Log Out of Account", size=14, weight="bold", color="red400"),
                                ]),
                                bgcolor="white", border_radius=14, padding=14,
                                shadow=ft.BoxShadow(spread_radius=1, blur_radius=6, color=ft.Colors.with_opacity(0.02, "green900")),
                                on_click=lambda e: login_page(),
                            ),
                        ]),
                    ],
                ),
            ),
            nav_bar("Profile", email),
        ])

    # ── START ────────────────────────────────────────────
    login_page()

if __name__ == "__main__":
    ft.run(main)