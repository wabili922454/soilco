import flet as ft


def main(page: ft.Page):
    page.title = "Soilco"
    page.window.width = 390
    page.window.height = 844
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = ft.Padding(top=0, left=0, right=0, bottom=0)
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = "#f0f7f0"

    def on_login(e):
        if not email_field.value or not password_field.value:
            status.value = "❌ Please fill in all fields"
            status.color = "red"
        else:
            status.value = f"✅ Welcome, {email_field.value}!"
            status.color = "green"
        page.update()

    def on_signup(e):
        status.value = "📝 Redirecting to Sign Up..."
        status.color = "green700"
        page.update()

    def on_forgot(e):
        status.value = "📧 Password reset link sent!"
        status.color = "orange"
        page.update()

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

    page.add(
        ft.Container(
            expand=True,
            bgcolor="#f0f7f0",
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=0,
                controls=[
                    # Logo area
                    ft.Container(
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=6,
                            controls=[
                                ft.Container(
                                    content=ft.Icon(
                                        ft.Icons.GRASS_ROUNDED,
                                        color="white",
                                        size=60,
                                    ),
                                    bgcolor="green700",
                                    border_radius=30,
                                    padding=20,
                                ),
                                ft.Text(
                                    "Soilco",
                                    size=36,
                                    weight="bold",
                                    color="green800",
                                ),
                                ft.Text(
                                    "Smart Soil Analysis",
                                    size=14,
                                    color="green600",
                                ),
                            ],
                        ),
                        padding=ft.Padding(top=60, bottom=40, left=0, right=0),
                    ),

                    # Card
                    ft.Container(
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=16,
                            controls=[
                                ft.Text(
                                    "Welcome Back",
                                    size=22,
                                    weight="bold",
                                    color="green900",
                                ),
                                email_field,
                                password_field,

                                # Forgot password
                                ft.Container(
                                    content=ft.TextButton(
                                        "Forgot Password?",
                                        on_click=on_forgot,
                                        style=ft.ButtonStyle(
                                            color="green700",
                                        ),
                                    ),
                                    alignment=ft.Alignment(1, 0),
                                    width=320,
                                ),

                                # Login button
                                ft.Button(
                                    "Login",
                                    on_click=on_login,
                                    width=320,
                                    height=50,
                                    style=ft.ButtonStyle(
                                        bgcolor="green700",
                                        color="white",
                                        shape=ft.RoundedRectangleBorder(radius=15),
                                        text_style=ft.TextStyle(
                                            size=16,
                                            weight="bold",
                                        ),
                                    ),
                                ),

                                status,

                                ft.Divider(color="green200"),

                                # Sign up row
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    controls=[
                                        ft.Text("Don't have an account?", color="grey700"),
                                        ft.TextButton(
                                            "Sign Up",
                                            on_click=on_signup,
                                            style=ft.ButtonStyle(
                                                color="green700",
                                            ),
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
    )


if __name__ == "__main__":
    ft.run(main)
