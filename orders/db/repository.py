from abc import ABC, abstractmethod

# TODO: This should be independent of sqlalchemy and order DB model

class OrderSrvRepo(ABC):
    """ This class contains only behaviour ie the methods that each concrete 
    sub-class must implement. The details of injecting a query engine(having DB
    connection etc.) is the responsibility of the concrete sub-class.
    """
    @abstractmethod
    def create_order(self, order):
        """Accepts order details in an Order object. Creates a new Order in the 
        database.
        """
        pass

    @abstractmethod
    def get_order_by_id(self, order_id):
        """Accepts a unique identifier for an order. It queries the database 
        using the id and returns the Order.
        """
        pass

    # @abstractmethod
    # def delete_order(self, order_id):
    #     pass
    #
    # @abstractmethod
    # def get_all_orders(self):
    #     pass


