class ReportService:
    def __init__(self, generator):
        self.generator = generator

    def build_report(self, cart):
        """
        Convierte el carrito en dict y genera reporte usando
        la implementación inyectada.
        """
        cart_data = cart.as_dict()
        return self.generator.generate(cart_data)
