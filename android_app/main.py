
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window

Window.clearcolor = (0.04, 0.06, 0.10, 1)


class TradingApp(App):

    def build(self):
        root = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        title = Label(
            text="[b]BINANCE AI TRADING BOT[/b]",
            markup=True,
            font_size="23sp",
            size_hint_y=0.18
        )
        root.add_widget(title)

        status = Label(
            text="[b]PAPER TRADING ACTIVE[/b]",
            markup=True,
            color=(0.2, 1, 0.5, 1),
            font_size="18sp"
        )
        root.add_widget(status)

        dashboard = GridLayout(
            cols=1,
            spacing=12
        )

        self.balance = Label(
            text="Balance: 100.00 USDT",
            font_size="22sp"
        )
        dashboard.add_widget(self.balance)

        dashboard.add_widget(
            Label(text="Trading pair: BTC/USDT", font_size="19sp")
        )

        dashboard.add_widget(
            Label(text="Strategy: Aggressive", font_size="19sp")
        )

        dashboard.add_widget(
            Label(text="Mode: Simulation only", font_size="17sp")
        )

        dashboard.add_widget(
            Label(
                text="Market feed: Not connected",
                font_size="16sp"
            )
        )

        root.add_widget(dashboard)

        button = Button(
            text="PAPER TRADING DASHBOARD",
            size_hint_y=0.2,
            font_size="18sp"
        )
        button.bind(
            on_press=lambda instance: setattr(
                self.balance,
                "text",
                "Balance: 100.00 USDT"
            )
        )

        root.add_widget(button)

        footer = Label(
            text="No real-money orders are enabled.",
            font_size="13sp",
            size_hint_y=0.12
        )
        root.add_widget(footer)

        return root


if __name__ == "__main__":
    TradingApp().run()

