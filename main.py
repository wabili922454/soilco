import flet as ft
import time
import threading


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
        controls = [
            ft.Icon(ft.Icons.GRASS_ROUNDED, color="white" if light else "green700", size=size),
        ]
        if show_text:
            controls += [
                ft.Text("Soilco", size=28, weight="bold", color="white" if light else "green800"),
                ft.Text("Smart Soil Analysis", size=12, color="#c8e6c9" if light else "green600"),
            ]
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
            controls=controls,
        )

    def switch(controls):
        page.controls.clear()
        for c in controls:
            page.controls.append(c)
        page.update()

    def show_irrigation_dialog(e):
        dialog = ft.AlertDialog(
            title=ft.Row(spacing=8, controls=[
                ft.Icon(ft.Icons.WATER_DROP, color="blue700", size=20),
                ft.Text("Daily Irrigation Alert", size=16, weight="bold", color="green900"),
            ]),
            content=ft.Container(
                width=300,
                content=ft.Column(spacing=12, tight=True, controls=[
                    ft.Container(
                        content=ft.Column(spacing=6, controls=[
                            ft.Row(spacing=8, controls=[
                                ft.Icon(ft.Icons.WB_SUNNY_OUTLINED, color="orange600", size=16),
                                ft.Text("Today's Weather", size=12, weight="bold", color="grey700"),
                            ]),
                            ft.Text("Temperature: -- °C", size=12, color="grey600"),
                            ft.Text("Rain forecast: -- mm", size=12, color="grey600"),
                            ft.Text("Humidity: --%", size=12, color="grey600"),
                        ]),
                        bgcolor="#f0f7f0", border_radius=10, padding=12,
                    ),
                    ft.Container(
                        content=ft.Column(spacing=6, controls=[
                            ft.Row(spacing=8, controls=[
                                ft.Icon(ft.Icons.WATER_DROP, color="blue700", size=16),
                                ft.Text("Adjusted Recommendation", size=12, weight="bold", color="grey700"),
                            ]),
                            ft.Text("Base irrigation: 0.0 mm/day", size=12, color="grey600"),
                            ft.Text("Weather adjustment: -- mm", size=12, color="grey600"),
                            ft.Text("Recommended today: -- mm", size=13, weight="bold", color="blue700"),
                        ]),
                        bgcolor="#e3f2fd", border_radius=10, padding=12,
                    ),
                    ft.Text(
                        "Connect a weather API and set your location to enable live daily recommendations.",
                        size=11, color="grey500", italic=True, text_align=ft.TextAlign.CENTER,
                    ),
                ]),
            ),
            actions=[
                ft.TextButton("Close", style=ft.ButtonStyle(color="green700"),
                    on_click=lambda e: close_it()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        def close_it():
            dialog.open = False
            page.update()

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # ─────────────────────────────────────────
    # SPLASH SCREEN
    # ─────────────────────────────────────────
    def show_splash():
        switch([
            ft.Container(
                expand=True,
                bgcolor="green700",
                alignment=ft.Alignment(0, 0),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=12,
                    controls=[logo(80, light=True)],
                ),
            )
        ])
        def go_to_login():
            time.sleep(2)
            show_login()
        threading.Thread(target=go_to_login, daemon=True).start()

    # ─────────────────────────────────────────
    # LOGIN SCREEN
    # ─────────────────────────────────────────
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
                        ft.Container(
                            content=ft.Column(
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
                                    ft.Button("Login", on_click=on_login, width=300, height=50,
                                        style=ft.ButtonStyle(bgcolor="green700", color="white",
                                            shape=ft.RoundedRectangleBorder(radius=15),
                                            text_style=ft.TextStyle(size=16, weight="bold"))),
                                    status,
                                    ft.Divider(color="green200"),
                                    ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
                                        ft.Text("Don't have an account?", color="grey700"),
                                        ft.TextButton("Sign Up", on_click=lambda e: show_signup(),
                                            style=ft.ButtonStyle(color="green700")),
                                    ]),
                                ],
                            ),
                            bgcolor="white", border_radius=25, padding=30,
                            margin=ft.Margin(left=20, right=20, top=0, bottom=40),
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=20,
                                color=ft.Colors.with_opacity(0.1, "green900")),
                        ),
                    ],
                ),
            )
        ])

    # ─────────────────────────────────────────
    # ANALYSIS RESULT SCREEN
    # ─────────────────────────────────────────
    def show_analysis(crop_name, email=""):
        irrigation_val = ft.Text("0.0 mm/day", size=20, weight="bold", color="green800")
        soil_type_val = ft.Text("Loamy", size=20, weight="bold", color="green800")
        weeks_val = ft.Text("0 weeks", size=20, weight="bold", color="green800")
        nitrogen_val = ft.Text("0.0 kg/ha", size=15, weight="bold", color="green700")
        phosphorus_val = ft.Text("0.0 kg/ha", size=15, weight="bold", color="green700")
        potassium_val = ft.Text("0.0 kg/ha", size=15, weight="bold", color="green700")

        # Irrigation alert dialog
        alert_text = ft.Text(
            "Based on today's weather and your location, no adjusted irrigation data is available yet. Connect a weather API to enable daily recommendations.",
            size=13, color="grey700", text_align=ft.TextAlign.CENTER,
        )
        irrigation_dialog = ft.AlertDialog(
            title=ft.Row(spacing=8, controls=[
                ft.Icon(ft.Icons.WATER_DROP, color="blue700", size=20),
                ft.Text("Daily Irrigation Alert", size=16, weight="bold", color="green900"),
            ]),
            content=ft.Container(
                width=300,
                content=ft.Column(spacing=12, tight=True, controls=[
                    ft.Container(
                        content=ft.Column(spacing=6, controls=[
                            ft.Row(spacing=8, controls=[
                                ft.Icon(ft.Icons.WB_SUNNY_OUTLINED, color="orange600", size=16),
                                ft.Text("Today's Weather", size=12, weight="bold", color="grey700"),
                            ]),
                            ft.Text("Temperature: -- °C", size=12, color="grey600"),
                            ft.Text("Rain forecast: -- mm", size=12, color="grey600"),
                            ft.Text("Humidity: --%", size=12, color="grey600"),
                        ]),
                        bgcolor="#f0f7f0", border_radius=10, padding=12,
                    ),
                    ft.Container(
                        content=ft.Column(spacing=6, controls=[
                            ft.Row(spacing=8, controls=[
                                ft.Icon(ft.Icons.WATER_DROP, color="blue700", size=16),
                                ft.Text("Adjusted Recommendation", size=12, weight="bold", color="grey700"),
                            ]),
                            ft.Text("Base irrigation: 0.0 mm/day", size=12, color="grey600"),
                            ft.Text("Weather adjustment: -- mm", size=12, color="grey600"),
                            ft.Text("Recommended today: -- mm", size=13, weight="bold", color="blue700"),
                        ]),
                        bgcolor="#e3f2fd", border_radius=10, padding=12,
                    ),
                    ft.Text(
                        "Connect a weather API and set your location to enable live daily recommendations.",
                        size=11, color="grey500", italic=True, text_align=ft.TextAlign.CENTER,
                    ),
                ]),
            ),
            actions=[
                ft.TextButton("Close", on_click=lambda e: close_dialog(),
                    style=ft.ButtonStyle(color="green700")),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        def open_dialog(e):
            page.overlay.append(irrigation_dialog)
            irrigation_dialog.open = True
            page.update()

        def close_dialog():
            irrigation_dialog.open = False
            page.update()

        def metric_card(title, value_widget, icon, color, extra=None):
            controls = [
                ft.Icon(icon, color=color, size=26),
                ft.Text(title, size=11, color="grey600"),
                value_widget,
            ]
            if extra:
                controls.append(extra)
            return ft.Container(
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6,
                    controls=controls,
                ),
                bgcolor="white", border_radius=20, padding=16, expand=True,
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=10,
                    color=ft.Colors.with_opacity(0.08, "green900")),
            )

        def fert_row(label, val):
            return ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[ft.Text(label, size=14, color="grey700"), val])

        switch([
            ft.AppBar(
                title=ft.Text(f"{crop_name} Analysis", color="white", weight="bold"),
                bgcolor="green700",
                leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color="white",
                    on_click=lambda e: show_home(email)),
            ),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=16, bottom=20),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO, spacing=16,
                    controls=[
                        ft.Container(
                            content=ft.Row(
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
                            ),
                            bgcolor="white", border_radius=20, padding=20,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10,
                                color=ft.Colors.with_opacity(0.08, "green900")),
                        ),
                        ft.Row(spacing=12, controls=[
                            metric_card(
                                "Irrigation", irrigation_val,
                                ft.Icons.WATER_DROP, "blue700",
                                extra=ft.Container(
                                    content=ft.Row(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=4,
                                        controls=[
                                            ft.Icon(ft.Icons.NOTIFICATIONS_OUTLINED, color="blue700", size=13),
                                            ft.Text("Daily Alert", size=11, color="blue700"),
                                        ],
                                    ),
                                    bgcolor="#e3f2fd", border_radius=8,
                                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                                    on_click=open_dialog, ink=True,
                                ),
                            ),
                            metric_card("Soil Type", soil_type_val, ft.Icons.LANDSCAPE, "brown400"),
                        ]),
                        ft.Container(
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Column(spacing=4, controls=[
                                        ft.Text("Expected Growth Time", size=12, color="grey600"),
                                        weeks_val,
                                    ]),
                                    ft.Icon(ft.Icons.SCHEDULE, color="green600", size=26),
                                ],
                            ),
                            bgcolor="white", border_radius=20, padding=20,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10,
                                color=ft.Colors.with_opacity(0.08, "green900")),
                        ),
                        ft.Container(
                            content=ft.Column(spacing=12, controls=[
                                ft.Text("Fertilizer Recommendation", size=16, weight="bold", color="green900"),
                                ft.Divider(color="green100"),
                                fert_row("Nitrogen (N)", nitrogen_val),
                                fert_row("Phosphorus (P)", phosphorus_val),
                                fert_row("Potassium (K)", potassium_val),
                            ]),
                            bgcolor="white", border_radius=20, padding=20,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10,
                                color=ft.Colors.with_opacity(0.08, "green900")),
                        ),
                    ],
                ),
            ),
        ])

    # ─────────────────────────────────────────
    # HOME SCREEN
    # ─────────────────────────────────────────
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

        # Placeholder previous crops
        previous_crops = [
            {"crop": "Maize", "date": "Feb 28", "weeks": "12", "status": "Optimal"},
            {"crop": "Wheat", "date": "Feb 20", "weeks": "8", "status": "Acidic"},
            {"crop": "Rice",  "date": "Feb 10", "weeks": "16", "status": "Alkaline"},
        ]

        def prev_crop_card(item):
            color = "green700" if item["status"] == "Optimal" else "orange700" if item["status"] == "Acidic" else "red600"
            return ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(spacing=12, controls=[
                            ft.Container(
                                content=ft.Icon(ft.Icons.GRASS, color="white", size=18),
                                bgcolor="green700", border_radius=10, padding=8,
                            ),
                            ft.Column(spacing=2, controls=[
                                ft.Text(item["crop"], size=14, weight="bold", color="green900"),
                                ft.Text(item["date"], size=11, color="grey500"),
                            ]),
                        ]),
                        ft.Column(horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2, controls=[
                            ft.Text(f"{item["weeks"]} weeks", size=13, weight="bold", color="green800"),
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
            )

        # Placeholder market prices
        market_crops = [
            {"name": "Maize",   "price": "0.00", "difficulty": "Easy",   "diff_color": "green600"},
            {"name": "Wheat",   "price": "0.00", "difficulty": "Medium", "diff_color": "orange600"},
            {"name": "Rice",    "price": "0.00", "difficulty": "Hard",   "diff_color": "red600"},
            {"name": "Soybean", "price": "0.00", "difficulty": "Easy",   "diff_color": "green600"},
            {"name": "Cotton",  "price": "0.00", "difficulty": "Hard",   "diff_color": "red600"},
        ]

        def market_row(item):
            return ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(spacing=10, controls=[
                            ft.Container(
                                content=ft.Icon(ft.Icons.GRASS, color="white", size=14),
                                bgcolor="green700", border_radius=8, padding=6,
                            ),
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
            ft.AppBar(
                title=ft.Text("Soilco", color="white", weight="bold"),
                bgcolor="green700",
                automatically_imply_leading=False,
                actions=[
                    ft.IconButton(icon=ft.Icons.MENU, icon_color="white",
                        on_click=lambda e: show_sidebar(email), tooltip="Menu")
                ],
            ),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                padding=ft.Padding(left=16, right=16, top=16, bottom=20),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO, spacing=16,
                    controls=[
                        # Header
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Column(spacing=2, controls=[
                                    ft.Text("Good day,", size=13, color="grey600"),
                                    ft.Text(email.split("@")[0].capitalize(), size=20,
                                        weight="bold", color="green900"),
                                ]),
                                ft.Icon(ft.Icons.GRASS_ROUNDED, color="green700", size=36),
                            ],
                        ),

                        # Weather widget (placeholder)
                        ft.Container(
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Column(spacing=4, controls=[
                                        ft.Text("Current Weather", size=12, color="#c8e6c9"),
                                        ft.Text("-- °C", size=32, weight="bold", color="white"),
                                        ft.Text("Location not set", size=12, color="#c8e6c9"),
                                    ]),
                                    ft.Column(
                                        horizontal_alignment=ft.CrossAxisAlignment.END,
                                        spacing=6,
                                        controls=[
                                            ft.Icon(ft.Icons.WB_SUNNY_OUTLINED, color="white", size=48),
                                            ft.Text("--", size=12, color="#c8e6c9"),
                                            ft.Row(spacing=8, controls=[
                                                ft.Row(spacing=2, controls=[
                                                    ft.Icon(ft.Icons.WATER_DROP_OUTLINED, color="#c8e6c9", size=12),
                                                    ft.Text("Humidity: --%", size=11, color="#c8e6c9"),
                                                ]),
                                            ]),
                                            ft.Row(spacing=2, controls=[
                                                ft.Icon(ft.Icons.AIR, color="#c8e6c9", size=12),
                                                ft.Text("Wind: -- km/h", size=11, color="#c8e6c9"),
                                            ]),
                                            ft.Row(spacing=2, controls=[
                                                ft.Icon(ft.Icons.UMBRELLA, color="#c8e6c9", size=12),
                                                ft.Text("Rain: -- mm", size=11, color="#c8e6c9"),
                                            ]),
                                        ],
                                    ),
                                ],
                            ),
                            bgcolor="green700",
                            border_radius=20, padding=20,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10,
                                color=ft.Colors.with_opacity(0.15, "green900")),
                        ),

                        # Crop analysis card
                        ft.Container(
                            content=ft.Column(spacing=12, controls=[
                                ft.Text("Crop Analysis", size=16, weight="bold", color="green900"),
                                crop_field,
                                ft.Button("Analyze", on_click=on_analyze, width=300, height=45,
                                    style=ft.ButtonStyle(bgcolor="green700", color="white",
                                        shape=ft.RoundedRectangleBorder(radius=12),
                                        text_style=ft.TextStyle(size=15, weight="bold"))),
                                status,
                            ]),
                            bgcolor="white", border_radius=20, padding=20,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10,
                                color=ft.Colors.with_opacity(0.08, "green900")),
                        ),

                        # Daily Alert card
                        ft.Container(
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Column(spacing=4, controls=[
                                        ft.Text("Daily Irrigation Alert", size=15, weight="bold", color="green900"),
                                        ft.Text("Weather-adjusted recommendation", size=11, color="grey500"),
                                    ]),
                                    ft.Container(
                                        content=ft.Row(spacing=4, controls=[
                                            ft.Icon(ft.Icons.NOTIFICATIONS_OUTLINED, color="white", size=14),
                                            ft.Text("View Alert", size=12, color="white", weight="bold"),
                                        ]),
                                        bgcolor="blue700", border_radius=10,
                                        padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                                        on_click=show_irrigation_dialog, ink=True,
                                    ),
                                ],
                            ),
                            bgcolor="white", border_radius=20, padding=20,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10,
                                color=ft.Colors.with_opacity(0.08, "green900")),
                        ),

                        # Market prices & AI difficulty
                        ft.Container(
                            content=ft.Column(spacing=0, controls=[
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
                            ]),
                            bgcolor="white", border_radius=20, padding=20,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10,
                                color=ft.Colors.with_opacity(0.08, "green900")),
                        ),

                        # Previous crops
                        ft.Column(spacing=10, controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("Previous Analyses", size=16, weight="bold", color="green900"),
                                    ft.TextButton("View All", style=ft.ButtonStyle(color="green600")),
                                ],
                            ),
                            *[prev_crop_card(c) for c in previous_crops],
                        ]),
                    ],
                ),
            ),
        ])

    # ─────────────────────────────────────────
    # SIDEBAR
    # ─────────────────────────────────────────
    def show_sidebar(email=""):
        def menu_item(icon, label, on_click=None):
            return ft.Container(
                content=ft.Row(spacing=16, controls=[
                    ft.Icon(icon, color="green700", size=22),
                    ft.Text(label, size=15, color="grey900"),
                ]),
                padding=ft.Padding(left=20, right=20, top=14, bottom=14),
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
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=8,
                    color=ft.Colors.with_opacity(0.06, "green900")),
            )

        switch([
            ft.AppBar(
                title=ft.Text("Menu", color="white", weight="bold"),
                bgcolor="green700",
                leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color="white",
                    on_click=lambda e: show_home(email)),
            ),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO, spacing=0,
                    controls=[
                        ft.Container(
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8,
                                controls=[
                                    ft.Container(
                                        content=ft.Icon(ft.Icons.PERSON, color="white", size=40),
                                        bgcolor="green700", border_radius=40, padding=20,
                                    ),
                                    ft.Text(email.split("@")[0].capitalize(), size=18,
                                        weight="bold", color="green900"),
                                    ft.Text(email, size=12, color="grey600"),
                                ],
                            ),
                            bgcolor="white",
                            padding=ft.Padding(top=24, bottom=24, left=0, right=0),
                            width=page.window.width,
                        ),
                        ft.Container(height=12),
                        section_label("Account"),
                        section_card([
                            menu_item(ft.Icons.PERSON_OUTLINE, "Edit Profile"),
                            divider(),
                            menu_item(ft.Icons.IMAGE_OUTLINED, "Profile Picture"),
                            divider(),
                            menu_item(ft.Icons.LOCK_OUTLINE, "Change Password"),
                        ]),
                        section_label("Preferences"),
                        section_card([
                            menu_item(ft.Icons.LOCATION_ON_OUTLINED, "Change Location"),
                            divider(),
                            menu_item(ft.Icons.LANGUAGE, "Change Region"),
                            divider(),
                            menu_item(ft.Icons.NOTIFICATIONS_OUTLINED, "Notifications"),
                            divider(),
                            menu_item(ft.Icons.DARK_MODE_OUTLINED, "Appearance"),
                        ]),
                        section_label("Support"),
                        section_card([
                            menu_item(ft.Icons.HELP_OUTLINE, "Help & FAQ"),
                            divider(),
                            menu_item(ft.Icons.FEEDBACK_OUTLINED, "Send Feedback"),
                            divider(),
                            menu_item(ft.Icons.INFO_OUTLINE, "About Soilco"),
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
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=8,
                                color=ft.Colors.with_opacity(0.06, "green900")),
                        ),
                    ],
                ),
            ),
        ])

    # ─────────────────────────────────────────
    # SIGN UP SCREEN
    # ─────────────────────────────────────────
    def show_signup():
        name_field = ft.TextField(label="Full Name", prefix_icon=ft.Icons.PERSON_OUTLINE,
            width=300, border_radius=15, border_color="green700",
            focused_border_color="green900", bgcolor="white")
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
            ft.AppBar(title=ft.Text("Sign Up", color="white", weight="bold"), bgcolor="green700",
                leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color="white",
                    on_click=lambda e: show_login())),
            ft.Container(
                expand=True, bgcolor="#f0f7f0",
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO, spacing=16,
                    controls=[
                        ft.Container(height=10),
                        logo(40),
                        ft.Container(
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16,
                                controls=[
                                    ft.Text("Create Account", size=20, weight="bold", color="green900"),
                                    name_field, email_field, password_field,
                                    ft.Button("Create Account", on_click=on_register, width=300, height=50,
                                        style=ft.ButtonStyle(bgcolor="green700", color="white",
                                            shape=ft.RoundedRectangleBorder(radius=15),
                                            text_style=ft.TextStyle(size=16, weight="bold"))),
                                    status,
                                    ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
                                        ft.Text("Already have an account?", color="grey700"),
                                        ft.TextButton("Login", on_click=lambda e: show_login(),
                                            style=ft.ButtonStyle(color="green700")),
                                    ]),
                                ],
                            ),
                            bgcolor="white", border_radius=25, padding=30,
                            margin=ft.Margin(left=20, right=20, top=0, bottom=30),
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=20,
                                color=ft.Colors.with_opacity(0.1, "green900")),
                        ),
                    ],
                ),
            ),
        ])

    # ─────────────────────────────────────────
    # FORGOT PASSWORD SCREEN
    # ─────────────────────────────────────────
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
            ft.AppBar(title=ft.Text("Forgot Password", color="white", weight="bold"), bgcolor="green700",
                leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color="white",
                    on_click=lambda e: show_login())),
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
                        ft.Container(
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16,
                                controls=[
                                    email_field,
                                    ft.Button("Send Reset Link", on_click=on_reset, width=300, height=50,
                                        style=ft.ButtonStyle(bgcolor="green700", color="white",
                                            shape=ft.RoundedRectangleBorder(radius=15),
                                            text_style=ft.TextStyle(size=16, weight="bold"))),
                                    status,
                                ],
                            ),
                            bgcolor="white", border_radius=25, padding=30,
                            margin=ft.Margin(left=20, right=20, top=0, bottom=20),
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=20,
                                color=ft.Colors.with_opacity(0.1, "green900")),
                        ),
                        ft.TextButton("Back to Login", on_click=lambda e: show_login(),
                            style=ft.ButtonStyle(color="green700")),
                    ],
                ),
            ),
        ])

    show_splash()


if __name__ == "__main__":
    ft.run(main)