from abc import ABC, abstractmethod

class ReportGenerator(ABC):
    
    @abstractmethod
    def generate(self, cart_data):
        """Genera un reporte a partir de los datos del carrito."""
        pass
