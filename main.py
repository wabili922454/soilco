import flet as ft

def main(page: ft.Page):
    page.title = "Soilco Analysis"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # UI Elements
    title = ft.Text("Soilco Dashboard", size=30, weight="bold", color="green")
    ph_input = ft.TextField(label="Soil pH", width=300, border_radius=10)
    result = ft.Text("", size=20)

    def on_analyze(e):
        try:
            val = float(ph_input.value)
            if 6.0 <= val <= 7.0:
                result.value = f"Analysis: {val} pH is Optimal!"
                result.color = "blue"
            else:
                result.value = "Analysis: Needs Adjustment"
                result.color = "red"
        except ValueError:
            result.value = "Please enter a valid number"
            result.color = "orange"
        page.update()

    page.add(
        title,
        # FIXED: Removed 'name=' and just passed the icon constant
        ft.Icon(ft.Icons.GRASS, color="green", size=50),
        ph_input,
        ft.ElevatedButton("Run Soil Test", on_click=on_analyze),
        result
    )

# UPDATED: Use run() instead of app()
ft.run(main)