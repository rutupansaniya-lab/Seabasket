# controllers/address_controller.py
from fastapi import HTTPException, status
from models.address_table import Address

class AddressController:

    def add_address(address_data, db, user):
        user_id = user.get('id')

        # Check if address already exists for this user
        address_query = db.query(Address).filter(Address.userId == user_id).first()

        if address_query is not None:
            raise HTTPException(status_code=422, detail="User already has an address")
        
        new_address = Address(
            userId=user_id,
            addressLine1=address_data.addressLine1
        )
        
        db.add(new_address)
        db.commit()
        db.refresh(new_address)
        
        return {
            "message": "Address added successfully",
            "address_id": new_address.id
        }

    def get_addresses(db, user):
        user_id = user.get('id')
        address = db.query(Address).filter(Address.userId == user_id).first()
        
        return {
            "addresses": address
        }

    def update_address(address_data, db, user):
        user_id = user.get('id')
        
        address_record = db.query(Address).filter(
            Address.userId == user_id
        ).first()
        
        if not address_record:
            raise HTTPException(status_code=404, detail="Address not found or does not belong to the user")
        
        address_record.addressLine1 = address_data.addressLine1
        db.commit()
        db.refresh(address_record)
        
        return {
            "message": "Address updated successfully",
            "updated_address": address_record
        }