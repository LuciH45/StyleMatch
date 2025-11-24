from .interfaces import ReportGenerator

class ExcelReportGenerator(ReportGenerator):
    def generate(self, cart_data):
        """
        Lógica simulada que devuelve contenido estilo CSV/Excel.
        """
        rows = ["Producto, Cantidad, Precio Total"]
        for item in cart_data["items"]:
            rows.append(f"{item['name']},{item['quantity']},{item['total_price']}")
        rows.append(f"TOTAL,,{cart_data['total_price']}")
        return "\n".join(rows)
