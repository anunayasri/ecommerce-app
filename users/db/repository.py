from abc import ABC, abstractmethod

# TODO: This should be independent of sqlalchemy and order DB model

class UserRepo(ABC):
    """ This class contains only behaviour ie the methods that each concrete 
    sub-class must implement. The details of injecting a query engine(having DB
    connection etc.) is the responsibility of the concrete sub-class.
    """
    @abstractmethod
    def create_user(self, user):
        """Accepts order details in an Order object. Creates a new Order in the 
        database.
        """
        pass

    @abstractmethod
    def get_user_by_username(self, username):
        """Accepts a unique identifier for a user. It queries the database 
        using the id and returns the user.
        """
        pass

