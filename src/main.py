import flet as ft
import time
import threading
import os
from backend.analysis_service import analyze_crop, get_coords_from_city
from backend.weather_service import get_weather, calculate_irrigation_advice
from backend.forum_service import get_forum_posts, post_to_forum
from backend.database_service import save_analysis, get_recent_analyses, update_user_preferences
from backend.auth_service import sign_in, sign_up, sign_out, reset_password, update_password, update_profile

welcome_flag = os.path.join(os.path.expanduser("~"), ".soilco_onboarding_seen")

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

# shared location and session state — updated on login and profile save
current_location = {"city": "Abuja", "lat": 9.0643305, "lon": 7.4892974}
current_user     = {"id": "", "email": "", "name": ""}


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
        sub_color  = "#c8e6c9" if light else ft.Colors.GREEN_600
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
    def splash_screen():
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

    # login
    def login_page():
        email_field = ft.TextField(label="Email", prefix_icon=ft.Icons.EMAIL_OUTLINED, width=300,
            border_radius=15, border_color="green700",
            keyboard_type=ft.KeyboardType.EMAIL, bgcolor="white")
        password_field = ft.TextField(label="Password", prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True, can_reveal_password=True, width=300,
            border_radius=15, border_color=ft.Colors.GREEN_700, bgcolor="white")
        status = ft.Text("", size=14)

        def login_pressed(e):
            if not email_field.value or not password_field.value:
                status.value = "fill in all fields"
                status.color = "red"
                page.update()
                return

            result = sign_in(email_field.value, password_field.value)
            if result["success"]:
                current_user["id"]    = result["user"].id
                current_user["email"] = result["user"].email
                home_page(result["user"].email)
            else:
                status.value = result.get("error", "login failed")
                status.color = "red"
                page.update()

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
                ft.TextButton("Sign Up", on_click=go_signup, style=ft.ButtonStyle(color=ft.Colors.GREEN_700)),
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

    # signup
    def signUp_page():
        name_field = ft.TextField(label="Full Name", prefix_icon=ft.Icons.PERSON_OUTLINE, width=300,
            border_radius=15, border_color=ft.Colors.GREEN_700, focused_border_color=ft.Colors.GREEN_900, bgcolor="white")
        email_field = ft.TextField(label="Email", prefix_icon=ft.Icons.EMAIL_OUTLINED, width=300,
            border_radius=15, border_color=ft.Colors.GREEN_700, focused_border_color=ft.Colors.GREEN_900,
            keyboard_type=ft.KeyboardType.EMAIL, bgcolor="white")
        password_field = ft.TextField(label="Password", prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True, can_reveal_password=True, width=300,
            border_radius=15, border_color=ft.Colors.GREEN_700, focused_border_color=ft.Colors.GREEN_900, bgcolor="white")
        status = ft.Text("", size=14)

        def CreateAcctPressed(e):
            if not name_field.value or not email_field.value or not password_field.value:
                status.value = "fill in all fields"
                status.color = "red"
                page.update()
                return

            result = sign_up(name_field.value, email_field.value, password_field.value)
            if result["success"]:
                current_user["id"]    = result["user"].id
                current_user["email"] = result["user"].email
                current_user["name"]  = name_field.value
                home_page(result["user"].email)
            else:
                status.value = result.get("error", "signup failed")
                status.color = "red"
                page.update()

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
                page.update()
                return
            result = reset_password(email_field.value)
            if result["success"]:
                status.value = f"Reset link sent to {email_field.value}"
                status.color = "green700"
            else:
                status.value = result.get("error", "reset failed")
                status.color = "red"
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
        farmer_name = email.split("@")[0].capitalize() if email else "Farmer"

        # live widgets updated by background thread
        temp_text     = ft.Text("-- °C",                   size=32, weight="bold", color="white")
        location_text = ft.Text(current_location["city"],  size=12,               color="#c8e6c9")
        hum_text      = ft.Text("Hum: --%",                size=11,               color="#c8e6c9")
        wind_text     = ft.Text("Wind: -- km/h",           size=11,               color="#c8e6c9")
        analyses_col  = ft.Column(spacing=10, controls=[
            ft.Text("Previous Analyses", size=16, weight="bold", color="green900"),
            ft.Text("Loading history...", size=13, color="grey500"),
        ])

        status_colors = {
            "Optimal": "green700", "Acidic": "orange700", "Alkaline": "blue700",
            "Easy": "green700", "Medium": "orange700", "Hard": "red700",
        }

        def open_analysis(crop_name):
            def handler(e):
                show_analysis(crop_name, email)
            return handler

        def prev_crop_card(item):
            crop  = item.get("crop_name") or item.get("crop", "Unknown")
            date  = (item.get("analyzed_at") or item.get("date", "--"))[:10]
            weeks = f"{item.get('growth_weeks') or item.get('weeks', '--')} wks"
            diff  = item.get("farming_difficulty") or item.get("status", "Optimal")
            badge_color = status_colors.get(diff, "grey500")
            return ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(spacing=12, controls=[
                            ft.Container(content=ft.Icon(ft.Icons.GRASS, color="white", size=18), bgcolor="green700", border_radius=10, padding=8),
                            ft.Column(spacing=2, controls=[
                                ft.Text(crop, size=14, weight="bold", color=ft.Colors.GREEN_900),
                                ft.Text(date, size=11,               color="grey500"),
                            ]),
                        ]),
                        ft.Column(horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2, controls=[
                            ft.Text(weeks, size=13, weight="bold", color="green800"),
                            ft.Container(content=ft.Text(diff, size=10, color="white"),
                                bgcolor=badge_color, border_radius=8, padding=ft.Padding(left=8, right=8, top=3, bottom=3)),
                        ]),
                    ],
                ),
                bgcolor="white", border_radius=14, padding=12,
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=6, color=ft.Colors.with_opacity(0.06, "green900")),
                on_click=open_analysis(crop), ink=True,
            )

        def load_home_data():
            # weather_service takes lat/lon directly
            lat = current_location["lat"]
            lon = current_location["lon"]
            w   = get_weather(lat, lon)
            if w:
                temp_text.value     = f"{w['temp']} °C"
                hum_text.value      = f"Hum: {w['humidity']}%"
                wind_text.value     = f"Wind: {w['wind']} km/h"
                location_text.value = current_location["city"]
                page.update()

            # get_recent_analyses fetches from supabase using real user_id
            history = get_recent_analyses(user_id=current_user["id"]) if current_user["id"] else None
            analyses_col.controls.clear()
            analyses_col.controls.append(
                ft.Text("Previous Analyses", size=16, weight="bold", color="green900")
            )
            if history:
                for item in history:
                    analyses_col.controls.append(prev_crop_card(item))
            else:
                for item in [
                    {"crop": "Maize", "date": "Feb 28", "weeks": "12", "status": "Optimal"},
                    {"crop": "Wheat", "date": "Feb 20", "weeks": "8",  "status": "Acidic"},
                    {"crop": "Rice",  "date": "Feb 10", "weeks": "16", "status": "Alkaline"},
                ]:
                    analyses_col.controls.append(prev_crop_card(item))
            page.update()

        threading.Thread(target=load_home_data, daemon=True).start()

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

        weather_widget = ft.Container(
            content=ft.Column(spacing=12, controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(spacing=4, controls=[
                            ft.Text("Current Weather", size=12, color="#c8e6c9"),
                            temp_text, location_text,
                        ]),
                        ft.Column(horizontal_alignment=ft.CrossAxisAlignment.END, spacing=6, controls=[
                            ft.Icon(ft.Icons.WB_SUNNY_OUTLINED, color="white", size=48),
                            ft.Row(spacing=2, controls=[
                                ft.Icon(ft.Icons.WATER_DROP_OUTLINED, color="#c8e6c9", size=12),
                                hum_text,
                            ]),
                            ft.Row(spacing=2, controls=[
                                ft.Icon(ft.Icons.AIR, color="#c8e6c9", size=12),
                                wind_text,
                            ]),
                        ]),
                    ],
                ),
            ]),
            bgcolor="green700", border_radius=20, padding=20,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.with_opacity(0.15, "green900")),
        )

        switch_pages([
            ft.Container(
                expand=True, bgcolor="white",
                padding=ft.Padding(left=16, right=16, top=50, bottom=20),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO, spacing=16,
                    controls=[greeting_row, weather_widget, analyses_col, ft.Container(height=70)],
                ),
            ),
            nav_bar("Home", email),
        ])

    # crop entry
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

    # analysis result
    def show_analysis(crop_name, email):
        irrigation_val = ft.Text("Loading...", size=20, weight="bold", color="green800")
        soil_type_val  = ft.Text("Loading...", size=20, weight="bold", color="green800")
        growth_val     = ft.Text("Loading...", size=20, weight="bold", color="green800")
        nitrogen_val   = ft.Text("Loading...", size=15, weight="bold", color="green700")
        phosphorus_val = ft.Text("Loading...", size=15, weight="bold", color="green700")
        potassium_val  = ft.Text("Loading...", size=15, weight="bold", color="green700")
        error_text     = ft.Text("", size=13, color="red", text_align=ft.TextAlign.CENTER)

        diff_badge_text = ft.Text("...", size=11, color="white", weight="bold")
        diff_icon_small = ft.Icon(ft.Icons.HOURGLASS_EMPTY, color="white", size=12)
        diff_badge_cont = ft.Container(
            content=ft.Row(spacing=5, controls=[diff_icon_small, diff_badge_text]),
            bgcolor=ft.Colors.GREY_400, border_radius=8,
            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
        )
        diff_icon_big  = ft.Icon(ft.Icons.HOURGLASS_EMPTY, color=ft.Colors.GREY_400, size=22)
        diff_desc_text = ft.Text("Analysing crop data...", size=13, color="grey700")
        diff_badge_row = ft.Container(
            content=ft.Row(spacing=5, controls=[
                ft.Icon(ft.Icons.HOURGLASS_EMPTY, color="white", size=12),
                ft.Text("...", size=11, color="white", weight="bold"),
            ]),
            bgcolor=ft.Colors.GREY_400, border_radius=8,
            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
        )

        irr_store = {"mm": "0"}

        def load_data():
            # analysis_service handles geocoding internally using current city
            result = analyze_crop(crop_name, location=current_location["city"])

            if not result or "error" in result:
                error_text.value = result.get("error", "Analysis failed.") if result else "Analysis failed."
                for w in [irrigation_val, soil_type_val, growth_val, nitrogen_val, phosphorus_val, potassium_val]:
                    w.value = "--"
                page.update()
                return

            d = result.get("farming_difficulty", "Medium")
            if d not in diff_color:
                d = "Medium"

            irr = result.get("irrigation_mm_per_day", "--")
            irr_store["mm"] = str(irr)

            irrigation_val.value  = f"{irr} mm/day"
            soil_type_val.value   = result.get("soil_type", "--")
            growth_val.value      = f"{result.get('growth_weeks', '--')} weeks"
            nitrogen_val.value    = f"{result.get('nitrogen_kg_ha', '--')} kg/ha"
            phosphorus_val.value  = f"{result.get('phosphorus_kg_ha', '--')} kg/ha"
            potassium_val.value   = f"{result.get('potassium_kg_ha', '--')} kg/ha"

            diff_badge_text.value   = d
            diff_icon_small.name    = DIFF_ICON[d]
            diff_badge_cont.bgcolor = diff_color[d]
            diff_icon_big.name      = DIFF_ICON[d]
            diff_icon_big.color     = diff_color[d]
            diff_desc_text.value    = DIFF_DESCRIPTION[d]
            diff_badge_row.content  = ft.Row(spacing=5, controls=[
                ft.Icon(DIFF_ICON[d], color="white", size=12),
                ft.Text(d, size=11, color="white", weight="bold"),
            ])
            diff_badge_row.bgcolor  = diff_color[d]
            page.update()

            # save_analysis stores result in supabase using real user_id
            if current_user["id"]:
                save_analysis(user_id=current_user["id"], crop_name=crop_name, analysis_data=result)

        threading.Thread(target=load_data, daemon=True).start()

        def go_home(e):
            home_page(email)

        def go_irrigation(e):
            show_daily_alert(crop_name, irr_store["mm"], email)

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
                    diff_badge_cont,
                ]),
            ],
        ))

        difficulty_card = ft.Container(
            content=ft.Column(spacing=10, controls=[
                ft.Row(spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                    diff_icon_big,
                    ft.Text("Growing Difficulty", size=15, weight="bold", color="green900"),
                    diff_badge_row,
                ]),
                ft.Divider(color="green100"),
                diff_desc_text,
                ft.Container(
                    content=ft.Row(spacing=8, controls=[
                        ft.Icon(ft.Icons.INFO_OUTLINE, color="green600", size=14),
                        ft.Text("Scored using soil pH and regional climate via Groq AI", size=11, color="grey500", expand=True),
                    ]),
                    bgcolor="#f0f7f0", border_radius=8,
                    padding=ft.Padding(left=10, right=10, top=8, bottom=8)),
            ]),
            bgcolor="white", border_radius=16, padding=16,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.with_opacity(0.08, "green900")),
        )

        irrigation_banner = ft.Container(
            content=ft.Row(spacing=10, controls=[
                ft.Icon(ft.Icons.WATER_DROP, color="white", size=18),
                ft.Column(spacing=1, expand=True, controls=[
                    ft.Text("Daily Irrigation Alert",             size=14, weight="bold", color="white"),
                    ft.Text("Tap to view today's water schedule", size=11,               color="#c8e6c9"),
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
                        header_card, error_text,
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

    # daily irrigation alert
    def show_daily_alert(crop_name, base_irrigation, email):
        # live weather widgets — updated by background thread
        temp_val    = ft.Text("-- °C",   size=15, weight="bold", color="white")
        hum_val     = ft.Text("--%",     size=15, weight="bold", color="white")
        rain_val    = ft.Text("-- mm",   size=15, weight="bold", color="white")
        wind_val    = ft.Text("-- km/h", size=15, weight="bold", color="white")
        rain_info   = ft.Text("-- mm",   size=13, weight="bold", color="green900")
        rec_val     = ft.Text("-- mm",   size=16, weight="bold", color="white")
        advice_text = ft.Text("",        size=12, color="grey600", italic=True)

        # schedule boxes — split adjusted irrigation across 3 sessions
        morning_mm   = ft.Text("-- mm", size=13, weight="bold", color="green700")
        afternoon_mm = ft.Text("-- mm", size=13, weight="bold", color="green700")
        evening_mm   = ft.Text("-- mm", size=13, weight="bold", color="green700")

        try:
            base_mm = float(base_irrigation)
        except (ValueError, TypeError):
            base_mm = 0.0

        def load_weather():
            # weather_service takes lat/lon directly — no geocoding needed
            lat = current_location["lat"]
            lon = current_location["lon"]
            w   = get_weather(lat, lon)
            if not w:
                return

            rain_mm  = w.get("rain", 0.0)
            adjusted = max(0.0, base_mm - rain_mm)

            # split across 3 watering sessions
            session = round(adjusted / 3, 1)

            temp_val.value     = f"{w['temp']} °C"
            hum_val.value      = f"{w['humidity']}%"
            rain_val.value     = f"{rain_mm} mm"
            wind_val.value     = f"{w['wind']} km/h"
            rain_info.value    = f"{rain_mm} mm"
            rec_val.value      = f"{adjusted} mm"
            morning_mm.value   = f"{session} mm"
            afternoon_mm.value = f"{session} mm"
            evening_mm.value   = f"{session} mm"

            # calculate_irrigation_advice gives smart watering tip based on temp + humidity
            advice = calculate_irrigation_advice(w["temp"], w["humidity"])
            advice_text.value  = advice["advice"]
            page.update()

        threading.Thread(target=load_weather, daemon=True).start()

        def go_back(e):
            show_analysis(crop_name, email)

        def info_row(icon, icon_color, label, value_widget):
            return ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(spacing=8, controls=[ft.Icon(icon, color=icon_color, size=18), ft.Text(label, size=13, color="grey700")]),
                    value_widget,
                ],
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
                                    temp_val,
                                    ft.Text("Temp", size=10, color="#c8e6c9"),
                                ]),
                                ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, controls=[
                                    ft.Icon(ft.Icons.WATER_DROP_OUTLINED, color="white", size=20),
                                    hum_val,
                                    ft.Text("Humidity", size=10, color="#c8e6c9"),
                                ]),
                                ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, controls=[
                                    ft.Icon(ft.Icons.UMBRELLA, color="white", size=20),
                                    rain_val,
                                    ft.Text("Rain", size=10, color="#c8e6c9"),
                                ]),
                                ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, controls=[
                                    ft.Icon(ft.Icons.AIR, color="white", size=20),
                                    wind_val,
                                    ft.Text("Wind", size=10, color="#c8e6c9"),
                                ]),
                            ]),
                        ]),
                        bgcolor="green700", border_radius=20, padding=20,
                        shadow=ft.BoxShadow(spread_radius=1, blur_radius=12, color=ft.Colors.with_opacity(0.15, "green900"))),

                    card(ft.Column(spacing=14, controls=[
                        ft.Text("Water Calculation", size=15, weight="bold", color="green900"),
                        ft.Divider(color="green100"),
                        info_row(ft.Icons.WATER_DROP, "blue700", f"Base irrigation for {crop_name}",
                            ft.Text(f"{base_mm} mm/day", size=13, weight="bold", color="green900")),
                        info_row(ft.Icons.UMBRELLA, "blue400", "Expected rainfall today", rain_info),
                        ft.Divider(color="green100"),
                        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                            ft.Text("Recommended today", size=15, weight="bold", color="green900"),
                            ft.Container(content=rec_val, bgcolor="green700", border_radius=10,
                                padding=ft.Padding(left=14, right=14, top=6, bottom=6)),
                        ]),
                        advice_text,
                    ])),

                    card(ft.Column(spacing=12, controls=[
                        ft.Text("Suggested Schedule", size=15, weight="bold", color="green900"),
                        ft.Divider(color="green100"),
                        ft.Row(spacing=12, controls=[
                            ft.Container(
                                content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, controls=[
                                    ft.Icon(ft.Icons.WB_TWILIGHT, color="orange600", size=22),
                                    ft.Text("Morning",  size=12, weight="bold", color="green900"),
                                    ft.Text("6:00 AM",  size=11,               color="grey500"),
                                    morning_mm,
                                ]),
                                expand=True, bgcolor="#f0f7f0", border_radius=12, padding=12, alignment=ft.Alignment(0, 0),
                            ),
                            ft.Container(
                                content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, controls=[
                                    ft.Icon(ft.Icons.WB_SUNNY, color="yellow700", size=22),
                                    ft.Text("Afternoon", size=12, weight="bold", color="green900"),
                                    ft.Text("2:00 PM",   size=11,               color="grey500"),
                                    afternoon_mm,
                                ]),
                                expand=True, bgcolor="#f0f7f0", border_radius=12, padding=12, alignment=ft.Alignment(0, 0),
                            ),
                            ft.Container(
                                content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, controls=[
                                    ft.Icon(ft.Icons.NIGHTS_STAY, color="blue700", size=22),
                                    ft.Text("Evening",  size=12, weight="bold", color="green900"),
                                    ft.Text("6:00 PM",  size=11,               color="grey500"),
                                    evening_mm,
                                ]),
                                expand=True, bgcolor="#f0f7f0", border_radius=12, padding=12, alignment=ft.Alignment(0, 0),
                            ),
                        ]),
                    ])),

                    ft.Text("* requires OWM_API_KEY in .env for live weather data",
                        size=11, color="grey400", italic=True, text_align=ft.TextAlign.CENTER),
                ]),
            ),
        ])

    # forum
    def forum_page(email):
        farmer_name = current_user["name"] or email.split("@")[0].capitalize() if email else "Farmer"

        msg_space = ft.TextField(
            hint_text="Write something...", border_radius=20,
            border_color="green200", focused_border_color="green700",
            bgcolor="white", expand=True, min_lines=1, max_lines=4,
            content_padding=ft.Padding(left=16, right=16, top=10, bottom=10),
        )
        posts_column = ft.Column(spacing=10, controls=[
            ft.Text("Loading posts...", size=13, color="grey500")
        ])

        def post_card(post_data):
            author = post_data.get("author_name") or post_data.get("author", "Farmer")
            text   = post_data.get("content")    or post_data.get("text",   "")
            time_s = str(post_data.get("created_at") or post_data.get("time", "Just now"))
            if len(time_s) > 10:
                time_s = time_s[:10]

            def on_reply(e):
                msg_space.value = f"@{author} "
                page.update()

            return ft.Container(
                content=ft.Column(spacing=8, controls=[
                    ft.Row(spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                        ft.Container(content=ft.Text(author[0], size=13, color="white", weight="bold"),
                            bgcolor="green700", border_radius=16, width=32, height=32, alignment=ft.Alignment(0, 0)),
                        ft.Column(spacing=1, controls=[
                            ft.Text(author, size=13, weight="bold", color="green900"),
                            ft.Text(time_s, size=10,               color="grey400"),
                        ]),
                    ]),
                    ft.Text(text, size=13, color="grey800"),
                    ft.Row(alignment=ft.MainAxisAlignment.END, controls=[
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
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=6, color=ft.Colors.with_opacity(0.06, "green900")),
            )

        def load_posts():
            # get_forum_posts fetches from supabase
            posts = get_forum_posts(limit=50)
            posts_column.controls.clear()
            if posts:
                for p in posts:
                    posts_column.controls.append(post_card(p))
            else:
                for p in [
                    {"author": "Alice", "text": "Best time to plant maize in Nairobi?",                  "time": "2h ago"},
                    {"author": "Bob",   "text": "Anyone tried SRI method for rice? Great results!",       "time": "5h ago"},
                    {"author": "Carol", "text": "My beans are yellowing — could be nitrogen deficiency?", "time": "1d ago"},
                ]:
                    posts_column.controls.append(post_card(p))
            page.update()

        threading.Thread(target=load_posts, daemon=True).start()

        def send(e):
            message_text = msg_space.value.strip() if msg_space.value else ""
            if not message_text:
                return
            # post_to_forum saves to supabase using real user_id
            post_to_forum(user_id=current_user["id"], author_name=farmer_name, content=message_text)
            posts_column.controls.insert(0, post_card({"author": farmer_name, "text": message_text, "time": "Just now"}))
            msg_space.value = ""
            page.update()

        switch_pages([
            appbar("Farmers Group"),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                content=ft.Column(spacing=0, controls=[
                    ft.Container(
                        content=ft.Row(spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                            ft.Container(content=ft.Icon(ft.Icons.GRASS_ROUNDED, color="white", size=20),
                                bgcolor="green700", border_radius=20, width=40, height=40, alignment=ft.Alignment(0, 0)),
                            ft.Column(spacing=2, controls=[
                                ft.Text("Soilco Farmers",       size=14, weight="bold", color="green900"),
                                ft.Text("Open community group", size=11,               color="grey500"),
                            ]),
                        ]),
                        bgcolor="white", padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                        shadow=ft.BoxShadow(spread_radius=0, blur_radius=4, color=ft.Colors.with_opacity(0.05, "green900"))),
                    ft.Container(expand=True,
                        padding=ft.Padding(left=16, right=16, top=12, bottom=8),
                        content=ft.Column(scroll=ft.ScrollMode.AUTO, spacing=0,
                            controls=[posts_column, ft.Container(height=70)])),
                    ft.Container(
                        content=ft.Row(spacing=10, controls=[
                            msg_space,
                            ft.Container(content=ft.Icon(ft.Icons.SEND, color="white", size=18),
                                bgcolor="green700", border_radius=20, width=44, height=44,
                                alignment=ft.Alignment(0, 0), on_click=send, ink=True),
                        ]),
                        bgcolor="white", padding=ft.Padding(left=12, right=12, top=10, bottom=10),
                        shadow=ft.BoxShadow(spread_radius=0, blur_radius=8, color=ft.Colors.with_opacity(0.08, "green900"), offset=ft.Offset(0, -2))),
                ]),
            ),
            nav_bar("Forum", email),
        ])

    # notifications
    def show_notifications(email):
        daily_switch  = ft.Switch(value=True,  active_color="green700")
        rain_switch   = ft.Switch(value=False, active_color="green700")
        weekly_switch = ft.Switch(value=True,  active_color="green700")
        tips_switch   = ft.Switch(value=False, active_color="green700")

        def go_back(e):
            profile_page(email)

        def on_save_prefs(e):
            if current_user["id"]:
                update_user_preferences(
                    user_id=current_user["id"],
                    irrigation_alerts=daily_switch.value,
                    weekly_reports=weekly_switch.value
                )

        def notif_row(label, subtitle, switch_ctrl):
            return ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(spacing=2, controls=[
                            ft.Text(label,    size=14, color="grey900"),
                            ft.Text(subtitle, size=11, color="grey500"),
                        ]),
                        switch_ctrl,
                    ],
                ),
                padding=ft.Padding(left=20, right=16, top=12, bottom=12),
            )

        switch_pages([
            appbar("Notifications", back_bttn=go_back),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=20, bottom=20),
                content=ft.Column(scroll=ft.ScrollMode.AUTO, spacing=16, controls=[
                    card(ft.Column(spacing=0, controls=[
                        ft.Container(content=ft.Text("Alerts", size=12, color="grey500", weight="bold"), padding=ft.Padding(left=20, right=0, top=12, bottom=4)),
                        notif_row("Daily Irrigation Alert", "Every morning at 7:00 AM",   daily_switch),
                        ft.Divider(color="green100", height=1),
                        notif_row("Rain Alerts",            "When heavy rain is forecast", rain_switch),
                    ]), padding=0),
                    card(ft.Column(spacing=0, controls=[
                        ft.Container(content=ft.Text("Updates", size=12, color="grey500", weight="bold"), padding=ft.Padding(left=20, right=0, top=12, bottom=4)),
                        notif_row("Weekly Summary", "Every Sunday evening",       weekly_switch),
                        ft.Divider(color="green100", height=1),
                        notif_row("Farming Tips",   "Weekly tips from Soilco AI", tips_switch),
                    ]), padding=0),
                    green_btn("Save Preferences", on_save_prefs, width=320),
                    ft.Text("* push notifications require the mobile app", size=11, color="grey400", italic=True),
                ]),
            ),
        ])

    # edit profile
    def show_edit_profile(email):
        name_field     = ft.TextField(label="Full Name",       prefix_icon=ft.Icons.PERSON_OUTLINE,       border_radius=15, border_color="green700", focused_border_color="green900", bgcolor="white")
        phone_field    = ft.TextField(label="Phone Number",    prefix_icon=ft.Icons.PHONE_OUTLINED,       border_radius=15, border_color="green700", focused_border_color="green900", keyboard_type=ft.KeyboardType.PHONE, bgcolor="white")
        farm_field     = ft.TextField(label="Farm Name",       prefix_icon=ft.Icons.GRASS,                border_radius=15, border_color="green700", focused_border_color="green900", bgcolor="white")
        location_field = ft.TextField(label="Location (City)", prefix_icon=ft.Icons.LOCATION_ON_OUTLINED, border_radius=15, border_color="green700", focused_border_color="green900", bgcolor="white",
                                      value=current_location["city"])
        status = ft.Text("", size=13, text_align=ft.TextAlign.CENTER)

        def on_save(e):
            new_city = location_field.value.strip() if location_field.value else ""
            if new_city:
                current_location["city"] = new_city
                # geocode the new city and update lat/lon for weather and analysis
                def update_coords():
                    lat, lon = get_coords_from_city(new_city)
                    if lat and lon:
                        current_location["lat"] = lat
                        current_location["lon"] = lon
                        print(f"location updated: {new_city} → {lat}, {lon}")
                threading.Thread(target=update_coords, daemon=True).start()

            # update_profile saves to supabase using real user_id
            if current_user["id"]:
                update_profile(
                    user_id=current_user["id"],
                    full_name=name_field.value or "",
                    phone=phone_field.value or "",
                    farm_name=farm_field.value or "",
                    location=new_city,
                )

            status.value = "Profile updated successfully"
            status.color = "green700"
            page.update()

        def go_back(e):
            profile_page(email)

        switch_pages([
            appbar("Edit Profile", back_bttn=go_back),
            ft.Container(expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=20, bottom=20),
                content=ft.Column(scroll=ft.ScrollMode.AUTO, spacing=16,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        card(ft.Column(spacing=14, controls=[
                            ft.Text("Personal Info", size=14, weight="bold", color="green900"),
                            ft.Divider(color="green100"),
                            name_field, phone_field, farm_field, location_field,
                        ])),
                        green_btn("Save Changes", on_save, width=320), status,
                    ])),
        ])

    # change password
    def show_change_password(email=""):
        current_field = ft.TextField(label="Current Password",     prefix_icon=ft.Icons.LOCK_OUTLINE, password=True, can_reveal_password=True, border_radius=15, border_color="green700", focused_border_color="green900", bgcolor="white")
        new_field     = ft.TextField(label="New Password",         prefix_icon=ft.Icons.LOCK_OPEN,    password=True, can_reveal_password=True, border_radius=15, border_color="green700", focused_border_color="green900", bgcolor="white")
        confirm_field = ft.TextField(label="Confirm New Password", prefix_icon=ft.Icons.LOCK_OPEN,    password=True, can_reveal_password=True, border_radius=15, border_color="green700", focused_border_color="green900", bgcolor="white")
        status        = ft.Text("", size=13, text_align=ft.TextAlign.CENTER)

        def on_save(e):
            fields_empty    = not current_field.value or not new_field.value or not confirm_field.value
            passwords_match = new_field.value == confirm_field.value
            if fields_empty:
                status.value = "Please fill in all fields"
                status.color = "red"
            elif not passwords_match:
                status.value = "New passwords do not match"
                status.color = "red"
            else:
                result = update_password(new_field.value)
                if result["success"]:
                    status.value = "Password updated successfully"
                    status.color = "green700"
                else:
                    status.value = result.get("error", "update failed")
                    status.color = "red"
            page.update()

        def go_back(e):
            profile_page(email)

        switch_pages([
            appbar("Change Password", back_bttn=go_back),
            ft.Container(expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=20, bottom=20),
                content=ft.Column(scroll=ft.ScrollMode.AUTO, spacing=16,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        card(ft.Column(spacing=14, controls=[
                            ft.Text("Update Password", size=14, weight="bold", color="green900"),
                            ft.Divider(color="green100"),
                            current_field, new_field, confirm_field,
                        ])),
                        green_btn("Save Password", on_save, width=320), status,
                    ])),
        ])

    # profile
    def profile_page(email=""):
        farmer_name = current_user["name"] or email.split("@")[0].capitalize() if email else "Farmer"
        user_email  = email or "farmer@soilco.app"

        def go_edit_profile(e):
            show_edit_profile(email)

        def go_change_password(e):
            show_change_password(email)

        def go_notifications(e):
            show_notifications(email)

        def go_logout(e):
            sign_out()
            current_user["id"]    = ""
            current_user["email"] = ""
            current_user["name"]  = ""
            current_location["city"] = "Abuja"
            current_location["lat"]  = 9.0643305
            current_location["lon"]  = 7.4892974
            login_page()

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

        switch_pages([
            appbar("Profile"),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                content=ft.Column(scroll=ft.ScrollMode.AUTO, spacing=0, controls=[
                    ft.Container(
                        content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10, controls=[
                            ft.Container(content=ft.Icon(ft.Icons.PERSON, color="white", size=52),
                                bgcolor="green700", border_radius=50, width=100, height=100, alignment=ft.Alignment(0, 0)),
                            ft.Text(farmer_name, size=20, weight="bold", color="green900"),
                            ft.Text(user_email,  size=12,               color="grey600"),
                            ft.Row(spacing=6, alignment=ft.MainAxisAlignment.CENTER, controls=[
                                ft.Icon(ft.Icons.LOCATION_ON, color="green600", size=14),
                                ft.Text(current_location["city"], size=12, color="grey500"),
                            ]),
                        ]),
                        bgcolor="white", padding=ft.Padding(top=28, bottom=24, left=0, right=0), width=page.window.width),
                    ft.Container(content=ft.Text("Account Settings", size=13, color="grey500", weight="bold"),
                        padding=ft.Padding(left=16, right=0, top=4, bottom=6)),
                    ft.Container(
                        content=ft.Column(spacing=0, controls=[
                            setting_row(ft.Icons.PERSON_OUTLINE, "Edit Profile",    go_edit_profile),
                            ft.Divider(color="green100", height=1),
                            setting_row(ft.Icons.LOCK_OUTLINE,   "Change Password", go_change_password),
                            ft.Divider(color="green100", height=1),
                            setting_row(ft.Icons.NOTIFICATIONS,  "Notifications",   go_notifications),
                        ]),
                        bgcolor="white", border_radius=16,
                        margin=ft.Margin(left=16, right=16, top=0, bottom=14),
                        shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color=ft.Colors.with_opacity(0.06, "green900"))),
                    ft.Container(
                        content=ft.Row(spacing=12, alignment=ft.MainAxisAlignment.CENTER, controls=[
                            ft.Icon(ft.Icons.LOGOUT, color="red600", size=20),
                            ft.Text("Logout", size=14, color="red600", weight="bold"),
                        ]),
                        bgcolor="white", border_radius=16,
                        margin=ft.Margin(left=16, right=16, top=0, bottom=80),
                        padding=ft.Padding(left=20, right=20, top=14, bottom=14),
                        on_click=go_logout, ink=True,
                        shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color=ft.Colors.with_opacity(0.06, "green900"))),
                ]),
            ),
            nav_bar("Profile", email),
        ])

    # start
    splash_screen()


if __name__ == "__main__":
    ft.run(main)