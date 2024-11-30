# Copyright (c) 2024, kusum and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.docstatus import DocStatus
from datetime import datetime

class LibraryMembership(Document):
    def before_submit(self):
        # Get today's date
        today = datetime.today().date()

        # Convert from_date and to_date to datetime.date if they are not already in date format
        if self.from_date and self.to_date:
            from_date = self._get_date(self.from_date)
            to_date = self._get_date(self.to_date)

            # Check if from_date is before or on today, and to_date is after from_date
            if from_date <= today and to_date > today:
                pass  # Allow submission if to_date is in the future and from_date is valid
            else:
                frappe.throw("The 'to_date' must be a future date to submit the membership.")
        
        # Check if there's an existing active membership
        exists = frappe.db.exists(
            "Library Membership",
            {
                "library_member": self.library_member,
                "docstatus": DocStatus.submitted(),
                "from_date": ("<=", today),  # Check if membership's 'from_date' is before or on today
                "to_date": (">", self.from_date),  # Ensure no active membership after this date
            },
        )
        
        if exists:
            frappe.throw("There is an active membership for this member.")

        loan_period = frappe.db.get_single_value("Library Settings", "loan_period")
        self.to_date = frappe.utils.add_days(self.from_date, loan_period or 30)

    

    def _get_date(self, date_field):
        """Helper function to convert the date field to datetime.date if it's in string format"""
        if isinstance(date_field, str):
            return datetime.strptime(date_field, "%Y-%m-%d").date()
        elif isinstance(date_field, datetime):
            return date_field.date()
        return date_field  # Assumes it's already a datetime.date object

    
    










