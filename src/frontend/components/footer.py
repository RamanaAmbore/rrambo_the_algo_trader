from dash import html


class FooterComponent:
    @staticmethod
    def create():
        return html.Footer(
            children=[
                html.Div(
                    children=[
                        html.Span("© 2025 Ramana Ambore, FRM, CFA Level 3 Candidate"),
                        html.Img(src="/assets/ramana.jpg", alt="Ramana Ambore")
                    ]
                )
            ]
        )
