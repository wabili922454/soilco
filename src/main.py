import flet as ft

def main(page: ft.Page):
    # 1. Setup - Modern Window sizing
    page.title = "Soilco"
    page.window.width = 390
    page.window.height = 844
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # 2. Modern Padding syntax (Padding.only instead of ft.padding.only)
    page.padding = ft.Padding(top=60, left=25, right=25, bottom=20)
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # 3. UI Elements
    title = ft.Text("Soilco Dashboard", size=28, weight="bold", color="green800")
    ph_input = ft.TextField(
        label="Enter Soil pH", 
        width=300, 
        border_radius=15
    )
    result = ft.Text("", size=18)

    def on_analyze(e):
        try:
            val = float(ph_input.value)
            result.value = f"✅ {val} pH is Optimal!" if 6.0 <= val <= 7.0 else "⚠️ Needs Adjustment"
            result.color = "blue" if 6.0 <= val <= 7.0 else "red"
        except:
            result.value = "❌ Enter a number"
        page.update()

    # 4. Building the UI (Using 'Button' instead of 'ElevatedButton')
    page.add(
        title,
        ft.Container(height=20),
        ft.Icon(ft.Icons.GRASS_ROUNDED, color="green", size=80),
        ph_input,
        ft.Button(
            "Run Soil Test", 
            on_click=on_analyze,
            width=200
        ),
        result
    )

# 5. Modern Start Command
if __name__ == "__main__":
    ft.run(main)