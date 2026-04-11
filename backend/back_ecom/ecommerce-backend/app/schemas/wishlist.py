from datetime import datetime


class WishlistSchema:
    def __init__(
        self,
        userId: str,
        productId: str
    ):
        self.userId = userId
        self.productId = productId
        self.addedAt = datetime.utcnow()
    
    def to_dict(self):
        return {
            "userId": self.userId,
            "productId": self.productId,
            "addedAt": self.addedAt
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            userId=data["userId"],
            productId=data["productId"]
        )
