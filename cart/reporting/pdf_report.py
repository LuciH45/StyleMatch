from .interfaces import ReportGenerator

class PdfReportGenerator(ReportGenerator):
    def generate(self, cart_data):
        """
        Lógica simple simulada que no genera PDF real,
        solo devuelve un string simulando el proceso.
        """
        content = "REPORTE PDF\n\n"
        for item in cart_data["items"]:
            content += f"- {item['name']} x{item['quantity']} = {item['total_price']}\n"
        content += f"\nTOTAL: {cart_data['total_price']}"
        return content
