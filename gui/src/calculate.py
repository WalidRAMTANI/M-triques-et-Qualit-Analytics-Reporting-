import flet as ft

class CalcButton(ft.ElevatedButton):
    def __init__(self, text, expand=1, **kwargs):
        super().__init__(text=text, expand=expand, **kwargs)


class DigitButton(CalcButton):
    def __init__(self, text, **kwargs):
        super().__init__(
            text=text,
            bgcolor=ft.Colors.WHITE24,
            color=ft.Colors.WHITE,
            **kwargs
        )


class ActionButton(CalcButton):
    def __init__(self, text, **kwargs):
        super().__init__(
            text=text,
            bgcolor=ft.Colors.ORANGE,
            color=ft.Colors.WHITE,
            **kwargs
        )


class ExtraActionButton(CalcButton):
    def __init__(self, text, **kwargs):
        super().__init__(
            text=text,
            bgcolor=ft.Colors.BLUE_GREY_100,
            color=ft.Colors.BLACK,
            **kwargs
        )


class CalculatorApp(ft.Container):
    def __init__(self):
        # Display text
        result = ft.Text(value="10", color=ft.Colors.WHITE, size=20)

        # Initialize the parent Container with proper attributes
        super().__init__(
            width=350,
            bgcolor=ft.Colors.BLACK,
            border=ft.border.all(20),
            padding=20,
            content=ft.Column([
                ft.Row([result], alignment=ft.MainAxisAlignment.END),
                ft.Row(controls=[
                    ActionButton("AC", on_click=self.button_clicked),
                    ActionButton("+/-", on_click=self.button_clicked),
                    ActionButton("%", on_click=self.button_clicked),
                    ActionButton("/", on_click=self.button_clicked),
                ]),
                ft.Row(controls=[
                    DigitButton("7", on_click=self.button_clicked),
                    DigitButton("8", on_click=self.button_clicked),
                    DigitButton("9", on_click=self.button_clicked),
                    ActionButton("*", on_click=self.button_clicked),
                ]),
                ft.Row(controls=[
                    DigitButton("4", on_click=self.button_clicked),
                    DigitButton("5", on_click=self.button_clicked),
                    DigitButton("6", on_click=self.button_clicked),
                    ActionButton("-", on_click=self.button_clicked),
                ]),
                ft.Row(controls=[
                    DigitButton("1", on_click=self.button_clicked),
                    DigitButton("2", on_click=self.button_clicked),
                    DigitButton("3", on_click=self.button_clicked),
                    ActionButton("+", on_click=self.button_clicked),
                ]),
                ft.Row(controls=[
                    DigitButton("0", expand=2, on_click=self.button_clicked),
                    DigitButton(".", on_click=self.button_clicked),
                    ActionButton("=", on_click=self.button_clicked),
                ]),
            ]),
        )

    def button_clicked(self, e):
        data = e.control.content
        print(f"Button clicked with data = {data}")
        if data == "AC":
            self.result.value = "0"