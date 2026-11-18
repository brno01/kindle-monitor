"""Icones pre-rasterizados (GERADO por tools/gerar_icones.py: nao edite a mao).

Origem de cada icone (do comentario <!-- Source: ... --> do SVG em tools/icones/):
- claude: https://cdn.jsdelivr.net/npm/simple-icons@16.38.0/icons/claude.svg (simple-icons 16.38.0). SVG file CC0 (Simple Icons); Claude is a trademark of Anthropic - private, non-public dashboard use only.

Formato: ICONES[nome][tamanho_px] = {"w": int, "h": int, "dados": (<base64 de zlib de w*h bytes de cobertura 0-255>)}
"""
ICONES = {
    'claude': {
        56: {
            "w": 56,
            "h": 56,
            "dados": (
                'eNqVVi1w6kAQjohARCAqIioiKhCICAQCEYGoQCAqEBUIBKICgUAgIiIQCGb6ZtqZdgaBQCAQTyAQERURiAgEAhGBQCAQEYgT927v'
                'h1x+aHgryO0d393ud/tziiJLP9i79djMg3KH1BHGGD1JM2/hzsyFaUcM8hXNWETdFvJwDxSGL/p1xgU9/8A9A46uE1Qt5uLeGe4k'
                'LDOols/LY8iAHa6XQfHEqj531zfo7TGcL9GCZ1wpHYiyyMapPgPWmNqC8YCfdqArL9lAi+GWTOvCuMFgO7YykP/9bNtlPlywZca9'
                'DUPqksYNwRUJViF0oB6n8CIdCPwG1H6Xww7ycUv2V40qjnTgQjDxzWHIknFjNrkvS8G2hvGGDPrk2+Ew/BYjo8Fnw1fQ2kyBnU/k'
                'S9LDQvwP0wSLjtjvj3q9C5cczaLMOPJVPxXh1oEvbQySTWxYp+GyV9SNMOcpIxVWYrGlKCseNBalZSSMybxy1RZOfBbKbNh8JT/D'
                'uoBNbgR1lUcE3pa/6HcODH0L5zbqrWwoOPzIkPF0HOJIzsYveWR6WJajNG7FnEp52b/gTFmLP5it0TLA8xS1JS8LhkpgTXfqC/K8'
                'NLF9lHFcw1mH8sRH2lbF9HGe7EwHoWDrLqcju92yKgZNNtX5BYL8SZMUyiA5H/jr6fSUjdnPezUeoxbCdwnyJs1YMav2bPtjOnPd'
                'TRDcuAS8si0tv4pqRuUcxx327moKYg/aTats3Ai5p3mO0V5W0BXHSXNPYy/BQjoV1R6zMcboRNGeHVfezk/Amqwlndrb2P4L8Eit'
                '9pfC8SCGqvAyOdP/JtJhIUpLqbs444sj9zZjxtlrKBPYUk4//CNdRFXPSqHPIu0nqEaqrkftogsbPZN744cbTupmOaRNl4T3qE/z'
                'twsTuyzy2yxL0ISYo0Gh8VWFnNVTKU/TCvh6LKVg/KJ3VaGEJfpKaCkvdKGhQxE915IViR3mUNKoaW3iPSv2lOJDUYMeEzYSVRes'
                '9M0oQaARvJEvCYvShXcG6D7oNQ6szYYtFqyP4MkWSIdbgS+7DnJSB3bo3Wjw4EdIGxph5xL1/AO5aXMfe9zI8s2dI+F9jSYTiR6m'
                'kQ6LspKoE3W5OutlUV+lnPRQkPFcq1yiiIKnzJzTfbWU5GZGMytAkdrxkAVa3kUwh9GD5MZraSfCEBJpKFa68usrJR8klh5FkbkS'
                'dH3WdG/hiuPFNQRpu3yOlkazTkG5Qwb3vVhTQqNE/3+cfkk8qu6V+nH5m5n/AJWh7FI='
            ),
        },
        40: {
            "w": 40,
            "h": 40,
            "dados": (
                'eNqNVB+wMlEUv7AQLATBQrAQBEEQBEEQBEEQPAiCBwsLwYMHHwRBsNDM92Z6M8FC0DcTBEEQBEHwYCEIgoWFIAiChQvnO/fs3rat'
                '3Zl3YPfcc3733POfsZAyW+/UlAelrbAUGgPAOdQqP7BOw+0RB52AbyNbSsGNBG4X8BayagquxAWwTLwN4AZSwzYTDdrEbgFW0jCv'
                'PuEyHuJ8TbAOgCX+fXF1LgHa8JO0XSEdC84F6EoB9CVuhwmphkxgMAi3Rh7f8hKHt4EbyFSE/JuxPMIVpp3hIVVIf+k8UylO4AXW'
                'AHCYsiOxFQWgjumBQ4lpPoVsAEzZF8E2sfrV6AnfYAMyiF/zjWBeLp4TbUPiJfk0xay938SZ117KYZLC+ye6wYaQPhPqpm+lFq7h'
                'fycrUK68moyIFxnLtv4sRd6WKSYF7fvzk+RX1cF7q6JnU0yG5FhFqbi47n4+MqxniLcctEUpe8kWiI6TNz1qJ13XS/VWrz9AstcR'
                'yh31kLr1ip55SU55n2z5KzYFeftRtzDn3v1gR6jsUHTB6ueuwwbVu5NDEM59sg1R2mvvA2XxsmU7k9O37If6kZ7KNzhcLPD90K2n'
                'raDQrF06TL8Ab0zBEecxXl3E/C+QT7McU3HQBmwNGxWduNWwo3ePQFFWr4XMjBr4iNH1RH2zC+xyLcItMW5RYRN7T2Mqh2Fw94MN'
                'sSgRUCnQr8LROcaaQUYwFF9n7St4xXgwOU84R/tDDDkmCLaId55WnLIJpwtLXBdnUUJcQplxvPtxyA4U3AWAXipgJ51fOiDPQ49x'
                'GUCQfTNpC+qOW5S7lIeyuWcnrGnlvktd9gvCpbH/DS6zPjYTxP8BVzWIoQ=='
            ),
        },
        30: {
            "w": 30,
            "h": 30,
            "dados": (
                'eNp1Uy1wo0AUfgKBQCAiIiIQFYiIiIiKCGRERURExQkEoqICURGRmUOcqIjoTDpzN9POcDMVFREnIiIiEBEnEBERCEREBAKBQCAQ'
                '371lD0Iuc59gv7ff+9m3byGq4J72ZkW0J4P+RacE/Ip9YHulKilQ6IIlOFyp5AGYCwKsxDILrJaqJ0CiEhmAJ52PqhScIX+/cLBD'
                'ZAITIpuNowx7Q+nysgNihSygS1YpXQUWTNcd6vOWTQ5OZHAV/Kq7CdhIx+SL4GestT3bkd60M+Owct4tANfHgr2Qm60TDyPeWb1y'
                'yAYhU9xftKsuOJxjIUoC7zLnTaPfRmiQddSR+3EoEWqddrhEupe0XJ7YNQ5W/mJu/0QLp5U7Uun+cDyWuEAZvkx7F8fqGcbAq9U4'
                'CIKNv/QcpdG7fp0i/77/yz7rGXkFih+F3Nxq+vg5YCORnT1wn7tRhJ2Uw65owppWmc3fnO5R2WI3gy8aQnS+yQfOsTHoG7KeD+sT'
                'eNwiaeQYmU00EXMP0TdyZMY7kmE9gwmXucnxSkqBHj2J4dpFPjr3y0PdqzQA+Ig8pSkN4vCs+kh4Ig5S5oMCqUb6bSPeIe/zskRc'
                'HRMYty/SXFdVQgSV+fXt+nchSuVT/w9m2eWToT8sPW46'
            ),
        },
    },
}
