import flet as ft


def main(page: ft.Page):
    page.title = "Soilco"
    page.window.width = 390
    page.window.height = 844
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = ft.Padding(top=0, left=0, right=0, bottom=0)
    page.bgcolor = "#f0f7f0"

    # ─────────────────────────────────────────
    # LOGIN SCREEN
    # ─────────────────────────────────────────
    def login_view():
        email_field = ft.TextField(
            label="Email",
            prefix_icon=ft.Icons.EMAIL_OUTLINED,
            width=320,
            border_radius=15,
            border_color="green700",
            focused_border_color="green900",
            keyboard_type=ft.KeyboardType.EMAIL,
            bgcolor="white",
        )
        password_field = ft.TextField(
            label="Password",
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True,
            can_reveal_password=True,
            width=320,
            border_radius=15,
            border_color="green700",
            focused_border_color="green900",
            bgcolor="white",
        )
        status = ft.Text("", size=14)

        def on_login(e):
            if not email_field.value or not password_field.value:
                status.value = "❌ Please fill in all fields"
                status.color = "red"
                page.update()
            else:
                page.go("/home")

        return ft.View(
            "/",
            bgcolor="#f0f7f0",
            padding=ft.Padding(top=0, left=0, right=0, bottom=0),
            controls=[
                ft.Container(
                    expand=True,
                    bgcolor="#f0f7f0",
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=0,
                        controls=[
                            ft.Container(
                                content=ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=6,
                                    controls=[
                                        ft.Container(
                                            content=ft.Icon(ft.Icons.GRASS_ROUNDED, color="white", size=60),
                                            bgcolor="green700",
                                            border_radius=30,
                                            padding=20,
                                        ),
                                        ft.Text("Soilco", size=36, weight="bold", color="green800"),
                                        ft.Text("Smart Soil Analysis", size=14, color="green600"),
                                    ],
                                ),
                                padding=ft.Padding(top=60, bottom=40, left=0, right=0),
                            ),
                            ft.Container(
                                content=ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=16,
                                    controls=[
                                        ft.Text("Welcome Back", size=22, weight="bold", color="green900"),
                                        email_field,
                                        password_field,
                                        ft.Container(
                                            content=ft.TextButton(
                                                "Forgot Password?",
                                                on_click=lambda e: page.go("/forgot"),
                                                style=ft.ButtonStyle(color="green700"),
                                            ),
                                            alignment=ft.Alignment(1, 0),
                                            width=320,
                                        ),
                                        ft.Button(
                                            "Login",
                                            on_click=on_login,
                                            width=320,
                                            height=50,
                                            style=ft.ButtonStyle(
                                                bgcolor="green700",
                                                color="white",
                                                shape=ft.RoundedRectangleBorder(radius=15),
                                                text_style=ft.TextStyle(size=16, weight="bold"),
                                            ),
                                        ),
                                        status,
                                        ft.Divider(color="green200"),
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            controls=[
                                                ft.Text("Don't have an account?", color="grey700"),
                                                ft.TextButton(
                                                    "Sign Up",
                                                    on_click=lambda e: page.go("/signup"),
                                                    style=ft.ButtonStyle(color="green700"),
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                bgcolor="white",
                                border_radius=25,
                                padding=30,
                                margin=ft.Margin(left=20, right=20, top=0, bottom=40),
                                shadow=ft.BoxShadow(
                                    spread_radius=1,
                                    blur_radius=20,
                                    color=ft.Colors.with_opacity(0.1, "green900"),
                                ),
                            ),
                        ],
                    ),
                )
            ],
        )

    # ─────────────────────────────────────────
    # HOME SCREEN (after login)
    # ─────────────────────────────────────────
    def home_view():
        return ft.View(
            "/home",
            bgcolor="#f0f7f0",
            controls=[
                ft.AppBar(
                    title=ft.Text("Soilco", color="white", weight="bold"),
                    bgcolor="green700",
                    automatically_imply_leading=False,
                ),
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text("🌱 Home Screen", size=24, color="green800", weight="bold"),
                ),
            ],
        )

    # ─────────────────────────────────────────
    # SIGN UP SCREEN
    # ─────────────────────────────────────────
    def signup_view():
        return ft.View(
            "/signup",
            bgcolor="#f0f7f0",
            controls=[
                ft.AppBar(
                    title=ft.Text("Sign Up", color="white", weight="bold"),
                    bgcolor="green700",
                    leading=ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_color="white",
                        on_click=lambda e: page.go("/"),
                    ),
                ),
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text("📝 Sign Up Screen", size=24, color="green800", weight="bold"),
                ),
            ],
        )

    # ─────────────────────────────────────────
    # FORGOT PASSWORD SCREEN
    # ─────────────────────────────────────────
    def forgot_view():
        return ft.View(
            "/forgot",
            bgcolor="#f0f7f0",
            controls=[
                ft.AppBar(
                    title=ft.Text("Forgot Password", color="white", weight="bold"),
                    bgcolor="green700",
                    leading=ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_color="white",
                        on_click=lambda e: page.go("/"),
                    ),
                ),
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text("🔑 Forgot Password Screen", size=24, color="green800", weight="bold"),
                ),
            ],
        )

    # ─────────────────────────────────────────
    # ROUTING
    # ─────────────────────────────────────────
    def route_change(e):
        page.views.clear()
        if page.route == "/" or page.route == "/login":
            page.views.append(login_view())
        elif page.route == "/home":
            page.views.append(home_view())
        elif page.route == "/signup":
            page.views.append(signup_view())
        elif page.route == "/forgot":
            page.views.append(forgot_view())
        page.update()

    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/")


if __name__ == "__main__":
    ft.run(main)