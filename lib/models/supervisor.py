class Supervisor(Employee):
    
    all = []
    
    def __init__(
        self,
        first_name: str,
        last_name: str,
        employee_id: int = None,
        product_line: str = None
    ):
        self.employee_id = employee_id
        self.supervisor_id = supervisor_id
        self.product_line = product_line
        Supervisor.all.append(self)
        
    def __str__(self):
        return f"{type(self).__name__}"
        
    @property
    def employee_id(self):
        return self._employee_id
    
    @employee_id.setter
    def employee_id(self, employee_id):
        validate_id(employee_id, str, 1, 20)
        self._employee_id = employee_id
    
    @property
    def product_line(self):
        return self._product_line
    
    @product_line.setter
    def product_line(self, product_line):
        validate_product_line(product_line)
        self._product_line = product_line